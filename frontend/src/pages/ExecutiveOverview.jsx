import { Link } from "react-router-dom";
import MetricCard from "../components/MetricCard";
import PageHeader from "../components/PageHeader";
import ScenarioHeatMap from "../components/charts/ScenarioHeatMap";
import { scenarios as fallbackScenarios } from "../data/mockData";
import { useWorkbench } from "../context/WorkbenchContext";
import { basisSuffix, basisTag, formatCurrency, formatMultiple, formatProbability } from "../utils/formatters";

const levelText = { 0: "Absent", 0.5: "Partial", 1: "Tested" };

export default function ExecutiveOverview() {
  const { config, overview, priorities, results, status, readiness, selectedScenarioId, setSelectedScenarioId, selectedScenario } = useWorkbench();
  const scenarios = config?.scenarios || fallbackScenarios;
  const scenario = selectedScenario || scenarios.find((item) => item.id === selectedScenarioId) || scenarios[0];
  const timeBasis = scenario?.timeBasis || "launch-event";
  const baseline = results?.baseline.metrics;
  const residual = results?.residual.metrics;
  const economics = results?.controlEconomics;
  const busy = ["loading", "refreshing"].includes(status);
  const overviewById = Object.fromEntries((overview?.scenarios || []).map((item) => [item.scenarioId, item]));
  const assetsById = Object.fromEntries((config?.criticalAssets || []).map((asset) => [asset.id, asset]));
  const controlsById = Object.fromEntries((config?.controls || []).map((control) => [control.id, control]));
  const topRecommendation = (priorities?.controls || []).find((row) => row.scenarios[selectedScenarioId]);
  const topControl = topRecommendation ? controlsById[topRecommendation.controlId] : null;
  const topCell = topRecommendation?.scenarios[selectedScenarioId];

  return (
    <div className="page">
      <PageHeader
        eyebrow="Decision view"
        title="Executive Overview"
        description="Financial exposure across four GTA VI launch risks, what the selected controls change, and the decision requested."
      >
        <label className="select-label">
          Scenario
          <select value={selectedScenarioId} onChange={(event) => setSelectedScenarioId(event.target.value)}>
            {scenarios.map((item) => (
              <option key={item.id} value={item.id}>{item.name}</option>
            ))}
          </select>
        </label>
      </PageHeader>

      <section className="scenario-overview-grid" aria-label="Four risk scenarios">
        {scenarios.map((item) => {
          const summary = overviewById[item.id];
          return (
            <button
              key={item.id}
              className={`scenario-tile${item.id === selectedScenarioId ? " active" : ""}`}
              onClick={() => setSelectedScenarioId(item.id)}
            >
              <span className={`severity-tag ${String(item.severity).toLowerCase()}`}>{item.severity}</span>
              <strong>{item.name}</strong>
              <span className="tile-value">{summary ? formatCurrency(summary.metrics.mean) : "—"}</span>
              <small>Baseline expected loss · {basisTag(item.timeBasis)}</small>
              <small>P95 {summary ? formatCurrency(summary.metrics.p95) : "—"} · P(loss) {summary ? formatProbability(summary.metrics.probabilityOfLoss) : "—"}</small>
            </button>
          );
        })}
      </section>

      <section className="scenario-banner">
        <div>
          <span className="critical-tag">{scenario?.severity}</span>
          <h2>{scenario?.name}</h2>
          <p>{scenario?.summary}</p>
          <div className="asset-chips">
            {(scenario?.assetIds || []).map((assetId) => assetsById[assetId] && (
              <span className="chip" key={assetId} title={assetsById[assetId].description}>{assetsById[assetId].name}</span>
            ))}
          </div>
        </div>
        <div className="readiness-ring" aria-label={`Launch readiness ${readiness?.current.score ?? "—"} now, ${readiness?.proposed.score ?? "—"} with selected plan`}>
          <strong>{readiness ? `${Math.round(readiness.current.score)}→${Math.round(readiness.proposed.score)}` : "—"}</strong>
          <span>launch readiness</span>
        </div>
      </section>

      <section className="metric-grid">
        <MetricCard label="Baseline expected loss" value={baseline ? formatCurrency(baseline.mean) : "—"} detail={`${basisTag(timeBasis)} · before controls`} tone="danger" />
        <MetricCard label="Residual expected loss" value={residual ? formatCurrency(residual.mean) : "—"} detail={`${basisTag(timeBasis)} · with selected controls`} tone="success" />
        <MetricCard label="Selected-control cost" value={economics ? formatCurrency(economics.estimatedCost) : "—"} detail={timeBasis === "launch-event" ? "USD · full first-year cost" : "USD · annualized"} />
        <MetricCard
          label="Expected loss avoided"
          value={economics ? formatCurrency(economics.lossesAvoided) : "—"}
          detail={busy ? "Running 10,000 trials…" : economics ? `Net ${formatCurrency(economics.netBenefit)} · ROSI ${formatMultiple(economics.rosi)}` : "Modelled benefit"}
        />
      </section>

      <section className="two-column">
        <article className="panel recommendation-panel">
          <span className="eyebrow">Top recommendation for this scenario</span>
          {topControl && topRecommendation ? (
            <>
              <h2>{topControl.name}</h2>
              <span className={`priority-badge p${topRecommendation.priority}`}>{topRecommendation.priorityLabel} · score {topRecommendation.priorityScore}</span>
              <p>{topControl.problem} {topControl.rationale}</p>
              <div className="recommendation-facts">
                <div><span>Loss avoided alone</span><strong>{formatCurrency(topCell.lossReduction)}</strong><small>{basisSuffix(topCell.timeBasis)}</small></div>
                <div><span>First-year cost</span><strong>{formatCurrency(topRecommendation.firstYearCost)}</strong><small>{topControl.costBasisLabel} cost basis</small></div>
                <div><span>First-year ROSI</span><strong>{formatMultiple(topRecommendation.firstYearRosi)}</strong><small>All covered scenarios</small></div>
              </div>
              <Link className="text-link" to="/control-planner">Open the Control Investment Planner →</Link>
            </>
          ) : <p>Loading control priorities…</p>}
          <div className="tail-compare">
            <span className="detail-label">Tail risk</span>
            <p>{baseline && residual ? `P95 ${formatCurrency(baseline.p95)} → ${formatCurrency(residual.p95)} ${basisSuffix(timeBasis)}` : "—"}</p>
            {baseline && residual && baseline.exceedance[1] && (
              <p>{`P(loss > ${formatCurrency(baseline.exceedance[1].threshold)}): ${formatProbability(baseline.exceedance[1].probability)} → ${formatProbability(residual.exceedance[1].probability)}`}</p>
            )}
          </div>
        </article>
        <article className="panel heatmap-placeholder">
          <span className="eyebrow">Scenario heat map</span>
          <h2>Comparative exposure (model-derived)</h2>
          <ScenarioHeatMap overview={overview} selectedScenarioId={selectedScenarioId} />
          <small>{overview?.meta.heatmapRule || "Placement comes from the simulation."} Launch-Day DDoS is per launch event; the others are annual.</small>
        </article>
      </section>

      <section className="panel readiness-panel">
        <div className="section-heading">
          <div>
            <span className="eyebrow">Launch Protection Readiness Index</span>
            <h2>{readiness ? `${Math.round(readiness.current.score)} now (${readiness.current.band}) → ${Math.round(readiness.proposed.score)} with the selected plan (${readiness.proposed.band})` : "Readiness"}</h2>
          </div>
        </div>
        <div className="table-scroll">
        <table className="stat-table readiness-table">
          <thead><tr><th>Component</th><th>Weight</th><th>Current</th><th>With selected plan</th><th>Driven by</th></tr></thead>
          <tbody>{(readiness?.components || []).map((component) => (
            <tr key={component.id}>
              <td title={component.currentRationale}>{component.name}</td>
              <td>{component.weight}</td>
              <td>{levelText[component.currentLevel]} ({component.currentPoints})</td>
              <td className={component.proposedLevel > component.currentLevel ? "improved" : ""}>{levelText[component.proposedLevel]} ({component.proposedPoints})</td>
              <td>{component.drivers.map((id) => controlsById[id]?.name || id).join(", ") || "—"}</td>
            </tr>
          ))}</tbody>
        </table>
        </div>
        <small className="readiness-formula">Score = Σ weight × level (0 absent, 0.5 planned or partial, 1 implemented and tested). 80–100 Ready, 60–79 Conditional readiness, below 60 Material readiness gaps. {readiness?.note}</small>
      </section>

      <p className="model-note"><strong>Important:</strong> every figure is USD and labeled as per launch event or annual. Inputs mix public facts, derived values, and team estimates; see the evidence register on the Risk Simulator page. This is a FAIR-style decision aid, not an official FAIR or NIST score.</p>
    </div>
  );
}
