"""Single source of truth for scenarios, model inputs, controls, attack paths, and evidence.

Every numeric model input carries an evidence class (Public fact, Derived value,
Team estimate, or Model assumption), sources, rationale, confidence, the control
relationship, and an owner/reviewer. The FAIR-style engine in backend/model/fair.py
reads only from this file, so the app, report, and slides stay consistent.
"""

ACCESS_DATE = "2026-11-22"
MODEL_SEED = 20261124
MODEL_TRIALS = 10_000
MODEL_VERSION = "2026-11-22-evidence-v1"

EVIDENCE_CLASSES = {
    "public-fact": "Public fact",
    "derived-value": "Derived value",
    "team-estimate": "Team estimate",
    "model-assumption": "Model assumption",
}

TIME_BASES = {
    "launch-event": {
        "label": "USD per launch event",
        "short": "per launch event",
        "window": "Seven-day GTA VI launch window (Nov 19-25, 2026)",
    },
    "annual": {
        "label": "USD per year",
        "short": "annual",
        "window": "Twelve-month period",
    },
}


# ---------------------------------------------------------------------------
# Evidence register
# ---------------------------------------------------------------------------

def _source(source_id, title, publisher, url, published, source_class, reliability, claim, use):
    return {
        "id": source_id,
        "title": title,
        "publisher": publisher,
        "url": url,
        "published": published,
        "accessDate": ACCESS_DATE,
        "type": source_class,
        "evidenceClass": source_class,
        "reliability": reliability,
        "claim": claim,
        "plannedUse": use,
        "owner": "Member 2",
        "reviewer": "Member 3",
    }


SOURCES = [
    _source(
        "ttwo-10k-fy2026",
        "Take-Two Interactive Form 10-K, fiscal year ended March 31, 2026",
        "U.S. SEC EDGAR",
        "https://www.sec.gov/Archives/edgar/data/0000946581/000162828026037434/ttwo-20260331.htm",
        "2026-05",
        "public-fact",
        "high",
        "Describes the September 2022 Rockstar intrusion, source-code protection, third-party access to "
        "proprietary information, a 2022 vendor help-desk compromise used to send players a malicious link, "
        "and 12,909 full-time employees (9,998 in product development).",
        "Company-specific evidence for Build Theft, Insider Leak, and Fake Downloads; workforce size for control costs.",
    ),
    _source(
        "gta5-launch-1b",
        "Grand Theft Auto 5 sales surpass $1 billion (Take-Two announcement)",
        "Engadget",
        "https://www.engadget.com/2013/09/20/grand-theft-auto-5-sales-surpass-1-billion/",
        "2013-09-20",
        "public-fact",
        "high",
        "GTA V reached $800 million in its first 24 hours and more than $1 billion in three days.",
        "Historical anchor for launch-window revenue concentration.",
    ),
    _source(
        "sensor-tower-gta6",
        "GTA VI pulls in estimated $1.84 billion by release day (Sensor Tower estimates)",
        "FOX 5 DC",
        "https://www.fox5dc.com/news/gta-vi-pulls-estimated-1-84-billion-release-day-more-than-double-gta-vs-launch-record",
        "2026-11-19",
        "public-fact",
        "medium",
        "Sensor Tower estimated about $1.65 billion by noon Nov 18 and $1.84 billion (19.05 million units) by release "
        "day; PS5 and Xbox Series X|S only; $80 standard and $100 ultimate editions. Third-party estimate, not Take-Two data.",
        "Derives hourly launch revenue at risk.",
    ),
    _source(
        "newzoo-gta6-forecast",
        "GTA 6 pre-orders point to record-breaking launch week (Newzoo analysis)",
        "GamesBeat",
        "https://gamesbeat.com/gta-6-pre-orders-point-to-record-breaking-launch-week/",
        "2026-07",
        "derived-value",
        "medium",
        "Newzoo projected $3.3 billion to $5.2 billion in launch-week sales (central case about $4.5 billion, ~51 million units at $88 ASP).",
        "Upper bound for launch-week revenue at risk.",
    ),
    _source(
        "gta6-launch-psn",
        "PSN Back Online After Two Outages Around GTA 6 Launch",
        "TechRepublic",
        "https://www.techrepublic.com/article/news-psn-back-online-gta-6-outages/",
        "2026-11",
        "public-fact",
        "medium",
        "PlayStation Network had service disruptions on Nov 18 and Nov 19, 2026 around the GTA VI launch; Sony gave no cause. "
        "Launch-week reporting found no widespread outage on Rockstar's own services.",
        "Evidence of third-party platform dependency and baseline launch capacity.",
    ),
    _source(
        "overwatch2-ddos",
        "Overwatch 2 launch derailed by major DDoS attack",
        "PC Gamer",
        "https://www.pcgamer.com/overwatch-2-ddos-attack-launch",
        "2022-10-04",
        "public-fact",
        "high",
        "Blizzard's president confirmed a mass DDoS attack during the Overwatch 2 launch; a second DDoS followed and connection problems lasted more than a day.",
        "Precedent for launch-day DDoS probability, success, and outage duration.",
    ),
    _source(
        "cloudflare-ddos-2025q3",
        "Cloudflare 2025 Q3 DDoS threat report, including Aisuru",
        "Cloudflare",
        "https://blog.cloudflare.com/ddos-threat-report-2025-q3/",
        "2025-12-03",
        "public-fact",
        "high",
        "The Aisuru botnet-for-hire launched record hyper-volumetric attacks (29.7 Tbps) and targeted gaming companies among others; "
        "gaming and gambling ranked among the most-attacked industries.",
        "Threat capability and targeting evidence for DDoS attack probability.",
    ),
    _source(
        "cloudflare-ddos-2026h1",
        "Cloudflare DDoS Threat Report H1 2026",
        "Cloudflare",
        "https://blog.cloudflare.com/ddos-threat-report-2026-h1/",
        "2026-08",
        "public-fact",
        "high",
        "935 attacks above 1 Tbps in H1 2026; most DDoS attacks are short-lived; automated always-on protection is recommended.",
        "Supports duration assumptions and the managed-protection control effect.",
    ),
    _source(
        "aws-shield-pricing",
        "AWS Shield pricing",
        "Amazon Web Services",
        "https://aws.amazon.com/shield/pricing/",
        "2026",
        "public-fact",
        "high",
        "Shield Advanced costs $3,000 per month per organization with a one-year commitment plus data-transfer usage fees.",
        "Public price floor for managed DDoS protection; enterprise CDN contracts are team estimates.",
    ),
    _source(
        "rockstar-hack-cost",
        "The GTA 6 leak cost Rockstar $5 million and thousands of hours of staff time",
        "GamesRadar+ (reporting BBC court coverage)",
        "https://www.gamesradar.com/the-gta-6-leak-cost-rockstar-dollar5-million-and-thousands-of-hours-of-staff-time",
        "2023-08",
        "public-fact",
        "high",
        "Rockstar told a UK court the 2022 intrusion cost about $5 million to recover from plus thousands of hours of staff time.",
        "Anchor for Build Theft investigation, recovery, and staff-disruption costs.",
    ),
    _source(
        "kurtaj-plea-2026",
        "GTA 6 hacker pleads guilty over 90-video leak Rockstar says cost $5 million",
        "International Business Times UK",
        "https://www.ibtimes.co.uk/gta-6-hacker-arion-kurtaj-pleads-guilty-rockstar-breach-1832693",
        "2026-11-16",
        "public-fact",
        "medium",
        "The Lapsus$ member behind the 2022 Rockstar intrusion pleaded guilty on Nov 16, 2026; 90 development clips were exposed and source code was threatened.",
        "Confirms the attack path and extortion element for Build Theft.",
    ),
    _source(
        "peer-code-theft",
        "Riot Games latest video-game maker to suffer breach",
        "Dark Reading",
        "https://www.darkreading.com/attacks-breaches/not-playing-games-riot-games-latest-video-game-maker-to-suffer-breach",
        "2023-01",
        "public-fact",
        "high",
        "Riot Games (2023), Electronic Arts (2021, Slack social engineering), and CD Projekt Red (2021) all had game source code stolen.",
        "Peer base rate for Build Theft frequency.",
    ),
    _source(
        "ibm-codb-2025",
        "IBM Cost of a Data Breach Report 2025 (press release)",
        "IBM",
        "https://newsroom.ibm.com/2025-07-30-ibm-report-13-of-organizations-reported-breaches-of-ai-models-or-applications,-97-of-which-reported-lacking-proper-ai-access-controls",
        "2025-07-30",
        "public-fact",
        "high",
        "Global average breach cost $4.44 million; U.S. average $10.22 million.",
        "Calibration range for breach-related loss magnitudes.",
    ),
    _source(
        "ibm-codb-2025-vectors",
        "Survey sees global decline in data breach costs (IBM 2025 attack-vector costs)",
        "Barracuda",
        "https://blog.barracuda.com/2025/09/02/survey-global-decline-data-breach-costs",
        "2025-09-02",
        "public-fact",
        "medium",
        "Malicious insider breaches averaged $4.92 million, supply-chain compromise $4.91 million, and phishing $4.8 million.",
        "Per-event calibration for Insider Leak and Fake Downloads.",
    ),
    _source(
        "ponemon-insider-2025",
        "The security risk organizations should not ignore: careless, negligent and malicious insiders",
        "Ponemon Institute",
        "https://www.ponemon.org/news-updates/blog/security/the-security-risk-organizations-should-not-ignore-careless-negligent-and-malicious-insiders.html",
        "2025",
        "public-fact",
        "high",
        "Average annualized insider-risk cost $17.4 million ($22.2 million in North America); average $3.7 million per malicious or criminal insider incident.",
        "Calibration for Insider Leak frequency and magnitude.",
    ),
    _source(
        "rockstar-firings-2025",
        "Rockstar says the employees it fired were leaking information",
        "PC Gamer",
        "https://www.pcgamer.com/games/grand-theft-auto/rockstar-says-the-employees-it-fired-were-leaking-information-but-its-not-going-to-escape-union-busting-accusations-that-easily",
        "2025-11",
        "public-fact",
        "medium",
        "Rockstar said it fired more than 30 employees in October 2025 for sharing confidential information in a public forum; the IWGB union disputes this and alleges union busting. Treated as a contested allegation.",
        "Context for Insider Leak; not used as proof of a leak.",
    ),
    _source(
        "kaspersky-gaming-2025",
        "Experts warn GTA and Minecraft being used to lure in cyberattack victims",
        "TechRadar Pro (Kaspersky research)",
        "https://www.techradar.com/pro/security/experts-warn-gta-and-minecraft-being-used-to-lure-in-cyberattack-victims-heres-how-to-stay-safe",
        "2025",
        "public-fact",
        "medium",
        "Kaspersky recorded more than 19 million attempts to download malicious files spoofing popular games (Apr 2024-Mar 2025); GTA is among the most abused titles.",
        "Frequency evidence for Fake Downloads and Phishing.",
    ),
    _source(
        "malwarebytes-gta6-demo",
        "Fake GTA 6 Extended Look and demo sites deliver an infostealer",
        "Malwarebytes",
        "https://www.malwarebytes.com/blog/news/2026/08/fake-gta-6-extended-look-and-demo-sites-deliver-an-infostealer",
        "2026-08",
        "public-fact",
        "high",
        "Fake GTA VI demo and PC download sites delivered infostealer malware; no legitimate demo or PC build exists.",
        "Confirms active GTA VI impersonation campaigns.",
    ),
    _source(
        "sony-psn-2011",
        "PSN outage will cost Sony $171.1 million",
        "GameSpot",
        "https://gamespot.com/articles/psn-outage-will-cost-sony-1711-million-earthquake-bill-18-billion/1100-6315079/",
        "2011-05",
        "public-fact",
        "high",
        "Sony estimated $171.1 million in costs for the 23-day 2011 PSN breach and outage, including 'Welcome Back' compensation.",
        "Extreme upper reference for outage make-goods and reputational loss.",
    ),
    _source(
        "bls-infosec",
        "Occupational Outlook Handbook: Information Security Analysts",
        "U.S. Bureau of Labor Statistics",
        "https://www.bls.gov/ooh/computer-and-information-technology/information-security-analysts.htm",
        "2025",
        "public-fact",
        "high",
        "Median pay $124,910 per year ($60.05 per hour) in May 2024.",
        "Labor-rate basis for response costs and control labor.",
    ),
    _source(
        "cisa-pr-mfa",
        "Implementing Phishing-Resistant MFA (fact sheet)",
        "CISA",
        "https://www.cisa.gov/sites/default/files/publications/fact-sheet-implementing-phishing-resistant-mfa-508c.pdf",
        "2022-10",
        "public-fact",
        "high",
        "FIDO/WebAuthn authentication is the widely available phishing-resistant MFA and resists MFA-fatigue and credential phishing.",
        "Supports the phishing-resistant MFA control effect.",
    ),
    _source(
        "nist-csf-2",
        "NIST Cybersecurity Framework (CSF) 2.0",
        "NIST",
        "https://nvlpubs.nist.gov/nistpubs/CSWP/NIST.CSWP.29.pdf",
        "2024-02-26",
        "public-fact",
        "high",
        "Organizes outcomes across Govern, Identify, Protect, Detect, Respond, and Recover.",
        "Control-to-outcome mapping.",
    ),
    _source(
        "fair-institute",
        "What is FAIR? (Factor Analysis of Information Risk)",
        "FAIR Institute",
        "https://www.fairinstitute.org/what-is-fair",
        "2025",
        "model-assumption",
        "high",
        "FAIR decomposes risk into loss event frequency and loss magnitude.",
        "Methodology reference; this project is FAIR-style, not a full FAIR ontology implementation.",
    ),
    _source(
        "stride-msft",
        "Microsoft Threat Modeling Tool threats (STRIDE)",
        "Microsoft Learn",
        "https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool-threats",
        "2022",
        "public-fact",
        "high",
        "Defines the STRIDE categories used for threat classification.",
        "STRIDE tags on attack steps.",
    ),
    _source("mitre-t1595", "MITRE ATT&CK: Active Scanning (T1595)", "MITRE", "https://attack.mitre.org/techniques/T1595/", "2025", "public-fact", "high", "Technique definition.", "Attack-step mapping."),
    _source("mitre-t1583", "MITRE ATT&CK: Acquire Infrastructure: Botnet (T1583.005)", "MITRE", "https://attack.mitre.org/techniques/T1583/005/", "2025", "public-fact", "high", "Technique definition.", "Attack-step mapping."),
    _source("mitre-t1498", "MITRE ATT&CK: Network Denial of Service (T1498)", "MITRE", "https://attack.mitre.org/techniques/T1498/", "2025", "public-fact", "high", "Technique definition.", "Attack-step mapping."),
    _source("mitre-t1499", "MITRE ATT&CK: Endpoint Denial of Service (T1499)", "MITRE", "https://attack.mitre.org/techniques/T1499/", "2025", "public-fact", "high", "Technique definition, including T1499.002 Service Exhaustion Flood and T1499.003 Application Exhaustion Flood.", "Attack-step mapping."),
    _source("mitre-t1566", "MITRE ATT&CK: Phishing (T1566)", "MITRE", "https://attack.mitre.org/techniques/T1566/", "2025", "public-fact", "high", "Technique definition.", "Attack-step mapping."),
    _source("mitre-t1621", "MITRE ATT&CK: Multi-Factor Authentication Request Generation (T1621)", "MITRE", "https://attack.mitre.org/techniques/T1621/", "2025", "public-fact", "high", "Technique definition.", "Attack-step mapping."),
    _source("mitre-t1078", "MITRE ATT&CK: Valid Accounts (T1078)", "MITRE", "https://attack.mitre.org/techniques/T1078/", "2025", "public-fact", "high", "Technique definition.", "Attack-step mapping."),
    _source("mitre-t1213", "MITRE ATT&CK: Data from Information Repositories (T1213)", "MITRE", "https://attack.mitre.org/techniques/T1213/", "2025", "public-fact", "high", "Technique definition.", "Attack-step mapping."),
    _source("mitre-t1567", "MITRE ATT&CK: Exfiltration Over Web Service (T1567)", "MITRE", "https://attack.mitre.org/techniques/T1567/", "2025", "public-fact", "high", "Technique definition.", "Attack-step mapping."),
    _source("mitre-t1608", "MITRE ATT&CK: Stage Capabilities: SEO Poisoning (T1608.006)", "MITRE", "https://attack.mitre.org/techniques/T1608/006/", "2025", "public-fact", "high", "Technique definition.", "Attack-step mapping."),
    _source("mitre-t1204", "MITRE ATT&CK: User Execution: Malicious File (T1204.002)", "MITRE", "https://attack.mitre.org/techniques/T1204/002/", "2025", "public-fact", "high", "Technique definition.", "Attack-step mapping."),
]


