import { useEffect, useMemo, useState } from "react";
import PageHeader from "../components/PageHeader";
import { attackStages as fallbackStages, scenarios as fallbackScenarios } from "../data/mockData";
import { useWorkbench } from "../context/WorkbenchContext";
import { effectText, readableEvidence } from "../utils/formatters";

function CompactPath({ title, subtitle, steps, controlsById, selectedControlIds }) {
  return (
    <article className="panel compact-path">
      <div className="compact-path-heading">
        <div><span className="eyebrow">{subtitle}</span><h3>{title}</h3></div>
      </div>
      <ol className="compact-steps">
        {steps.map((step) => {
          const interrupted = step.controlIds.some((id) => selectedControlIds.includes(id));
          return (
            <li key={step.id} className={interrupted ? "interrupted" : ""}>
              <span className="compact-number">{step.number}</span>
              <strong>{step.title}</strong>
              <small>{step.technique} · STRIDE: {step.stride}</small>
              <p>{step.evidence}</p>
              <div className="control-chips">
                {step.controlIds.map((id) => controlsById[id] && (
                  <span key={id} className={`control-chip${selectedControlIds.includes(id) ? " active" : ""}`}>{controlsById[id].name}</span>
                ))}
              </div>
            </li>
          );
        })}
      </ol>
    </article>
  );
}

