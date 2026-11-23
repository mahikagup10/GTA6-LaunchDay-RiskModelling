import MetricCard from "../components/MetricCard";
import PageHeader from "../components/PageHeader";
import EvidenceRegister from "../components/EvidenceRegister";
import LossDistributionChart from "../components/charts/LossDistributionChart";
import SensitivityChart from "../components/charts/SensitivityChart";
import TornadoChart from "../components/charts/TornadoChart";
import { useWorkbench } from "../context/WorkbenchContext";
import {
  basisSuffix,
  basisTag,
  formatCurrency,
  formatInputValue,
  formatProbability,
  readableEvidence,
} from "../utils/formatters";

const groupOrder = ["frequency", "vulnerability", "duration", "primary-driver", "primary", "secondary-probability", "secondary"];

export default function RiskSimulator() {
  const { config, selectedScenarioId, setSelectedScenarioId, selectedScenario, results, status, runSimulation, seed, trials, selectedControlIds } = useWorkbench();
  const baseline = results?.baseline.metrics;
  const residual = results?.residual.metrics;
  const scenarios = config?.scenarios || [];
  const timeBasis = selectedScenario?.timeBasis || "launch-event";
  const busy = status === "loading" || status === "refreshing";
  const inputs = [...(selectedScenario?.inputs || [])].sort((a, b) => groupOrder.indexOf(a.group) - groupOrder.indexOf(b.group));
  const controlNames = Object.fromEntries((config?.controls || []).map((control) => [control.id, control.name]));

  const statRows = baseline && residual ? [
    ["Mean (expected loss)", formatCurrency(baseline.mean), formatCurrency(residual.mean)],
    ["P50 (median)", formatCurrency(baseline.p50), formatCurrency(residual.p50)],
    ["P90", formatCurrency(baseline.p90), formatCurrency(residual.p90)],
    ["P95 (tail risk)", formatCurrency(baseline.p95), formatCurrency(residual.p95)],
    ["P99", formatCurrency(baseline.p99), formatCurrency(residual.p99)],
    ["P(any loss event)", formatProbability(baseline.probabilityOfLoss), formatProbability(residual.probabilityOfLoss)],
    ...baseline.exceedance.map((item, index) => [
      `P(loss > ${formatCurrency(item.threshold)})`,
      formatProbability(item.probability),
      formatProbability(residual.exceedance[index]?.probability),
    ]),
  ] : [];

  return (
    <div className="page">
      <PageHeader eyebrow="FAIR-style analysis" title="Risk Simulator" description="Reproducible Monte Carlo analysis of frequency, conditional success, and component losses, with baseline and selected-control results side by side.">
        <label className="select-label">
          Scenario
          <select value={selectedScenarioId} onChange={(event) => setSelectedScenarioId(event.target.value)}>
            {scenarios.map((scenario) => <option key={scenario.id} value={scenario.id}>{scenario.name}</option>)}
          </select>
        </label>
      </PageHeader>

      <div className="basis-row">
        <span className="time-basis-badge">{basisTag(timeBasis)}</span>
        <span>{timeBasis === "launch-event" ? "Seven-day GTA VI launch window. Compare with first-year control cost." : "Twelve-month period. Compare with annualized control cost."}</span>
      </div>

      <section className="simulator-grid">
        <article className="panel inputs-panel">
          <span className="eyebrow">Model inputs</span>
          <h2>{selectedScenario?.name || "Scenario"} inputs</h2>
          <div className="estimate-key"><span>Low</span><span>Most likely</span><span>High</span></div>
          {inputs.map((item) => (
            <div className="input-row assumption-row" key={item.key} title={item.rationale}>
              <span>{item.label}<i className={`mini-dot ${item.evidenceType}`} title={readableEvidence(item.evidenceType)} /></span>
              <strong>{formatInputValue(item, item.low)} / {formatInputValue(item, item.mode)} / {formatInputValue(item, item.high)}</strong>
            </div>
          ))}
          <button className="primary-button" onClick={runSimulation} disabled={busy}>{busy ? `Running ${trials.toLocaleString()} trials…` : `Rerun ${trials.toLocaleString()} trials`}</button>
          <small>Fixed seed {seed}. The same inputs and controls always give the same result. Selected controls: {selectedControlIds.length ? selectedControlIds.map((id) => controlNames[id] || id).join(", ") : "none"}.</small>
        </article>
        <div>
          <section className="metric-grid compact">
            <MetricCard label="Baseline mean" value={baseline ? formatCurrency(baseline.mean) : "—"} detail={`Expected loss ${basisSuffix(timeBasis)}`} tone="danger" />
            <MetricCard label="Residual mean" value={residual ? formatCurrency(residual.mean) : "—"} detail={`With selected controls, ${basisSuffix(timeBasis)}`} tone="success" />
            <MetricCard label="Baseline P95" value={baseline ? formatCurrency(baseline.p95) : "—"} detail={residual ? `Residual P95 ${formatCurrency(residual.p95)}` : "Tail risk"} />
          </section>
          <article className="panel interactive-chart-panel">
            <span className="eyebrow">Loss distribution · {basisTag(timeBasis)}</span>
            <LossDistributionChart baseline={results?.baseline.histogram} residual={results?.residual.histogram} basisLabel={basisTag(timeBasis)} />
            <small>
              {results ? `Bars show trials with a loss. ${formatProbability(results.baseline.histogram.zeroShare)} of baseline trials and ${formatProbability(results.residual.histogram.zeroShare)} of residual trials had no loss. ` : ""}
              The mean can exceed P50 because rare large losses pull the average up.
            </small>
          </article>
          <article className="panel stats-panel">
            <span className="eyebrow">Baseline vs. selected controls · {basisTag(timeBasis)}</span>
            <div className="table-scroll"><table className="stat-table">
              <thead><tr><th>Metric</th><th>Baseline</th><th>Selected controls</th></tr></thead>
              <tbody>{statRows.map(([label, base, res]) => (
                <tr key={label}><td>{label}</td><td>{base}</td><td>{res}</td></tr>
              ))}</tbody>
            </table></div>
          </article>
        </div>
      </section>

      <section className="two-column sensitivity-row">
        <article className="panel sensitivity-panel">
          <span className="eyebrow">Top sensitivity drivers (Spearman)</span>
          <SensitivityChart drivers={results?.sensitivity} />
          <small>Rank correlation between each sampled input and baseline loss across {trials.toLocaleString()} trials.</small>
        </article>
        <article className="panel sensitivity-panel">
          <span className="eyebrow">What moves expected loss most (low/high swing)</span>
          <TornadoChart rows={results?.tornado} baselineMean={baseline?.mean} />
          <small>Each bar fixes one input at its low or high value while the others stay uncertain. The dotted line is the baseline mean.</small>
        </article>
      </section>

      <EvidenceRegister scenario={selectedScenario} methodology={config?.methodology} sources={config?.sources} />
    </div>
  );
}
