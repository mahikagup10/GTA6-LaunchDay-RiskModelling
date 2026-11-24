import MetricCard from "../components/MetricCard";
import PageHeader from "../components/PageHeader";
import EvidenceRegister from "../components/EvidenceRegister";
import LossDistributionChart from "../components/charts/LossDistributionChart";
import SensitivityChart from "../components/charts/SensitivityChart";
import { useWorkbench } from "../context/WorkbenchContext";
import { formatCurrency, formatPercent } from "../utils/formatters";

export default function RiskSimulator() {
  const { config, selectedScenarioId, setSelectedScenarioId, results, status, runSimulation } = useWorkbench();
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
      <div className="basis-note" role="note">
        Loss basis: <strong>{results?.meta?.basisLabel || (selectedScenarioId === "launch-ddos" ? "per 7-day launch window" : "per year")}</strong>.
        {selectedScenarioId === "launch-ddos" ? " GTA VI launched Nov 19 2026, so this is a launch-window what-if." : " Annual scenarios use Poisson event counts."}
        {" "}Frequency, vulnerability and control effects are team estimates; see the evidence register below.
      </div>
      <section className="simulator-grid">
        <article className="panel inputs-panel">
          <span className="eyebrow">Model assumptions</span>
          <h2>{selectedScenarioId === "launch-ddos" ? "Launch-window exposure" : "Annualized exposure"}</h2>
          <div className="estimate-key"><span>Low</span><span>Most likely</span><span>High</span></div>
          {assumptionRows.map(([label, estimate, formatter]) => (
            <div className="input-row assumption-row" key={label}>
              <span>{label}</span>
              <strong>{formatter(estimate.low)} / {formatter(estimate.mode)} / {formatter(estimate.high)}</strong>
            </div>
          ))}
          <button className="primary-button" onClick={runSimulation} disabled={status === "loading" || status === "refreshing"}>{status === "loading" || status === "refreshing" ? "Running 10,000 simulations…" : "Run 10,000 simulations"}</button>
          <small>Fixed seed: 20261124 (matches the Excel workbook). Rerunning the same assumptions produces the same result.</small>
        </article>
        <div>
          <section className="metric-grid compact">
            <MetricCard label="Baseline mean" value={baseline ? formatCurrency(baseline.mean) : "—"} detail="Expected loss" />
            <MetricCard label="Residual mean" value={residual ? formatCurrency(residual.mean) : "—"} detail="Selected controls" />
            <MetricCard label="P95 loss" value={baseline ? formatCurrency(baseline.p95) : "—"} detail={residual ? `Residual ${formatCurrency(residual.p95)}` : "Baseline"} />
            <MetricCard label="Above $25M" value={baseline ? formatPercent(baseline.probabilityAbove["25"]) : "—"} detail={residual ? `Residual ${formatPercent(residual.probabilityAbove["25"])}` : "Baseline probability"} />
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
      <EvidenceRegister scenario={selectedScenario} methodology={config?.methodology} sources={config?.sources} />
    </div>
  );
}

