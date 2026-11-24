from copy import deepcopy

from backend.data.evidence_profiles import EVIDENCE_PROFILES, EVIDENCE_SOURCES


ACCESS_DATE = "2026-11-21"
ATTACK_PATH_ACCESS_DATE = "2026-11-24"


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
        "id": "mitre-t1078",
        "title": "MITRE ATT&CK: Valid Accounts (T1078)",
        "url": "https://attack.mitre.org/techniques/T1078/",
        "accessDate": ATTACK_PATH_ACCESS_DATE,
        "type": "public-fact",
    },
    {
        "id": "mitre-t1083",
        "title": "MITRE ATT&CK: File and Directory Discovery (T1083)",
        "url": "https://attack.mitre.org/techniques/T1083/",
        "accessDate": ATTACK_PATH_ACCESS_DATE,
        "type": "public-fact",
    },
    {
        "id": "mitre-t1005",
        "title": "MITRE ATT&CK: Data from Local System (T1005)",
        "url": "https://attack.mitre.org/techniques/T1005/",
        "accessDate": ATTACK_PATH_ACCESS_DATE,
        "type": "public-fact",
    },
    {
        "id": "mitre-t1567",
        "title": "MITRE ATT&CK: Exfiltration Over Web Service (T1567)",
        "url": "https://attack.mitre.org/techniques/T1567/",
        "accessDate": ATTACK_PATH_ACCESS_DATE,
        "type": "public-fact",
    },
    {
        "id": "mitre-t1583-001",
        "title": "MITRE ATT&CK: Acquire Infrastructure—Domains (T1583.001)",
        "url": "https://attack.mitre.org/techniques/T1583/001/",
        "accessDate": ATTACK_PATH_ACCESS_DATE,
        "type": "public-fact",
    },
    {
        "id": "mitre-t1608-001",
        "title": "MITRE ATT&CK: Stage Capabilities—Upload Malware (T1608.001)",
        "url": "https://attack.mitre.org/techniques/T1608/001/",
        "accessDate": ATTACK_PATH_ACCESS_DATE,
        "type": "public-fact",
    },
    {
        "id": "mitre-t1566-002",
        "title": "MITRE ATT&CK: Phishing—Spearphishing Link (T1566.002)",
        "url": "https://attack.mitre.org/techniques/T1566/002/",
        "accessDate": ATTACK_PATH_ACCESS_DATE,
        "type": "public-fact",
    },
    {
        "id": "mitre-t1204-002",
        "title": "MITRE ATT&CK: User Execution—Malicious File (T1204.002)",
        "url": "https://attack.mitre.org/techniques/T1204/002/",
        "accessDate": ATTACK_PATH_ACCESS_DATE,
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
SOURCES.extend(EVIDENCE_SOURCES)


METHODOLOGY = {
    "name": "Team FAIR-style Monte Carlo model",
    "description": "A decision-support model structured around event frequency, conditional success, and loss magnitude.",
    "formula": "Successful events × primary loss + secondary-loss events × secondary loss",
    "sampling": "Triangular low, most-likely, and high estimates; 10,000 paired trials with fixed seed 243.",
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


_source_lookup = {source["id"]: source for source in SOURCES}
for _scenario in SCENARIOS:
    _legacy_assumptions = deepcopy(_scenario["assumptions"])
    for _assumption in _legacy_assumptions.values():
        _assumption["evidenceIds"] = ["open-fair-methodology"]

    _evidence = deepcopy(EVIDENCE_PROFILES[_scenario["id"]])
    _scenario["analysisBasis"] = _evidence["analysisBasis"]
    _scenario["defaultAssumptionProfileId"] = "evidence-anchored"
    _scenario["assumptionProfiles"] = {
        "evidence-anchored": {
            "id": "evidence-anchored",
            "name": "Evidence-anchored",
            "description": "Workbook-derived ranges tied to explicit evidence and transparent team judgments.",
            "assumptions": _evidence["assumptions"],
            "secondaryLossProbability": _evidence["secondaryLossProbability"],
        },
        "original-team": {
            "id": "original-team",
            "name": "Original team estimates",
            "description": "The app's earlier broad estimates, retained for comparison rather than treated as equally authoritative.",
            "assumptions": _legacy_assumptions,
            "secondaryLossProbability": {
                "value": 1.0,
                "unit": "probability per successful event",
                "rationale": "Legacy behavior added secondary loss after every successful event.",
                "confidence": "low",
                "evidenceType": "model-assumption",
                "evidenceIds": ["open-fair-methodology"],
            },
        },
    }
    _scenario["assumptions"] = _evidence["assumptions"]
    _scenario["secondaryLossProbability"] = _evidence["secondaryLossProbability"]
    if "lossDerivation" in _evidence:
        _scenario["lossDerivation"] = _evidence["lossDerivation"]

    for _profile in _scenario["assumptionProfiles"].values():
        for _assumption in list(_profile["assumptions"].values()) + [_profile["secondaryLossProbability"]]:
            _ids = _assumption.get("evidenceIds", ["open-fair-methodology"])
            _assumption["sources"] = [_source_lookup[source_id] for source_id in _ids if source_id in _source_lookup]


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


CONTROL_EFFECT_RATIONALES = {
    "cdn-scrubbing": "Expected to reduce attack traffic reaching origin services, lower conditional disruption likelihood, and modestly reduce outage losses.",
    "rate-limiting": "Expected to constrain abusive request patterns and protect constrained application capacity during a traffic surge.",
    "incident-drills": "Expected to shorten escalation and recovery time, limiting direct restoration costs and downstream stakeholder effects.",
    "repository-hardening": "Expected to make build-system compromise materially harder and reduce the scope and cost of a successful intrusion.",
    "least-privilege": "Expected to reduce unnecessary access opportunities and limit the data or systems reachable after account misuse.",
    "dlp-monitoring": "Expected to improve detection and containment of unusual data movement, reducing the probability and scale of material loss.",
    "contractor-offboarding": "Expected to reduce exposure from stale contractor access and shorten the window in which former users retain privileges.",
    "brand-monitoring": "Expected to identify impersonation campaigns sooner, support faster takedown, and reduce customer and reputation impacts.",
    "phishing-resistant-mfa": "Expected to materially reduce credential-based compromise and limit losses from successful impersonation campaigns.",
}

_control_method_source = next(source for source in SOURCES if source["id"] == "nist-csf-2")
for _control in CONTROLS:
    _control["effectEvidence"] = {
        "evidenceType": "team-estimate",
        "rationale": CONTROL_EFFECT_RATIONALES[_control["id"]],
        "confidence": _control["confidence"],
        "source": {
            **_control_method_source,
            "scope": "Control-framework reference only; the quantitative multipliers are team-developed estimates for this decision model and require organizational validation.",
        },
    }


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


# DDoS remains the deeply researched showcase. The other paths are concise,
# decision-oriented narratives that reuse the same interaction pattern.
ATTACK_CHAINS = {
    "launch-ddos": ATTACK_CHAIN,
    "source-code-theft": [
        {
            "id": "source-valid-access", "number": "01", "title": "Obtain development access",
            "technique": "T1078 — Valid Accounts", "stride": "Spoofing / Elevation of Privilege",
            "attackerAction": "Use stolen, reused, or insufficiently revoked credentials to enter a repository, developer platform, VPN, or build service.",
            "defenderSignal": "Login from an unusual device or location, impossible travel, dormant-account use, or abnormal authentication failures followed by success.",
            "businessEffect": "The attacker gains trusted access to proprietary development systems without immediately deploying obvious malware.",
            "decisionQuestion": "Can the team prevent or quickly challenge abnormal use of a valid developer account?",
            "evidenceType": "public-fact", "confidence": "high",
            "controlIds": ["phishing-resistant-mfa", "least-privilege", "repository-hardening"],
            "controlIntervention": "Phishing-resistant MFA blocks many credential-only attacks; least privilege and repository hardening restrict what a compromised identity can reach.",
            "sourceIds": ["mitre-t1078"],
        },
        {
            "id": "source-discovery", "number": "02", "title": "Discover repositories and builds",
            "technique": "T1083 — File and Directory Discovery", "stride": "Information Disclosure",
            "attackerAction": "Search accessible repositories, shared drives, build outputs, secrets, and project directories to identify high-value source and release assets.",
            "defenderSignal": "Unusual repository enumeration, broad search activity, access to projects outside the user's role, or rapid metadata queries.",
            "businessEffect": "The attacker identifies the code, credentials, and build artefacts with the greatest competitive or launch value.",
            "decisionQuestion": "Would current access boundaries stop one compromised account from discovering multiple critical projects?",
            "evidenceType": "public-fact", "confidence": "medium",
            "controlIds": ["least-privilege", "repository-hardening", "dlp-monitoring"],
            "controlIntervention": "Role-based repository access limits discovery scope, while behavior monitoring flags enumeration inconsistent with the account's normal work.",
            "sourceIds": ["mitre-t1083"],
        },
        {
            "id": "source-collection", "number": "03", "title": "Collect source and secrets",
            "technique": "T1005 — Data from Local System", "stride": "Information Disclosure",
            "attackerAction": "Clone repositories or collect source code, build configurations, signing material, development secrets, and unreleased assets.",
            "defenderSignal": "Large or unusual clones, archive creation, bulk downloads, secret-file access, or activity outside normal working patterns.",
            "businessEffect": "Sensitive intellectual property is assembled into a form that can be removed, leaked, or used to compromise builds.",
            "decisionQuestion": "Can monitoring distinguish a legitimate build workflow from unusual bulk collection?",
            "evidenceType": "public-fact", "confidence": "medium",
            "controlIds": ["repository-hardening", "dlp-monitoring"],
            "controlIntervention": "Repository protections constrain bulk operations and secret exposure; DLP and behavior analytics identify unusual collection volume.",
            "sourceIds": ["mitre-t1005"],
        },
        {
            "id": "source-exfiltration", "number": "04", "title": "Exfiltrate and exploit",
            "technique": "T1567 — Exfiltration Over Web Service", "stride": "Information Disclosure / Repudiation",
            "attackerAction": "Transfer collected assets to external cloud, code-hosting, or file-sharing services and potentially publish or monetize them.",
            "defenderSignal": "High outbound data volume, uploads to personal services, newly created archives, unusual tokens, or public appearance of internal material.",
            "businessEffect": "The organization faces investigation and rebuild costs, competitive exposure, partner concerns, and possible launch delay.",
            "decisionQuestion": "Can the team block the transfer and revoke access before the material leaves organizational control?",
            "evidenceType": "team-estimate", "confidence": "medium",
            "controlIds": ["dlp-monitoring", "incident-drills", "repository-hardening"],
            "controlIntervention": "DLP can detect or block unusual transfers; rehearsed response accelerates token revocation, containment, evidence preservation, and stakeholder decisions.",
            "sourceIds": ["mitre-t1567"],
        },
    ],
    "insider-leak": [
        {
            "id": "insider-authorized-access", "number": "01", "title": "Use trusted access",
            "technique": "T1078 — Valid Accounts", "stride": "Elevation of Privilege / Repudiation",
            "attackerAction": "An employee, contractor, or former worker uses legitimate or insufficiently revoked access to reach confidential systems.",
            "defenderSignal": "Dormant-account use, access after role change, unusual working hours, policy exceptions, or repeated access to material unrelated to assigned duties.",
            "businessEffect": "Trusted access allows the actor to blend malicious or careless activity with legitimate business work.",
            "decisionQuestion": "Are access changes and contractor departures reflected in systems quickly enough?",
            "evidenceType": "public-fact", "confidence": "high",
            "controlIds": ["contractor-offboarding", "least-privilege"],
            "controlIntervention": "Automated offboarding closes stale accounts, while least-privilege reviews align current access with current job responsibilities.",
            "sourceIds": ["mitre-t1078"],
        },
        {
            "id": "insider-discovery", "number": "02", "title": "Locate sensitive material",
            "technique": "T1083 — File and Directory Discovery", "stride": "Information Disclosure",
            "attackerAction": "Search project folders, collaboration platforms, repositories, or customer records for valuable unreleased or regulated information.",
            "defenderSignal": "Broad search queries, access across unrelated projects, repeated denied requests, or sudden interest in high-sensitivity folders.",
            "businessEffect": "The actor identifies which files could cause the greatest launch, privacy, legal, or reputational harm.",
            "decisionQuestion": "Do data classifications and access boundaries make abnormal discovery visible?",
            "evidenceType": "public-fact", "confidence": "medium",
            "controlIds": ["least-privilege", "dlp-monitoring"],
            "controlIntervention": "Least privilege reduces reachable material; DLP and behavioral monitoring identify access inconsistent with a person's normal role.",
            "sourceIds": ["mitre-t1083"],
        },
        {
            "id": "insider-collection", "number": "03", "title": "Collect or copy data",
            "technique": "T1005 — Data from Local System", "stride": "Information Disclosure / Repudiation",
            "attackerAction": "Copy, export, screenshot, archive, or otherwise collect confidential material using legitimate applications or local tools.",
            "defenderSignal": "Bulk downloads, unusual printing, removable-media activity, archive creation, or sudden changes in normal data-transfer volume.",
            "businessEffect": "Confidential information moves from controlled systems into a portable form that is easier to leak or misuse.",
            "decisionQuestion": "Can the team intervene before collection becomes an external disclosure?",
            "evidenceType": "public-fact", "confidence": "medium",
            "controlIds": ["dlp-monitoring", "least-privilege"],
            "controlIntervention": "DLP policies and behavior analytics detect sensitive exports and unusual volume; permissions limit the amount available to collect.",
            "sourceIds": ["mitre-t1005"],
        },
        {
            "id": "insider-disclosure", "number": "04", "title": "Disclose externally",
            "technique": "T1567 — Exfiltration Over Web Service", "stride": "Information Disclosure / Repudiation",
            "attackerAction": "Upload the material to personal cloud storage, messaging, social media, press contacts, or public file-sharing services.",
            "defenderSignal": "Uploads to unsanctioned services, outbound sharing links, unusual forwarding, or confidential material appearing outside the organization.",
            "businessEffect": "The disclosure can trigger containment, legal, notification, partner, customer-trust, and competitive consequences.",
            "decisionQuestion": "Can the organization contain access and coordinate legal, communications, and technical response quickly?",
            "evidenceType": "team-estimate", "confidence": "medium",
            "controlIds": ["dlp-monitoring", "incident-drills", "contractor-offboarding"],
            "controlIntervention": "DLP can block common transfer routes; offboarding and practiced incident response shorten the period of continued access and external harm.",
            "sourceIds": ["mitre-t1567"],
        },
    ],
    "fake-downloads": [
        {
            "id": "fake-domain", "number": "01", "title": "Create lookalike infrastructure",
            "technique": "T1583.001 — Acquire Infrastructure: Domains", "stride": "Spoofing",
            "attackerAction": "Register lookalike domains and create websites or accounts that imitate the official product, company, support team, or download experience.",
            "defenderSignal": "New typo-squatted domains, copied branding, suspicious certificates, impersonating social accounts, or paid advertisements using launch terms.",
            "businessEffect": "Customers may mistake attacker-controlled infrastructure for an official source because it visually resembles the real brand.",
            "decisionQuestion": "How quickly can the team discover and begin takedown of impersonating infrastructure?",
            "evidenceType": "public-fact", "confidence": "high",
            "controlIds": ["brand-monitoring", "incident-drills"],
            "controlIntervention": "Brand monitoring detects lookalike domains and accounts; rehearsed escalation speeds registrar, platform, legal, and communications action.",
            "sourceIds": ["mitre-t1583-001"],
        },
        {
            "id": "fake-payload", "number": "02", "title": "Stage the fake download",
            "technique": "T1608.001 — Stage Capabilities: Upload Malware", "stride": "Tampering",
            "attackerAction": "Upload a malicious installer, credential-harvesting page, or altered file and present it as an early build, launcher, patch, or promotion.",
            "defenderSignal": "Files using company names, copied download pages, malicious hashes, unexpected signing information, or newly hosted payloads.",
            "businessEffect": "A believable malicious asset is prepared to steal credentials, infect devices, or exploit customer interest in the launch.",
            "decisionQuestion": "Can official channels make authentic downloads and signing information easy to verify?",
            "evidenceType": "public-fact", "confidence": "medium",
            "controlIds": ["brand-monitoring", "phishing-resistant-mfa"],
            "controlIntervention": "Monitoring supports payload and hosting takedown; phishing-resistant MFA limits the usefulness of credentials captured from workforce users.",
            "sourceIds": ["mitre-t1608-001"],
        },
        {
            "id": "fake-delivery", "number": "03", "title": "Distribute deceptive links",
            "technique": "T1566.002 — Phishing: Spearphishing Link", "stride": "Spoofing / Tampering",
            "attackerAction": "Spread links through email, social media, advertisements, search results, communities, or direct messages using launch-related urgency.",
            "defenderSignal": "Reported messages, repeated shortened links, sudden traffic to lookalike domains, or campaigns copying official announcements.",
            "businessEffect": "The campaign reaches customers, partners, or employees and borrows trust from the legitimate launch and brand.",
            "decisionQuestion": "Can warnings and takedowns reach likely victims before the campaign scales?",
            "evidenceType": "public-fact", "confidence": "high",
            "controlIds": ["brand-monitoring", "incident-drills", "phishing-resistant-mfa"],
            "controlIntervention": "Monitoring accelerates discovery and takedown; MFA protects workforce accounts, while drills coordinate warnings, support, and platform escalation.",
            "sourceIds": ["mitre-t1566-002"],
        },
        {
            "id": "fake-execution", "number": "04", "title": "Victim executes or signs in",
            "technique": "T1204.002 — User Execution: Malicious File", "stride": "Tampering / Information Disclosure",
            "attackerAction": "A victim downloads and runs the file or enters credentials into the fraudulent service, enabling malware, theft, fraud, or follow-on compromise.",
            "defenderSignal": "Customer reports, endpoint alerts, credential abuse, support spikes, malicious-file telemetry, or compromised accounts promoting the campaign.",
            "businessEffect": "Victims can suffer device compromise or account theft, while the organization incurs response, support, fraud, and reputation costs.",
            "decisionQuestion": "Can the team contain compromised accounts, support victims, and clearly direct users to official channels?",
            "evidenceType": "team-estimate", "confidence": "medium",
            "controlIds": ["phishing-resistant-mfa", "brand-monitoring", "incident-drills"],
            "controlIntervention": "MFA reduces credential replay against protected accounts; monitoring and response procedures support takedown, victim guidance, and containment.",
            "sourceIds": ["mitre-t1204-002"],
        },
    ],
}


def get_scenario(scenario_id):
    return next((scenario for scenario in SCENARIOS if scenario["id"] == scenario_id), None)


def get_control(control_id):
    return next((control for control in CONTROLS if control["id"] == control_id), None)