METHODOLOGY = {
    "name": "Team FAIR-style Monte Carlo model",
    "version": MODEL_VERSION,
    "description": (
        "Each scenario combines event frequency, conditional success, and component-level primary and "
        "secondary loss. Launch-Day DDoS is measured per seven-day launch event; the other three scenarios are annual."
    ),
    "formula": "Loss = material loss events x (primary loss + secondary-effect indicator x secondary loss)",
    "sampling": (
        f"Triangular low / most-likely / high inputs; {MODEL_TRIALS:,} trials with fixed seed {MODEL_SEED}. "
        "Annual event counts use a Poisson draw on threat event frequency, thinned by conditional success."
    ),
    "controlRule": (
        "Each control multiplies only the factors it genuinely influences by (1 - effectiveness); effectiveness is "
        "sampled from its low / likely / high range and stacks multiplicatively. Baseline and residual runs share "
        "the same random draws, so differences come only from controls."
    ),
    "costRule": (
        "Launch event view charges the full first-year cost (one-time + annual + per-launch) to the launch event, a conservative choice. "
        "Annual view uses annual cost + one-time cost amortized over 3 years + per-launch cost x 1 launch per year."
    ),
    "disclaimer": (
        "This is a team-designed FAIR-style model for decision support, not an official Open FAIR, NIST, or MITRE assessment. "
        "It makes no claim about Take-Two's private controls or architecture."
    ),
    "sourceIds": ["fair-institute", "nist-csf-2"],
    "timing": (
        "Inputs are an ex-ante estimate for the Nov 19-25, 2026 launch window. Launch-week observations (Rockstar services held; "
        "PSN disruptions on Nov 18-19) are used as calibration evidence. The same structure applies to the later GTA VI online and PC launches."
    ),
}


CRITICAL_ASSETS = [
    {
        "id": "launch-services",
        "name": "Launch online services and storefront dependencies",
        "description": "Rockstar account sign-in, launcher and store APIs, DNS and CDN, entitlement checks, and the PlayStation and Xbox storefronts the launch depends on.",
    },
    {
        "id": "builds-source",
        "name": "Unreleased builds, source code, and development pipeline",
        "description": "Repositories, build systems, development footage, and collaboration tools used by about 10,000 product-development staff.",
    },
    {
        "id": "player-accounts",
        "name": "Player accounts and personal data",
        "description": "Rockstar accounts, linked platform identities, purchase history, and support records.",
    },
    {
        "id": "brand-channels",
        "name": "Brand, official channels, and player trust",
        "description": "Official websites, social channels, and the reputation that drives launch and recurrent spending.",
    },
    {
        "id": "workforce-access",
        "name": "Workforce and third-party access",
        "description": "Employee, contractor, and vendor identities, plus support and collaboration platforms with access to sensitive data.",
    },
]


