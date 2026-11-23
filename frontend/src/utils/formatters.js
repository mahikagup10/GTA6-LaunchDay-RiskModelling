export function formatCurrency(value) {
  if (value == null || Number.isNaN(value)) return "—";
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    notation: "compact",
    maximumFractionDigits: 1,
  }).format(value);
}

export function formatPercent(value, digits = 0) {
  if (value == null || Number.isNaN(value)) return "—";
  return new Intl.NumberFormat("en-US", {
    style: "percent",
    maximumFractionDigits: digits,
    minimumFractionDigits: 0,
  }).format(value);
}

export function formatProbability(value) {
  if (value == null || Number.isNaN(value)) return "—";
  if (value > 0 && value < 0.001) return "<0.1%";
  return formatPercent(value, value < 0.1 ? 1 : 0);
}

export function formatMultiple(value) {
  if (value == null || Number.isNaN(value)) return "—";
  return `${value.toFixed(1)}×`;
}

export function basisSuffix(timeBasis) {
  return timeBasis === "launch-event" ? "per launch event" : "per year";
}

export function basisTag(timeBasis) {
  return timeBasis === "launch-event" ? "USD · launch event" : "USD · annual";
}

export function formatInputValue(item, value) {
  const unit = item.unit || "";
  if (unit.startsWith("USD")) return formatCurrency(value);
  if (unit.startsWith("probability") || unit.startsWith("fraction")) return formatPercent(value);
  if (unit.startsWith("hours")) return `${value} h`;
  return Number.isInteger(value) ? `${value}` : value.toFixed(1);
}

export function readableEvidence(value = "model-assumption") {
  return {
    "public-fact": "Public fact",
    "derived-value": "Derived value",
    "team-estimate": "Team estimate",
    "model-assumption": "Model assumption",
  }[value] || value.replaceAll("-", " ");
}

export function effectText(effect) {
  const pct = (value) => Math.round(value * 100);
  return `−${pct(effect.likely)}% (${pct(effect.low)}–${pct(effect.high)}%)`;
}
