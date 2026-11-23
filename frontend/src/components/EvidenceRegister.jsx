import { formatInputValue, readableEvidence } from "../utils/formatters";

const groupLabels = {
  frequency: "Frequency",
  vulnerability: "Conditional success",
  duration: "Duration",
  "primary-driver": "Primary loss driver",
  primary: "Primary loss",
  "secondary-probability": "Secondary probability",
  secondary: "Secondary loss",
};

export default function EvidenceRegister({ scenario, methodology, sources = [] }) {
  if (!scenario?.inputs || !methodology) return null;
  const sourcesById = Object.fromEntries(sources.map((source) => [source.id, source]));
  const usedSourceIds = new Set(scenario.inputs.flatMap((item) => item.sourceIds));
  const scenarioSources = sources.filter((source) => usedSourceIds.has(source.id));
  const classCounts = scenario.inputs.reduce((counts, item) => {
    counts[item.evidenceType] = (counts[item.evidenceType] || 0) + 1;
    return counts;
  }, {});

  return (
    <details className="panel evidence-register" open>
      <summary>
        <div>
          <span className="eyebrow">Transparency layer</span>
          <h2>Methodology and evidence register</h2>
        </div>
        <span>{scenario.inputs.length} model inputs · {scenarioSources.length} sources</span>
      </summary>

      <div className="loss-event-statement">
        <span className="detail-label">Loss event statement · {scenario.timeBasisLabel}</span>
        <p>{scenario.lossEventStatement}</p>
      </div>

      <div className="methodology-overview">
        <div>
          <span className="detail-label">Model</span>
          <strong>{methodology.name}</strong>
          <p>{methodology.description}</p>
        </div>
        <div>
          <span className="detail-label">Loss calculation</span>
          <strong>{methodology.formula}</strong>
          <p>{methodology.sampling}</p>
        </div>
        <div>
          <span className="detail-label">Control and cost treatment</span>
          <strong>Targeted multipliers, reconciled cost basis</strong>
          <p>{methodology.controlRule} {methodology.costRule}</p>
        </div>
      </div>

      <div className="evidence-legend" aria-label="Evidence type legend">
        <span><i className="legend-dot fact" />Public fact {classCounts["public-fact"] ? `(${classCounts["public-fact"]})` : ""}</span>
        <span><i className="legend-dot derived" />Derived value {classCounts["derived-value"] ? `(${classCounts["derived-value"]})` : ""}</span>
        <span><i className="legend-dot estimate" />Team estimate {classCounts["team-estimate"] ? `(${classCounts["team-estimate"]})` : ""}</span>
        <span><i className="legend-dot assumption" />Model assumption {classCounts["model-assumption"] ? `(${classCounts["model-assumption"]})` : ""}</span>
      </div>

      <section className="assumption-register">
        <div className="register-heading">
          <div><h3>{scenario.name} inputs</h3><p>Every input shows its range, distribution, evidence class, sources, rationale, confidence, and control relationship.</p></div>
          <span>Low / most likely / high</span>
        </div>
        {scenario.inputs.map((item) => (
          <article className="assumption-item" key={item.key}>
            <div>
              <span className={`evidence-badge ${item.evidenceType}`}>{readableEvidence(item.evidenceType)}</span>
              <h3>{item.label}</h3>
              <p>{item.rationale}</p>
            </div>
            <div className="estimate-values">
              <strong>{formatInputValue(item, item.low)}</strong>
              <strong>{formatInputValue(item, item.mode)}</strong>
              <strong>{formatInputValue(item, item.high)}</strong>
            </div>
            <div className="assumption-meta">
              <span>Group<strong>{groupLabels[item.group] || item.group}</strong></span>
              <span>Confidence<strong>{item.confidence}</strong></span>
              <span>Unit<strong>{item.unit}</strong></span>
            </div>
            <div className="provenance-note">
              {item.sourceIds.map((sourceId) => sourcesById[sourceId] && (
                <a key={sourceId} href={sourcesById[sourceId].url} target="_blank" rel="noreferrer">{sourcesById[sourceId].title}</a>
              ))}
              <small>Triangular · Owner {item.owner} · Reviewer {item.reviewer}</small>
              <p>{item.controlRelationship}</p>
            </div>
          </article>
        ))}
      </section>

      <section className="source-register">
        <div className="register-heading"><div><h3>Source register</h3><p>Sources behind this scenario's inputs. Every source shows publisher, date, reliability, and the claim used.</p></div></div>
        <div className="source-grid">
          {scenarioSources.map((source) => (
            <a href={source.url} target="_blank" rel="noreferrer" key={source.id} title={source.claim}>
              <span>{readableEvidence(source.evidenceClass)} · {source.reliability} reliability</span>
              <strong>{source.title}</strong>
              <small>{source.publisher} · {source.published} · accessed {source.accessDate}</small>
            </a>
          ))}
        </div>
      </section>

      {methodology.timing && <p className="methodology-disclaimer timing">{methodology.timing}</p>}
      <p className="methodology-disclaimer">{methodology.disclaimer}</p>
    </details>
  );
}
