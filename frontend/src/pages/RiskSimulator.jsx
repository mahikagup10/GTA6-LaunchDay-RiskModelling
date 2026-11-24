import { useEffect, useMemo, useState } from "react";
import MetricCard from "../components/MetricCard";
import PageHeader from "../components/PageHeader";
import EvidenceRegister from "../components/EvidenceRegister";
import LossDistributionChart from "../components/charts/LossDistributionChart";
import SensitivityChart from "../components/charts/SensitivityChart";
import { useWorkbench } from "../context/WorkbenchContext";
import { formatCurrency, formatPercent } from "../utils/formatters";

const inputDefinitions = [
  { key: "threatEventFrequency", label: "Threat event frequency", unit: "events", step: "0.01", toDisplay: (value) => value, toModel: (value) => value },
  { key: "vulnerability", label: "Conditional success", unit: "%", step: "1", maximum: 100, toDisplay: (value) => value * 100, toModel: (value) => value / 100 },
  { key: "primaryLoss", label: "Primary loss", unit: "$M", step: "1", toDisplay: (value) => value / 1_000_000, toModel: (value) => value * 1_000_000 },
  { key: "secondaryLoss", label: "Secondary loss", unit: "$M", step: "1", toDisplay: (value) => value / 1_000_000, toModel: (value) => value * 1_000_000 },
];

const estimateKeys = ["low", "mode", "high"];
const estimateLabels = { low: "Low", mode: "Most likely", high: "High" };

function createDraft(assumptions, secondaryProbability) {
  if (!assumptions) return {};
  return {
    ...Object.fromEntries(inputDefinitions.map((definition) => [
    definition.key,
    Object.fromEntries(estimateKeys.map((estimateKey) => [
      estimateKey,
      String(definition.toDisplay(assumptions[definition.key][estimateKey])),
    ])),
    ])),
    secondaryLossProbability: String((secondaryProbability ?? 1) * 100),
  };
}

function normalizeDraft(draft) {
  const normalized = {};

  inputDefinitions.forEach((definition) => {
    const rawValues = estimateKeys.map((estimateKey) => draft[definition.key]?.[estimateKey]);
    if (rawValues.some((value) => value == null || String(value).trim() === "")) {
      throw new Error(`${definition.label} requires numeric low, most-likely, and high values.`);
    }
    const displayValues = rawValues.map((value) => Number(value));
    if (displayValues.some((value) => !Number.isFinite(value))) {
      throw new Error(`${definition.label} requires numeric low, most-likely, and high values.`);
    }
    if (displayValues.some((value) => value < 0)) {
      throw new Error(`${definition.label} cannot contain negative values.`);
    }
    if (definition.maximum != null && displayValues.some((value) => value > definition.maximum)) {
      throw new Error(`${definition.label} must remain between 0 and ${definition.maximum}${definition.unit}.`);
    }
    if (!(displayValues[0] <= displayValues[1] && displayValues[1] <= displayValues[2])) {
      throw new Error(`${definition.label} must follow Low ≤ Most likely ≤ High.`);
    }

    normalized[definition.key] = Object.fromEntries(estimateKeys.map((estimateKey, index) => [
      estimateKey,
      definition.toModel(displayValues[index]),
    ]));
  });

  const secondaryProbability = Number(draft.secondaryLossProbability);
  if (!Number.isFinite(secondaryProbability) || secondaryProbability < 0 || secondaryProbability > 100) {
    throw new Error("Secondary-loss probability must be between 0% and 100%.");
  }
  normalized.secondaryLossProbability = secondaryProbability / 100;

  return normalized;
}

function statisticValue(value, formatter) {
  return value == null ? "—" : formatter(value);
}

