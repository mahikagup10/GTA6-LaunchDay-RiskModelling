const CACHE_VERSION = 2;
const CONFIG_KEY = "cyber-workbench:config";
const SIMULATION_PREFIX = "cyber-workbench:simulation:";
const PORTFOLIO_PREFIX = "cyber-workbench:portfolio:";

function readEnvelope(key) {
  try {
    const raw = window.localStorage.getItem(key);
    if (!raw) return null;
    const envelope = JSON.parse(raw);
    return envelope.version === CACHE_VERSION ? envelope : null;
  } catch {
    return null;
  }
}

function writeEnvelope(key, data) {
  try {
    window.localStorage.setItem(key, JSON.stringify({
      version: CACHE_VERSION,
      savedAt: new Date().toISOString(),
      data,
    }));
  } catch {
    // Storage can be blocked in private browsing. Live API use still works.
  }
}

export function simulationRequestKey(payload) {
  const controls = [...payload.controlIds].sort().join(",") || "none";
  return `${payload.scenarioId}:${payload.trials}:${payload.seed}:${controls}`;
}

export function readCachedConfig() {
  return readEnvelope(CONFIG_KEY);
}

export function cacheConfig(config) {
  writeEnvelope(CONFIG_KEY, config);
}

export function readCachedSimulation(payload) {
  return readEnvelope(`${SIMULATION_PREFIX}${simulationRequestKey(payload)}`);
}

export function cacheSimulation(payload, results) {
  writeEnvelope(`${SIMULATION_PREFIX}${simulationRequestKey(payload)}`, results);
}

function portfolioRequestKey(payload) {
  const controls = [...payload.controlIds].sort().join(",") || "none";
  return `${payload.trials}:${payload.seed}:${controls}`;
}

export function readCachedPortfolio(payload) {
  return readEnvelope(`${PORTFOLIO_PREFIX}${portfolioRequestKey(payload)}`);
}

export function cachePortfolio(payload, results) {
  writeEnvelope(`${PORTFOLIO_PREFIX}${portfolioRequestKey(payload)}`, results);
}

const OVERVIEW_KEY = "cyber-workbench:overview";
const PRIORITY_KEY = "cyber-workbench:priorities";

export function readCachedOverview() {
  return readEnvelope(OVERVIEW_KEY);
}

export function cacheOverview(data) {
  writeEnvelope(OVERVIEW_KEY, data);
}

export function readCachedPriorities() {
  return readEnvelope(PRIORITY_KEY);
}

export function cachePriorities(data) {
  writeEnvelope(PRIORITY_KEY, data);
}
