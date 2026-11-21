import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState } from "react";
import { getConfig, simulateRisk } from "../services/api";
import {
  cacheConfig,
  cacheSimulation,
  readCachedConfig,
  readCachedSimulation,
  simulationRequestKey,
} from "../utils/cache";

const WorkbenchContext = createContext(null);

export function WorkbenchProvider({ children }) {
  const [selectedScenarioId, setSelectedScenarioIdState] = useState("launch-ddos");
  const [analysisMode, setAnalysisMode] = useState("launch-event");
  const [selectedControlIds, setSelectedControlIds] = useState([
    "cdn-scrubbing",
    "rate-limiting",
  ]);
  const [config, setConfig] = useState(null);
  const [results, setResults] = useState(null);
  const [status, setStatus] = useState("loading");
  const [error, setError] = useState("");
  const [lastUpdatedAt, setLastUpdatedAt] = useState(null);
  const activeRequestId = useRef(0);
  const resultsRef = useRef(null);
  const resultsKeyRef = useRef("");

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

  useEffect(() => {
    loadConfig();
  }, [loadConfig]);

  const setSelectedScenarioId = useCallback((scenarioId) => {
    setSelectedScenarioIdState(scenarioId);
    const scenario = config?.scenarios.find((item) => item.id === scenarioId);
    setSelectedControlIds(scenario?.recommendedControlIds || []);
  }, [config]);

  const runSimulation = useCallback(async () => {
    const payload = {
      scenarioId: selectedScenarioId,
      controlIds: selectedControlIds,
      analysisMode,
      trials: 10_000,
      seed: 243,
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
  }, [analysisMode, selectedControlIds, selectedScenarioId]);

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
    setAnalysisMode("launch-event");
  }, [config, selectedScenarioId]);

  const retryConnection = useCallback(() => {
    loadConfig();
    runSimulation();
  }, [loadConfig, runSimulation]);

  const readinessBreakdown = useMemo(() => {
    const scenario = config?.scenarios.find((item) => item.id === selectedScenarioId);
    const baseline = scenario?.readinessProfile || {
      prevent: scenario?.readinessBase || 40,
      detect: scenario?.readinessBase || 40,
      respond: scenario?.readinessBase || 40,
      recover: scenario?.readinessBase || 40,
    };
    const next = { ...baseline };

    selectedControlIds.forEach((controlId) => {
      const control = config?.controls.find((item) => item.id === controlId);
      if (!control?.readinessImpact || !control.coverage.includes(selectedScenarioId)) return;
      Object.entries(control.readinessImpact).forEach(([dimension, points]) => {
        next[dimension] = Math.min(100, next[dimension] + points);
      });
    });

    return next;
  }, [config, selectedControlIds, selectedScenarioId]);

  const readinessScore = useMemo(() => {
    const values = Object.values(readinessBreakdown);
    return Math.round(values.reduce((total, value) => total + value, 0) / values.length);
  }, [readinessBreakdown]);

  const value = useMemo(
    () => ({
      selectedScenarioId,
      setSelectedScenarioId,
      analysisMode,
      setAnalysisMode,
      selectedControlIds,
      toggleControl,
      resetScenario,
      config,
      results,
      status,
      error,
      lastUpdatedAt,
      runSimulation,
      retryConnection,
      readinessScore,
      readinessBreakdown,
    }),
    [selectedScenarioId, setSelectedScenarioId, analysisMode, selectedControlIds, toggleControl, resetScenario, config, results, status, error, lastUpdatedAt, runSimulation, retryConnection, readinessScore, readinessBreakdown],
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

