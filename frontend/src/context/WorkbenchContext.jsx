import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { getConfig, simulateRisk } from "../services/api";

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

  useEffect(() => {
    getConfig()
      .then(setConfig)
      .catch((requestError) => setError(requestError.message));
  }, []);

  const setSelectedScenarioId = useCallback((scenarioId) => {
    setSelectedScenarioIdState(scenarioId);
    const scenario = config?.scenarios.find((item) => item.id === scenarioId);
    setSelectedControlIds(scenario?.recommendedControlIds || []);
  }, [config]);

  const runSimulation = useCallback(async () => {
    setStatus("loading");
    setError("");
    try {
      const nextResults = await simulateRisk({
        scenarioId: selectedScenarioId,
        controlIds: selectedControlIds,
        analysisMode,
        trials: 10_000,
        seed: 243,
      });
      setResults(nextResults);
      setStatus("ready");
    } catch (requestError) {
      setStatus("error");
      setError(requestError.message);
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

  const readinessScore = useMemo(() => {
    const scenario = config?.scenarios.find((item) => item.id === selectedScenarioId);
    return Math.min(100, (scenario?.readinessBase || 40) + selectedControlIds.length * 12);
  }, [config, selectedControlIds.length, selectedScenarioId]);

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
      runSimulation,
      readinessScore,
    }),
    [selectedScenarioId, setSelectedScenarioId, analysisMode, selectedControlIds, toggleControl, resetScenario, config, results, status, error, runSimulation, readinessScore],
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