export default function AttackPaths() {
  const [activeStage, setActiveStage] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const { config, demoResetVersion, selectedControlIds, selectedScenarioId, setSelectedScenarioId } = useWorkbench();
  const scenarios = config?.scenarios || fallbackScenarios;
  const attackStages = config?.attackChain || fallbackStages;
  const stage = attackStages[Math.min(activeStage, attackStages.length - 1)];
  const controlsById = useMemo(
    () => Object.fromEntries((config?.controls || []).map((control) => [control.id, control])),
    [config],
  );
  const sourcesById = useMemo(
    () => Object.fromEntries((config?.sources || []).map((source) => [source.id, source])),
    [config],
  );
  const ddosScenario = scenarios.find((item) => item.id === "launch-ddos");
  const inputLabels = Object.fromEntries((ddosScenario?.inputs || []).map((item) => [item.key, item.label]));
  const ddosSelected = selectedScenarioId === "launch-ddos" ? selectedControlIds : [];
  const stageControls = (stage.controlIds || []).map((id) => controlsById[id]).filter(Boolean);
  const stageSources = (stage.sourceIds || []).map((id) => sourcesById[id]).filter(Boolean);
  const isInterrupted = (item) => (item.controlIds || []).some((id) => ddosSelected.includes(id));
  const interruptedCount = attackStages.filter(isInterrupted).length;

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
  }, [demoResetVersion]);

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
      <PageHeader eyebrow="Threat narrative" title="Attack Paths" description="How each attack becomes a financial loss, and where the selected controls interrupt it." />

      <section className="scenario-list">
        {scenarios.map((scenario) => (
          <button
            key={scenario.id}
            className={`scenario-card${scenario.id === "launch-ddos" ? " featured" : ""}${scenario.id === selectedScenarioId ? " active" : ""}`}
            onClick={() => setSelectedScenarioId(scenario.id)}
          >
            <span>{scenario.severity} · {scenario.depth === "detailed" ? "Detailed path" : scenario.depth === "comparison" ? "Comparison path" : "Summary"}</span>
            <h3>{scenario.name}</h3>
            <p>{scenario.summary}</p>
            {scenario.mitre && <small className="mapping-line">ATT&CK: {scenario.mitre.join(", ")}</small>}
            {scenario.stride && <small className="mapping-line">STRIDE: {scenario.stride.join(", ")}</small>}
          </button>
        ))}
      </section>

      <section className="panel attack-panel">
        <div className="section-heading">
          <div>
            <span className="eyebrow">Detailed pathway · {interruptedCount} of {attackStages.length} steps interrupted by selected controls</span>
            <h2>Launch-Day DDoS attack chain</h2>
            {selectedScenarioId !== "launch-ddos" && (
              <button className="text-link as-button" onClick={() => setSelectedScenarioId("launch-ddos")}>Select Launch-Day DDoS to see control highlights →</button>
            )}
          </div>
          <div className="chain-controls" aria-label="Attack chain playback controls">
            <button className="chain-control" onClick={() => moveStage(-1)} disabled={activeStage === 0} aria-label="Previous attack stage">←</button>
            <button className={isPlaying ? "chain-control play active" : "chain-control play"} onClick={togglePlayback} aria-pressed={isPlaying}>
              {isPlaying ? "Pause" : activeStage === attackStages.length - 1 ? "Replay" : "Play path"}
            </button>
            <button className="chain-control" onClick={() => moveStage(1)} disabled={activeStage === attackStages.length - 1} aria-label="Next attack stage">→</button>
          </div>
        </div>
        <div className="chain-progress" aria-hidden="true"><span style={{ width: `${(activeStage / (attackStages.length - 1)) * 100}%` }} /></div>
        <div className="attack-chain seven" aria-label="Launch-Day DDoS stages">
          {attackStages.map((item, index) => (
            <button
              key={item.id || item.number}
              className={`stage-button${index === activeStage ? " active" : ""}${index < activeStage ? " complete" : ""}${isInterrupted(item) ? " interrupted" : ""}`}
              onClick={() => selectStage(index)}
              aria-current={index === activeStage ? "step" : undefined}
            >
              <span>{isInterrupted(item) ? "⛨ " : ""}{item.number}</span>{item.title}
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
            <span className={`evidence-badge ${stage.evidenceType || "model-assumption"}`}>{readableEvidence(stage.evidenceType)}</span>
          </div>

          <div className="stage-narrative-grid">
            <article>
              <span className="detail-label">Defender signal</span>
              <p>{stage.defenderSignal}</p>
            </article>
            <article>
              <span className="detail-label">Business effect</span>
              <p>{stage.businessEffect || stage.effect}</p>
            </article>
            <article>
              <span className="detail-label">Decision question</span>
              <p>{stage.decisionQuestion}</p>
            </article>
          </div>

          <div className="stage-meta-grid four">
            <div><span className="detail-label">MITRE ATT&CK</span><strong>{stage.technique}</strong></div>
            <div><span className="detail-label">STRIDE</span><strong>{stage.stride}</strong></div>
            <div><span className="detail-label">Asset affected</span><strong>{stage.asset || "—"}</strong></div>
            <div><span className="detail-label">Model factors</span><strong>{(stage.modelFactors || []).map((key) => inputLabels[key] || key).join("; ") || "—"}</strong></div>
          </div>

          <div className="control-interruption">
            <div>
              <span className="detail-label">Control interruption point</span>
              <p>{stage.controlIntervention}</p>
            </div>
            <div className="control-effects">
              {stageControls.length ? stageControls.map((control) => {
                const effects = control.effects?.["launch-ddos"] || {};
                const relevant = Object.entries(effects).filter(([key]) => (stage.modelFactors || []).includes(key));
                const shown = relevant.length ? relevant : Object.entries(effects);
                return (
                  <div className={`control-effect${ddosSelected.includes(control.id) ? " active" : ""}`} key={control.id}>
                    <strong>{control.name}{ddosSelected.includes(control.id) ? " · selected" : ""}</strong>
                    <small>{shown.map(([key, effect]) => `${inputLabels[key] || key} ${effectText(effect)}`).join(" · ")}</small>
                  </div>
                );
              }) : <span className="control-chip">No modeled control at this step</span>}
            </div>
          </div>

          <div className="stage-evidence">
            <span className="detail-label">Evidence and sources</span>
            {stageSources.length ? stageSources.map((source) => (
              <a href={source.url} target="_blank" rel="noreferrer" key={source.id}>
                {source.title}<small>{source.publisher} · accessed {source.accessDate}</small>
              </a>
            )) : <p>Team-developed step; see the evidence register.</p>}
          </div>
        </div>
        <p className="model-note">This chain is a plausible model built from public threat information and team assumptions. It makes no claim about Take-Two's private architecture.</p>
      </section>

      <section className="compact-path-grid">
        {config?.attackPaths?.["source-code-theft"] && (
          <CompactPath
            title="Build and Source Code Theft"
            subtitle="Comparison path (company-specific evidence)"
            steps={config.attackPaths["source-code-theft"]}
            controlsById={controlsById}
            selectedControlIds={selectedScenarioId === "source-code-theft" ? selectedControlIds : []}
          />
        )}
        {config?.attackPaths?.["insider-leak"] && (
          <CompactPath
            title="Insider or Contractor Leak"
            subtitle="Summary path"
            steps={config.attackPaths["insider-leak"]}
            controlsById={controlsById}
            selectedControlIds={selectedScenarioId === "insider-leak" ? selectedControlIds : []}
          />
        )}
        {config?.attackPaths?.["fake-downloads"] && (
          <CompactPath
            title="Fake Downloads and Phishing"
            subtitle="Summary path"
            steps={config.attackPaths["fake-downloads"]}
            controlsById={controlsById}
            selectedControlIds={selectedScenarioId === "fake-downloads" ? selectedControlIds : []}
          />
        )}
      </section>

      {config?.watchlist && (
        <section className="panel watchlist">
          <span className="eyebrow">Additional risks monitored (not modeled)</span>
          <div className="asset-chips">{config.watchlist.map((item) => <span className="chip" key={item}>{item}</span>)}</div>
        </section>
      )}
    </div>
  );
}
