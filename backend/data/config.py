ACCESS_DATE = "2026-11-22"


ASSUMPTION_METHOD_SOURCE = {
    "id": "open-fair-methodology",
    "title": "The Open Group: Open FAIR 2 Foundation risk-analysis concepts",
    "url": "https://help.opengroup.org/hc/en-us/articles/32130434422290-Competency-to-Role-Mapping-Open-FAIR-2-Foundation",
    "accessDate": ACCESS_DATE,
    "type": "methodology-reference",
}


SOURCES = [
    ASSUMPTION_METHOD_SOURCE,
    {
        "id": "mitre-t1595",
        "title": "MITRE ATT&CK: Active Scanning (T1595)",
        "url": "https://attack.mitre.org/techniques/T1595/",
        "accessDate": ACCESS_DATE,
        "type": "public-fact",
    },
    {
        "id": "mitre-t1584",
        "title": "MITRE ATT&CK: Compromise Infrastructure (T1584)",
        "url": "https://attack.mitre.org/techniques/T1584/",
        "accessDate": ACCESS_DATE,
        "type": "public-fact",
    },
    {
        "id": "mitre-t1498",
        "title": "MITRE ATT&CK: Network Denial of Service (T1498)",
        "url": "https://attack.mitre.org/techniques/T1498/",
        "accessDate": ACCESS_DATE,
        "type": "public-fact",
    },
    {
        "id": "mitre-t1499",
        "title": "MITRE ATT&CK: Endpoint Denial of Service (T1499)",
        "url": "https://attack.mitre.org/techniques/T1499/",
        "accessDate": ACCESS_DATE,
        "type": "public-fact",
    },
    {
        "id": "nist-csf-2",
        "title": "NIST Cybersecurity Framework 2.0",
        "url": "https://www.nist.gov/cyberframework",
        "accessDate": ACCESS_DATE,
        "type": "public-fact",
    },
]


METHODOLOGY = {
    "name": "Team FAIR-style Monte Carlo model",
    "description": "A decision-support model structured around event frequency, conditional success, and loss magnitude.",
    "formula": "Successful loss events × (primary loss + secondary loss)",
    "sampling": "Triangular low, most-likely, and high estimates; 10,000 trials with fixed seed 20261124 (class project plan). Baseline and residual share the same random draws (paired comparison).",
    "controlRule": "Controls multiply frequency, vulnerability, primary loss, or secondary loss; shared controls are costed once in portfolio mode.",
    "disclaimer": "This is a team-designed FAIR-style model, not an official Open FAIR, NIST, or MITRE assessment.",
    "sourceIds": ["open-fair-methodology", "nist-csf-2"],
}


