import AssetsAtRisk from "../components/AssetsAtRisk";
import MetricCard from "../components/MetricCard";
import PageHeader from "../components/PageHeader";
import ScenarioHeatMap from "../components/charts/ScenarioHeatMap";
import { scenarios as fallbackScenarios } from "../data/mockData";
import { useWorkbench } from "../context/WorkbenchContext";
import { formatCurrency } from "../utils/formatters";

export default function ExecutiveOverview() {
  const { config, results, status, readinessScore, readinessBreakdown, selectedScenarioId, setSelectedScenarioId } = useWorkbench();
  const scenarios = config?.scenarios || fallbackScenarios;
  const selectedScenario = scenarios.find((scenario) => scenario.id === selectedScenarioId);
  const baseline = results?.baseline.metrics;
  const residual = results?.residual.metrics;
  const reduction = results?.comparison.expectedLossReduction;
  const selectedControls = (config?.controls || []).filter((control) => results?.controlEconomics.selectedControlIds.includes(control.id));

  return (
    <div className="page">
      <PageHeader
        eyebrow="Decision view"
        title="Executive Overview"
        description="A concise view of financial exposure, launch readiness, and the controls that matter most."
      >
        <label className="select-label">
          Scenario
          <select value={selectedScenarioId} onChange={(event) => setSelectedScenarioId(event.target.value)}>
            {scenarios.map((scenario) => (
              <option key={scenario.id} value={scenario.id}>{scenario.name}</option>
            ))}
          </select>
        </label>
      </PageHeader>

      <section className="scenario-banner">
        <div>
          <span className="critical-tag">{selectedScenario.severity}</span>
          <h2>{selectedScenario.name}</h2>
          <p>{selectedScenario.summary}</p>
        </div>
        <div className="readiness-ring" aria-label={`Readiness score ${readinessScore} out of 100`}>
          <strong>{readinessScore}</strong>
          <span>/ 100 readiness</span>
        </div>
      </section>

      <section className="metric-grid">
        <MetricCard label="Baseline expected loss" value={baseline ? formatCurrency(baseline.mean) : "—"} detail="Before selected controls" tone="danger" />
        <MetricCard label="Residual expected loss" value={residual ? formatCurrency(residual.mean) : "—"} detail="With selected controls" tone="success" />
        <MetricCard label="Expected loss avoided" value={reduction != null ? formatCurrency(reduction) : "—"} detail="Modelled benefit" />
        <MetricCard label="Baseline P90 loss" value={baseline ? formatCurrency(baseline.p90) : "—"} detail={["loading", "refreshing"].includes(status) ? "Running 10,000 trials…" : "Severe but plausible outcome"} />
      </section>

      <section className="two-column">
        <article className="panel">
          <span className="eyebrow">Team readiness index</span>
          <h2>Readiness by decision dimension</h2>
          <p>{selectedControls.length ? `${selectedControls.map((control) => control.name).join(" and ")} produce the current residual-risk estimate for ${selectedScenario.name}.` : "Select controls in the investment planner to calculate a residual-risk estimate."}</p>
          <div className="readiness-dimensions">
            {Object.entries(readinessBreakdown).map(([dimension, value]) => (
              <div className="readiness-dimension" key={dimension}>
                <div><span>{dimension}</span><strong>{value}</strong></div>
                <div className="progress-track"><span style={{ width: `${value}%` }} /></div>
              </div>
            ))}
          </div>
          <small className="readiness-formula">Overall score = average of Prevent, Detect, Respond, and Recover after selected-control points are applied.</small>
        </article>
        <article className="panel heatmap-placeholder">
          <span className="eyebrow">Scenario heat map</span>
          <h2>Comparative exposure</h2>
          <ScenarioHeatMap />
          <small>Team-assessed relative placement; hover over a diamond or cell for detail.</small>
        </article>
      </section>

      <AssetsAtRisk
        assets={config?.assets || []}
        scenarios={scenarios}
        controls={config?.controls || []}
        sources={config?.sources || []}
        selectedScenarioId={selectedScenarioId}
      />

      <p className="model-note"><strong>Important:</strong> readiness is a team-designed decision-support index. It is not an official FAIR or NIST score.</p>
    </div>
  );
}

