"""Evidence-anchored model inputs transcribed from the team workbook.

Excel is an evidence and review artefact only. The running application uses these
Python values so Flask remains the single calculation engine.
"""

EVIDENCE_SOURCES = [
    {
        "id": "ttwo-q2-fy27",
        "title": "Take-Two Q2 FY2027 earnings release",
        "url": "https://www.sec.gov/Archives/edgar/data/946581/000162828026072175/ttwo2q27earningsrelease.htm",
        "accessDate": "2026-11-09",
        "type": "public-fact",
        "reviewNote": "Primary SEC filing used for company guidance. Team should recheck the filing before final submission.",
    },
    {
        "id": "ttwo-fy26-10k",
        "title": "Take-Two FY2026 Form 10-K",
        "url": "https://ir.take2games.com/static-files/31b9a69d-016e-4d72-9d91-b911f1313bed",
        "accessDate": "2026-11-20",
        "type": "public-fact",
        "reviewNote": "Primary company filing used as organizational context.",
    },
    {
        "id": "psn-ddos-precedent",
        "title": "PlayStation Network DDoS outage precedent",
        "url": "https://www.theregister.com/2014/12/27/playstation_clambers_back_online/",
        "accessDate": "2026-11-20",
        "type": "public-fact",
        "reviewNote": "Historical sector precedent; it informs a range but does not predict this scenario directly.",
    },
    {
        "id": "rockstar-recovery-report",
        "title": "Reported Rockstar leak recovery cost",
        "url": "https://www.gamesradar.com/the-gta-6-leak-cost-rockstar-dollar5-million-and-thousands-of-hours-of-staff-time/",
        "accessDate": "2026-11-20",
        "type": "secondary-reporting",
        "reviewNote": "Secondary reporting. Use cautiously and seek the underlying court record for the final evidence register.",
    },
    {
        "id": "cloudflare-ddos-report",
        "title": "Cloudflare DDoS threat report",
        "url": "https://blog.cloudflare.com/ddos-threat-report-2026-q3/",
        "accessDate": "2026-11-20",
        "type": "industry-report",
        "reviewNote": "Industry threat context; not a company-specific probability measurement.",
    },
    {
        "id": "open-fair",
        "title": "The Open Group Open FAIR",
        "url": "https://www.opengroup.org/open-fair",
        "accessDate": "2026-11-20",
        "type": "methodology-reference",
        "reviewNote": "Supports the model structure, not the numeric estimates.",
    },
]


def estimate(low, mode, high, unit, rationale, confidence, evidence_type, evidence_ids):
    return {
        "low": low,
        "mode": mode,
        "high": high,
        "unit": unit,
        "rationale": rationale,
        "confidence": confidence,
        "evidenceType": evidence_type,
        "evidenceIds": evidence_ids,
    }


