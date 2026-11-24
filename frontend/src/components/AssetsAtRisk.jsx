import { useEffect, useMemo, useState } from "react";

function AssetIcon({ name }) {
  const paths = {
    network: <><rect x="4" y="5" width="16" height="5" rx="2" /><path d="M8 10v4m8-4v4M5 19h6v-5H5v5Zm8 0h6v-5h-6v5Z" /></>,
    code: <><path d="m9 7-5 5 5 5m6-10 5 5-5 5M13 5l-2 14" /></>,
    key: <><circle cx="8" cy="12" r="4" /><path d="M12 12h8m-3 0v3m-3-3v2" /></>,
    file: <><path d="M6 3h8l4 4v14H6V3Z" /><path d="M14 3v5h5M9 13h6m-6 4h6" /></>,
    shield: <><path d="M12 3 5 6v5c0 4.8 2.8 8 7 10 4.2-2 7-5.2 7-10V6l-7-3Z" /><path d="m9 12 2 2 4-5" /></>,
    users: <><circle cx="9" cy="9" r="3" /><path d="M3.5 19c.6-3.1 2.4-5 5.5-5s4.9 1.9 5.5 5M16 7.5a2.5 2.5 0 0 1 0 5m.5 2c2.2.5 3.5 2 4 4.5" /></>,
  };

  return (
    <span className="asset-icon" aria-hidden="true">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">
        {paths[name] || paths.shield}
      </svg>
    </span>
  );
}

function titleCase(value = "") {
  return value.charAt(0).toUpperCase() + value.slice(1);
}

export default function AssetsAtRisk({ assets = [], scenarios = [], controls = [], sources = [], selectedScenarioId }) {
  const [view, setView] = useState("scenario");
  const visibleAssets = useMemo(
    () => view === "all" ? assets : assets.filter((asset) => asset.scenarioIds.includes(selectedScenarioId)),
    [assets, selectedScenarioId, view],
  );
  const [selectedAssetId, setSelectedAssetId] = useState(visibleAssets[0]?.id || "");

  useEffect(() => {
    if (!visibleAssets.some((asset) => asset.id === selectedAssetId)) {
      setSelectedAssetId(visibleAssets[0]?.id || "");
    }
  }, [selectedAssetId, visibleAssets]);

  const selectedAsset = visibleAssets.find((asset) => asset.id === selectedAssetId) || visibleAssets[0];
  const scenarioLookup = useMemo(() => Object.fromEntries(scenarios.map((item) => [item.id, item])), [scenarios]);
  const controlLookup = useMemo(() => Object.fromEntries(controls.map((item) => [item.id, item])), [controls]);
  const sourceLookup = useMemo(() => Object.fromEntries(sources.map((item) => [item.id, item])), [sources]);
  const selectedScenario = scenarioLookup[selectedScenarioId];

  if (!assets.length) return null;

  return (
    <section className="assets-section panel" aria-labelledby="assets-at-risk-heading">
      <div className="assets-heading">
        <div>
          <span className="eyebrow">Business assets</span>
          <h2 id="assets-at-risk-heading">Assets at risk</h2>
          <p>Connect what the organization depends on to the threats, financial exposure, and controls intended to protect it.</p>
        </div>
        <div className="asset-view-toggle" aria-label="Asset view">
          <button type="button" className={view === "scenario" ? "active" : ""} onClick={() => setView("scenario")}>Selected scenario</button>
          <button type="button" className={view === "all" ? "active" : ""} onClick={() => setView("all")}>All assets</button>
        </div>
      </div>

      <div className="asset-context-line">
        <strong>{view === "all" ? "Organization-wide portfolio" : selectedScenario?.name}</strong>
        <span>{visibleAssets.length} {visibleAssets.length === 1 ? "asset" : "assets"} shown</span>
      </div>

      <div className="asset-workspace">
        <div className="asset-card-grid" role="list" aria-label="Assets at risk">
          {visibleAssets.map((asset) => (
            <button
              type="button"
              role="listitem"
              key={asset.id}
              className={`asset-card ${selectedAsset?.id === asset.id ? "selected" : ""}`}
              onClick={() => setSelectedAssetId(asset.id)}
              aria-pressed={selectedAsset?.id === asset.id}
            >
              <AssetIcon name={asset.icon} />
              <span className="asset-card-copy">
                <small>{asset.category}</small>
                <strong>{asset.name}</strong>
                <span>{asset.financialBasis.displayValue}</span>
              </span>
              <span className={`asset-criticality ${asset.criticality.toLowerCase()}`}>{asset.criticality}</span>
            </button>
          ))}
        </div>

        {selectedAsset && (
          <article className="asset-detail" aria-live="polite">
            <div className="asset-detail-title">
              <AssetIcon name={selectedAsset.icon} />
              <div>
                <span className="eyebrow">Selected asset</span>
                <h3>{selectedAsset.name}</h3>
              </div>
            </div>
            <p>{selectedAsset.description}</p>

            <div className="asset-value-basis">
              <span>{selectedAsset.financialBasis.label}</span>
              <strong>{selectedAsset.financialBasis.displayValue}</strong>
              <small>{selectedAsset.financialBasis.explanation}</small>
              <div>
                <span>{selectedAsset.financialBasis.classification}</span>
                <span>{selectedAsset.financialBasis.confidence} confidence</span>
              </div>
            </div>

            <div className="asset-detail-grid">
              <div>
                <span className="detail-label">Threat scenarios</span>
                <div className="asset-chips">
                  {selectedAsset.scenarioIds.map((id) => <span key={id}>{scenarioLookup[id]?.name || id}</span>)}
                </div>
              </div>
              <div>
                <span className="detail-label">STRIDE exposure</span>
                <div className="asset-chips muted">
                  {selectedAsset.stride.map((item) => <span key={item}>{item}</span>)}
                </div>
              </div>
              <div className="asset-controls">
                <span className="detail-label">Related controls</span>
                <div className="asset-chips controls">
                  {selectedAsset.controlIds.map((id) => <span key={id}>{controlLookup[id]?.name || id}</span>)}
                </div>
              </div>
            </div>

            <div className="asset-sources">
              <span className="detail-label">Evidence basis</span>
              {selectedAsset.sourceIds.map((id) => {
                const source = sourceLookup[id];
                return source ? <a key={id} href={source.url} target="_blank" rel="noreferrer">{source.title}<small>{titleCase(source.type.replaceAll("-", " "))} · accessed {source.accessDate}</small></a> : null;
              })}
            </div>
          </article>
        )}
      </div>

      <p className="asset-disclaimer"><strong>Interpretation:</strong> these figures are exposure proxies or scenario-loss ranges. They are not audited asset valuations, replacement costs, or market values.</p>
    </section>
  );
}
