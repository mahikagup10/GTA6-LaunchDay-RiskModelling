import { useEffect, useState } from "react";
import PageHeader from "../components/PageHeader";
import LossDistributionChart from "../components/charts/LossDistributionChart";
import { controls as fallbackControls } from "../data/mockData";
import { useWorkbench } from "../context/WorkbenchContext";
import { simulatePortfolio } from "../services/api";
import { cachePortfolio, readCachedPortfolio } from "../utils/cache";
import { formatCurrency, formatPercent } from "../utils/formatters";

export default function ControlPlanner() {
  const { config, results, status, assumptionProfileId, selectedScenarioId, setSelectedScenarioId, selectedControlIds, toggleControl, resetScenario, demoResetVersion } = useWorkbench();
  const [plannerMode, setPlannerMode] = useState("scenario");
  const [portfolioControlIds, setPortfolioControlIds] = useState(null);
  const [portfolioResults, setPortfolioResults] = useState(null);
  const [portfolioStatus, setPortfolioStatus] = useState("idle");
  const [portfolioError, setPortfolioError] = useState("");
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
  const recommendations = plannerMode === "portfolio" ? portfolioResults?.controlRecommendations || [] : results?.controlRecommendations || [];
  const recommendationById = Object.fromEntries(recommendations.map((item) => [item.controlId, item]));
  const prioritySort = (left, right) => (recommendationById[left.id]?.priorityRank || 999) - (recommendationById[right.id]?.priorityRank || 999);

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
      assumptionProfileId,
      trials: 10_000,
      seed: 243,
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
  }, [assumptionProfileId, plannerMode, portfolioControlIds]);

  const recommendedControls = controls.filter((control) => recommendedIds.includes(control.id)).sort(prioritySort);
  const additionalControls = controls.filter((control) => (
    !recommendedIds.includes(control.id)
    && (!control.coverage || control.coverage.includes(selectedScenarioId))
  )).sort(prioritySort);
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
    const recommendation = recommendationById[control.id];
    const expectedCost = control.cost.low != null
      ? (control.cost.low + control.cost.mode + control.cost.high) / 3
      : control.cost;

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
          {recommendation && <div className="standalone-economics">
            <span><small>Priority</small><strong>#{recommendation.priorityRank}</strong></span>
            <span><small>Loss avoided</small><strong>{formatCurrency(recommendation.lossesAvoided)}</strong></span>
            <span><small>Net benefit</small><strong>{formatCurrency(recommendation.netBenefit)}</strong></span>
            <span><small>ROSI</small><strong>{recommendation.rosi == null ? "—" : `${recommendation.rosi.toFixed(1)}×`}</strong></span>
          </div>}
          {control.effectEvidence && <details className="control-evidence">
            <summary>Why these effect estimates?</summary>
            <p>{control.effectEvidence.rationale}</p>
            <div><span className="evidence-badge team-estimate">Team estimate</span><strong>Confidence: {control.effectEvidence.confidence}</strong></div>
            <a href={control.effectEvidence.source.url} target="_blank" rel="noreferrer">{control.effectEvidence.source.title}</a>
            <small>Accessed {control.effectEvidence.source.accessDate}. {control.effectEvidence.source.scope}</small>
          </details>}
        </div>
        <div><span>Expected modelled cost</span><strong>{formatCurrency(expectedCost)}</strong><small>{control.cost.low != null && `${formatCurrency(control.cost.low)}–${formatCurrency(control.cost.high)} range · ${formatCurrency(control.cost.mode)} most likely`}</small></div>
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
          <div><span className="guide-mark recommended" /><strong>Pathway-preselected</strong><p>Directly mapped to the scenario; financial priority is shown on each card.</p></div>
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
      {plannerMode === "portfolio" && portfolioResults && <>
        <section className="metric-grid portfolio-tail-grid">
          <div className="metric-card"><span>Baseline portfolio P95</span><strong>{formatCurrency(portfolioResults.portfolio.baselineMetrics.p95)}</strong><small>Severe combined outcome</small></div>
          <div className="metric-card success"><span>Residual portfolio P95</span><strong>{formatCurrency(portfolioResults.portfolio.residualMetrics.p95)}</strong><small>With selected controls</small></div>
          <div className="metric-card"><span>Baseline portfolio P99</span><strong>{formatCurrency(portfolioResults.portfolio.baselineMetrics.p99)}</strong><small>Extreme tail outcome</small></div>
          <div className="metric-card success"><span>Residual above $100M</span><strong>{formatPercent(portfolioResults.portfolio.residualMetrics.probabilityAbove100m)}</strong><small>Selected-control tail probability</small></div>
        </section>
        <article className="panel portfolio-distribution">
          <span className="eyebrow">Combined portfolio distribution</span>
          <LossDistributionChart baseline={portfolioResults.portfolio.baselineHistogram} residual={portfolioResults.portfolio.residualHistogram} />
          <small>Each trial combines launch-event DDoS with annual losses from the other three scenarios.</small>
        </article>
      </>}
      {plannerMode === "portfolio" && portfolioResults && (
        <section className="portfolio-breakdown panel">
          <div className="control-section-heading">
            <div><h2>Scenario-by-scenario impact</h2><p>A true portfolio distribution combines each trial: launch-event DDoS plus annual estimates for the other scenarios.</p></div>
            <span>{portfolioResults.meta.trialsPerScenario.toLocaleString()} trials each</span>
          </div>
          <div className="portfolio-table-wrap">
            <table className="portfolio-table">
              <thead><tr><th>Scenario</th><th>Basis</th><th>Baseline</th><th>Residual</th><th>Loss avoided</th><th>Controls</th></tr></thead>
              <tbody>{portfolioResults.scenarios.map((scenario) => (
                <tr key={scenario.scenarioId}>
                  <td>{scenario.scenarioName}</td>
                  <td>{scenario.analysisBasis === "launch-event" ? "Launch event" : "Annual"}</td>
                  <td>{formatCurrency(scenario.baselineMean)}</td>
                  <td>{formatCurrency(scenario.residualMean)}</td>
                  <td>{formatCurrency(scenario.lossesAvoided)}</td>
                  <td>{scenario.selectedControlIds.length}</td>
                </tr>
              ))}</tbody>
            </table>
          </div>
        </section>
      )}
      {plannerMode === "scenario" ? (
        <>
          {controlSection("Pathway-preselected controls", "The model starts with these controls because they directly interrupt the scenario pathway. Priority numbers separately rank standalone expected net benefit.", recommendedControls, true)}
          {controlSection("Additional applicable controls", "These controls also cover the selected scenario and can be toggled into the comparison.", additionalControls)}
          {controlSection("Controls for other scenarios", "These remain visible for cross-scenario planning but cannot affect the current model.", otherScenarioControls)}
        </>
      ) : controlSection("Portfolio controls", "Controls are ordered by standalone portfolio net benefit. Toggle any combination to test organization-wide cost and benefit.", [...controls].sort(prioritySort), false, true)}
      {recommendations.length > 0 && <p className="model-note"><strong>Recommendation method:</strong> {plannerMode === "portfolio" ? portfolioResults?.recommendationMethod : results?.recommendationMethod} Standalone values are not additive because controls can overlap.</p>}
      <p className="model-note">{(plannerMode === "portfolio" ? portfolioStatus === "loading" : status === "loading") ? "Recalculating control economics…" : plannerMode === "portfolio" ? "Portfolio economics sum expected loss across four separate scenario models; shared control costs are counted once." : "Control economics are calculated by the same fixed-seed simulation used across all four pages."}</p>
    </div>
  );
}