EVIDENCE_PROFILES = {
    "launch-ddos": {
        "analysisBasis": "launch-event",
        "secondaryLossProbability": {
            "value": 0.35,
            "unit": "probability per successful event",
            "rationale": "Secondary stakeholder loss is possible but is not assumed to follow every successful disruption.",
            "confidence": "low",
            "evidenceType": "team-estimate",
            "evidenceIds": ["open-fair"],
        },
        "assumptions": {
            "threatEventFrequency": estimate(0.60, 0.85, 0.97, "probability in launch window", "Range combines a high-profile launch judgment with current DDoS threat context.", "medium", "model-assumption", ["cloudflare-ddos-report"]),
            "vulnerability": estimate(0.04, 0.12, 0.35, "conditional success probability", "Conditional disruption chance after accounting for expected launch resilience, with uncertainty retained.", "low", "team-estimate", ["psn-ddos-precedent"]),
            "primaryLoss": estimate(841_372.2826, 9_701_086.9565, 80_618_206.5217, "USD", "Calculated from outage duration, daily net bookings, launch uplift, online-dependent share, unrecovered share, and response cost.", "medium", "derived-value", ["ttwo-q2-fy27", "psn-ddos-precedent"]),
            "secondaryLoss": estimate(3_425_000, 13_700_000, 85_625_000, "USD", "Scenario range based on 0.1%, 0.4%, and 2.5% of a $3.425B reference revenue figure.", "low", "derived-value", ["ttwo-q2-fy27"]),
        },
        "lossDerivation": {
            "formula": "Outage days × average daily net bookings × launch uplift × online-dependent share × unrecovered share + response cost",
            "inputs": [
                {"name": "Outage duration", "low": 0.25, "mode": 1, "high": 3, "unit": "days", "evidenceIds": ["psn-ddos-precedent"]},
                {"name": "Average daily net bookings", "low": 36_413_043, "mode": 37_228_261, "high": 38_043_478, "unit": "USD/day", "evidenceIds": ["ttwo-q2-fy27"]},
                {"name": "Launch uplift multiplier", "low": 1, "mode": 1.5, "high": 2.5, "unit": "multiplier", "evidenceIds": []},
                {"name": "Online-dependent share", "low": 0.25, "mode": 0.40, "high": 0.55, "unit": "share", "evidenceIds": []},
                {"name": "Unrecovered share", "low": 0.15, "mode": 0.30, "high": 0.45, "unit": "share", "evidenceIds": []},
                {"name": "Response cost", "low": 500_000, "mode": 3_000_000, "high": 10_000_000, "unit": "USD", "evidenceIds": []},
            ],
        },
    },
    "source-code-theft": {
        "analysisBasis": "annual",
        "secondaryLossProbability": {"value": 0.30, "unit": "probability per successful event", "rationale": "Only a subset of successful events is assumed to create material downstream stakeholder loss.", "confidence": "low", "evidenceType": "team-estimate", "evidenceIds": ["open-fair"]},
        "assumptions": {
            "threatEventFrequency": estimate(0.6, 1.5, 3, "events per year", "Team range for material targeted repository or build-system attempts.", "low", "team-estimate", ["open-fair"]),
            "vulnerability": estimate(0.03, 0.10, 0.25, "conditional success probability", "Judgment range for success before the selected controls.", "low", "team-estimate", ["open-fair"]),
            "primaryLoss": estimate(2_800_000, 5_000_000, 25_000_000, "USD", "Anchored to reported recovery-cost context and widened for investigation, rebuild, and legal costs.", "low", "evidence-anchored-estimate", ["rockstar-recovery-report"]),
            "secondaryLoss": estimate(1_000_000, 6_000_000, 60_000_000, "USD", "Team range for competitive, partner, and launch-delay consequences when secondary loss occurs.", "low", "team-estimate", ["open-fair"]),
        },
    },
    "insider-leak": {
        "analysisBasis": "annual",
        "secondaryLossProbability": {"value": 0.25, "unit": "probability per successful event", "rationale": "Not every contained insider event produces external stakeholder consequences.", "confidence": "low", "evidenceType": "team-estimate", "evidenceIds": ["open-fair"]},
        "assumptions": {
            "threatEventFrequency": estimate(0.3, 0.8, 1.5, "events per year", "Team range for material insider or contractor misuse events.", "low", "team-estimate", ["open-fair"]),
            "vulnerability": estimate(0.05, 0.15, 0.35, "conditional success probability", "Judgment range based on access concentration and monitoring uncertainty.", "low", "team-estimate", ["open-fair"]),
            "primaryLoss": estimate(1_500_000, 4_900_000, 18_000_000, "USD", "Team estimate for investigation, notification, legal, and containment.", "low", "team-estimate", ["ttwo-fy26-10k"]),
            "secondaryLoss": estimate(500_000, 5_000_000, 40_000_000, "USD", "Team range for partner, customer, reputation, and competitive consequences.", "low", "team-estimate", ["open-fair"]),
        },
    },
    "fake-downloads": {
        "analysisBasis": "annual",
        "secondaryLossProbability": {"value": 0.20, "unit": "probability per successful event", "rationale": "A material campaign may be contained before broad fraud or reputation effects develop.", "confidence": "low", "evidenceType": "team-estimate", "evidenceIds": ["open-fair"]},
        "assumptions": {
            "threatEventFrequency": estimate(4, 12, 30, "campaigns per year", "Team range reflecting repeated impersonation campaigns over a year.", "low", "team-estimate", ["open-fair"]),
            "vulnerability": estimate(0.02, 0.06, 0.15, "conditional material-success probability", "Judgment range for a campaign causing material customer or workforce harm.", "low", "team-estimate", ["open-fair"]),
            "primaryLoss": estimate(500_000, 3_000_000, 12_000_000, "USD", "Team estimate for response, takedown, support, and credential-reset costs.", "low", "team-estimate", ["open-fair"]),
            "secondaryLoss": estimate(500_000, 4_000_000, 30_000_000, "USD", "Team range for fraud, brand, trust, and downstream compromise effects.", "low", "team-estimate", ["open-fair"]),
        },
    },
}
