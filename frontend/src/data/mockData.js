export const scenarios = [
  {
    id: "launch-ddos",
    name: "Launch-Day DDoS",
    summary: "A coordinated traffic flood disrupts the public launch and revenue-critical services.",
    severity: "Critical",
  },
  {
    id: "source-code-theft",
    name: "Build & Source Code Theft",
    summary: "Compromised development access exposes proprietary code and build assets.",
    severity: "High",
  },
  {
    id: "insider-leak",
    name: "Insider or Contractor Leak",
    summary: "A trusted person releases confidential product or customer information.",
    severity: "High",
  },
  {
    id: "fake-downloads",
    name: "Fake Downloads & Phishing",
    summary: "Impersonation campaigns distribute malicious downloads and steal credentials.",
    severity: "Medium",
  },
];

export const controls = [
  {
    id: "cdn-scrubbing",
    name: "CDN and DDoS scrubbing",
    target: "Frequency and vulnerability",
    cost: 850000,
    confidence: "High",
  },
  {
    id: "rate-limiting",
    name: "Adaptive rate limiting",
    target: "Vulnerability",
    cost: 260000,
    confidence: "Medium",
  },
  {
    id: "incident-drills",
    name: "Launch incident drills",
    target: "Loss magnitude",
    cost: 120000,
    confidence: "Medium",
  },
];

export const attackStages = [
  {
    number: "01",
    title: "Reconnaissance",
    technique: "T1595 — Active Scanning",
    stride: "Information Disclosure",
    effect: "Attackers identify public endpoints and capacity limits.",
  },
  {
    number: "02",
    title: "Botnet preparation",
    technique: "T1584 — Compromise Infrastructure",
    stride: "Spoofing",
    effect: "Distributed infrastructure is prepared before launch day.",
  },
  {
    number: "03",
    title: "Traffic flood",
    technique: "T1498 — Network Denial of Service",
    stride: "Denial of Service",
    effect: "Traffic overwhelms edge and origin capacity.",
  },
  {
    number: "04",
    title: "Business disruption",
    technique: "T1499 — Endpoint Denial of Service",
    stride: "Denial of Service",
    effect: "Customers cannot access launch services, support, or purchases.",
  },
];