SCENARIOS = [
    {
        "id": "launch-ddos",
        "name": "Launch-Day DDoS",
        "severity": "Critical",
        "summary": "A coordinated traffic flood disrupts the public launch and revenue-critical services.",
        "modelStatus": "implemented",
        "readinessBase": 44,
        "readinessProfile": {"prevent": 42, "detect": 55, "respond": 43, "recover": 36},
        "recommendedControlIds": ["cdn-scrubbing", "rate-limiting"],
        "assumptions": {
            "threatEventFrequency": {
                "low": 0.45,
                "mode": 0.80,
                "high": 1.30,
                "unit": "events per analysis period",
                "rationale": "Team estimate for a high-visibility launch window.",
                "confidence": "medium",
                "evidenceType": "model-assumption",
            },
            "vulnerability": {
                "low": 0.20,
                "mode": 0.42,
                "high": 0.68,
                "unit": "conditional success probability",
                "rationale": "Team estimate before launch-specific resilience controls.",
                "confidence": "medium",
                "evidenceType": "model-assumption",
            },
            "primaryLoss": {
                "low": 18_000_000,
                "mode": 46_000_000,
                "high": 72_000_000,
                "unit": "USD",
                "rationale": "Estimated outage response, restoration, and direct launch disruption.",
                "confidence": "low",
                "evidenceType": "team-estimate",
            },
            "secondaryLoss": {
                "low": 8_000_000,
                "mode": 28_000_000,
                "high": 65_000_000,
                "unit": "USD",
                "rationale": "Estimated customer, reputation, contractual, and downstream effects.",
                "confidence": "low",
                "evidenceType": "team-estimate",
            },
        },
    },
    {
        "id": "source-code-theft",
        "name": "Build & Source Code Theft",
        "severity": "High",
        "summary": "Compromised development access exposes proprietary code and build assets.",
        "modelStatus": "implemented",
        "readinessBase": 46,
        "readinessProfile": {"prevent": 48, "detect": 45, "respond": 46, "recover": 45},
        "recommendedControlIds": ["repository-hardening", "least-privilege"],
        "assumptions": {
            "threatEventFrequency": {
                "low": 0.15,
                "mode": 0.40,
                "high": 0.85,
                "unit": "events per analysis period",
                "rationale": "Team estimate for targeted repository or build-system access attempts.",
                "confidence": "low",
                "evidenceType": "model-assumption",
            },
            "vulnerability": {
                "low": 0.14,
                "mode": 0.32,
                "high": 0.58,
                "unit": "conditional success probability",
                "rationale": "Team estimate before repository hardening and least-privilege controls.",
                "confidence": "low",
                "evidenceType": "model-assumption",
            },
            "primaryLoss": {
                "low": 12_000_000,
                "mode": 35_000_000,
                "high": 85_000_000,
                "unit": "USD",
                "rationale": "Estimated investigation, rebuild, legal, and intellectual-property response costs.",
                "confidence": "low",
                "evidenceType": "team-estimate",
            },
            "secondaryLoss": {
                "low": 8_000_000,
                "mode": 28_000_000,
                "high": 75_000_000,
                "unit": "USD",
                "rationale": "Estimated competitive, partner, customer, and launch-delay consequences.",
                "confidence": "low",
                "evidenceType": "team-estimate",
            },
        },
    },
    {
        "id": "insider-leak",
        "name": "Insider or Contractor Leak",
        "severity": "High",
        "summary": "A trusted person releases confidential product or customer information.",
        "modelStatus": "implemented",
        "readinessBase": 42,
        "readinessProfile": {"prevent": 40, "detect": 44, "respond": 43, "recover": 41},
        "recommendedControlIds": ["least-privilege", "dlp-monitoring"],
        "assumptions": {
            "threatEventFrequency": {
                "low": 0.20,
                "mode": 0.55,
                "high": 0.95,
                "unit": "events per analysis period",
                "rationale": "Team estimate for material insider or contractor misuse events.",
                "confidence": "low",
                "evidenceType": "model-assumption",
            },
            "vulnerability": {
                "low": 0.12,
                "mode": 0.28,
                "high": 0.50,
                "unit": "conditional success probability",
                "rationale": "Team estimate based on access concentration and monitoring gaps.",
                "confidence": "low",
                "evidenceType": "model-assumption",
            },
            "primaryLoss": {
                "low": 6_000_000,
                "mode": 22_000_000,
                "high": 60_000_000,
                "unit": "USD",
                "rationale": "Estimated investigation, notification, legal, and containment costs.",
                "confidence": "low",
                "evidenceType": "team-estimate",
            },
            "secondaryLoss": {
                "low": 5_000_000,
                "mode": 18_000_000,
                "high": 55_000_000,
                "unit": "USD",
                "rationale": "Estimated partner, customer, reputation, and competitive consequences.",
                "confidence": "low",
                "evidenceType": "team-estimate",
            },
        },
    },
    {
        "id": "fake-downloads",
        "name": "Fake Downloads & Phishing",
        "severity": "Medium",
        "summary": "Impersonation campaigns distribute malicious downloads and steal credentials.",
        "modelStatus": "implemented",
        "readinessBase": 40,
        "readinessProfile": {"prevent": 38, "detect": 42, "respond": 41, "recover": 39},
        "recommendedControlIds": ["brand-monitoring", "phishing-resistant-mfa"],
        "assumptions": {
            "threatEventFrequency": {
                "low": 0.35,
                "mode": 0.70,
                "high": 1.00,
                "unit": "events per analysis period",
                "rationale": "Team estimate for material impersonation campaigns during a launch period.",
                "confidence": "low",
                "evidenceType": "model-assumption",
            },
            "vulnerability": {
                "low": 0.12,
                "mode": 0.30,
                "high": 0.55,
                "unit": "conditional success probability",
                "rationale": "Team estimate for a campaign causing material customer or workforce harm.",
                "confidence": "low",
                "evidenceType": "model-assumption",
            },
            "primaryLoss": {
                "low": 3_000_000,
                "mode": 12_000_000,
                "high": 35_000_000,
                "unit": "USD",
                "rationale": "Estimated response, takedown, customer support, and credential-reset costs.",
                "confidence": "low",
                "evidenceType": "team-estimate",
            },
            "secondaryLoss": {
                "low": 4_000_000,
                "mode": 20_000_000,
                "high": 65_000_000,
                "unit": "USD",
                "rationale": "Estimated fraud, brand, customer trust, and downstream compromise consequences.",
                "confidence": "low",
                "evidenceType": "team-estimate",
            },
        },
    },
]


