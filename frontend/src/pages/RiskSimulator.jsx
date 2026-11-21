import MetricCard from "../components/MetricCard";
import PageHeader from "../components/PageHeader";
import LossDistributionChart from "../components/charts/LossDistributionChart";
import SensitivityChart from "../components/charts/SensitivityChart";
import { useWorkbench } from "../context/WorkbenchContext";
import { formatCurrency, formatPercent } from "../utils/formatters";

export default function RiskSimulator() {
  const { config, selectedScenarioId, setSelectedScenarioId, analysisMode, setAnalysisMode, results, status, error, runSimulation } = useWorkbench();
  const baseline = results?.baseline.metrics;
  const residual = results?.residual.metrics;
  const scenarios = config?.scenarios || [];
  const selectedScenario = scenarios.find((scenario) => scenario.id === selectedScenarioId);
  const assumptions = selectedScenario?.assumptions;

  const assumptionRows = assumptions ? [
    ["Threat event frequency", assumptions.threatEventFrequency, (value) => value.toFixed(2)],
    ["Conditional success", assumptions.vulnerability, (value) => formatPercent(value)],
    ["Primary loss", assumptions.primaryLoss, formatCurrency],
    ["Secondary loss", assumptions.secondaryLoss, formatCurrency],
  ] : [];

  return (
    <div className="page">
      <PageHeader eyebrow="FAIR-style analysis" title="Risk Simulator" description="Test transparent frequency, vulnerability, and loss assumptions using reproducible Monte Carlo analysis.">
        <label className="select-label">
          Scenario
          <select value={selectedScenarioId} onChange={(event) => setSelectedScenarioId(event.target.value)}>
            {scenarios.map((scenario) => <option key={scenario.id} value={scenario.id}>{scenario.name}</option>)}
          </select>
        </label>
      </PageHeader>
      <div className="segmented-control" aria-label="Analysis mode">
        <button className={analysisMode === "launch-event" ? "active" : ""} onClick={() => setAnalysisMode("launch-event")}>Launch event</button>
        <button className={analysisMode === "annual" ? "active" : ""} onClick={() => setAnalysisMode("annual")}>Annual</button>
      </div>
      {error && <div className="status-message warning">{error}</div>}

      <section className="simulator-grid">
        <article className="panel inputs-panel">
          <span className="eyebrow">Model assumptions</span>
          <h2>{analysisMode === "launch-event" ? "Launch-event exposure" : "Annualized exposure"}</h2>
          <div className="estimate-key"><span>Low</span><span>Most likely</span><span>High</span></div>
          {assumptionRows.map(([label, estimate, formatter]) => (
            <div className="input-row assumption-row" key={label}>
              <span>{label}</span>
              <strong>{formatter(estimate.low)} / {formatter(estimate.mode)} / {formatter(estimate.high)}</strong>
            </div>
          ))}
          <button className="primary-button" onClick={runSimulation} disabled={status === "loading"}>{status === "loading" ? "Running 10,000 simulations…" : "Run 10,000 simulations"}</button>
          <small>Fixed seed: 243. Rerunning the same assumptions produces the same result.</small>
        </article>
        <div>
          <section className="metric-grid compact">
            <MetricCard label="Baseline mean" value={baseline ? formatCurrency(baseline.mean) : "—"} detail="Expected loss" />
            <MetricCard label="Residual mean" value={residual ? formatCurrency(residual.mean) : "—"} detail="Selected controls" />
            <MetricCard label="Above $50M" value={baseline ? formatPercent(baseline.probabilityAbove50m) : "—"} detail="Baseline probability" />
          </section>
          <article className="panel interactive-chart-panel">
            <span className="eyebrow">Loss distribution</span>
            <LossDistributionChart baseline={results?.baseline.histogram} residual={results?.residual.histogram} />
            <small>Hover to compare the baseline and selected-control residual distributions.</small>
          </article>
          <article className="panel sensitivity-panel">
            <span className="eyebrow">Top sensitivity drivers</span>
            <SensitivityChart drivers={results?.sensitivity} />
            <small>Absolute Spearman rank correlation with baseline loss.</small>
          </article>
        </div>
      </section>
    </div>
  );
}

