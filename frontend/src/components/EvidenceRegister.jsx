import { formatCurrency, formatPercent } from "../utils/formatters";

const assumptionLabels = {
  threatEventFrequency: "Threat event frequency",
  vulnerability: "Conditional success probability",
  primaryLoss: "Primary loss",
  secondaryLoss: "Secondary loss",
};

function formatEstimate(key, value) {
  if (key === "vulnerability") return formatPercent(value);
  if (key === "primaryLoss" || key === "secondaryLoss") return formatCurrency(value);
  return value.toFixed(2);
}

function readableType(value = "model-assumption") {
  return value.replaceAll("-", " ");
}

export default function EvidenceRegister({ scenario, methodology, sources = [] }) {
  if (!scenario?.assumptions || !methodology) return null;

  return (
    <details className="panel evidence-register" open>
      <summary>
        <div>
          <span className="eyebrow">Transparency layer</span>
          <h2>Methodology & evidence register</h2>
        </div>
        <span>{Object.keys(scenario.assumptions).length} model inputs</span>
      </summary>

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
          <span className="detail-label">Control treatment</span>
          <strong>Explicit parameter multipliers</strong>
          <p>{methodology.controlRule}</p>
          {methodology.disclaimer && <p className="model-disclaimer">{methodology.disclaimer}</p>}
        </div>
      </div>

      <div className="evidence-legend" aria-label="Evidence type legend">
        <span><i className="legend-dot fact" />Public fact</span>
        <span><i className="legend-dot derived" />Derived value</span>
        <span><i className="legend-dot estimate" />Team estimate</span>
        <span><i className="legend-dot assumption" />Model assumption</span>
      </div>

      <section className="assumption-register">
        <div className="register-heading">
          <div><h3>{scenario.name} inputs</h3><p>Every numeric input exposes its range, rationale, confidence, and provenance.</p></div>
          <span>Low / most likely / high</span>
        </div>
        {Object.entries(scenario.assumptions).map(([key, assumption]) => (
          <article className="assumption-item" key={key}>
            <div>
              <span className={`evidence-badge ${assumption.evidenceType}`}>{readableType(assumption.evidenceType)}</span>
              <h3>{assumptionLabels[key] || key}</h3>
              <p>{assumption.rationale}</p>
            </div>
            <div className="estimate-values">
              <strong>{formatEstimate(key, assumption.low)}</strong>
              <strong>{formatEstimate(key, assumption.mode)}</strong>
              <strong>{formatEstimate(key, assumption.high)}</strong>
            </div>
            <div className="assumption-meta">
              <span>Confidence<strong>{assumption.confidence}</strong></span>
              <span>Unit<strong>{assumption.unit}</strong></span>
            </div>
            <div className="provenance-note">
              <a href={assumption.source.url} target="_blank" rel="noreferrer">{assumption.source.title}</a>
              <small>Accessed {assumption.source.accessDate}{assumption.evidenceRef ? ` · Evidence ${assumption.evidenceRef}` : ""}{assumption.source.anchorIds?.length ? ` · Anchors ${assumption.source.anchorIds.join(", ")}` : ""}</small>
              <p>{assumption.source.scope}</p>
            </div>
          </article>
        ))}
      </section>

      <section className="source-register">
        <div className="register-heading"><div><h3>Source register</h3><p>Public references used for methodology, control framing, and attack-technique mappings.</p></div></div>
        <div className="source-grid">
          {sources.map((source) => (
            <a href={source.url} target="_blank" rel="noreferrer" key={source.id}>
              <span>{readableType(source.type)}</span>
              <strong>{source.title}</strong>
              <small>Accessed {source.accessDate}</small>
            </a>
          ))}
        </div>
      </section>

      <p className="methodology-disclaimer">{methodology.disclaimer}</p>
    </details>
  );
}