for _scenario in SCENARIOS:
    for _assumption in _scenario.get("assumptions", {}).values():
        _assumption["source"] = {
            **ASSUMPTION_METHOD_SOURCE,
            "scope": "Methodology reference only; the numeric range is a team-developed estimate requiring validation.",
        }


CONTROLS = [
    {
        "id": "cdn-scrubbing",
        "name": "CDN and DDoS scrubbing",
        "category": "Protect",
        "readinessImpact": {"prevent": 22, "detect": 8, "respond": 18, "recover": 8},
        "cost": {"low": 650_000, "mode": 850_000, "high": 1_100_000},
        "implementationWeeks": {"low": 2, "mode": 4, "high": 7},
        "confidence": "high",
        "effects": {
            "frequencyMultiplier": 0.75,
            "vulnerabilityMultiplier": 0.55,
            "primaryLossMultiplier": 0.92,
            "secondaryLossMultiplier": 0.95,
        },
        "coverage": ["launch-ddos"],
    },
    {
        "id": "rate-limiting",
        "name": "Adaptive rate limiting",
        "category": "Protect",
        "readinessImpact": {"prevent": 18, "detect": 12, "respond": 8, "recover": 4},
        "cost": {"low": 180_000, "mode": 260_000, "high": 390_000},
        "implementationWeeks": {"low": 2, "mode": 3, "high": 5},
        "confidence": "medium",
        "effects": {
            "frequencyMultiplier": 1.0,
            "vulnerabilityMultiplier": 0.70,
            "primaryLossMultiplier": 0.94,
            "secondaryLossMultiplier": 1.0,
        },
        "coverage": ["launch-ddos"],
    },
    {
        "id": "incident-drills",
        "name": "Launch incident drills",
        "category": "Respond & recover",
        "readinessImpact": {"prevent": 0, "detect": 10, "respond": 22, "recover": 22},
        "cost": {"low": 80_000, "mode": 120_000, "high": 190_000},
        "implementationWeeks": {"low": 1, "mode": 2, "high": 4},
        "confidence": "medium",
        "effects": {
            "frequencyMultiplier": 1.0,
            "vulnerabilityMultiplier": 0.92,
            "primaryLossMultiplier": 0.78,
            "secondaryLossMultiplier": 0.70,
        },
        "coverage": ["launch-ddos", "source-code-theft", "insider-leak", "fake-downloads"],
    },
    {
        "id": "repository-hardening",
        "name": "Repository and CI/CD hardening",
        "category": "Protect",
        "readinessImpact": {"prevent": 24, "detect": 14, "respond": 10, "recover": 6},
        "cost": {"low": 380_000, "mode": 550_000, "high": 780_000},
        "implementationWeeks": {"low": 4, "mode": 7, "high": 12},
        "confidence": "medium",
        "effects": {
            "frequencyMultiplier": 0.92,
            "vulnerabilityMultiplier": 0.52,
            "primaryLossMultiplier": 0.82,
            "secondaryLossMultiplier": 0.88,
        },
        "coverage": ["source-code-theft"],
    },
    {
        "id": "least-privilege",
        "name": "Least-privilege access reviews",
        "category": "Prevent",
        "readinessImpact": {"prevent": 24, "detect": 8, "respond": 6, "recover": 4},
        "cost": {"low": 210_000, "mode": 320_000, "high": 470_000},
        "implementationWeeks": {"low": 3, "mode": 6, "high": 10},
        "confidence": "medium",
        "effects": {
            "frequencyMultiplier": 0.85,
            "vulnerabilityMultiplier": 0.65,
            "primaryLossMultiplier": 0.90,
            "secondaryLossMultiplier": 0.90,
        },
        "coverage": ["source-code-theft", "insider-leak"],
    },
    {
        "id": "dlp-monitoring",
        "name": "DLP and behavior monitoring",
        "category": "Detect & respond",
        "readinessImpact": {"prevent": 8, "detect": 24, "respond": 18, "recover": 4},
        "cost": {"low": 290_000, "mode": 410_000, "high": 620_000},
        "implementationWeeks": {"low": 5, "mode": 8, "high": 14},
        "confidence": "medium",
        "effects": {
            "frequencyMultiplier": 0.90,
            "vulnerabilityMultiplier": 0.68,
            "primaryLossMultiplier": 0.82,
            "secondaryLossMultiplier": 0.70,
        },
        "coverage": ["source-code-theft", "insider-leak"],
    },
    {
        "id": "contractor-offboarding",
        "name": "Contractor offboarding automation",
        "category": "Prevent",
        "readinessImpact": {"prevent": 20, "detect": 10, "respond": 8, "recover": 4},
        "cost": {"low": 85_000, "mode": 140_000, "high": 230_000},
        "implementationWeeks": {"low": 2, "mode": 4, "high": 7},
        "confidence": "medium",
        "effects": {
            "frequencyMultiplier": 0.70,
            "vulnerabilityMultiplier": 0.72,
            "primaryLossMultiplier": 0.90,
            "secondaryLossMultiplier": 0.85,
        },
        "coverage": ["insider-leak"],
    },
    {
        "id": "brand-monitoring",
        "name": "Brand monitoring and takedown",
        "category": "Detect & respond",
        "readinessImpact": {"prevent": 8, "detect": 24, "respond": 18, "recover": 6},
        "cost": {"low": 190_000, "mode": 280_000, "high": 420_000},
        "implementationWeeks": {"low": 2, "mode": 4, "high": 6},
        "confidence": "medium",
        "effects": {
            "frequencyMultiplier": 0.72,
            "vulnerabilityMultiplier": 0.88,
            "primaryLossMultiplier": 0.70,
            "secondaryLossMultiplier": 0.60,
        },
        "coverage": ["fake-downloads"],
    },
    {
        "id": "phishing-resistant-mfa",
        "name": "Phishing-resistant MFA",
        "category": "Prevent",
        "readinessImpact": {"prevent": 26, "detect": 8, "respond": 6, "recover": 4},
        "cost": {"low": 320_000, "mode": 480_000, "high": 720_000},
        "implementationWeeks": {"low": 4, "mode": 8, "high": 14},
        "confidence": "high",
        "effects": {
            "frequencyMultiplier": 1.0,
            "vulnerabilityMultiplier": 0.48,
            "primaryLossMultiplier": 0.80,
            "secondaryLossMultiplier": 0.75,
        },
        "coverage": ["fake-downloads", "source-code-theft"],
    },
]


