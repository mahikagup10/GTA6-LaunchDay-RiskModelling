import { useEffect, useMemo, useState } from "react";
import PageHeader from "../components/PageHeader";
import ControlHeatMap from "../components/charts/ControlHeatMap";
import { useWorkbench } from "../context/WorkbenchContext";
import { simulatePortfolio } from "../services/api";
import { cachePortfolio, readCachedPortfolio } from "../utils/cache";
import { basisSuffix, basisTag, effectText, formatCurrency, formatMultiple, formatPercent } from "../utils/formatters";

export default function ControlPlanner() {
  const {
    config, results, status, priorities, priorityById, selectedScenarioId, setSelectedScenarioId, selectedScenario,
    selectedControlIds, toggleControl, resetScenario, demoResetVersion, seed, trials,
  } = useWorkbench();
  const [plannerMode, setPlannerMode] = useState("scenario");
  const [portfolioControlIds, setPortfolioControlIds] = useState(null);
  const [portfolioResults, setPortfolioResults] = useState(null);
  const [portfolioStatus, setPortfolioStatus] = useState("idle");
  const [portfolioError, setPortfolioError] = useState("");
  const [selectedCell, setSelectedCell] = useState(null);
  const controls = config?.controls || [];
  const scenarios = config?.scenarios || [];
  const scenarioNames = Object.fromEntries(scenarios.map((scenario) => [scenario.id, scenario.name]));
  const controlsById = Object.fromEntries(controls.map((control) => [control.id, control]));
  const recommendedIds = selectedScenario?.recommendedControlIds || [];
  const activePortfolioIds = portfolioControlIds || [];
  const timeBasis = plannerMode === "portfolio" ? "first-year" : (selectedScenario?.timeBasis || "launch-event");
  const economics = plannerMode === "portfolio" ? portfolioResults?.controlEconomics : results?.controlEconomics;
  const breakdownById = Object.fromEntries((results?.controlBreakdown || []).map((row) => [row.controlId, row]));

  const inputLabels = useMemo(() => {
    const labels = {};
    scenarios.forEach((scenario) => scenario.inputs?.forEach((item) => { labels[`${scenario.id}:${item.key}`] = item.label; }));
    return labels;
  }, [scenarios]);
  const stepTitles = useMemo(() => {
    const titles = {};
    Object.entries(config?.attackPaths || {}).forEach(([scenarioId, steps]) => steps.forEach((step) => { titles[`${scenarioId}:${step.id}`] = step.title; }));
    return titles;
  }, [config]);

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
    setSelectedCell(null);
    if (config) setPortfolioControlIds(config.controls.map((control) => control.id));
  }, [config, demoResetVersion]);

  useEffect(() => {
    if (plannerMode !== "portfolio" || portfolioControlIds === null) return undefined;
    let cancelled = false;
    setPortfolioStatus("loading");
    setPortfolioError("");

    const payload = { controlIds: portfolioControlIds, trials, seed };

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
  }, [plannerMode, portfolioControlIds, seed, trials]);

  const recommendedControls = controls.filter((control) => recommendedIds.includes(control.id));
  const additionalControls = controls.filter((control) => !recommendedIds.includes(control.id) && control.coverage.includes(selectedScenarioId));
  const otherScenarioControls = controls.filter((control) => !control.coverage.includes(selectedScenarioId));

  function effectSummary(control, scenarioId) {
    const effects = control.effects?.[scenarioId];
    if (!effects) return `Applies to ${control.coverage.map((id) => scenarioNames[id] || id).join(", ")}`;
    return Object.entries(effects).map(([key, effect]) => `${inputLabels[`${scenarioId}:${key}`] || key} ${effectText(effect)}`).join(" · ");
  }

  function togglePortfolioControl(controlId) {
    setPortfolioControlIds((current) => (
      current.includes(controlId) ? current.filter((id) => id !== controlId) : [...current, controlId]
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
    const selected = portfolioMode ? activePortfolioIds.includes(control.id) : selectedControlIds.includes(control.id);
    const applicable = portfolioMode || control.coverage.includes(selectedScenarioId);
    const implementation = control.implementationWeeks;
    const toggle = portfolioMode ? togglePortfolioControl : toggleControl;
    const priority = priorityById[control.id];
    const standalone = breakdownById[control.id];
    const cell = priority?.scenarios?.[selectedScenarioId];
    const scenarioForEffects = portfolioMode ? control.coverage[0] : selectedScenarioId;

    return (
      <article className={`control-card wide${selected ? " selected" : ""}${!applicable ? " unavailable" : ""}`} key={control.id}>
        <button className="toggle" role="switch" aria-checked={selected} disabled={!applicable} aria-label={`${selected ? "Disable" : "Enable"} ${control.name}`} onClick={() => toggle(control.id)}><span /></button>
        <div className="control-description">
          <div className="control-title-row">
            <h3>{control.name}</h3>
            <span className="category-badge">{control.group}</span>
            {recommended && <span className="recommended-badge">Recommended</span>}
            {priority && <span className={`priority-badge p${priority.priority}`} title={priority.elevationReason || priority.priorityLabel}>P{priority.priority} · {priority.priorityScore}</span>}
          </div>
          <p>{applicable ? effectSummary(control, scenarioForEffects) : `Switch to ${control.coverage.map((id) => scenarioNames[id] || id).join(" or ")} to enable`}</p>
          <small>Coverage: {control.coverage.map((id) => scenarioNames[id] || id).join(", ")} · Confidence: {control.confidence}</small>
          <small>NIST CSF 2.0: {control.nist.join(", ")} ({control.nistFunctions.join(", ")}){control.mitre?.length ? ` · ATT&CK: ${control.mitre.join(", ")}` : ""} · Owner: {control.owner}</small>
        </div>
        <div><span>Cost ({control.costBasisLabel.toLowerCase()})</span><strong>{formatCurrency(control.cost.likely)}</strong><small>{formatCurrency(control.cost.low)}–{formatCurrency(control.cost.high)}</small></div>
        <div><span>Implementation</span><strong>{implementation.mode} weeks</strong><small>{implementation.low}–{implementation.high} week range</small></div>
        <div>
          <span>{portfolioMode ? "First-year ROSI" : "Stand-alone ROSI"}</span>
          <strong>{portfolioMode
            ? formatMultiple(priority?.firstYearRosi)
            : standalone ? formatMultiple(standalone.standaloneRosi) : cell ? formatMultiple((cell.lossReduction - cell.comparableCost) / cell.comparableCost) : "—"}</strong>
          <small>{portfolioMode
            ? `Avoids ${formatCurrency(priority?.firstYearLossReduction)} in year one`
            : cell ? `Avoids ${formatCurrency(cell.lossReduction)} ${basisSuffix(cell.timeBasis)}` : `Confidence ${control.confidence}`}</small>
        </div>
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

  const cellDetail = selectedCell && priorities ? (() => {
    const row = priorities.controls.find((item) => item.controlId === selectedCell.controlId);
    const control = controlsById[selectedCell.controlId];
    const detail = row?.scenarios[selectedCell.scenarioId];
    return { row, control, detail };
  })() : null;

  const busy = plannerMode === "portfolio" ? portfolioStatus === "loading" : status === "loading";
  const costDetail = plannerMode === "portfolio" ? "USD · first-year cost, shared controls once" : timeBasis === "launch-event" ? "USD · full first-year cost" : "USD · annualized cost";
  const lossDetail = plannerMode === "portfolio" ? "USD · launch event + year one" : basisTag(timeBasis);

  return (
    <div className="page">
      <PageHeader
        eyebrow="Investment case"
        title="Control Investment Planner"
        description={plannerMode === "portfolio"
          ? "First-year view across all four scenarios: one GTA VI launch event plus twelve months of the annual risks."
          : `Costs, modeled effects, and priority for ${selectedScenario?.name || "the selected scenario"}.`}
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
      {plannerMode === "portfolio" ? (
        <section className="portfolio-guide">
          <strong>Portfolio rule</strong>
          <p>{portfolioResults?.meta.basis || "Shared controls are costed once, then applied to every scenario they cover."}</p>
          <span>{activePortfolioIds.length} of {controls.length} selected</span>
        </section>
      ) : (
        <section className="portfolio-guide">
          <strong>Cost basis</strong>
          <p>{economics?.costBasisNote || "Control cost is put on the same time basis as the scenario's loss."}</p>
          <span>{basisTag(timeBasis)}</span>
        </section>
      )}
      {portfolioError && plannerMode === "portfolio" && <div className="status-message warning">{portfolioError}</div>}
      <section className="planner-summary five">
        <div><span>Selected investment</span><strong>{formatCurrency(economics?.estimatedCost || 0)}</strong><small>{costDetail}{economics?.costRange ? ` · range ${formatCurrency(economics.costRange.low)}–${formatCurrency(economics.costRange.high)}` : ""}</small></div>
        <div><span>Expected loss avoided</span><strong>{formatCurrency(economics?.lossesAvoided || 0)}</strong><small>{lossDetail}</small></div>
        <div><span>Net benefit</span><strong>{formatCurrency(economics?.netBenefit || 0)}</strong><small>Loss avoided − cost</small></div>
        <div><span>Modeled ROSI</span><strong>{formatMultiple(economics?.rosi ?? 0)}</strong><small>Net benefit ÷ cost</small></div>
        <div><span>P95 reduction</span><strong>{plannerMode === "portfolio" ? "—" : formatCurrency(economics?.p95Reduction || 0)}</strong><small>{plannerMode === "portfolio" ? "See per-scenario table" : "Tail risk, baseline − residual"}</small></div>
      </section>

      {plannerMode === "portfolio" && portfolioResults && (
        <section className="portfolio-breakdown panel">
          <div className="control-section-heading">
            <div><h2>Scenario-by-scenario impact</h2><p>First-year exposure = one launch event + one year of each annual scenario.</p></div>
            <span>{portfolioResults.meta.trialsPerScenario.toLocaleString()} trials each</span>
          </div>
          <div className="portfolio-table-wrap">
            <table className="portfolio-table">
              <thead><tr><th>Scenario</th><th>Basis</th><th>Baseline</th><th>Residual</th><th>Loss avoided</th><th>Baseline P95</th><th>Residual P95</th><th>Controls</th></tr></thead>
              <tbody>{portfolioResults.scenarios.map((scenario) => (
                <tr key={scenario.scenarioId}>
                  <td>{scenario.scenarioName}</td>
                  <td>{basisSuffix(scenario.timeBasis)}</td>
                  <td>{formatCurrency(scenario.baselineMean)}</td>
                  <td>{formatCurrency(scenario.residualMean)}</td>
                  <td>{formatCurrency(scenario.lossesAvoided)}</td>
                  <td>{formatCurrency(scenario.baselineP95)}</td>
                  <td>{formatCurrency(scenario.residualP95)}</td>
                  <td>{scenario.selectedControlIds.length}</td>
                </tr>
              ))}</tbody>
            </table>
          </div>
        </section>
      )}

      <section className="two-column heat-row">
        <article className="panel">
          <span className="eyebrow">Control-to-scenario benefit heat map</span>
          <h2>Where each control pays off</h2>
          <ControlHeatMap heatmap={priorities?.heatmap} onSelect={setSelectedCell} selectedCell={selectedCell} />
          <small>Each cell is the expected loss the control avoids on its own in that scenario (USD per launch event or per year). Intensity: high ≥ 30% of the scenario's mean loss, medium 10–30%, low below 10%. Click a cell for details.</small>
        </article>
        <article className="panel heat-detail">
          <span className="eyebrow">Cell detail</span>
          {cellDetail?.control && cellDetail.detail ? (
            <>
              <h2>{cellDetail.control.name}</h2>
              <p><strong>{scenarioNames[selectedCell.scenarioId]}</strong>: avoids {formatCurrency(cellDetail.detail.lossReduction)} {basisSuffix(cellDetail.detail.timeBasis)} ({formatPercent(cellDetail.detail.reductionShare)} of the scenario's expected loss) and cuts P95 by {formatCurrency(cellDetail.detail.p95Reduction)}.</p>
              <span className="detail-label">Model factors changed</span>
              <ul>{Object.entries(cellDetail.control.effects[selectedCell.scenarioId]).map(([key, effect]) => (
                <li key={key}>{inputLabels[`${selectedCell.scenarioId}:${key}`] || key}: {effectText(effect)}</li>
              ))}</ul>
              <span className="detail-label">Attack steps interrupted</span>
              <ul>{(cellDetail.detail.attackSteps || []).map((stepId) => <li key={stepId}>{stepTitles[`${selectedCell.scenarioId}:${stepId}`] || stepId}</li>)}</ul>
              <span className="detail-label">Why</span>
              <p>{cellDetail.control.rationale}</p>
            </>
          ) : selectedCell ? <p>This control does not apply to {scenarioNames[selectedCell.scenarioId]}.</p> : <p>Click a heat-map cell to see the attack steps and model factors behind it.</p>}
        </article>
      </section>

      {priorities && (
        <section className="panel priority-panel">
          <div className="control-section-heading">
            <div><h2>Recommendation priority and implementation sequence</h2><p>100-point score: expected loss reduction 35, reduction per dollar 25, P95 reduction 20, scenarios helped 10, feasibility and confidence 10. First-year view.</p></div>
          </div>
          <div className="portfolio-table-wrap">
            <table className="portfolio-table priority-table">
              <thead><tr><th>#</th><th>Control</th><th>Priority</th><th>Score</th><th>Year-one loss avoided</th><th>First-year cost</th><th>ROSI</th><th>P95 reduction</th><th>Weeks</th></tr></thead>
              <tbody>{[...priorities.controls].sort((a, b) => a.sequence - b.sequence).map((row) => (
                <tr key={row.controlId} title={row.elevationReason || ""}>
                  <td>{row.sequence}</td>
                  <td>{row.name}{row.elevated ? " *" : ""}</td>
                  <td><span className={`priority-badge p${row.priority}`}>{row.priorityLabel.replace(" - ", ": ")}</span></td>
                  <td>{row.priorityScore}</td>
                  <td>{formatCurrency(row.firstYearLossReduction)}</td>
                  <td>{formatCurrency(row.firstYearCost)}</td>
                  <td>{formatMultiple(row.firstYearRosi)}</td>
                  <td>{formatCurrency(row.p95ReductionTotal)}</td>
                  <td>{controlsById[row.controlId]?.implementationWeeks.mode}</td>
                </tr>
              ))}</tbody>
            </table>
          </div>
          <small>* Elevated above its score as a prerequisite: testing moves protection and failover to "implemented and tested" and validates the other launch controls.</small>
        </section>
      )}

      {plannerMode === "scenario" ? (
        <>
          {controlSection("Recommended for this scenario", "Preselected because they best match this scenario's attack path.", recommendedControls, true)}
          {controlSection("Additional applicable controls", "These also cover the selected scenario and can be toggled into the comparison.", additionalControls)}
          {controlSection("Controls for other scenarios", "Visible for cross-scenario planning; switch scenarios to test them.", otherScenarioControls)}
        </>
      ) : controlSection("Portfolio controls", "Toggle any control to test its organization-wide first-year cost and benefit.", controls, false, true)}
      <p className="model-note">{busy ? "Recalculating control economics…" : plannerMode === "portfolio" ? "Portfolio economics add one launch event to one year of the annual scenarios; shared control costs are counted once." : "Economics come from the same fixed-seed simulation used on every page. Vendor effectiveness claims are treated as supporting evidence, not proven Take-Two performance."}</p>
    </div>
  );
}