export default function RiskSimulator() {
  const {
    config,
    selectedScenarioId,
    setSelectedScenarioId,
    analysisMode,
    setAnalysisMode,
    assumptionProfileId,
    setAssumptionProfileId,
    selectedControlIds,
    results,
    status,
    currentAppliedAssumptions,
    applyScenarioAssumptions,
    resetScenarioAssumptions,
  } = useWorkbench();
  const [draft, setDraft] = useState({});
  const [validationError, setValidationError] = useState("");
  const baseline = results?.baseline.metrics;
  const residual = results?.residual.metrics;
  const scenarios = config?.scenarios || [];
  const selectedScenario = scenarios.find((scenario) => scenario.id === selectedScenarioId);
  const selectedProfile = selectedScenario?.assumptionProfiles?.[assumptionProfileId];
  const configuredAssumptions = selectedProfile?.assumptions || selectedScenario?.assumptions;
  const configuredSecondaryProbability = selectedProfile?.secondaryLossProbability?.value ?? selectedScenario?.secondaryLossProbability?.value ?? 1;

  useEffect(() => {
    setDraft(createDraft(currentAppliedAssumptions || configuredAssumptions, currentAppliedAssumptions?.secondaryLossProbability ?? configuredSecondaryProbability));
    setValidationError("");
  }, [configuredAssumptions, configuredSecondaryProbability, currentAppliedAssumptions, selectedScenarioId]);

  const savedDraft = useMemo(
    () => createDraft(currentAppliedAssumptions || configuredAssumptions, currentAppliedAssumptions?.secondaryLossProbability ?? configuredSecondaryProbability),
    [configuredAssumptions, configuredSecondaryProbability, currentAppliedAssumptions],
  );
  const hasUnappliedChanges = JSON.stringify(draft) !== JSON.stringify(savedDraft);
  const isRunning = status === "loading" || status === "refreshing";
  const naturalBasis = selectedScenario?.analysisBasis || "annual";
  const usesNaturalBasis = analysisMode === naturalBasis;

  function updateDraft(assumptionKey, estimateKey, value) {
    setDraft((current) => ({
      ...current,
      [assumptionKey]: {
        ...current[assumptionKey],
        [estimateKey]: value,
      },
    }));
  }

  function applyInputs() {
    try {
      const normalized = normalizeDraft(draft);
      setValidationError("");
      applyScenarioAssumptions(normalized);
    } catch (error) {
      setValidationError(error.message);
    }
  }

  function restoreDefaults() {
    setDraft(createDraft(configuredAssumptions, configuredSecondaryProbability));
    setValidationError("");
    resetScenarioAssumptions();
  }

  function downloadScenarioSummary() {
    if (!selectedScenario || !results) return;
    const summary = {
      generatedAt: new Date().toISOString(),
      scenario: { id: selectedScenario.id, name: selectedScenario.name, summary: selectedScenario.summary },
      model: {
        methodology: config?.methodology?.name,
        analysisMode,
        naturalAnalysisBasis: naturalBasis,
        assumptionProfile: selectedProfile?.name,
        trials: results.meta.trials,
        seed: results.meta.seed,
        secondaryLossProbability: results.meta.secondaryLossProbability,
      },
      assumptions: currentAppliedAssumptions || configuredAssumptions,
      selectedControlIds,
      baseline: results.baseline.metrics,
      residual: results.residual.metrics,
      comparison: results.comparison,
      controlEconomics: results.controlEconomics,
      sensitivity: results.sensitivity,
      note: "Team FAIR-style decision-support model; not an official FAIR or NIST assessment.",
    };
    const blob = new Blob([JSON.stringify(summary, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `${selectedScenario.id}-risk-summary.json`;
    link.click();
    URL.revokeObjectURL(url);
  }

  const statistics = [
    ["Mean", baseline?.mean, residual?.mean, formatCurrency],
    ["P50", baseline?.p50, residual?.p50, formatCurrency],
    ["P90", baseline?.p90, residual?.p90, formatCurrency],
    ["P95", baseline?.p95, residual?.p95, formatCurrency],
    ["P99 (extreme tail)", baseline?.p99, residual?.p99, formatCurrency],
    ["Probability above $10M", baseline?.probabilityAbove10m, residual?.probabilityAbove10m, formatPercent],
    ["Probability above $25M", baseline?.probabilityAbove25m, residual?.probabilityAbove25m, formatPercent],
    ["Probability above $50M", baseline?.probabilityAbove50m, residual?.probabilityAbove50m, formatPercent],
    ["Probability above $100M", baseline?.probabilityAbove100m, residual?.probabilityAbove100m, formatPercent],
  ];

  return (
    <div className="page">
      <PageHeader eyebrow="FAIR-style analysis" title="Risk Simulator" description="Edit transparent frequency, vulnerability, and loss assumptions, then run reproducible Monte Carlo analysis.">
        <div className="simulator-header-actions">
          <label className="select-label">Scenario
            <select value={selectedScenarioId} onChange={(event) => setSelectedScenarioId(event.target.value)}>
              {scenarios.map((scenario) => <option key={scenario.id} value={scenario.id}>{scenario.name}</option>)}
            </select>
          </label>
          <button className="secondary-button" onClick={downloadScenarioSummary} disabled={!results}>Download summary</button>
        </div>
      </PageHeader>
      <div className="segmented-control" aria-label="Analysis mode">
        <button className={analysisMode === "launch-event" ? "active" : ""} aria-pressed={analysisMode === "launch-event"} onClick={() => setAnalysisMode("launch-event")}>Launch event</button>
        <button className={analysisMode === "annual" ? "active" : ""} aria-pressed={analysisMode === "annual"} onClick={() => setAnalysisMode("annual")}>Annual</button>
      </div>
      <div className={usesNaturalBasis ? "basis-notice" : "basis-notice warning"}>
        <strong>Recommended basis: {naturalBasis === "launch-event" ? "Launch event" : "Annual"}.</strong>
        <span>{usesNaturalBasis ? " Current results use the scenario's natural decision period." : " You selected a different period; interpret and document the comparison carefully."}</span>
      </div>
      <div className="profile-row">
        <label className="select-label">Assumption profile
          <select value={assumptionProfileId} onChange={(event) => setAssumptionProfileId(event.target.value)}>
            {Object.values(selectedScenario?.assumptionProfiles || {}).map((profile) => <option key={profile.id} value={profile.id}>{profile.name}</option>)}
          </select>
        </label>
        <p><strong>{selectedProfile?.name}:</strong> {selectedProfile?.description}</p>
      </div>
      <section className="model-run-summary" aria-label="Current model run summary">
        <div><span>Scenario</span><strong>{selectedScenario?.name}</strong></div>
        <div><span>Period</span><strong>{analysisMode === "launch-event" ? "Launch event" : "Annual"}</strong></div>
        <div><span>Profile</span><strong>{selectedProfile?.name || assumptionProfileId}</strong></div>
        <div><span>Trials</span><strong>{results?.meta.trials?.toLocaleString() || "10,000"}</strong></div>
        <div><span>Seed</span><strong>{results?.meta.seed ?? 243}</strong></div>
        <div><span>Secondary-loss chance</span><strong>{formatPercent(results?.meta.secondaryLossProbability ?? configuredSecondaryProbability)}</strong></div>
      </section>

      <section className="simulator-grid">
        <article className="panel inputs-panel">
          <div className="input-panel-heading">
            <div><span className="eyebrow">Editable model assumptions</span><h2>{analysisMode === "launch-event" ? "Launch-event exposure" : "Annualized exposure"}</h2></div>
            <span className={currentAppliedAssumptions ? "input-source custom" : "input-source"}>{currentAppliedAssumptions ? "Custom" : "Team defaults"}</span>
          </div>
          <p className="input-guidance">Loss values are entered in millions of dollars. Conditional success is entered as a percentage.</p>
          <div className="estimate-input-header"><span /><span>Low</span><span>Most likely</span><span>High</span></div>
          {inputDefinitions.map((definition) => (
            <div className="estimate-input-row" key={definition.key}>
              <label>{definition.label}<small>{definition.unit}</small></label>
              {estimateKeys.map((estimateKey) => (
                <input
                  key={estimateKey}
                  type="number"
                  min="0"
                  max={definition.maximum}
                  step={definition.step}
                  value={draft[definition.key]?.[estimateKey] ?? ""}
                  aria-label={`${definition.label} ${estimateLabels[estimateKey]}`}
                  onChange={(event) => updateDraft(definition.key, estimateKey, event.target.value)}
                />
              ))}
            </div>
          ))}
          <div className="single-input-row">
            <label>Secondary-loss occurrence<small>% of successful events</small></label>
            <input type="number" min="0" max="100" step="1" value={draft.secondaryLossProbability ?? ""} aria-label="Secondary-loss occurrence probability" onChange={(event) => setDraft((current) => ({ ...current, secondaryLossProbability: event.target.value }))} />
            <p>Secondary loss is added only in this share of successful events—not automatically every time.</p>
          </div>
          {validationError && <div className="input-validation" role="alert">{validationError}</div>}
          <div className="input-actions">
            <button className="primary-button" onClick={applyInputs} disabled={isRunning || !configuredAssumptions}>{isRunning ? "Running 10,000 simulations…" : "Apply inputs & run"}</button>
            <button className="text-button" onClick={restoreDefaults} disabled={isRunning || !configuredAssumptions}>Restore team defaults</button>
          </div>
          <small className={hasUnappliedChanges ? "draft-status pending" : "draft-status"}>{hasUnappliedChanges ? "Changes are staged. Apply them to update results across the app." : "Displayed results match these inputs."}</small>
          <small>Fixed seed: 243. Identical inputs produce identical results.</small>
        </article>
        <div>
          <section className="metric-grid compact simulator-summary">
            <MetricCard label="Baseline mean" value={baseline ? formatCurrency(baseline.mean) : "—"} detail="Before controls" />
            <MetricCard label="Residual mean" value={residual ? formatCurrency(residual.mean) : "—"} detail="Selected controls" />
            <MetricCard label="Expected loss avoided" value={results ? formatCurrency(results.comparison.expectedLossReduction) : "—"} detail="Baseline minus residual" />
          </section>
          <article className="panel statistics-panel">
            <div className="statistics-heading">
              <div><span className="eyebrow">Complete result set</span><h2>Percentiles & thresholds</h2></div>
              <span>{results?.meta.assumptionsSource === "custom" ? "Custom inputs" : "Team defaults"}</span>
            </div>
            <div className="statistics-table-wrap">
              <table className="statistics-table">
                <thead><tr><th>Measure</th><th>Baseline</th><th>Residual</th></tr></thead>
                <tbody>{statistics.map(([label, baselineValue, residualValue, formatter]) => (
                  <tr key={label}><td>{label}</td><td>{statisticValue(baselineValue, formatter)}</td><td>{statisticValue(residualValue, formatter)}</td></tr>
                ))}</tbody>
              </table>
            </div>
            {(baseline?.p50 === 0 || residual?.p50 === 0) && <p className="p50-explanation"><strong>Why is P50 $0?</strong> At least half of simulated periods had no successful material loss event. Less frequent successful events still create a positive mean and upper-tail loss.</p>}
          </article>
          <article className="panel interactive-chart-panel">
            <span className="eyebrow">Loss distribution</span>
            <LossDistributionChart baseline={results?.baseline.histogram} residual={results?.residual.histogram} />
            <small>Hover to compare the baseline and selected-control residual distributions.</small>
          </article>
          <article className="panel sensitivity-panel">
            <span className="eyebrow">Top sensitivity drivers</span>
            <SensitivityChart drivers={results?.sensitivity} />
            <small>Absolute Spearman rank correlation with baseline loss.</small>
            <div className="tornado-list">
              <h3>Low-to-high sensitivity</h3>
              <p>Each input is moved from its low to high estimate while the same simulated trials are reused.</p>
              {results?.tornadoSensitivity?.map((driver) => <div key={driver.name}><span>{driver.name}</span><strong>{formatCurrency(driver.swing)} swing</strong></div>)}
            </div>
          </article>
        </div>
      </section>
      {results?.meta.assumptionsSource === "custom" && <p className="model-note"><strong>Custom-input notice:</strong> current results use user-entered assumptions. The evidence register below documents the team-default estimates rather than the edited values.</p>}
      <EvidenceRegister scenario={selectedScenario} profileId={assumptionProfileId} methodology={config?.methodology} sources={config?.sources} />
    </div>
  );
}