ATTACK_CHAIN = [
    {
        "id": "reconnaissance",
        "number": "01",
        "title": "Reconnaissance",
        "technique": "T1595 — Active Scanning",
        "stride": "Information Disclosure",
        "attackerAction": "Probe public IP ranges, services, APIs, DNS records, and launch infrastructure to identify exposed endpoints and likely capacity limits.",
        "defenderSignal": "Unusual scanning patterns, repeated requests across endpoints, and traffic from unfamiliar networks before the launch window.",
        "businessEffect": "Attackers gain the targeting information needed to focus later traffic on the services with the greatest launch-day business value.",
        "decisionQuestion": "Can the team detect and triage reconnaissance before launch-day traffic peaks?",
        "effect": "Attackers identify public endpoints and capacity limits.",
        "evidenceType": "public-fact",
        "confidence": "high",
        "controlIds": ["rate-limiting", "incident-drills"],
        "controlIntervention": "Rate-limit abnormal probing and use launch drills to rehearse escalation when pre-launch scanning exceeds normal patterns.",
        "sourceIds": ["mitre-t1595"],
    },
    {
        "id": "botnet-preparation",
        "number": "02",
        "title": "Botnet preparation",
        "technique": "T1584 — Compromise Infrastructure",
        "stride": "Spoofing",
        "attackerAction": "Compromise or rent distributed infrastructure, including botnet capacity, that can generate traffic from many locations and sources.",
        "defenderSignal": "Threat-intelligence indicators, reputation changes, and small test floods that resemble later attack infrastructure.",
        "businessEffect": "The attacker obtains enough distributed capacity to make simple source blocking ineffective and to blend malicious requests with legitimate launch traffic.",
        "decisionQuestion": "Is upstream scrubbing capacity provisioned and tested before the public launch?",
        "effect": "Distributed infrastructure is prepared before launch day.",
        "evidenceType": "public-fact",
        "confidence": "medium",
        "controlIds": ["cdn-scrubbing", "incident-drills"],
        "controlIntervention": "Pre-provision CDN and scrubbing capacity, validate routing changes, and rehearse activation before malicious volume arrives.",
        "sourceIds": ["mitre-t1584"],
    },
    {
        "id": "traffic-flood",
        "number": "03",
        "title": "Traffic flood",
        "technique": "T1498 — Network Denial of Service",
        "stride": "Denial of Service",
        "attackerAction": "Direct a high-volume or reflected traffic flood at public launch endpoints, network links, DNS, and origin services.",
        "defenderSignal": "Rapid bandwidth growth, connection spikes, geographic anomalies, elevated error rates, and origin saturation.",
        "businessEffect": "Legitimate customers experience timeouts and failed transactions as edge, network, or origin capacity is exhausted.",
        "decisionQuestion": "Can traffic be absorbed or diverted before origin services become unavailable?",
        "effect": "Traffic overwhelms edge and origin capacity.",
        "evidenceType": "public-fact",
        "confidence": "high",
        "controlIds": ["cdn-scrubbing", "rate-limiting"],
        "controlIntervention": "Scrub volumetric traffic upstream and apply adaptive rate limits to protect origin capacity while preserving legitimate requests.",
        "sourceIds": ["mitre-t1498"],
    },
    {
        "id": "business-disruption",
        "number": "04",
        "title": "Business disruption",
        "technique": "T1499 — Endpoint Denial of Service",
        "stride": "Denial of Service",
        "attackerAction": "Sustain application or service exhaustion long enough to degrade customer-facing endpoints and dependent business workflows.",
        "defenderSignal": "Service health checks fail, queues grow, support contacts spike, and launch conversion or availability drops below agreed thresholds.",
        "businessEffect": "Customers cannot access launch services, support, or purchases, causing response costs, lost revenue, reputational harm, and secondary stakeholder impacts.",
        "decisionQuestion": "Can the team restore priority services and communicate clearly while mitigation remains active?",
        "effect": "Customers cannot access launch services, support, or purchases.",
        "evidenceType": "team-estimate",
        "confidence": "medium",
        "controlIds": ["incident-drills", "cdn-scrubbing"],
        "controlIntervention": "Execute the rehearsed response plan, prioritize critical services, activate stakeholder communications, and maintain upstream mitigation.",
        "sourceIds": ["mitre-t1499"],
    },
]


