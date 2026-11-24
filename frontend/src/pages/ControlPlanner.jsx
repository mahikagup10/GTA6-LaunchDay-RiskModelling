import { useEffect, useState } from "react";
import PageHeader from "../components/PageHeader";
import { controls as fallbackControls } from "../data/mockData";
import { MODEL_SEED, useWorkbench } from "../context/WorkbenchContext";
import { getPriorities, simulatePortfolio } from "../services/api";
import { cachePortfolio, readCachedPortfolio } from "../utils/cache";
import { formatCurrency } from "../utils/formatters";

export default function ControlPlanner() {
  const { config, results, status, selectedScenarioId, setSelectedScenarioId, selectedControlIds, toggleControl, resetScenario, demoResetVersion } = useWorkbench();
  const [plannerMode, setPlannerMode] = useState("scenario");
  const [portfolioControlIds, setPortfolioControlIds] = useState(null);
  const [portfolioResults, setPortfolioResults] = useState(null);
  const [portfolioStatus, setPortfolioStatus] = useState("idle");
  const [portfolioError, setPortfolioError] = useState("");
  const [priorities, setPriorities] = useState(null);
  const controls = config?.controls || fallbackControls;
  const scenarios = config?.scenarios || [];
  const selectedScenario = scenarios.find((scenario) => scenario.id === selectedScenarioId);
  const scenarioNames = Object.fromEntries(scenarios.map((scenario) => [scenario.id, scenario.name]));
  const recommendedIds = selectedScenario?.recommendedControlIds || [];
  const activePortfolioIds = portfolioControlIds || [];
  const economics = plannerMode === "portfolio" ? portfolioResults?.controlEconomics : results?.controlEconomics;
  const selectedCost = economics?.estimatedCost || 0;
  const avoidedLoss = economics?.lossesAvoided || 0;
  const netBenefit = economics?.netBenefit || 0;
  const rosi = economics?.rosi || 0;

  useEffect(() => {
    getPriorities().then(setPriorities).catch(() => setPriorities(null));
  }, []);

  useEffect(() => {
    if (config && portfolioControlIds === null) {
      setPortfolioControlIds(config.controls.map((control) => control.id));
    }
  }, [config, portfolioControlIds]);

  useEffect(() => {
    setPlannerMode("scenario");
    setPortfolioResults(null);
    setPortfolioStatus("idle");
    setPortfolioError("");
    if (config) setPortfolioControlIds(config.controls.map((control) => control.id));
  }, [config, demoResetVersion]);

  useEffect(() => {
    if (plannerMode !== "portfolio" || portfolioControlIds === null) return undefined;
    let cancelled = false;
    setPortfolioStatus("loading");
    setPortfolioError("");

    const payload = {
      controlIds: portfolioControlIds,
      trials: 10_000,
      seed: MODEL_SEED,
    };

    simulatePortfolio(payload)
      .then((nextResults) => {
        if (!cancelled) {
          setPortfolioResults(nextResults);
          cachePortfolio(payload, nextResults);
          setPortfolioStatus("ready");
        }
      })
      .catch((requestError) => {
        if (!cancelled) {
          const cached = readCachedPortfolio(payload);
          if (cached) {
            setPortfolioResults(cached.data);
            setPortfolioError(`${requestError.message} Showing the last matching saved portfolio.`);
            setPortfolioStatus("cached");
          } else {
            setPortfolioResults(null);
            setPortfolioError(requestError.message);
            setPortfolioStatus("error");
          }
        }
      });

    return () => { cancelled = true; };
  }, [plannerMode, portfolioControlIds]);

  const recommendedControls = controls.filter((control) => recommendedIds.includes(control.id));
  const additionalControls = controls.filter((control) => (
    !recommendedIds.includes(control.id)
    && (!control.coverage || control.coverage.includes(selectedScenarioId))
  ));
  const otherScenarioControls = controls.filter((control) => (
    control.coverage && !control.coverage.includes(selectedScenarioId)
  ));

  function effectSummary(control) {
    if (!control.effects) return control.target || "Effect details pending";
    const effects = [];
    if (control.effects.frequencyMultiplier < 1) {
      effects.push(`frequency −${Math.round((1 - control.effects.frequencyMultiplier) * 100)}%`);
    }
    if (control.effects.vulnerabilityMultiplier < 1) {
      effects.push(`vulnerability −${Math.round((1 - control.effects.vulnerabilityMultiplier) * 100)}%`);
    }
    const primaryReduction = Math.round((1 - control.effects.primaryLossMultiplier) * 100);
    const secondaryReduction = Math.round((1 - control.effects.secondaryLossMultiplier) * 100);
    if (primaryReduction || secondaryReduction) {
      effects.push(`loss −${primaryReduction}% primary / −${secondaryReduction}% secondary`);
    }
    return effects.join(" · ");
  }

  function togglePortfolioControl(controlId) {
    setPortfolioControlIds((current) => (
      current.includes(controlId)
        ? current.filter((id) => id !== controlId)
        : [...current, controlId]
    ));
  }

  function resetActivePlanner() {
    if (plannerMode === "portfolio") {
      setPortfolioControlIds(controls.map((control) => control.id));
    } else {
      resetScenario();
    }
  }

  function renderControl(control, recommended = false, portfolioMode = false) {
    const selected = portfolioMode
      ? activePortfolioIds.includes(control.id)
      : selectedControlIds.includes(control.id);
    const applicable = portfolioMode || !control.coverage || control.coverage.includes(selectedScenarioId);
    const implementation = control.implementationWeeks;
    const toggle = portfolioMode ? togglePortfolioControl : toggleControl;

    return (
      <article className={`control-card${selected ? " selected" : ""}${!applicable ? " unavailable" : ""}`} key={control.id}>
        <button className="toggle" role="switch" aria-checked={selected} disabled={!applicable} aria-label={`${selected ? "Disable" : "Enable"} ${control.name}`} onClick={() => toggle(control.id)}><span /></button>
        <div className="control-description">
          <div className="control-title-row">
            <h3>{control.name}</h3>
            <span className="category-badge">{control.category || "Control"}</span>
            {recommended && <span className="recommended-badge">Recommended</span>}
          </div>
          <p>{applicable ? effectSummary(control) : `Switch to ${control.coverage.map((id) => scenarioNames[id] || id).join(" or ")} to enable`}</p>
          {control.coverage && <small>Coverage: {control.coverage.map((id) => scenarioNames[id] || id).join(", ")}</small>}
        </div>
        <div><span>Expected cost (low–high)</span><strong>{formatCurrency(control.cost.expected ?? control.cost.mode ?? control.cost)}</strong><small>{control.cost.low != null && `${formatCurrency(control.cost.low)}–${formatCurrency(control.cost.high)}`}</small></div>
        <div><span>Implementation</span><strong>{implementation ? `${implementation.mode} weeks` : "—"}</strong><small>{implementation && `${implementation.low}–${implementation.high} week range`}</small></div>
        <div><span>Confidence</span><strong>{control.confidence}</strong></div>
      </article>
    );
  }

  function controlSection(title, description, sectionControls, recommended = false, portfolioMode = false) {
    if (!sectionControls.length) return null;
    return (
      <section className="control-section">
        <div className="control-section-heading">
          <div><h2>{title}</h2><p>{description}</p></div>
          <span>{sectionControls.length} control{sectionControls.length === 1 ? "" : "s"}</span>
        </div>
        <div className="control-list">{sectionControls.map((control) => renderControl(control, recommended, portfolioMode))}</div>
      </section>
    );
  }

  return (
    <div className="page">
      <PageHeader
        eyebrow="Investment case"
        title="Control Investment Planner"
        description={plannerMode === "portfolio"
          ? "Estimate the combined investment and modelled benefit of controls across all four attack scenarios."
          : `Compare explicit control costs and modelled effects for ${selectedScenario?.name || "the selected scenario"}.`}
      >
        <div className="planner-actions">
          {plannerMode === "scenario" && <label className="select-label">
            Scenario
            <select value={selectedScenarioId} onChange={(event) => setSelectedScenarioId(event.target.value)}>
              {scenarios.map((scenario) => <option key={scenario.id} value={scenario.id}>{scenario.name}</option>)}
            </select>
          </label>}
          <button className="secondary-button" onClick={resetActivePlanner}>{plannerMode === "portfolio" ? "Select all controls" : "Reset recommendations"}</button>
        </div>
      </PageHeader>
      <div className="planner-mode" aria-label="Planner view">
        <button className={plannerMode === "scenario" ? "active" : ""} onClick={() => setPlannerMode("scenario")}>Selected scenario</button>
        <button className={plannerMode === "portfolio" ? "active" : ""} onClick={() => setPlannerMode("portfolio")}>All-scenario portfolio</button>
      </div>
      {plannerMode === "scenario" ? (
        <section className="planner-guide" aria-label="Control availability guide">
          <div><span className="guide-mark recommended" /><strong>Recommended</strong><p>Preselected for the current scenario.</p></div>
          <div><span className="guide-mark available" /><strong>Additional</strong><p>Applicable and available to test.</p></div>
          <div><span className="guide-mark unavailable" /><strong>Other scenario</strong><p>Switch scenarios to enable it.</p></div>
        </section>
      ) : (
        <section className="portfolio-guide">
          <strong>Portfolio rule</strong>
          <p>Every control is available. Shared controls are costed once, then applied to every scenario they cover.</p>
          <span>{activePortfolioIds.length} of {controls.length} selected</span>
        </section>
      )}
      {portfolioError && plannerMode === "portfolio" && <div className="status-message warning">{portfolioError}</div>}
      <section className="planner-summary">
        <div><span>Selected investment</span><strong>{formatCurrency(selectedCost)}</strong></div>
        <div><span>Expected loss avoided</span><strong>{formatCurrency(avoidedLoss)}</strong></div>
        <div><span>Net benefit</span><strong>{formatCurrency(netBenefit)}</strong></div>
        <div><span>Modelled ROSI</span><strong>{rosi.toFixed(1)}×</strong></div>
      </section>
      {plannerMode === "portfolio" && portfolioResults && (
        <section className="portfolio-breakdown panel">
          <div className="control-section-heading">
            <div><h2>Scenario-by-scenario impact</h2><p>Portfolio = one launch window + one year of the other three scenarios, summed trial by trial. Portfolio P95: {formatCurrency(portfolioResults.portfolio.baselineP95)} baseline, {formatCurrency(portfolioResults.portfolio.residualP95)} residual.</p></div>
            <span>{portfolioResults.meta.trialsPerScenario.toLocaleString()} trials each</span>
          </div>
          <div className="portfolio-table-wrap">
            <table className="portfolio-table">
              <thead><tr><th>Scenario</th><th>Basis</th><th>Baseline mean</th><th>Residual mean</th><th>Baseline P95</th><th>Loss avoided</th><th>Allocated cost</th><th>Controls</th></tr></thead>
              <tbody>{portfolioResults.scenarios.map((scenario) => (
                <tr key={scenario.scenarioId}>
                  <td>{scenario.scenarioName}</td>
                  <td>{scenario.analysisBasis === "launch-window" ? "7-day launch window" : "per year"}</td>
                  <td>{formatCurrency(scenario.baselineMean)}</td>
                  <td>{formatCurrency(scenario.residualMean)}</td>
                  <td>{formatCurrency(scenario.baselineP95)}</td>
                  <td>{formatCurrency(scenario.lossesAvoided)}</td>
                  <td>{formatCurrency(scenario.allocatedCost)}</td>
                  <td>{scenario.selectedControlIds.length}</td>
                </tr>
              ))}</tbody>
            </table>
          </div>
        </section>
      )}
      {plannerMode === "scenario" ? (
        <>
          {controlSection("Recommended for this scenario", "The model starts with these controls selected because they best match the scenario pathway.", recommendedControls, true)}
          {controlSection("Additional applicable controls", "These controls also cover the selected scenario and can be toggled into the comparison.", additionalControls)}
          {controlSection("Controls for other scenarios", "These remain visible for cross-scenario planning but cannot affect the current model.", otherScenarioControls)}
        </>
      ) : controlSection("Portfolio controls", "Toggle any control to test its organization-wide cost and combined modelled benefit.", controls, false, true)}
      {priorities && (
        <section className="panel priority-panel">
          <div className="control-section-heading">
            <div><h2>Control priority ranking</h2><p>Each control evaluated alone with analytic expected loss. Score weights and tier cutoffs (P1 ≥ 60, P2 ≥ 40) are team policy assumptions.</p></div>
            <span>Same scoring as the Excel workbook</span>
          </div>
          <div className="priority-table-wrap">
            <table className="priority-table">
              <thead><tr><th>Control</th><th>Expected cost</th><th>Loss avoided</th><th>ROSI</th><th>Score</th><th>Tier</th></tr></thead>
              <tbody>{priorities.controls.map((row) => (
                <tr key={row.controlId}>
                  <td>{row.name}</td>
                  <td>{formatCurrency(row.expectedCost)}</td>
                  <td>{formatCurrency(row.totalLossAvoided)}</td>
                  <td>{row.rosi.toFixed(1)}×</td>
                  <td>{row.priorityScore.toFixed(1)}</td>
                  <td>{row.tier}</td>
                </tr>
              ))}</tbody>
            </table>
          </div>
        </section>
      )}
      <p className="model-note">{(plannerMode === "portfolio" ? portfolioStatus === "loading" : status === "loading") ? "Recalculating control economics…" : plannerMode === "portfolio" ? "Portfolio economics sum expected loss across four separate scenario models; shared control costs are counted once." : "Costs are expected (triangular-mean) values, split equally across the scenarios each control covers. Control effects are team estimates, not vendor-measured."}</p>
    </div>
  );
}