WATCHLIST = [
    "Account takeover and credential stuffing",
    "Ransomware and extortion",
    "Cloud or critical third-party outage",
    "Payment fraud and refund abuse",
    "Software supply-chain compromise",
    "API abuse and cheating infrastructure",
    "Customer-data breach",
    "Destructive attacks against development or production systems",
]


# ---------------------------------------------------------------------------
# Scenario inputs
# ---------------------------------------------------------------------------

def _inp(key, label, group, low, mode, high, unit, evidence, sources, rationale, confidence, relationship,
         owner="Member 3", reviewer="Member 2"):
    return {
        "key": key,
        "label": label,
        "group": group,
        "low": low,
        "mode": mode,
        "high": high,
        "unit": unit,
        "distribution": "triangular",
        "evidenceType": evidence,
        "evidenceClass": EVIDENCE_CLASSES[evidence],
        "sourceIds": sources,
        "rationale": rationale,
        "confidence": confidence,
        "controlRelationship": relationship,
        "owner": owner,
        "reviewer": reviewer,
    }


DDOS_INPUTS = [
    _inp(
        "attackProbability", "Probability of a material DDoS attempt", "frequency",
        0.50, 0.80, 0.95, "probability per launch window", "team-estimate",
        ["overwatch2-ddos", "cloudflare-ddos-2025q3", "sensor-tower-gta6"],
        "GTA VI is the highest-profile launch on record and gaming is among the most-attacked industries. "
        "Overwatch 2 was hit by two DDoS attacks on launch day. Attack attempts are treated as likely, not certain.",
        "medium", "Not reduced by defensive controls: attackers still try.",
    ),
    _inp(
        "conditionalSuccess", "Conditional success (material degradation)", "vulnerability",
        0.10, 0.25, 0.45, "probability given an attempt", "team-estimate",
        ["gta6-launch-psn", "overwatch2-ddos"],
        "Rockstar's launch infrastructure held under record legitimate demand, which suggests real baseline capacity, "
        "but a mature operator (Blizzard) was still degraded. Material = players unable to sign in, download, or buy for at least one hour.",
        "low", "Reduced by managed DDoS protection, application-abuse protection, and resilience testing.",
    ),
    _inp(
        "outageHours", "Material degradation duration", "duration",
        2, 8, 36, "hours per material outage", "team-estimate",
        ["overwatch2-ddos", "cloudflare-ddos-2026h1", "gta6-launch-psn"],
        "Most attacks are short, but impact outlasts the flood. Overwatch 2 problems persisted more than a day; "
        "the Nov 18 PSN disruption lasted minutes to hours.",
        "low", "Reduced by managed protection, failover architecture, war room, testing, and IR readiness.",
    ),
    _inp(
        "hourlyRevenueAtRisk", "Launch revenue at risk per hour", "primary-driver",
        4_000_000, 8_000_000, 16_000_000, "USD per hour", "derived-value",
        ["sensor-tower-gta6", "newzoo-gta6-forecast", "gta5-launch-1b"],
        "Sensor Tower estimates rose from about $1.65B (noon Nov 18) to $1.84B (release day): roughly $190M in ~24 hours, "
        "or ~$8M per hour of new sales. Newzoo's higher launch-week forecast sets the upper bound.",
        "medium", "Not changed by controls (it is demand, not exposure).",
    ),
    _inp(
        "lostRevenueFraction", "Share of at-risk revenue permanently lost", "primary-driver",
        0.02, 0.08, 0.20, "fraction of hourly revenue", "team-estimate",
        ["gta5-launch-1b"],
        "Most buyers retry after an outage, so most revenue is delayed rather than lost. Losses come from abandoned purchases, "
        "refund-driven cancellations, and holiday buyers who switch titles.",
        "low", "Reduced by resilient architecture (virtual queue and graceful degradation keep buyers in line).",
    ),
    _inp(
        "responseCost", "Incident response and provider escalation", "primary",
        400_000, 1_200_000, 3_500_000, "USD per material outage", "derived-value",
        ["bls-infosec", "ibm-codb-2025"],
        "About 150 engineers and responders for ~72 hours at a $100-$150 loaded hourly rate (BLS median $60/hour before overhead), "
        "plus emergency vendor services.",
        "medium", "Reduced by IR retainer and exercises, and by the launch war room.",
    ),
    _inp(
        "emergencyInfrastructure", "Emergency infrastructure and scrubbing", "primary",
        200_000, 1_000_000, 4_000_000, "USD per material outage", "team-estimate",
        ["aws-shield-pricing"],
        "On-demand scrubbing, surge cloud capacity, and attack-traffic egress. Public pricing shows these costs scale with traffic volume.",
        "low", "Reduced by managed DDoS protection (contracted capacity and cost protection).",
    ),
    _inp(
        "refundsMakeGoods", "Refunds, credits, and make-good offers", "primary",
        1_000_000, 6_000_000, 30_000_000, "USD per material outage", "team-estimate",
        ["sony-psn-2011", "overwatch2-ddos"],
        "Platforms and publishers typically compensate players after launch outages. Sony's far larger 23-day 2011 outage "
        "cost $171M including compensation, which caps the plausible range well above this one.",
        "low", "Reduced by resilient architecture (shorter, partial outages).",
    ),
    _inp(
        "supportSurge", "Player support surge", "primary",
        300_000, 1_500_000, 5_000_000, "USD per material outage", "team-estimate",
        ["sensor-tower-gta6"],
        "With about 19 million launch-day players, even 1-3% contacting support at a few dollars per contact produces a seven-figure cost.",
        "low", "Reduced by the launch war room (proactive status updates).",
    ),
    _inp(
        "secondaryProbability", "Probability of secondary effects", "secondary-probability",
        0.25, 0.45, 0.70, "probability given a material outage", "team-estimate",
        ["overwatch2-ddos", "sony-psn-2011"],
        "Not every outage produces lasting reputational or partner effects; longer and more visible outages do.",
        "low", "Reduced by the launch war room (clear communications).",
    ),
    _inp(
        "reputationLoss", "Reputational and future-demand loss", "secondary",
        3_000_000, 20_000_000, 90_000_000, "USD per material outage", "team-estimate",
        ["sony-psn-2011"],
        "Lost future recurrent spending and slower attach to later online content. Bounded below Sony's 2011 total because "
        "a DDoS outage is shorter and exposes no personal data.",
        "low", "Indirectly reduced via the secondary-effect probability.",
    ),
    _inp(
        "partnerLegal", "Partner, platform, and consumer-complaint effects", "secondary",
        200_000, 2_000_000, 10_000_000, "USD per material outage", "team-estimate",
        ["ttwo-10k-fy2026"],
        "Platform-partner and retail commitments plus consumer complaints. The 10-K notes heavy dependence on platform providers.",
        "low", "Indirectly reduced via the secondary-effect probability.",
    ),
]


BUILD_THEFT_INPUTS = [
    _inp(
        "threatEventFrequency", "Targeted intrusion attempts reaching a foothold", "frequency",
        0.5, 1.2, 3.0, "events per year", "team-estimate",
        ["ttwo-10k-fy2026", "peer-code-theft", "kurtaj-plea-2026"],
        "Rockstar (2022), EA (2021), CD Projekt Red (2021), and Riot (2023) show sustained targeting of AAA studios through "
        "social engineering and stolen credentials. The 10-K also describes a 2022 vendor help-desk compromise.",
        "low", "Reduced by vendor access governance (fewer third-party entry points).",
    ),
    _inp(
        "conditionalSuccess", "Conditional success (material code or build exfiltration)", "vulnerability",
        0.05, 0.12, 0.25, "probability given an attempt", "team-estimate",
        ["peer-code-theft", "rockstar-hack-cost"],
        "Implies about 0.2 successful thefts per year (one every ~5 years), consistent with one confirmed Rockstar incident "
        "and a peer base rate of roughly 0.1-0.2 per large publisher-year.",
        "low", "Reduced by phishing-resistant MFA, build access and PAM, and insider-risk monitoring.",
    ),
    _inp(
        "investigationRecovery", "Forensics, investigation, and recovery", "primary",
        1_500_000, 4_000_000, 9_000_000, "USD per event", "derived-value",
        ["rockstar-hack-cost"],
        "Rockstar told a UK court the 2022 intrusion cost about $5M to recover from, excluding staff time.",
        "medium", "Reduced by the IR retainer and exercises.",
    ),
    _inp(
        "staffDisruption", "Staff time and schedule disruption", "primary",
        500_000, 1_500_000, 6_000_000, "USD per event", "derived-value",
        ["rockstar-hack-cost", "ttwo-10k-fy2026", "bls-infosec"],
        "'Thousands of hours of staff time' at $100-$150 loaded rates, plus schedule disruption across ~10,000 product-development staff.",
        "medium", "Not directly reduced by modeled controls.",
    ),
    _inp(
        "legalLawEnforcement", "Legal and law-enforcement support", "primary",
        200_000, 1_000_000, 4_000_000, "USD per event", "team-estimate",
        ["kurtaj-plea-2026"],
        "Outside counsel, prosecution support, and takedown requests over a multi-year case.",
        "low", "Not directly reduced by modeled controls.",
    ),
    _inp(
        "securityRebuild", "Credential resets and pipeline rebuild", "primary",
        300_000, 1_000_000, 4_000_000, "USD per event", "team-estimate",
        ["ttwo-10k-fy2026"],
        "Rotating secrets, re-imaging build systems, and emergency hardening after compromise.",
        "low", "Not directly reduced by modeled controls.",
    ),
    _inp(
        "secondaryProbability", "Probability of public leak or extortion effects", "secondary-probability",
        0.30, 0.50, 0.75, "probability given an event", "team-estimate",
        ["kurtaj-plea-2026", "peer-code-theft"],
        "Extortion groups often publish when unpaid (Rockstar 2022 clips; CD Projekt Red code auctions).",
        "medium", "Reduced by the IR retainer and exercises.",
    ),
    _inp(
        "marketingDisruption", "Marketing and reveal-value disruption", "secondary",
        2_000_000, 10_000_000, 50_000_000, "USD per event", "team-estimate",
        ["rockstar-hack-cost", "kurtaj-plea-2026"],
        "Loss of a controlled reveal. Kept moderate because the GTA VI trailer still broke records after the 2022 leak.",
        "low", "Indirectly reduced via the secondary-effect probability.",
    ),
    _inp(
        "competitiveIPLoss", "Competitive, cheating, and piracy exposure", "secondary",
        1_000_000, 5_000_000, 30_000_000, "USD per event", "team-estimate",
        ["peer-code-theft"],
        "Riot warned that exposed source code raises the likelihood of new cheats; stolen engine code can aid piracy and competitors.",
        "low", "Reduced by build access and PAM (segmentation limits what can be taken).",
    ),
]