def get_scenario(scenario_id):
    return next((scenario for scenario in SCENARIOS if scenario["id"] == scenario_id), None)


def get_control(control_id):
    return next((control for control in CONTROLS if control["id"] == control_id), None)



# ======================================================================
# EVIDENCE-ANCHORED INPUT SET ("Set A") -- single source of truth shared
# with GTA6_FAIR_Monte_Carlo.xlsx (Evidence + Inputs sheets, IDs E##/I##).
# Everything below overrides the earlier uncited team estimates. Every value
# is labelled public-fact / derived / team-estimate / model-assumption.
# ======================================================================
SEED = 20261124
TRIALS = 10_000
THRESHOLDS_M = (10, 25, 50, 100)  # material-loss thresholds, $M (team policy)

_E = lambda i, t, u, d, c="High": {"id": i, "title": t, "url": u, "accessDate": d, "type": "public-fact", "confidence": c}
SOURCES.extend([
    _E("E01", "Take-Two Q2 FY27 results release (SEC Form 8-K): FY27 net bookings guidance $8.0-8.2B", "https://www.sec.gov/Archives/edgar/data/0000946581/000162828026072175/ttwo2q27earningsrelease.htm", "2026-11-22"),
    _E("E05", "Take-Two / Rockstar release (SEC 8-K Ex. 99.1): GTA VI day-one retail sales", "https://www.sec.gov/Archives/edgar/data/0000946581/000162828026075217/exhibit9918k.htm", "2026-11-22"),
    _E("E06", "Take-Two FY2026 Form 10-K (employees, GTA share, 2022 incident cost language)", "https://ir.take2games.com/static-files/31b9a69d-016e-4d72-9d91-b911f1313bed", "2026-11-22"),
    _E("E09", "GamesRadar: Rockstar told UK court the 2022 hack cost $5M to recover", "https://gamesradar.com/the-gta-6-leak-cost-rockstar-dollar5-million-and-thousands-of-hours-of-staff-time", "2026-11-22", "Medium"),
    _E("E10", "Insurance Journal (Bloomberg): Uber loss from the same actor, $2.8M", "https://www.insurancejournal.com/news/international/2023/08/25/737799.htm", "2026-11-22", "Medium"),
    _E("E11", "CBS/AP: Sony PlayStation Network 2011 breach cost ~$171M", "https://www.cbsnews.com/news/playstation-network-breach-has-cost-sony-171-million", "2026-11-22"),
    _E("E12", "The Register: PSN back online after Lizard Squad Christmas 2014 attack", "https://www.theregister.com/2014/12/27/playstation_clambers_back_online/", "2026-11-22"),
    _E("E13", "Cloudflare DDoS Threat Report 2026 Q3", "https://blog.cloudflare.com/ddos-threat-report-2026-q3/", "2026-11-22"),
    _E("E14", "IBM Cost of a Data Breach Report 2025", "https://newsroom.ibm.com/2025-07-30-ibm-report-13-of-organizations-reported-breaches-of-ai-models-or-applications,-97-of-which-reported-lacking-proper-ai-access-controls", "2026-11-22"),
    _E("E15", "Verizon 2026 DBIR (via Help Net Security)", "https://helpnetsecurity.com/2026/05/20/verizon-2026-dbir-findings", "2026-11-22", "Medium"),
    _E("E16", "Yubico: YubiKey 5 NFC list price $58", "https://www.yubico.com/cr/product/yubikey-5-series/yubikey-5-nfc", "2026-11-22"),
    _E("E18", "AWS Shield pricing (Advanced ~$3,000/month floor)", "https://aws.amazon.com/shield/pricing/", "2026-11-22", "Medium"),
])

