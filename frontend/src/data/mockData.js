// Offline fallback content shown only before the Flask config loads.
// The source of truth is backend/data/config.py.
export const scenarios = [
  {
    id: "launch-ddos",
    name: "Launch-Day DDoS",
    summary: "A coordinated traffic flood degrades sign-in, downloads, and purchases during the GTA VI launch window.",
    severity: "Critical",
    timeBasis: "launch-event",
    depth: "detailed",
  },
  {
    id: "source-code-theft",
    name: "Build & Source Code Theft",
    summary: "Social engineering or stolen credentials expose unreleased builds, footage, and source code.",
    severity: "High",
    timeBasis: "annual",
    depth: "comparison",
  },
  {
    id: "insider-leak",
    name: "Insider or Contractor Leak",
    summary: "A trusted employee, contractor, or vendor discloses unreleased content or player data.",
    severity: "High",
    timeBasis: "annual",
    depth: "summary",
  },
  {
    id: "fake-downloads",
    name: "Fake Downloads & Phishing",
    summary: "Fake GTA VI downloads, demos, and phishing sites steal player and workforce credentials.",
    severity: "Medium",
    timeBasis: "annual",
    depth: "summary",
  },
];

export const attackStages = [
  "Target and dependency reconnaissance",
  "Attack infrastructure prepared",
  "Network-layer flood begins",
  "Application or service exhaustion",
  "Service degradation and cascading failure",
  "Detection, response, and recovery",
  "Business loss event",
].map((title, index) => ({
  id: `stage-${index + 1}`,
  number: String(index + 1).padStart(2, "0"),
  title,
  technique: "Loading…",
  stride: "Loading…",
  effect: "Start the Flask backend to load the full attack chain.",
  controlIds: [],
}));