INSIDER_INPUTS = [
    _inp(
        "threatEventFrequency", "Insider disclosure incidents with material potential", "frequency",
        1.0, 3.0, 6.0, "events per year", "team-estimate",
        ["ponemon-insider-2025", "ttwo-10k-fy2026", "rockstar-firings-2025"],
        "Ponemon reports frequent insider events per organization each year; this counts only the material subset across "
        "12,909 employees plus contractors. Rockstar's 2025 leak allegation is contested and used only as context.",
        "low", "Reduced by vendor access governance (contractor offboarding and access review).",
    ),
    _inp(
        "conditionalSuccess", "Conditional success (leak becomes public or harmful)", "vulnerability",
        0.08, 0.18, 0.35, "probability given an incident", "team-estimate",
        ["ponemon-insider-2025"],
        "Most incidents are contained internally; a minority reach the public or a competitor.",
        "low", "Reduced by insider-risk monitoring, build access and PAM, and phishing-resistant MFA.",
    ),
    _inp(
        "investigationLegal", "Investigation, HR, and legal response", "primary",
        300_000, 800_000, 2_500_000, "USD per event", "derived-value",
        ["ponemon-insider-2025", "ibm-codb-2025-vectors"],
        "Ponemon averages $3.7M per malicious insider incident and IBM $4.92M per malicious insider breach; this is the investigation share.",
        "medium", "Reduced by the IR retainer and exercises.",
    ),
    _inp(
        "containmentTakedown", "Containment and content takedown", "primary",
        100_000, 300_000, 1_000_000, "USD per event", "team-estimate",
        ["ponemon-insider-2025"],
        "Takedown requests, platform reports, and access revocation.",
        "low", "Reduced by the IR retainer and exercises.",
    ),
    _inp(
        "dataNotification", "Player-data notification (if data involved)", "primary",
        0, 200_000, 3_000_000, "USD per event", "derived-value",
        ["ibm-codb-2025"],
        "Most leaks involve product content, not personal data; IBM puts average notification near $390K, with a long tail in the U.S.",
        "low", "Not directly reduced by modeled controls.",
    ),
    _inp(
        "businessDisruption", "Business and marketing-plan disruption", "primary",
        300_000, 1_500_000, 6_000_000, "USD per event", "team-estimate",
        ["rockstar-firings-2025"],
        "Rework of marketing beats and internal disruption after a leak.",
        "low", "Not directly reduced by modeled controls.",
    ),
    _inp(
        "secondaryProbability", "Probability of secondary effects", "secondary-probability",
        0.25, 0.40, 0.60, "probability given an event", "team-estimate",
        ["ponemon-insider-2025"],
        "Lasting reputational or legal effects follow only some leaks.",
        "low", "Reduced by insider-risk monitoring (fast attribution through watermarking).",
    ),
    _inp(
        "reputationMarketing", "Reputational and marketing-value loss", "secondary",
        500_000, 4_000_000, 25_000_000, "USD per event", "team-estimate",
        ["rockstar-firings-2025"],
        "Loss of controlled reveals and player trust; higher for unannounced titles.",
        "low", "Indirectly reduced via the secondary-effect probability.",
    ),
    _inp(
        "regulatoryLegal", "Regulatory and litigation follow-on", "secondary",
        200_000, 1_000_000, 8_000_000, "USD per event", "team-estimate",
        ["rockstar-firings-2025", "ibm-codb-2025"],
        "Employment litigation or privacy regulators can follow an insider case; the 2025 dismissals led to tribunal claims.",
        "low", "Indirectly reduced via the secondary-effect probability.",
    ),
]


PHISHING_INPUTS = [
    _inp(
        "threatEventFrequency", "Impersonation campaigns requiring a response", "frequency",
        4.0, 10.0, 20.0, "campaigns per year", "team-estimate",
        ["kaspersky-gaming-2025", "malwarebytes-gta6-demo", "ttwo-10k-fy2026"],
        "GTA is among the most abused game brands for malware lures, fake GTA VI demos and PC builds circulated through 2026, "
        "and the 10-K reports a compromised vendor help desk used to message players.",
        "medium", "Reduced by vendor access governance (secure support tooling).",
    ),
    _inp(
        "conditionalSuccess", "Conditional success (material player or workforce harm)", "vulnerability",
        0.05, 0.12, 0.25, "probability given a campaign", "team-estimate",
        ["kaspersky-gaming-2025"],
        "Most campaigns are taken down or ignored; a minority cause account takeovers or fraud that Take-Two must absorb.",
        "low", "Reduced by brand protection, application-abuse protection (bot defense), and phishing-resistant MFA.",
    ),
    _inp(
        "takedownInvestigation", "Takedown and investigation", "primary",
        50_000, 200_000, 600_000, "USD per event", "team-estimate",
        ["malwarebytes-gta6-demo"],
        "Registrar and host takedowns, malware analysis, and coordination.",
        "low", "Reduced by the IR retainer and exercises.",
    ),
    _inp(
        "supportAccountRecovery", "Support and account recovery", "primary",
        100_000, 600_000, 2_500_000, "USD per event", "team-estimate",
        ["kaspersky-gaming-2025"],
        "Account-recovery tickets and support for affected players.",
        "low", "Reduced by brand protection (fewer victims reach support).",
    ),
    _inp(
        "fraudChargebacks", "Fraud and chargebacks absorbed", "primary",
        50_000, 300_000, 2_000_000, "USD per event", "team-estimate",
        ["ttwo-10k-fy2026"],
        "Fraudulent purchases on taken-over accounts and chargebacks.",
        "low", "Not directly reduced by modeled controls.",
    ),
    _inp(
        "secondaryProbability", "Probability of secondary effects", "secondary-probability",
        0.15, 0.30, 0.50, "probability given an event", "team-estimate",
        ["ibm-codb-2025-vectors"],
        "Brand or regulatory follow-on effects occur only for larger campaigns.",
        "low", "Reduced by brand protection (official advisories).",
    ),
    _inp(
        "brandRegulatory", "Brand-trust and regulatory effects", "secondary",
        500_000, 3_000_000, 20_000_000, "USD per event", "derived-value",
        ["ibm-codb-2025-vectors"],
        "Sized so the average total per material event lands near IBM's $4.8M phishing-breach average.",
        "low", "Indirectly reduced via the secondary-effect probability.",
    ),
]