_SRC = {s["id"]: s for s in SOURCES}
_SCOPE_ANCHORED = "Anchoring evidence for this input; the numeric range is a {kind} (see workbook Evidence sheet, {ref})."


def _set(sid, key, low, mode, high, unit, kind, conf, ref, anchors, rationale):
    a = get_scenario(sid)["assumptions"][key]
    a.update(low=low, mode=mode, high=high, unit=unit, confidence=conf, evidenceType=kind, rationale=rationale, evidenceRef=ref)
    src = _SRC[anchors[0]] if anchors else ASSUMPTION_METHOD_SOURCE
    a["source"] = {**src, "scope": _SCOPE_ANCHORED.format(kind=kind.replace("-", " "), ref=ref),
                   "anchorIds": list(anchors)}


def get_scenario(scenario_id):
    return next((x for x in SCENARIOS if x["id"] == scenario_id), None)


def get_control(control_id):
    return next((x for x in CONTROLS if x["id"] == control_id), None)


_Q3_MID = (3_350_000_000 + 3_500_000_000) / 2  # E02/E03 (Zacks summary of E01; verify in slides)
_DAILY = _Q3_MID / 92                            # E04
# DDoS primary loss = outage days x daily bookings x launch multiplier x online share x unrecovered share + response cost.
# Low/likely/high from the workbook Derivations sheet (values reproduced here, rounded).
_set("launch-ddos", "threatEventFrequency", 0.60, 0.85, 0.97, "probability per 7-day window", "team-estimate", "low", "I01", ["E13", "E12"],
     "Attempts on a top launch are near-certain; not measurable for Take-Two specifically.")
_set("launch-ddos", "vulnerability", 0.04, 0.12, 0.35, "probability", "team-estimate", "low", "I02", ["E13"],
     "Most attacks are short and small (96% <10 min, 98% <1 Gbps); the tail is >1 Tbps and application-layer floods.")
_set("launch-ddos", "primaryLoss", 841_372.28, 9_701_086.96, 80_618_206.52, "USD", "derived-value", "low", "I03", ["E01", "E12"],
     "Outage days x average daily Q3 net bookings x launch multiplier x online share x unrecovered share + response cost.")
_set("launch-ddos", "secondaryLoss", 3_425_000, 13_700_000, 85_625_000, "USD", "derived-value", "low", "I04", ["E11"],
     "0.1% / 0.4% / 2.5% of Q3 guidance midpoint ($3.425B); percentages are team estimates.")
_set("source-code-theft", "threatEventFrequency", 0.6, 1.5, 3.0, "events per year", "team-estimate", "low", "I05", ["E09"],
     "Targeted intrusion campaigns per year on dev/build environments; reference class Rockstar 2022.")
_set("source-code-theft", "vulnerability", 0.03, 0.10, 0.25, "probability", "team-estimate", "low", "I06", ["E09"],
     "Implied ~0.2 events/yr is consistent with 1-2 known Take-Two incidents in ~6 years (calibration check).")
_set("source-code-theft", "primaryLoss", 2_800_000, 5_000_000, 25_000_000, "USD", "public-fact", "medium", "I07", ["E09", "E10", "E14"],
     "Low = Uber loss (E10); mode = Rockstar-reported $5M (E09); high ~2.5x IBM US average (E14), team estimate.")
