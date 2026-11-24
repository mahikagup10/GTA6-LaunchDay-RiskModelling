import { useEffect, useMemo, useState } from "react";
import PageHeader from "../components/PageHeader";
import { attackStages as fallbackStages, scenarios as fallbackScenarios } from "../data/mockData";
import { useWorkbench } from "../context/WorkbenchContext";

export default function AttackPaths() {
  const [activeStage, setActiveStage] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const { config, selectedScenarioId: selectedPathId, setSelectedScenarioId: setSelectedPathId } = useWorkbench();
  const scenarios = config?.scenarios || fallbackScenarios;
  const attackChains = config?.attackChains || { "launch-ddos": config?.attackChain || fallbackStages };
  const attackStages = attackChains[selectedPathId] || attackChains["launch-ddos"] || fallbackStages;
  const pathDetails = config?.attackPathDetails?.[selectedPathId];
  const selectedScenario = scenarios.find((scenario) => scenario.id === selectedPathId) || scenarios[0];
  const stage = attackStages[activeStage];
  const controlsById = useMemo(
    () => Object.fromEntries((config?.controls || []).map((control) => [control.id, control])),
    [config],
  );
  const sourcesById = useMemo(
    () => Object.fromEntries((config?.sources || []).map((source) => [source.id, source])),
    [config],
  );
  const stageControls = (stage.controlIds || []).map((id) => controlsById[id]).filter(Boolean);
  const stageSources = (stage.sourceIds || []).map((id) => sourcesById[id]).filter(Boolean);

  useEffect(() => {
    if (!isPlaying) return undefined;

    const timer = window.setTimeout(() => {
      setActiveStage((current) => {
        const nextStage = Math.min(current + 1, attackStages.length - 1);
        if (nextStage === attackStages.length - 1) setIsPlaying(false);
        return nextStage;
      });
    }, 2800);

    return () => window.clearTimeout(timer);
  }, [activeStage, attackStages.length, isPlaying]);

  useEffect(() => {
    setActiveStage(0);
    setIsPlaying(false);
  }, [selectedPathId]);

  function selectStage(index) {
    setIsPlaying(false);
    setActiveStage(index);
  }

  function togglePlayback() {
    if (!isPlaying && activeStage === attackStages.length - 1) {
      setActiveStage(0);
    }
    setIsPlaying((current) => !current);
  }

  function moveStage(direction) {
    setIsPlaying(false);
    setActiveStage((current) => Math.min(Math.max(current + direction, 0), attackStages.length - 1));
  }

  return (
    <div className="page">
      <PageHeader eyebrow="Threat narrative" title="Attack Paths" description="Trace how a cyber event becomes measurable business impact and where controls interrupt the chain." />

      <section className="scenario-list">
        {scenarios.map((scenario) => (
          <button
            type="button"
            key={scenario.id}
            className={`scenario-card scenario-selector${scenario.id === selectedPathId ? " selected" : ""}${scenario.id === "launch-ddos" ? " featured" : ""}`}
            onClick={() => setSelectedPathId(scenario.id)}
            aria-pressed={scenario.id === selectedPathId}
          >
            <span>{scenario.severity}</span>
            <h3>{scenario.name}</h3>
            <p>{scenario.summary}</p>
            <small>{scenario.id === "launch-ddos" ? "Detailed showcase" : "Concise 4-stage path"}</small>
          </button>
        ))}
      </section>

      <section className="panel attack-panel">
        <div className="section-heading">
          <div><span className="eyebrow">{selectedPathId === "launch-ddos" ? "Detailed showcase pathway" : "Concise scenario pathway"}</span><h2>{selectedScenario?.name} attack chain</h2></div>
          <div className="chain-controls" aria-label="Attack chain playback controls">
            <button className="chain-control" onClick={() => moveStage(-1)} disabled={activeStage === 0} aria-label="Previous attack stage">←</button>
            <button className={isPlaying ? "chain-control play active" : "chain-control play"} onClick={togglePlayback} aria-pressed={isPlaying}>
              {isPlaying ? "Pause" : activeStage === attackStages.length - 1 ? "Replay" : "Play path"}
            </button>
            <button className="chain-control" onClick={() => moveStage(1)} disabled={activeStage === attackStages.length - 1} aria-label="Next attack stage">→</button>
          </div>
        </div>

        {pathDetails && <div className="ddos-deep-dive">
          <div className="deep-dive-heading">
            <div><span className="eyebrow">Technical system view</span><h3>How attack traffic becomes business loss</h3></div>
            <p>{pathDetails.modelConnection}</p>
          </div>
          <div className="technical-flow" aria-label="DDoS technical traffic flow">
            {pathDetails.technicalFlow.map((node, index) => <div className="flow-node" key={node.name}>
              <span>{String(index + 1).padStart(2, "0")}</span>
              <strong>{node.name}</strong>
              <small>{node.detail}</small>
            </div>)}
          </div>
          <div className="response-timeline" aria-label="DDoS response timeline">
            {pathDetails.responseTimeline.map((item) => <div key={item.phase}>
              <span>{item.phase}</span>
              <p>{item.decision}</p>
            </div>)}
          </div>
        </div>}

        <div className="chain-progress" aria-hidden="true"><span style={{ width: `${(activeStage / (attackStages.length - 1)) * 100}%` }} /></div>
        <div className="attack-chain" aria-label={`${selectedScenario?.name} stages`}>
          {attackStages.map((item, index) => (
            <button
              key={item.id}
              className={`stage-button${index === activeStage ? " active" : ""}${index < activeStage ? " complete" : ""}`}
              onClick={() => selectStage(index)}
              aria-current={index === activeStage ? "step" : undefined}
            >
              <span>{index < activeStage ? "✓" : item.number}</span>{item.title}
            </button>
          ))}
        </div>

        <div className="stage-content" key={stage.id} aria-live="polite">
          <div className="stage-intro">
            <div>
              <span className="stage-count">Stage {activeStage + 1} of {attackStages.length}</span>
              <h3>{stage.title}</h3>
              <p>{stage.attackerAction || stage.effect}</p>
            </div>
            <span className={`evidence-badge ${stage.evidenceType || "model-assumption"}`}>{(stage.evidenceType || "model-assumption").replace("-", " ")}</span>
          </div>

          <div className="stage-narrative-grid">
            <article>
              <span className="detail-label">Defender signal</span>
              <p>{stage.defenderSignal || "Stage-specific monitoring evidence will be added."}</p>
            </article>
            <article>
              <span className="detail-label">Business effect</span>
              <p>{stage.businessEffect || stage.effect}</p>
            </article>
            <article>
              <span className="detail-label">Decision question</span>
              <p>{stage.decisionQuestion || "Which control can interrupt this stage?"}</p>
            </article>
          </div>

          {stage.substeps && <div className="ddos-stage-depth">
            <article>
              <span className="detail-label">Technical substeps</span>
              <ol>{stage.substeps.map((substep) => <li key={substep}>{substep}</li>)}</ol>
            </article>
            <article>
              <span className="detail-label">Measurable indicators</span>
              <div className="indicator-chips">{stage.technicalIndicators.map((indicator) => <span key={indicator}>{indicator}</span>)}</div>
            </article>
          </div>}

          {stage.fairEffects && <div className="fair-linkage">
            <div><span className="eyebrow">Attack-to-model connection</span><h3>How this stage changes quantified risk</h3></div>
            <div>{stage.fairEffects.map((item) => <article key={item.factor}><strong>{item.factor}</strong><p>{item.effect}</p></article>)}</div>
          </div>}

          <div className="stage-meta-grid">
            <div><span className="detail-label">MITRE ATT&CK</span><strong>{stage.technique}</strong></div>
            <div><span className="detail-label">STRIDE</span><strong>{stage.stride}</strong></div>
            <div><span className="detail-label">Evidence confidence</span><strong>{stage.confidence || "Medium"}</strong></div>
          </div>

          <div className="control-interruption">
            <div>
              <span className="detail-label">Control interruption point</span>
              <p>{stage.controlIntervention || "Relevant controls reduce the likelihood or impact of this stage."}</p>
            </div>
            <div className="control-chips">
              {stageControls.length ? stageControls.map((control) => (
                <span className="control-chip" key={control.id}>{control.name}</span>
              )) : <span className="control-chip">Control mapping pending</span>}
            </div>
          </div>

          {stage.executiveDecision && <div className="executive-decision">
            <span className="detail-label">Executive decision at this stage</span>
            <strong>{stage.executiveDecision}</strong>
          </div>}

          <div className="stage-evidence">
            <span className="detail-label">Evidence and sources</span>
            {stageSources.length ? stageSources.map((source) => (
              <a href={source.url} target="_blank" rel="noreferrer" key={source.id}>
                {source.title}<small>Accessed {source.accessDate}</small>
              </a>
            )) : <p>Team-developed scenario assumption; external validation is pending.</p>}
          </div>
        </div>
      </section>
    </div>
  );
}