SCENARIOS = [
    {
        "id": "launch-ddos",
        "name": "Launch-Day DDoS",
        "severity": "Critical",
        "depth": "detailed",
        "summary": "A coordinated traffic flood degrades sign-in, downloads, and purchases during the GTA VI launch window.",
        "lossEventStatement": (
            "During the seven-day GTA VI launch window, an external actor (botnet-for-hire operator, hacktivist, or extortion group) "
            "floods Rockstar-operated services or a launch-critical dependency, leaving players unable to sign in, download, or buy for "
            "at least one hour. Losses: response, emergency infrastructure, lost sales, refunds and make-goods, support, and secondary "
            "reputational and partner effects."
        ),
        "timeBasis": "launch-event",
        "assetIds": ["launch-services", "brand-channels", "player-accounts"],
        "mitre": ["T1595", "T1583.005", "T1498", "T1499.002", "T1499.003"],
        "stride": ["Denial of Service", "Spoofing", "Information Disclosure"],
        "recommendedControlIds": ["managed-ddos-protection", "app-abuse-protection", "launch-resilience-testing", "launch-war-room"],
        "thresholds": [10_000_000, 25_000_000, 50_000_000, 100_000_000],
        "model": {
            "type": "launch-event",
            "frequencyKey": "attackProbability",
            "successKey": "conditionalSuccess",
            "interruptionKeys": ["outageHours", "hourlyRevenueAtRisk", "lostRevenueFraction"],
            "primaryKeys": ["responseCost", "emergencyInfrastructure", "refundsMakeGoods", "supportSurge"],
            "secondaryProbabilityKey": "secondaryProbability",
            "secondaryKeys": ["reputationLoss", "partnerLegal"],
        },
        "inputs": DDOS_INPUTS,
    },
    {
        "id": "source-code-theft",
        "name": "Build & Source Code Theft",
        "severity": "High",
        "depth": "comparison",
        "summary": "Social engineering or stolen credentials expose unreleased builds, footage, and source code.",
        "lossEventStatement": (
            "An external extortion group compromises an employee, contractor, or collaboration tool through social engineering or stolen "
            "credentials and exfiltrates unreleased builds, development footage, or source code, followed by public leak or extortion. "
            "Measured as expected annual loss."
        ),
        "timeBasis": "annual",
        "assetIds": ["builds-source", "workforce-access", "brand-channels"],
        "mitre": ["T1566", "T1621", "T1078", "T1213", "T1567"],
        "stride": ["Spoofing", "Elevation of Privilege", "Information Disclosure"],
        "recommendedControlIds": ["phishing-resistant-mfa", "build-access-pam"],
        "thresholds": [10_000_000, 25_000_000, 50_000_000, 100_000_000],
        "model": {
            "type": "annual",
            "frequencyKey": "threatEventFrequency",
            "successKey": "conditionalSuccess",
            "interruptionKeys": [],
            "primaryKeys": ["investigationRecovery", "staffDisruption", "legalLawEnforcement", "securityRebuild"],
            "secondaryProbabilityKey": "secondaryProbability",
            "secondaryKeys": ["marketingDisruption", "competitiveIPLoss"],
        },
        "inputs": BUILD_THEFT_INPUTS,
    },
    {
        "id": "insider-leak",
        "name": "Insider or Contractor Leak",
        "severity": "High",
        "depth": "summary",
        "summary": "A trusted employee, contractor, or vendor discloses unreleased content or player data.",
        "lossEventStatement": (
            "An employee, contractor, or vendor staff member with legitimate access discloses unreleased content, confidential plans, "
            "or player data, intentionally or negligently, through public forums, social media, or unauthorized transfer. Measured as expected annual loss."
        ),
        "timeBasis": "annual",
        "assetIds": ["builds-source", "player-accounts", "workforce-access"],
        "mitre": ["T1078", "T1213", "T1567"],
        "stride": ["Information Disclosure", "Repudiation"],
        "recommendedControlIds": ["insider-risk-monitoring", "vendor-access-governance"],
        "thresholds": [10_000_000, 25_000_000, 50_000_000],
        "model": {
            "type": "annual",
            "frequencyKey": "threatEventFrequency",
            "successKey": "conditionalSuccess",
            "interruptionKeys": [],
            "primaryKeys": ["investigationLegal", "containmentTakedown", "dataNotification", "businessDisruption"],
            "secondaryProbabilityKey": "secondaryProbability",
            "secondaryKeys": ["reputationMarketing", "regulatoryLegal"],
        },
        "inputs": INSIDER_INPUTS,
    },
    {
        "id": "fake-downloads",
        "name": "Fake Downloads & Phishing",
        "severity": "Medium",
        "depth": "summary",
        "summary": "Fake GTA VI downloads, demos, and phishing sites steal player and workforce credentials.",
        "lossEventStatement": (
            "Criminals impersonate Rockstar or GTA VI (fake PC downloads, demos, giveaways, phishing sites, or a compromised vendor "
            "support channel) to deliver infostealers or harvest credentials, causing account takeovers, fraud, support and takedown "
            "costs, and brand harm that Take-Two absorbs. Measured as expected annual loss."
        ),
        "timeBasis": "annual",
        "assetIds": ["player-accounts", "brand-channels", "workforce-access"],
        "mitre": ["T1608.006", "T1204.002", "T1566"],
        "stride": ["Spoofing", "Information Disclosure"],
        "recommendedControlIds": ["brand-protection", "app-abuse-protection"],
        "thresholds": [5_000_000, 10_000_000, 25_000_000, 50_000_000],
        "model": {
            "type": "annual",
            "frequencyKey": "threatEventFrequency",
            "successKey": "conditionalSuccess",
            "interruptionKeys": [],
            "primaryKeys": ["takedownInvestigation", "supportAccountRecovery", "fraudChargebacks"],
            "secondaryProbabilityKey": "secondaryProbability",
            "secondaryKeys": ["brandRegulatory"],
        },
        "inputs": PHISHING_INPUTS,
    },
]

for _scenario in SCENARIOS:
    _scenario["timeBasisLabel"] = TIME_BASES[_scenario["timeBasis"]]["label"]
    _scenario["modelStatus"] = "implemented"
    # Backward-compatible dictionary view keyed by input name.
    _scenario["assumptions"] = {item["key"]: item for item in _scenario["inputs"]}


# ---------------------------------------------------------------------------
# Controls
# ---------------------------------------------------------------------------

def _eff(low, likely, high):
    return {"low": low, "likely": likely, "high": high}