_set("source-code-theft", "secondaryLoss", 1_000_000, 6_000_000, 60_000_000, "USD", "team-estimate", "low", "I08", ["E11"],
     "High end about one-third of Sony PSN 2011 (E11); P(secondary | event) = 0.30.")
_set("insider-leak", "threatEventFrequency", 0.3, 0.8, 1.5, "events per year", "team-estimate", "low", "I09", ["E15"],
     "Third parties involved in 48% of breaches (E15); no Take-Two base rate.")
_set("insider-leak", "vulnerability", 0.05, 0.15, 0.35, "probability", "team-estimate", "low", "I10", ["E15"],
     "No public base rate for contractor-leak conversion.")
_set("insider-leak", "primaryLoss", 1_500_000, 4_900_000, 18_000_000, "USD", "public-fact", "medium", "I11", ["E14"],
     "Mode = IBM malicious-insider average $4.92M (E14); range is a team spread.")
_set("insider-leak", "secondaryLoss", 500_000, 5_000_000, 40_000_000, "USD", "team-estimate", "low", "I12", ["E11"],
     "Leaked-content, competitive and legal effects; P(secondary | event) = 0.25.")
_set("fake-downloads", "threatEventFrequency", 4, 12, 30, "events per year", "team-estimate", "low", "I13", ["E13"],
     "Impersonation/phishing campaigns around a GTA VI launch are near-certain; count is a judgment.")
_set("fake-downloads", "vulnerability", 0.02, 0.06, 0.15, "probability", "team-estimate", "low", "I14", ["E14"],
     "Most campaigns harm players, not the publisher.")
_set("fake-downloads", "primaryLoss", 500_000, 3_000_000, 12_000_000, "USD", "public-fact", "low", "I15", ["E14"],
     "Mode near IBM phishing/credential breach range, discounted because most victims are players.")
_set("fake-downloads", "secondaryLoss", 500_000, 4_000_000, 30_000_000, "USD", "team-estimate", "low", "I16", ["E11"],
     "Brand, trust and consumer-protection exposure; P(secondary | event) = 0.20.")

# P(secondary loss occurs | event): workbook Inputs row "P(secondary loss | event)".
for _sid, _p in (("launch-ddos", 0.35), ("source-code-theft", 0.30), ("insider-leak", 0.25), ("fake-downloads", 0.20)):
    get_scenario(_sid)["probabilitySecondary"] = _p
    get_scenario(_sid)["analysisBasis"] = "launch-window" if _sid == "launch-ddos" else "annual"

# Control costs (low, mode, high). Only MFA differs from the earlier config.
get_control("phishing-resistant-mfa")["cost"] = {"low": 400_000, "mode": 750_000, "high": 1_600_000}
for _c in CONTROLS:
    _c["cost"]["expected"] = round((_c["cost"]["low"] + _c["cost"]["mode"] + _c["cost"]["high"]) / 3)
    _c["costEvidence"] = ("Derived from E06 x E16 (12,909 staff x 2 keys x $58 = $1.50M hardware ceiling)" if _c["id"] == "phishing-resistant-mfa"
                          else "DDoS floor anchored on E18 (AWS Shield Advanced ~$3k/month); enterprise scrubbing is quote-based" if _c["id"] == "cdn-scrubbing"
                          else "Team estimate; replace with vendor quote or hours x rate before submission")
    _c["effectsEvidenceType"] = "team-estimate"

# Priority-score feasibility/confidence judgments (1-5), team estimates.
for _id, _f in zip([c["id"] for c in CONTROLS], [4, 4, 5, 3, 4, 3, 4, 4, 3]):
    get_control(_id)["feasibility"] = _f

METHODOLOGY.update(
    sampling="Triangular low/likely/high inputs; 10,000 trials; fixed seed 20261124. Baseline and residual share the same random draws.",
    formula="Successful events x (primary loss + secondary loss x [secondary occurs])",
    eventRule="Launch window (DDoS): Bernoulli(min(1, TEF)) x Bernoulli(vulnerability). Annual scenarios: Poisson thinning, successes ~ Poisson(TEF x vulnerability), capped at 6.",
    thresholds="Material-loss thresholds $10M / $25M / $50M / $100M are team policy assumptions.",
    priorityScore="Loss reduction 35, reduction per $ 25, P95 reduction proxy 20, scenarios helped 10, feasibility 10; P1 >= 60, P2 >= 40, else P3 (team policy).",
    disclaimer="Team-designed FAIR-style model, not an official Open FAIR, NIST or MITRE assessment. Frequency, vulnerability and control-effect inputs are team estimates anchored on cited reference classes, not measured Take-Two facts.",
    launchNote="GTA VI launched Nov 19 2026, so the launch-window DDoS scenario is a launch-window what-if/retrospective.",
)


