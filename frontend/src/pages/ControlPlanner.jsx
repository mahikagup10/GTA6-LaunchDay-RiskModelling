import PageHeader from "../components/PageHeader";
import { controls as fallbackControls } from "../data/mockData";
import { useWorkbench } from "../context/WorkbenchContext";
import { formatCurrency } from "../utils/formatters";

export default function ControlPlanner() {
  const { config, results, status, selectedScenarioId, selectedControlIds, toggleControl, resetScenario } = useWorkbench();
  const controls = config?.controls || fallbackControls;
  const scenarios = config?.scenarios || [];
  const selectedScenario = scenarios.find((scenario) => scenario.id === selectedScenarioId);
  const scenarioNames = Object.fromEntries(scenarios.map((scenario) => [scenario.id, scenario.name]));
  const economics = results?.controlEconomics;
  const selectedCost = economics?.estimatedCost || 0;
  const avoidedLoss = economics?.lossesAvoided || 0;
  const netBenefit = economics?.netBenefit || 0;
  const rosi = economics?.rosi || 0;

  return (
    <div className="page">
      <PageHeader eyebrow="Investment case" title="Control Investment Planner" description={`Compare explicit control costs and modelled effects for ${selectedScenario?.name || "the selected scenario"}.`}>
        <button className="secondary-button" onClick={resetScenario}>Reset recommended controls</button>
      </PageHeader>
      <section className="planner-summary">
        <div><span>Selected investment</span><strong>{formatCurrency(selectedCost)}</strong></div>
        <div><span>Expected loss avoided</span><strong>{formatCurrency(avoidedLoss)}</strong></div>
        <div><span>Net benefit</span><strong>{formatCurrency(netBenefit)}</strong></div>
        <div><span>Modelled ROSI</span><strong>{rosi.toFixed(1)}×</strong></div>
      </section>
      <section className="control-list">
        {controls.map((control) => {
          const selected = selectedControlIds.includes(control.id);
          const applicable = !control.coverage || control.coverage.includes(selectedScenarioId);
          const effects = control.effects || {};
          const targets = [
            effects.frequencyMultiplier < 1 && "frequency",
            effects.vulnerabilityMultiplier < 1 && "vulnerability",
            (effects.primaryLossMultiplier < 1 || effects.secondaryLossMultiplier < 1) && "loss magnitude",
          ].filter(Boolean).join(", ") || control.target;
          return (
            <article className={`control-card${selected ? " selected" : ""}${!applicable ? " unavailable" : ""}`} key={control.id}>
              <button className="toggle" role="switch" aria-checked={selected} disabled={!applicable} aria-label={`${selected ? "Disable" : "Enable"} ${control.name}`} onClick={() => toggleControl(control.id)}><span /></button>
              <div>
                <h3>{control.name}</h3>
                <p>{applicable ? `Changes: ${targets}` : "Not applicable to this scenario"}</p>
                {control.coverage && <small>Coverage: {control.coverage.map((id) => scenarioNames[id] || id).join(", ")}</small>}
              </div>
              <div><span>Estimated cost</span><strong>{formatCurrency(control.cost.mode ?? control.cost)}</strong></div>
              <div><span>Confidence</span><strong>{control.confidence}</strong></div>
            </article>
          );
        })}
      </section>
      <p className="model-note">{status === "loading" ? "Recalculating shared control economics…" : "Control economics are calculated by the same fixed-seed simulation used across all four pages."}</p>
    </div>
  );
}

