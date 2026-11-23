import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState } from "react";
import { getConfig, getOverview, getPriorities, simulateRisk } from "../services/api";
import {
  cacheConfig,
  cacheOverview,
  cachePriorities,
  cacheSimulation,
  readCachedConfig,
  readCachedOverview,
  readCachedPriorities,
  readCachedSimulation,
  simulationRequestKey,
} from "../utils/cache";

const WorkbenchContext = createContext(null);

export const MODEL_SEED = 20261124;
export const MODEL_TRIALS = 10_000;
const DEFAULT_SCENARIO = "launch-ddos";
const DEFAULT_CONTROLS = [
  "managed-ddos-protection",
  "app-abuse-protection",
  "launch-resilience-testing",
  "launch-war-room",
];

export function WorkbenchProvider({ children }) {
  const [selectedScenarioId, setSelectedScenarioIdState] = useState(DEFAULT_SCENARIO);
  const [selectedControlIds, setSelectedControlIds] = useState(DEFAULT_CONTROLS);
  const [config, setConfig] = useState(null);
  const [overview, setOverview] = useState(null);
  const [priorities, setPriorities] = useState(null);
  const [results, setResults] = useState(null);
  const [status, setStatus] = useState("loading");
  const [error, setError] = useState("");
  const [lastUpdatedAt, setLastUpdatedAt] = useState(null);
  const [demoResetVersion, setDemoResetVersion] = useState(0);
  const activeRequestId = useRef(0);
  const resultsRef = useRef(null);
  const resultsKeyRef = useRef("");

  const seed = config?.model?.seed || MODEL_SEED;
  const trials = config?.model?.trials || MODEL_TRIALS;
  const selectedScenario = config?.scenarios.find((item) => item.id === selectedScenarioId) || null;
  const analysisMode = selectedScenario?.timeBasis || (selectedScenarioId === DEFAULT_SCENARIO ? "launch-event" : "annual");

  const loadConfig = useCallback(async () => {
    const cached = readCachedConfig();
    if (cached) setConfig((current) => current || cached.data);

    try {
      const nextConfig = await getConfig();
      setConfig(nextConfig);
      cacheConfig(nextConfig);
      return true;
    } catch (requestError) {
      if (!cached) setError(requestError.message);
      return false;
    }
  }, []);

  const loadSummaries = useCallback(async () => {
    const cachedOverview = readCachedOverview();
    const cachedPriorities = readCachedPriorities();
    if (cachedOverview) setOverview((current) => current || cachedOverview.data);
    if (cachedPriorities) setPriorities((current) => current || cachedPriorities.data);

    const [overviewResult, priorityResult] = await Promise.allSettled([getOverview(), getPriorities()]);
    if (overviewResult.status === "fulfilled") {
      setOverview(overviewResult.value);
      cacheOverview(overviewResult.value);
    }
    if (priorityResult.status === "fulfilled") {
      setPriorities(priorityResult.value);
      cachePriorities(priorityResult.value);
    }
  }, []);

  useEffect(() => {
    loadConfig();
    loadSummaries();
  }, [loadConfig, loadSummaries]);

  const setSelectedScenarioId = useCallback((scenarioId) => {
    setSelectedScenarioIdState(scenarioId);
    const scenario = config?.scenarios.find((item) => item.id === scenarioId);
    setSelectedControlIds(scenario?.recommendedControlIds || []);
  }, [config]);

  const runSimulation = useCallback(async () => {
    const payload = {
      scenarioId: selectedScenarioId,
      controlIds: selectedControlIds,
      trials,
      seed,
    };
    const requestKey = simulationRequestKey(payload);
    const requestId = activeRequestId.current + 1;
    activeRequestId.current = requestId;

    if (resultsKeyRef.current !== requestKey) {
      resultsRef.current = null;
      setResults(null);
    }
    setStatus(resultsKeyRef.current === requestKey && resultsRef.current ? "refreshing" : "loading");
    setError("");
    try {
      const nextResults = await simulateRisk(payload);
      if (activeRequestId.current !== requestId) return;
      resultsRef.current = nextResults;
      resultsKeyRef.current = requestKey;
      setResults(nextResults);
      setLastUpdatedAt(new Date().toISOString());
      cacheSimulation(payload, nextResults);
      setStatus("ready");
    } catch (requestError) {
      if (activeRequestId.current !== requestId) return;
      const cached = readCachedSimulation(payload);
      if (cached) {
        resultsRef.current = cached.data;
        resultsKeyRef.current = requestKey;
        setResults(cached.data);
        setLastUpdatedAt(cached.savedAt);
        setStatus("cached");
        setError(`${requestError.message} Showing the last matching saved calculation.`);
      } else {
        resultsRef.current = null;
        resultsKeyRef.current = "";
        setResults(null);
        setStatus("error");
        setError(requestError.message);
      }
    }
  }, [selectedControlIds, selectedScenarioId, seed, trials]);

  useEffect(() => {
    runSimulation();
  }, [runSimulation]);

  const toggleControl = useCallback((controlId) => {
    const control = config?.controls.find((item) => item.id === controlId);
    if (control && !control.coverage.includes(selectedScenarioId)) return;

    setSelectedControlIds((current) =>
      current.includes(controlId)
        ? current.filter((id) => id !== controlId)
        : [...current, controlId],
    );
  }, [config, selectedScenarioId]);

  const resetScenario = useCallback(() => {
    const scenario = config?.scenarios.find((item) => item.id === selectedScenarioId);
    setSelectedControlIds(scenario?.recommendedControlIds || []);
  }, [config, selectedScenarioId]);

  const resetDemo = useCallback(() => {
    const launchScenario = config?.scenarios.find((item) => item.id === DEFAULT_SCENARIO);
    setSelectedScenarioIdState(DEFAULT_SCENARIO);
    setSelectedControlIds(launchScenario?.recommendedControlIds || DEFAULT_CONTROLS);
    setError("");
    setDemoResetVersion((current) => current + 1);
  }, [config]);

  const retryConnection = useCallback(() => {
    loadConfig();
    loadSummaries();
    runSimulation();
  }, [loadConfig, loadSummaries, runSimulation]);

  const readiness = results?.readiness || null;
  const readinessScore = readiness?.proposed?.score ?? null;

  const priorityById = useMemo(
    () => Object.fromEntries((priorities?.controls || []).map((row) => [row.controlId, row])),
    [priorities],
  );

  const value = useMemo(
    () => ({
      selectedScenarioId,
      setSelectedScenarioId,
      selectedScenario,
      analysisMode,
      selectedControlIds,
      toggleControl,
      resetScenario,
      resetDemo,
      demoResetVersion,
      config,
      overview,
      priorities,
      priorityById,
      results,
      status,
      error,
      lastUpdatedAt,
      runSimulation,
      retryConnection,
      readiness,
      readinessScore,
      seed,
      trials,
    }),
    [selectedScenarioId, setSelectedScenarioId, selectedScenario, analysisMode, selectedControlIds, toggleControl, resetScenario, resetDemo, demoResetVersion, config, overview, priorities, priorityById, results, status, error, lastUpdatedAt, runSimulation, retryConnection, readiness, readinessScore, seed, trials],
  );

  return (
    <WorkbenchContext.Provider value={value}>
      {children}
    </WorkbenchContext.Provider>
  );
}

export function useWorkbench() {
  const context = useContext(WorkbenchContext);

  if (!context) {
    throw new Error("useWorkbench must be used inside WorkbenchProvider");
  }

  return context;
}