def _node(n, i, title, tech, stride, act, sig, biz, q, ev, conf, ctrls, interv, srcs):
    return {"id": i, "number": f"{n:02d}", "title": title, "technique": tech, "stride": stride,
            "attackerAction": act, "defenderSignal": sig, "businessEffect": biz, "decisionQuestion": q,
            "effect": biz, "evidenceType": ev, "confidence": conf, "controlIds": ctrls,
            "controlIntervention": interv, "sourceIds": srcs}


ATTACK_CHAIN = [
    _node(1, "reconnaissance", "Reconnaissance", "T1595 Active Scanning", "Information Disclosure",
          "Probe public IP ranges, DNS, APIs and launch services to find exposed endpoints and capacity limits.",
          "Unusual scanning and repeated requests across endpoints before the launch window.",
          "Attackers learn which launch services carry the most business value.",
          "Can we detect and triage reconnaissance before traffic peaks?", "public-fact", "high",
          ["rate-limiting", "incident-drills"], "Rate-limit probing; rehearse escalation when scanning exceeds normal patterns.", ["mitre-t1595"]),
    _node(2, "attack-infrastructure", "Attack infrastructure preparation", "T1584 Compromise Infrastructure", "Spoofing",
          "Assemble botnets or rent DDoS-for-hire capacity and compromised hosts.",
          "Threat-intel chatter, extortion notes, abnormal pre-launch traffic from new networks.",
          "Attack capacity is staged outside Take-Two's visibility.",
          "Do we have threat intelligence and partner channels before launch?", "public-fact", "medium",
          ["incident-drills"], "Pre-agreed escalation with CDN, platform and ISP partners.", ["mitre-t1584"]),
    _node(3, "network-flood", "Network flood", "T1498 Network Denial of Service", "Denial of Service",
          "Volumetric flood against edge, login and matchmaking endpoints at launch.",
          "Traffic spike beyond forecast, saturation at the edge.",
          "Login and storefront latency; players cannot connect.",
          "Is scrubbing capacity sized for a worst-case launch flood?", "public-fact", "high",
          ["cdn-scrubbing"], "Upstream scrubbing absorbs volumetric traffic before it reaches origin.", ["mitre-t1498", "E13"]),
    _node(4, "application-exhaustion", "Application and service exhaustion", "T1499.002/.003 Endpoint DoS", "Denial of Service",
          "Layer-7 floods and expensive-request abuse against APIs, auth and purchase services.",
          "Error rates, queue depth and autoscaling alarms.",
          "Core services slow or fail even when the network layer holds.",
          "Do rate limits and load tests cover login, store and matchmaking?", "public-fact", "high",
          ["rate-limiting", "cdn-scrubbing"], "Adaptive rate limiting and tested capacity cap request abuse.", ["mitre-t1499"]),
    _node(5, "cascading-degradation", "Degradation and cascading failure", "T1499 Endpoint DoS", "Denial of Service",
          "Degraded services cascade into dependent systems (entitlements, payments, partner APIs).",
          "Dependency timeouts and partner status alerts.",
          "Partial or full outage window; support load rises.",
          "Is there tested failover and graceful degradation?", "model-assumption", "medium",
          ["incident-drills"], "Failover and degraded-mode drills limit the blast radius.", ["E12"]),
    _node(6, "detection-response", "Detection, response and recovery", "NIST CSF 2.0 Detect / Respond / Recover", "Repudiation",
          "Defender triage, escalation, mitigation and customer communication.",
          "Time to detect, time to mitigate, comms cadence.",
          "Outage duration is the main driver of primary loss.",
          "How fast can we cut outage duration?", "model-assumption", "medium",
          ["incident-drills", "cdn-scrubbing"], "Rehearsed playbooks shorten outage days (the largest term in primary loss).", ["nist-csf-2"]),
    _node(7, "business-loss", "Business loss event", "FAIR loss magnitude", "n/a",
          "Outage converts into primary loss (lost/delayed bookings, response) and secondary loss (brand, partner, regulatory).",
          "Net bookings vs guidance, review and social sentiment.",
          "Measured in the Monte Carlo as primary + secondary loss.",
          "What is the change in expected and tail loss from the control plan?", "derived-value", "low",
          ["cdn-scrubbing", "rate-limiting", "incident-drills"], "Residual risk = baseline minus modelled control effect (team-estimated multipliers).", ["E01", "E11"]),
]