CONTROLS = [
    {
        "id": "managed-ddos-protection",
        "shortName": "Managed DDoS protection",
        "name": "Managed DDoS protection and upstream scrubbing",
        "group": "Launch traffic protection",
        "category": "Protect",
        "problem": "Volumetric floods can saturate links and origin capacity before in-house teams can react.",
        "description": "Always-on scrubbing with CDN or Anycast distribution, contracted surge capacity, and provider filtering.",
        "nist": ["PR.IR-04", "DE.CM-01", "RS.MI-01"],
        "nistFunctions": ["Protect", "Detect", "Respond"],
        "mitre": ["T1498"],
        "cost": {"basis": "annual", "low": 800_000, "likely": 1_500_000, "high": 3_000_000},
        "implementationWeeks": {"low": 2, "mode": 4, "high": 8},
        "owner": "Infrastructure and SRE lead",
        "dependencies": [],
        "confidence": "high",
        "evidenceIds": ["cloudflare-ddos-2026h1", "aws-shield-pricing", "overwatch2-ddos"],
        "rationale": "Always-on protection addresses the dominant failure mode. The public AWS price is a floor; an enterprise CDN contract for a top publisher is a team estimate.",
        "effects": {
            "launch-ddos": {
                "conditionalSuccess": _eff(0.40, 0.55, 0.70),
                "outageHours": _eff(0.15, 0.30, 0.45),
                "emergencyInfrastructure": _eff(0.30, 0.50, 0.70),
            },
        },
        "attackSteps": {"launch-ddos": ["infrastructure-prepared", "network-flood", "service-degradation"]},
        "readiness": [
            {"component": "ddosProtection", "level": 0.5},
            {"component": "ddosProtection", "level": 1.0, "requires": ["launch-resilience-testing"]},
        ],
    },
    {
        "id": "app-abuse-protection",
        "shortName": "WAF, bots, rate limiting",
        "name": "WAF, bot management, and adaptive rate limiting",
        "group": "Application abuse protection",
        "category": "Protect",
        "problem": "Application-layer floods exhaust login, store, and API capacity while blending in with real launch traffic.",
        "description": "WAF rules, bot management, adaptive rate limits, caching, queues, and circuit breakers on login, store, and API paths.",
        "nist": ["PR.IR-03", "PR.PS-01", "DE.CM-01"],
        "nistFunctions": ["Protect", "Detect"],
        "mitre": ["T1499.002", "T1499.003"],
        "cost": {"basis": "annual", "low": 400_000, "likely": 800_000, "high": 1_500_000},
        "implementationWeeks": {"low": 2, "mode": 4, "high": 6},
        "owner": "Platform engineering lead",
        "dependencies": ["managed-ddos-protection"],
        "confidence": "medium",
        "evidenceIds": ["mitre-t1499", "cloudflare-ddos-2026h1"],
        "rationale": "Targets application exhaustion that volumetric scrubbing alone misses; bot defense also blunts credential stuffing with stolen player credentials.",
        "effects": {
            "launch-ddos": {
                "conditionalSuccess": _eff(0.20, 0.35, 0.50),
                "outageHours": _eff(0.05, 0.10, 0.20),
            },
            "fake-downloads": {
                "conditionalSuccess": _eff(0.05, 0.15, 0.25),
            },
        },
        "attackSteps": {"launch-ddos": ["recon", "service-exhaustion"], "fake-downloads": ["credential-abuse"]},
        "readiness": [
            {"component": "ddosProtection", "level": 0.5},
            {"component": "ddosProtection", "level": 1.0, "requires": ["launch-resilience-testing", "managed-ddos-protection"]},
        ],
    },
    {
        "id": "resilient-architecture",
        "shortName": "Resilient architecture",
        "name": "Capacity reservation, service isolation, and multi-region failover",
        "group": "Resilient architecture",
        "category": "Recover",
        "problem": "Shared dependencies fail together when malicious and legitimate demand combine.",
        "description": "Reserved launch capacity, autoscaling, service isolation, graceful degradation, a virtual queue, and multi-region failover.",
        "nist": ["PR.IR-03", "PR.IR-04", "RC.RP-01"],
        "nistFunctions": ["Protect", "Recover"],
        "mitre": ["T1498", "T1499"],
        "cost": {"basis": "one-time", "low": 1_500_000, "likely": 3_000_000, "high": 6_000_000},
        "implementationWeeks": {"low": 6, "mode": 10, "high": 16},
        "owner": "Chief architect",
        "dependencies": [],
        "confidence": "medium",
        "evidenceIds": ["gta6-launch-psn", "overwatch2-ddos"],
        "rationale": "Cuts outage duration and keeps buyers in a queue instead of losing them. It reduces impact, not attack probability.",
        "effects": {
            "launch-ddos": {
                "outageHours": _eff(0.25, 0.40, 0.55),
                "lostRevenueFraction": _eff(0.10, 0.20, 0.30),
                "refundsMakeGoods": _eff(0.10, 0.20, 0.30),
            },
        },
        "attackSteps": {"launch-ddos": ["service-degradation", "business-loss"]},
        "readiness": [
            {"component": "failoverRecovery", "level": 0.5},
            {"component": "failoverRecovery", "level": 1.0, "requires": ["launch-resilience-testing"]},
        ],
    },
    {
        "id": "launch-resilience-testing",
        "shortName": "Resilience testing",
        "name": "Load, stress, DDoS-simulation, and failover testing",
        "group": "Validation and exercises",
        "category": "Identify",
        "problem": "Untested protections and failover paths fail under real launch pressure.",
        "description": "Pre-launch load and stress tests, DDoS simulation with the provider, and failover and recovery drills.",
        "nist": ["ID.IM-02", "ID.RA-01", "PR.IR-04"],
        "nistFunctions": ["Identify", "Protect"],
        "mitre": ["T1498", "T1499"],
        "cost": {"basis": "per-launch", "low": 250_000, "likely": 500_000, "high": 1_000_000},
        "implementationWeeks": {"low": 2, "mode": 3, "high": 5},
        "owner": "Launch readiness lead",
        "dependencies": [],
        "confidence": "medium",
        "evidenceIds": ["gta6-launch-psn", "cloudflare-ddos-2026h1"],
        "rationale": "Prerequisite: it turns protection and failover from 'implemented' into 'implemented and tested' in the readiness index and finds weak points before attackers do.",
        "prerequisite": True,
        "effects": {
            "launch-ddos": {
                "conditionalSuccess": _eff(0.10, 0.20, 0.30),
                "outageHours": _eff(0.05, 0.15, 0.25),
            },
        },
        "attackSteps": {"launch-ddos": ["recon", "service-exhaustion", "service-degradation"]},
        "readiness": [{"component": "loadTesting", "level": 1.0}],
    },
    {
        "id": "launch-war-room",
        "shortName": "Launch war room",
        "name": "Traffic monitoring, launch war room, and escalation runbook",
        "group": "Monitoring and response",
        "category": "Detect & respond",
        "problem": "Slow detection and unclear escalation stretch a short flood into a long outage and a support surge.",
        "description": "24/7 launch war room, traffic anomaly monitoring, provider and platform escalation contacts, and player status communications.",
        "nist": ["DE.CM-01", "DE.AE-02", "RS.MA-01", "RS.CO-03"],
        "nistFunctions": ["Detect", "Respond"],
        "mitre": ["T1498", "T1499"],
        "cost": {"basis": "per-launch", "low": 300_000, "likely": 600_000, "high": 1_000_000},
        "implementationWeeks": {"low": 1, "mode": 3, "high": 5},
        "owner": "Security operations lead",
        "dependencies": [],
        "confidence": "medium",
        "evidenceIds": ["overwatch2-ddos", "bls-infosec"],
        "rationale": "Shortens time to mitigate and keeps players informed, which cuts support demand and secondary effects.",
        "effects": {
            "launch-ddos": {
                "outageHours": _eff(0.15, 0.25, 0.35),
                "responseCost": _eff(0.05, 0.10, 0.20),
                "supportSurge": _eff(0.10, 0.20, 0.30),
                "secondaryProbability": _eff(0.10, 0.20, 0.30),
            },
        },
        "attackSteps": {"launch-ddos": ["infrastructure-prepared", "detect-respond", "business-loss"]},
        "readiness": [
            {"component": "monitoringComms", "level": 0.5},
            {"component": "monitoringComms", "level": 1.0, "requires": ["launch-resilience-testing"]},
            {"component": "incidentResponse", "level": 0.5},
        ],
    },
    {
        "id": "ir-retainer-exercises",
        "shortName": "IR retainer and exercises",
        "name": "Incident response retainer and tabletop exercises",
        "group": "Monitoring and response",
        "category": "Respond & recover",
        "problem": "Investigation and containment take longer, and cost more, without pre-arranged experts and rehearsed roles.",
        "description": "IR retainer with a forensics firm plus cross-functional tabletop exercises for all four scenarios.",
        "nist": ["RS.MA-01", "RC.RP-01", "ID.IM-02"],
        "nistFunctions": ["Respond", "Recover", "Identify"],
        "mitre": [],
        "cost": {"basis": "annual", "low": 250_000, "likely": 400_000, "high": 700_000},
        "implementationWeeks": {"low": 2, "mode": 4, "high": 6},
        "owner": "CISO",
        "dependencies": [],
        "confidence": "medium",
        "evidenceIds": ["ponemon-insider-2025", "ibm-codb-2025"],
        "rationale": "Ponemon finds incidents contained in under 31 days cost $10.6M versus $18.7M after 91+ days; rehearsed response shortens containment.",
        "effects": {
            "launch-ddos": {
                "responseCost": _eff(0.10, 0.20, 0.30),
                "outageHours": _eff(0.05, 0.10, 0.15),
            },
            "source-code-theft": {
                "investigationRecovery": _eff(0.15, 0.25, 0.35),
                "secondaryProbability": _eff(0.05, 0.10, 0.20),
            },
            "insider-leak": {
                "investigationLegal": _eff(0.10, 0.20, 0.30),
                "containmentTakedown": _eff(0.10, 0.20, 0.30),
            },
            "fake-downloads": {
                "takedownInvestigation": _eff(0.10, 0.20, 0.30),
            },
        },
        "attackSteps": {
            "launch-ddos": ["detect-respond"],
            "source-code-theft": ["leak-extortion"],
            "insider-leak": ["insider-disclosure"],
            "fake-downloads": ["credential-abuse"],
        },
        "readiness": [{"component": "incidentResponse", "level": 1.0}],
    },
    {
        "id": "phishing-resistant-mfa",
        "shortName": "Phishing-resistant MFA",
        "name": "Phishing-resistant MFA (FIDO2 keys) for staff, contractors, and vendors",
        "group": "Identity and build protection",
        "category": "Protect",
        "problem": "Social engineering, MFA fatigue, and stolen credentials gave attackers access at Rockstar (2022), EA, and Riot.",
        "description": "FIDO2 security keys for every employee, contractor, and vendor account with access to builds, collaboration, or support tools.",
        "nist": ["PR.AA-01", "PR.AA-03"],
        "nistFunctions": ["Protect"],
        "mitre": ["T1566", "T1621", "T1078"],
        "cost": {"basis": "one-time", "low": 400_000, "likely": 800_000, "high": 1_500_000},
        "implementationWeeks": {"low": 4, "mode": 8, "high": 14},
        "owner": "Identity and access management lead",
        "dependencies": [],
        "confidence": "high",
        "evidenceIds": ["cisa-pr-mfa", "peer-code-theft", "ttwo-10k-fy2026"],
        "rationale": "Directly breaks the initial-access step of the most relevant attack path. Cost assumes two keys per user for ~13,000 staff plus contractors and rollout labor (team estimate).",
        "effects": {
            "source-code-theft": {"conditionalSuccess": _eff(0.35, 0.50, 0.65)},
            "insider-leak": {"conditionalSuccess": _eff(0.00, 0.05, 0.10)},
            "fake-downloads": {"conditionalSuccess": _eff(0.05, 0.10, 0.20)},
        },
        "attackSteps": {"source-code-theft": ["social-engineering", "valid-account"], "insider-leak": ["insider-access"], "fake-downloads": ["credential-abuse"]},
        "readiness": [],
    },
    {
        "id": "build-access-pam",
        "shortName": "Build access and PAM",
        "name": "Restricted build access, PAM, and repository hardening",
        "group": "Identity and build protection",
        "category": "Protect",
        "problem": "Broad standing access lets one compromised or careless account reach builds and source code.",
        "description": "Least-privilege build access, privileged access management, secrets scanning, and segmented build pipelines.",
        "nist": ["PR.AA-05", "PR.DS-01", "DE.CM-03"],
        "nistFunctions": ["Protect", "Detect"],
        "mitre": ["T1078", "T1213"],
        "cost": {"basis": "annual", "low": 600_000, "likely": 1_000_000, "high": 1_800_000},
        "implementationWeeks": {"low": 6, "mode": 10, "high": 16},
        "owner": "Engineering security lead",
        "dependencies": ["phishing-resistant-mfa"],
        "confidence": "medium",
        "evidenceIds": ["ttwo-10k-fy2026", "peer-code-theft"],
        "rationale": "Limits what any single identity can take, which lowers both success and the scope of what leaks.",
        "effects": {
            "source-code-theft": {
                "conditionalSuccess": _eff(0.25, 0.40, 0.55),
                "competitiveIPLoss": _eff(0.10, 0.20, 0.30),
            },
            "insider-leak": {"conditionalSuccess": _eff(0.15, 0.25, 0.35)},
        },
        "attackSteps": {"source-code-theft": ["valid-account", "collection"], "insider-leak": ["insider-collection"]},
        "readiness": [],
    },
    {
        "id": "insider-risk-monitoring",
        "shortName": "Insider-risk monitoring",
        "name": "Insider-risk monitoring, DLP, and build watermarking",
        "group": "Monitoring and response",
        "category": "Detect & respond",
        "problem": "Leaks are hard to detect early and hard to attribute after the fact.",
        "description": "User-activity analytics, data-loss prevention on repositories and chat, and forensic watermarking of builds and footage.",
        "nist": ["DE.CM-03", "PR.DS-01", "PR.DS-02"],
        "nistFunctions": ["Detect", "Protect"],
        "mitre": ["T1567", "T1213"],
        "cost": {"basis": "annual", "low": 500_000, "likely": 900_000, "high": 1_600_000},
        "implementationWeeks": {"low": 5, "mode": 8, "high": 14},
        "owner": "Insider risk program lead",
        "dependencies": [],
        "confidence": "medium",
        "evidenceIds": ["ponemon-insider-2025"],
        "rationale": "Earlier detection and attribution shorten containment, which Ponemon links to much lower cost.",
        "effects": {
            "insider-leak": {
                "conditionalSuccess": _eff(0.20, 0.35, 0.50),
                "secondaryProbability": _eff(0.10, 0.20, 0.30),
            },
            "source-code-theft": {"conditionalSuccess": _eff(0.05, 0.15, 0.25)},
        },
        "attackSteps": {"insider-leak": ["insider-collection", "insider-disclosure"], "source-code-theft": ["exfiltration"]},
        "readiness": [],
    },
    {
        "id": "vendor-access-governance",
        "shortName": "Vendor access governance",
        "name": "Third-party access review, secure support tooling, and contractor offboarding",
        "group": "Vendor and collaboration controls",
        "category": "Govern",
        "problem": "Vendors and contractors hold access to sensitive data and player-facing tools (the 10-K describes a compromised vendor help desk).",
        "description": "Quarterly third-party access reviews, hardened support platforms, contract security and incident requirements, and automated offboarding.",
        "nist": ["GV.SC-05", "GV.SC-07", "PR.AA-05"],
        "nistFunctions": ["Govern", "Protect"],
        "mitre": ["T1078"],
        "cost": {"basis": "annual", "low": 300_000, "likely": 500_000, "high": 900_000},
        "implementationWeeks": {"low": 4, "mode": 6, "high": 10},
        "owner": "Third-party risk manager",
        "dependencies": [],
        "confidence": "medium",
        "evidenceIds": ["ttwo-10k-fy2026", "ibm-codb-2025-vectors"],
        "rationale": "Removes stale and excessive third-party access; supply-chain compromise averaged $4.91M per breach in IBM's 2025 study.",
        "effects": {
            "insider-leak": {"threatEventFrequency": _eff(0.15, 0.25, 0.35)},
            "source-code-theft": {"threatEventFrequency": _eff(0.05, 0.15, 0.25)},
            "fake-downloads": {"threatEventFrequency": _eff(0.05, 0.10, 0.20)},
        },
        "attackSteps": {"insider-leak": ["insider-access"], "source-code-theft": ["social-engineering"], "fake-downloads": ["lure-staging"]},
        "readiness": [],
    },
    {
        "id": "brand-protection",
        "shortName": "Brand protection and takedown",
        "name": "Brand monitoring, fake-download takedown, and player advisories",
        "group": "Monitoring and response",
        "category": "Detect & respond",
        "problem": "Fake demos, PC builds, and giveaways reach players faster than manual takedowns.",
        "description": "Continuous brand and domain monitoring, rapid takedown service, and official-channel advisories that there is no PC version or demo.",
        "nist": ["DE.CM-09", "RS.MI-01", "RS.CO-03"],
        "nistFunctions": ["Detect", "Respond"],
        "mitre": ["T1608.006", "T1204.002"],
        "cost": {"basis": "annual", "low": 200_000, "likely": 350_000, "high": 600_000},
        "implementationWeeks": {"low": 2, "mode": 3, "high": 5},
        "owner": "Brand protection lead",
        "dependencies": [],
        "confidence": "medium",
        "evidenceIds": ["kaspersky-gaming-2025", "malwarebytes-gta6-demo"],
        "rationale": "Faster takedown and clear advisories cut the number of players who reach a malicious file.",
        "effects": {
            "fake-downloads": {
                "conditionalSuccess": _eff(0.25, 0.40, 0.55),
                "supportAccountRecovery": _eff(0.05, 0.15, 0.25),
                "secondaryProbability": _eff(0.10, 0.20, 0.30),
            },
        },
        "attackSteps": {"fake-downloads": ["lure-staging", "malicious-file"]},
        "readiness": [],
    },
]

