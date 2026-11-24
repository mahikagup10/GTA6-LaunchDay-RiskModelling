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

function formatDerivationValue(input, value) {
  if (input.unit === "USD" || input.unit === "USD/day") return formatCurrency(value);
  if (input.unit === "share") return formatPercent(value);
  return `${Number(value).toLocaleString()} ${input.unit}`;
}

export default function EvidenceRegister({ scenario, profileId, methodology, sources = [] }) {
  const profile = scenario?.assumptionProfiles?.[profileId];
  const assumptions = profile?.assumptions || scenario?.assumptions;
  const secondaryProbability = profile?.secondaryLossProbability || scenario?.secondaryLossProbability;
  if (!assumptions || !methodology) return null;

  return (
    <details className="panel evidence-register" open>
      <summary>
        <div>
          <span className="eyebrow">Transparency layer</span>
          <h2>Methodology & evidence register</h2>
        </div>
        <span>{Object.keys(assumptions).length + 1} model inputs</span>
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
        </div>
      </div>

      <div className="evidence-legend" aria-label="Evidence type legend">
        <span><i className="legend-dot fact" />Public fact</span>
        <span><i className="legend-dot estimate" />Team estimate</span>
        <span><i className="legend-dot assumption" />Model assumption</span>
        <span><i className="legend-dot derived-value" />Derived value</span>
      </div>

      <section className="assumption-register">
        <div className="register-heading">
          <div><h3>{scenario.name} inputs</h3><p>Every numeric input exposes its range, rationale, confidence, and provenance.</p></div>
          <span>Low / most likely / high</span>
        </div>
        {Object.entries(assumptions).map(([key, assumption]) => (
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
            <div className="provenance-note">{(assumption.sources || []).map((source) => <div key={source.id}><a href={source.url} target="_blank" rel="noreferrer">{source.title}</a><small>Accessed {source.accessDate}</small><p>{source.reviewNote || "Reference used to support or frame this estimate."}</p></div>)}</div>
          </article>
        ))}
        {secondaryProbability && <article className="assumption-item">
          <div><span className={`evidence-badge ${secondaryProbability.evidenceType}`}>{readableType(secondaryProbability.evidenceType)}</span><h3>Secondary-loss occurrence probability</h3><p>{secondaryProbability.rationale}</p></div>
          <div className="estimate-values single"><strong>{formatPercent(secondaryProbability.value)}</strong></div>
          <div className="assumption-meta"><span>Confidence<strong>{secondaryProbability.confidence}</strong></span><span>Unit<strong>{secondaryProbability.unit}</strong></span></div>
          <div className="provenance-note">{(secondaryProbability.sources || []).map((source) => <div key={source.id}><a href={source.url} target="_blank" rel="noreferrer">{source.title}</a><small>Accessed {source.accessDate}</small></div>)}</div>
        </article>}
      </section>

      {scenario.lossDerivation && profileId === "evidence-anchored" && <section className="derivation-register">
        <div className="register-heading"><div><h3>DDoS primary-loss derivation</h3><p>The dollar range is calculated from visible components rather than entered as one unexplained figure.</p></div></div>
        <div className="derivation-formula">{scenario.lossDerivation.formula}</div>
        <div className="derivation-grid">{scenario.lossDerivation.inputs.map((input) => <div key={input.name}><strong>{input.name}</strong><span>{formatDerivationValue(input, input.low)}</span><span>{formatDerivationValue(input, input.mode)}</span><span>{formatDerivationValue(input, input.high)}</span></div>)}</div>
        <p className="methodology-disclaimer">The revenue guidance is a public fact. Launch multipliers, dependency shares, unrecovered shares, and response costs remain explicit team assumptions that should be validated.</p>
      </section>}

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

