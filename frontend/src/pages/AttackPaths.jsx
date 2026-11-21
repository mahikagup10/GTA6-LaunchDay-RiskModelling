import { useEffect, useMemo, useState } from "react";
import PageHeader from "../components/PageHeader";
import { attackStages as fallbackStages, scenarios as fallbackScenarios } from "../data/mockData";
import { useWorkbench } from "../context/WorkbenchContext";

export default function AttackPaths() {
  const [activeStage, setActiveStage] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const { config } = useWorkbench();
  const scenarios = config?.scenarios || fallbackScenarios;
  const attackStages = config?.attackChain || fallbackStages;
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
          <article key={scenario.id} className={scenario.id === "launch-ddos" ? "scenario-card featured" : "scenario-card"}>
            <span>{scenario.severity}</span>
            <h3>{scenario.name}</h3>
            <p>{scenario.summary}</p>
          </article>
        ))}
      </section>

      <section className="panel attack-panel">
        <div className="section-heading">
          <div><span className="eyebrow">Detailed pathway</span><h2>Launch-Day DDoS attack chain</h2></div>
          <div className="chain-controls" aria-label="Attack chain playback controls">
            <button className="chain-control" onClick={() => moveStage(-1)} disabled={activeStage === 0} aria-label="Previous attack stage">←</button>
            <button className={isPlaying ? "chain-control play active" : "chain-control play"} onClick={togglePlayback} aria-pressed={isPlaying}>
              {isPlaying ? "Pause" : activeStage === attackStages.length - 1 ? "Replay" : "Play path"}
            </button>
            <button className="chain-control" onClick={() => moveStage(1)} disabled={activeStage === attackStages.length - 1} aria-label="Next attack stage">→</button>
          </div>
        </div>
        <div className="chain-progress" aria-hidden="true"><span style={{ width: `${(activeStage / (attackStages.length - 1)) * 100}%` }} /></div>
        <div className="attack-chain" aria-label="Launch-Day DDoS stages">
          {attackStages.map((item, index) => (
            <button
              key={item.number}
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