for _control in CONTROLS:
    _control["coverage"] = list(_control["effects"].keys())
    # Backward-compatible alias used by older UI code.
    _control["cost"]["mode"] = _control["cost"]["likely"]
    _control["costBasisLabel"] = {
        "annual": "Annual",
        "one-time": "One-time",
        "per-launch": "Per launch",
    }[_control["cost"]["basis"]]


# ---------------------------------------------------------------------------
# Launch Protection Readiness Index
# ---------------------------------------------------------------------------

READINESS_MODEL = {
    "name": "Launch Protection Readiness Index",
    "note": "Operational evidence score, not the probability of avoiding an attack. Weights, current levels, and cutoffs are team policy assumptions.",
    "levels": {"0": "Absent", "0.5": "Planned or partial", "1": "Implemented and tested"},
    "bands": [
        {"min": 80, "label": "Ready"},
        {"min": 60, "label": "Conditional readiness"},
        {"min": 0, "label": "Material readiness gaps"},
    ],
    "components": [
        {
            "id": "ddosProtection", "name": "DDoS protection and traffic management", "weight": 25, "current": 0.5,
            "currentRationale": "Assumes platform and cloud baseline protection is in place but not launch-tested at scale.",
        },
        {
            "id": "loadTesting", "name": "Load, stress, and resilience testing", "weight": 25, "current": 0.5,
            "currentRationale": "Launch infrastructure held under record demand, which implies load testing; DDoS simulation is not evidenced.",
        },
        {
            "id": "failoverRecovery", "name": "Failover and recovery tested", "weight": 20, "current": 0.0,
            "currentRationale": "No public evidence of tested multi-region failover for launch services.",
        },
        {
            "id": "incidentResponse", "name": "Incident response and escalation readiness", "weight": 15, "current": 0.5,
            "currentRationale": "A security organization exists (10-K); launch-specific escalation testing is not evidenced.",
        },
        {
            "id": "monitoringComms", "name": "Monitoring, player communications, and partner coordination", "weight": 15, "current": 0.5,
            "currentRationale": "Rockstar runs a public service-status page; joint platform-partner escalation is not evidenced.",
        },
    ],
}


# ---------------------------------------------------------------------------
# Attack paths
# ---------------------------------------------------------------------------

ATTACK_CHAIN = [
    {
        "id": "recon",
        "number": "01",
        "title": "Target and dependency reconnaissance",
        "technique": "T1595 - Active Scanning",
        "mitre": ["T1595"],
        "stride": "Information Disclosure",
        "asset": "Public endpoints, APIs, authentication, DNS, storefront, and download services",
        "attackerAction": "Map public endpoints, sign-in and store APIs, DNS, and CDN edges to find the bottleneck most likely to fail on launch day.",
        "defenderSignal": "Scanning across launch domains, repeated probes of login and store APIs, and small test bursts before launch.",
        "businessEffect": "Attackers learn which service to hit for the largest revenue and reputation impact.",
        "decisionQuestion": "Do we know our own launch dependencies and bottlenecks better than the attacker?",
        "effect": "Attackers identify public endpoints and capacity limits.",
        "evidenceType": "public-fact",
        "confidence": "high",
        "controlIds": ["app-abuse-protection", "launch-resilience-testing"],
        "controlIntervention": "Attack-surface and dependency review through resilience testing; rate limiting slows probing.",
        "modelFactors": ["conditionalSuccess"],
        "sourceIds": ["mitre-t1595"],
    },
    {
        "id": "infrastructure-prepared",
        "number": "02",
        "title": "Attack infrastructure prepared",
        "technique": "T1583.005 - Acquire Infrastructure: Botnet",
        "mitre": ["T1583.005"],
        "stride": "Spoofing",
        "asset": "Third-party botnet, proxy, and reflection capacity (outside Take-Two)",
        "attackerAction": "Rent or build botnet, proxy, reflection, or amplification capacity; Aisuru-class botnets-for-hire sell multi-terabit floods cheaply.",
        "defenderSignal": "Threat-intelligence chatter naming the launch, provider warnings, and reputation changes on attacking networks.",
        "businessEffect": "The attacker gains enough distributed capacity to defeat simple source blocking.",
        "decisionQuestion": "Are provider escalation contacts and contracted capacity agreed before launch?",
        "effect": "Distributed infrastructure is ready before launch day.",
        "evidenceType": "public-fact",
        "confidence": "medium",
        "controlIds": ["managed-ddos-protection", "launch-war-room"],
        "controlIntervention": "Threat-intelligence monitoring, provider coordination, and pre-arranged escalation contacts.",
        "modelFactors": ["conditionalSuccess", "outageHours"],
        "sourceIds": ["mitre-t1583", "cloudflare-ddos-2025q3"],
    },
    {
        "id": "network-flood",
        "number": "03",
        "title": "Network-layer flood begins",
        "technique": "T1498 - Network Denial of Service",
        "mitre": ["T1498"],
        "stride": "Denial of Service; Spoofing",
        "asset": "Network links, DNS, CDN edges, and origin capacity",
        "attackerAction": "Direct or reflected volumetric traffic targets network capacity at the moment real demand peaks.",
        "defenderSignal": "Bandwidth and packet-rate spikes, geographic anomalies, and origin saturation.",
        "businessEffect": "Legitimate players see timeouts as edge or origin capacity is exhausted.",
        "decisionQuestion": "Can the flood be absorbed upstream before origin services fail?",
        "effect": "Traffic overwhelms edge and origin capacity.",
        "evidenceType": "public-fact",
        "confidence": "high",
        "controlIds": ["managed-ddos-protection"],
        "controlIntervention": "Upstream scrubbing, CDN or Anycast distribution, and provider filtering.",
        "modelFactors": ["conditionalSuccess", "emergencyInfrastructure"],
        "sourceIds": ["mitre-t1498", "cloudflare-ddos-2026h1"],
    },
    {
        "id": "service-exhaustion",
        "number": "04",
        "title": "Application or service exhaustion",
        "technique": "T1499.002 / T1499.003 - Service and Application Exhaustion Flood",
        "mitre": ["T1499.002", "T1499.003"],
        "stride": "Denial of Service",
        "asset": "Login, storefront, entitlement, download, API, and database resources",
        "attackerAction": "Request floods target expensive operations such as sign-in, entitlement checks, and store APIs.",
        "defenderSignal": "Rising error rates and latency on login and store APIs with normal-looking bandwidth.",
        "businessEffect": "Players cannot sign in, verify licenses, or complete purchases.",
        "decisionQuestion": "Can bots be separated from real players without blocking real players?",
        "effect": "Sign-in and store services are overwhelmed.",
        "evidenceType": "public-fact",
        "confidence": "high",
        "controlIds": ["app-abuse-protection", "launch-resilience-testing"],
        "controlIntervention": "Rate limiting, bot management, caching, queues, circuit breakers, and WAF rules.",
        "modelFactors": ["conditionalSuccess", "outageHours"],
        "sourceIds": ["mitre-t1499"],
    },
    {
        "id": "service-degradation",
        "number": "05",
        "title": "Service degradation and cascading failure",
        "technique": "No separate ATT&CK technique (impact of steps 3-4)",
        "mitre": [],
        "stride": "Denial of Service",
        "asset": "Shared dependencies: authentication, databases, and platform storefront integrations",
        "attackerAction": "Malicious and legitimate launch demand combine; shared dependencies fail together.",
        "defenderSignal": "Health checks fail across several services and queues back up.",
        "businessEffect": "A partial slowdown becomes a broad outage affecting millions of players.",
        "decisionQuestion": "Do critical services degrade gracefully or fail together?",
        "effect": "Shared dependencies fail together.",
        "evidenceType": "team-estimate",
        "confidence": "medium",
        "controlIds": ["resilient-architecture", "managed-ddos-protection", "launch-resilience-testing"],
        "controlIntervention": "Autoscaling, service isolation, graceful degradation, multi-region failover, and capacity reservations.",
        "modelFactors": ["outageHours", "lostRevenueFraction"],
        "sourceIds": ["gta6-launch-psn"],
    },
    {
        "id": "detect-respond",
        "number": "06",
        "title": "Detection, response, and recovery",
        "technique": "Defender step (no ATT&CK technique)",
        "mitre": [],
        "stride": "Denial of Service",
        "asset": "Security operations, providers, platform partners, and player communications",
        "attackerAction": "The attacker sustains or shifts vectors while defenders respond.",
        "defenderSignal": "Teams detect abnormal traffic, activate providers, apply emergency rules, and post player updates.",
        "businessEffect": "Speed of response sets outage duration, response cost, and support demand.",
        "decisionQuestion": "Is there a tested runbook with clear escalation criteria and staffed roles?",
        "effect": "Response speed sets how long the outage lasts.",
        "evidenceType": "team-estimate",
        "confidence": "medium",
        "controlIds": ["launch-war-room", "ir-retainer-exercises"],
        "controlIntervention": "Monitoring, tested runbook, escalation criteria, response staffing, recovery validation, and a communication plan.",
        "modelFactors": ["outageHours", "responseCost", "supportSurge", "secondaryProbability"],
        "sourceIds": ["overwatch2-ddos"],
    },
    {
        "id": "business-loss",
        "number": "07",
        "title": "Business loss event",
        "technique": "FAIR loss magnitude (feeds the Risk Simulator)",
        "mitre": [],
        "stride": "Denial of Service",
        "asset": "Launch revenue, player trust, and partner relationships",
        "attackerAction": "Degraded availability turns into measurable financial loss.",
        "defenderSignal": "Refund requests, support spikes, social sentiment, and partner escalations.",
        "businessEffect": "Response cost, emergency infrastructure, lost sales, refunds and credits, support demand, and possible reputational and partner loss.",
        "decisionQuestion": "Which investment reduces expected and tail loss most per dollar?",
        "effect": "Availability loss becomes financial loss.",
        "evidenceType": "derived-value",
        "confidence": "medium",
        "controlIds": ["resilient-architecture", "launch-war-room"],
        "controlIntervention": "Graceful degradation keeps buyers in a queue; clear communications reduce refunds, support, and reputational effects.",
        "modelFactors": ["hourlyRevenueAtRisk", "lostRevenueFraction", "refundsMakeGoods", "reputationLoss"],
        "sourceIds": ["sensor-tower-gta6", "sony-psn-2011"],
    },
]


BUILD_THEFT_PATH = [
    {
        "id": "social-engineering",
        "number": "01",
        "title": "Social engineering of staff or a vendor",
        "technique": "T1566 Phishing; T1621 MFA Request Generation",
        "stride": "Spoofing",
        "controlIds": ["phishing-resistant-mfa", "vendor-access-governance"],
        "modelFactors": ["threatEventFrequency", "conditionalSuccess"],
        "evidence": "Rockstar 2022 and EA 2021 intrusions began with social engineering of collaboration access.",
    },
    {
        "id": "valid-account",
        "number": "02",
        "title": "Valid account used on collaboration and build tools",
        "technique": "T1078 Valid Accounts",
        "stride": "Elevation of Privilege",
        "controlIds": ["phishing-resistant-mfa", "build-access-pam"],
        "modelFactors": ["conditionalSuccess"],
        "evidence": "Stolen or socially engineered credentials gave internal access (Take-Two 10-K; peer incidents).",
    },
    {
        "id": "collection",
        "number": "03",
        "title": "Discovery and collection from repositories",
        "technique": "T1213 Data from Information Repositories",
        "stride": "Information Disclosure",
        "controlIds": ["build-access-pam"],
        "modelFactors": ["conditionalSuccess", "competitiveIPLoss"],
        "evidence": "The 2022 attacker reached internal chat and development footage.",
    },
    {
        "id": "exfiltration",
        "number": "04",
        "title": "Exfiltration of builds, footage, or code",
        "technique": "T1567 Exfiltration Over Web Service",
        "stride": "Information Disclosure",
        "controlIds": ["insider-risk-monitoring"],
        "modelFactors": ["conditionalSuccess"],
        "evidence": "About 90 development clips were taken and source code was threatened.",
    },
    {
        "id": "leak-extortion",
        "number": "05",
        "title": "Public leak or extortion becomes a loss event",
        "technique": "FAIR loss magnitude",
        "stride": "Information Disclosure",
        "controlIds": ["ir-retainer-exercises"],
        "modelFactors": ["investigationRecovery", "secondaryProbability", "marketingDisruption"],
        "evidence": "Rockstar reported about $5M in recovery cost plus thousands of staff hours.",
    },
]


INSIDER_PATH = [
    {
        "id": "insider-access",
        "number": "01",
        "title": "Trusted access to confidential content",
        "technique": "T1078 Valid Accounts",
        "stride": "Elevation of Privilege",
        "controlIds": ["vendor-access-governance", "phishing-resistant-mfa"],
        "modelFactors": ["threatEventFrequency", "conditionalSuccess"],
        "evidence": "12,909 employees plus contractors and vendors hold some level of access (Take-Two 10-K).",
    },
    {
        "id": "insider-collection",
        "number": "02",
        "title": "Collection from repositories and chat",
        "technique": "T1213 Data from Information Repositories",
        "stride": "Information Disclosure",
        "controlIds": ["build-access-pam", "insider-risk-monitoring"],
        "modelFactors": ["conditionalSuccess"],
        "evidence": "Broad standing access raises what one person can collect.",
    },
    {
        "id": "insider-disclosure",
        "number": "03",
        "title": "Disclosure outside the company",
        "technique": "T1567 Exfiltration Over Web Service",
        "stride": "Information Disclosure; Repudiation",
        "controlIds": ["insider-risk-monitoring", "ir-retainer-exercises"],
        "modelFactors": ["secondaryProbability", "investigationLegal"],
        "evidence": "Rockstar's 2025 leak allegation is contested by the IWGB; treated as context, not fact.",
    },
]


FAKE_DOWNLOADS_PATH = [
    {
        "id": "lure-staging",
        "number": "01",
        "title": "Fake demo, PC build, or giveaway staged",
        "technique": "T1608.006 SEO Poisoning",
        "stride": "Spoofing",
        "controlIds": ["brand-protection", "vendor-access-governance"],
        "modelFactors": ["threatEventFrequency", "conditionalSuccess"],
        "evidence": "Fake GTA VI demo and PC download sites circulated in 2026 (Malwarebytes).",
    },
    {
        "id": "malicious-file",
        "number": "02",
        "title": "Player runs a malicious installer",
        "technique": "T1204.002 User Execution: Malicious File",
        "stride": "Spoofing",
        "controlIds": ["brand-protection"],
        "modelFactors": ["conditionalSuccess"],
        "evidence": "Kaspersky logged 19M+ attempts to download malware posing as popular games in one year.",
    },
    {
        "id": "credential-abuse",
        "number": "03",
        "title": "Stolen credentials used for account takeover",
        "technique": "T1566 Phishing (credential harvesting)",
        "stride": "Information Disclosure",
        "controlIds": ["app-abuse-protection", "phishing-resistant-mfa", "ir-retainer-exercises"],
        "modelFactors": ["conditionalSuccess", "supportAccountRecovery"],
        "evidence": "Infostealers harvest saved passwords and session cookies used to take over accounts.",
    },
]


ATTACK_PATHS = {
    "launch-ddos": ATTACK_CHAIN,
    "source-code-theft": BUILD_THEFT_PATH,
    "insider-leak": INSIDER_PATH,
    "fake-downloads": FAKE_DOWNLOADS_PATH,
}


def get_scenario(scenario_id):
    return next((scenario for scenario in SCENARIOS if scenario["id"] == scenario_id), None)


def get_control(control_id):
    return next((control for control in CONTROLS if control["id"] == control_id), None)


def get_input(scenario, key):
    return scenario["assumptions"].get(key)
