"""Export the approved results package and model documentation.

Usage (from the project root, with the Python environment active):
    python3 -m backend.model.export_results            # results/ + docs/FAIR_MODEL.md
    python3 -m backend.model.export_results --samples  # also writes sampled inputs per scenario

Everything is generated from backend/data/config.py and backend/model/fair.py,
so the report and slides can reuse exactly the numbers the app shows.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np

from backend.data.config import (
    ATTACK_PATHS,
    CONTROLS,
    EVIDENCE_CLASSES,
    METHODOLOGY,
    MODEL_SEED,
    MODEL_TRIALS,
    MODEL_VERSION,
    READINESS_MODEL,
    SCENARIOS,
    SOURCES,
    TIME_BASES,
)
from backend.model.fair import (
    AMORTIZATION_YEARS,
    PRIORITY_WEIGHTS,
    control_priorities,
    readiness,
    run_portfolio,
    run_simulation,
    simulate_losses,
)

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "results"
DOCS = ROOT / "docs"


def money(value):
    if value is None:
        return "n/a"
    sign = "-" if value < 0 else ""
    value = abs(value)
    if value >= 1e9:
        return f"{sign}${value / 1e9:,.2f}B"
    if value >= 1e6:
        return f"{sign}${value / 1e6:,.1f}M"
    if value >= 1e3:
        return f"{sign}${value / 1e3:,.0f}K"
    return f"{sign}${value:,.0f}"


def pct(value, digits=1):
    return "n/a" if value is None else f"{value * 100:.{digits}f}%"


def fmt_input(item, value):
    unit = item["unit"]
    if unit.startswith("USD"):
        return money(value)
    if unit.startswith("probability") or unit.startswith("fraction"):
        return pct(value, 0)
    return f"{value:g}"


def write_csv(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def build_package():
    scenario_results = {}
    for scenario in SCENARIOS:
        baseline = run_simulation(scenario["id"], [], include_breakdown=False)
        recommended = run_simulation(scenario["id"], scenario["recommendedControlIds"])
        scenario_results[scenario["id"]] = {"baseline": baseline, "recommended": recommended}
    priorities = control_priorities()
    portfolio_all = run_portfolio()
    p1_ids = [row["controlId"] for row in priorities["controls"] if row["priority"] == 1]
    portfolio_p1 = run_portfolio(control_ids=p1_ids)
    return {
        "modelVersion": MODEL_VERSION,
        "seed": MODEL_SEED,
        "trials": MODEL_TRIALS,
        "methodology": METHODOLOGY,
        "scenarios": scenario_results,
        "priorities": priorities,
        "portfolioAllControls": portfolio_all,
        "portfolioPriority1": portfolio_p1,
        "readinessCurrent": readiness([]),
        "readinessPriority1": readiness(p1_ids),
    }


def export_csvs(package):
    input_rows = []
    for scenario in SCENARIOS:
        for item in scenario["inputs"]:
            input_rows.append({
                "scenario": scenario["name"],
                "timeBasis": TIME_BASES[scenario["timeBasis"]]["label"],
                "factor": item["label"],
                "key": item["key"],
                "low": item["low"],
                "mostLikely": item["mode"],
                "high": item["high"],
                "unit": item["unit"],
                "distribution": item["distribution"],
                "evidenceClass": item["evidenceClass"],
                "sources": "; ".join(item["sourceIds"]),
                "confidence": item["confidence"],
                "controlRelationship": item["controlRelationship"],
                "rationale": item["rationale"],
                "owner": item["owner"],
                "reviewer": item["reviewer"],
            })
    write_csv(RESULTS / "model_inputs.csv", input_rows, list(input_rows[0].keys()))

    control_rows = []
    priority_by_id = {row["controlId"]: row for row in package["priorities"]["controls"]}
    for control in CONTROLS:
        row = priority_by_id[control["id"]]
        effects = []
        for scenario_id, factors in control["effects"].items():
            for factor, effect in factors.items():
                effects.append(f"{scenario_id}:{factor} -{effect['likely']:.0%} ({effect['low']:.0%}-{effect['high']:.0%})")
        control_rows.append({
            "sequence": row["sequence"],
            "control": control["name"],
            "group": control["group"],
            "problem": control["problem"],
            "scenarios": "; ".join(control["coverage"]),
            "attackSteps": "; ".join(f"{k}:{','.join(v)}" for k, v in control["attackSteps"].items()),
            "nist": "; ".join(control["nist"]),
            "costBasis": control["costBasisLabel"],
            "costLow": control["cost"]["low"],
            "costLikely": control["cost"]["likely"],
            "costHigh": control["cost"]["high"],
            "effects": "; ".join(effects),
            "implementationWeeks": control["implementationWeeks"]["mode"],
            "owner": control["owner"],
            "dependencies": "; ".join(control["dependencies"]),
            "evidence": "; ".join(control["evidenceIds"]),
            "confidence": control["confidence"],
            "firstYearLossReduction": round(row["firstYearLossReduction"]),
            "p95ReductionTotal": round(row["p95ReductionTotal"]),
            "firstYearNetBenefit": round(row["firstYearNetBenefit"]),
            "firstYearRosi": round(row["firstYearRosi"], 2),
            "priorityScore": row["priorityScore"],
            "priority": row["priorityLabel"],
            "rationale": control["rationale"],
        })
    control_rows.sort(key=lambda r: r["sequence"])
    write_csv(RESULTS / "control_catalogue.csv", control_rows, list(control_rows[0].keys()))

    result_rows = []
    for scenario in SCENARIOS:
        for label, key in (("Baseline", "baseline"), ("Recommended controls", "recommended")):
            result = package["scenarios"][scenario["id"]][key]
            metrics = result["baseline" if key == "baseline" else "residual"]["metrics"]
            row = {
                "scenario": scenario["name"],
                "timeBasis": TIME_BASES[scenario["timeBasis"]]["label"],
                "case": label,
                "controls": "; ".join(result["controlEconomics"]["selectedControlIds"]),
                "mean": round(metrics["mean"]),
                "p50": round(metrics["p50"]),
                "p90": round(metrics["p90"]),
                "p95": round(metrics["p95"]),
                "p99": round(metrics["p99"]),
                "probabilityOfLoss": round(metrics["probabilityOfLoss"], 4),
            }
            for item in metrics["exceedance"]:
                row[f"P(>{money(item['threshold'])})"] = round(item["probability"], 4)
            result_rows.append(row)
    fields = []
    for row in result_rows:
        for field in row:
            if field not in fields:
                fields.append(field)
    write_csv(RESULTS / "scenario_results.csv", result_rows, fields)

    write_csv(
        RESULTS / "evidence_register.csv",
        [{**source, "class": EVIDENCE_CLASSES.get(source["evidenceClass"], source["evidenceClass"])} for source in SOURCES],
        ["id", "title", "publisher", "url", "published", "accessDate", "class", "reliability", "claim", "plannedUse", "owner", "reviewer"],
    )


def export_samples():
    folder = RESULTS / "samples"
    for scenario in SCENARIOS:
        baseline, residual, draws = simulate_losses(scenario["id"], scenario["recommendedControlIds"])
        rows = []
        keys = list(draws.samples.keys())
        for index in range(draws.trials):
            row = {key: float(draws.samples[key][index]) for key in keys}
            row["baselineLoss"] = float(baseline[index])
            row["residualLoss"] = float(residual[index])
            rows.append(row)
        write_csv(folder / f"{scenario['id']}_samples.csv", rows, keys + ["baselineLoss", "residualLoss"])


def markdown(package):
    lines = []
    add = lines.append
    add("# FAIR-style model: inputs, method, and results")
    add("")
    add(f"_Generated by `python3 -m backend.model.export_results` · model version `{MODEL_VERSION}` · "
        f"{MODEL_TRIALS:,} trials · seed {MODEL_SEED}. Do not edit by hand; edit `backend/data/config.py` and re-run._")
    add("")
    add("## 1. Method")
    add("")
    add(f"- **Structure.** {METHODOLOGY['description']}")
    add(f"- **Formula.** {METHODOLOGY['formula']}.")
    add(f"- **Sampling.** {METHODOLOGY['sampling']}")
    add(f"- **Controls.** {METHODOLOGY['controlRule']}")
    add(f"- **Cost basis.** {METHODOLOGY['costRule']}")
    add(f"- **Timing.** {METHODOLOGY['timing']}")
    add("- **Evidence classes.** Public fact, Derived value, Team estimate, Model assumption.")
    add(f"- **Disclaimer.** {METHODOLOGY['disclaimer']}")
    add("")
    add("Launch-event trial (Launch-Day DDoS):")
    add("")
    add("```")
    add("attack     = U1 < attackProbability")
    add("material   = attack and U2 < conditionalSuccess x control multipliers")
    add("primary    = outageHours x hourlyRevenueAtRisk x lostRevenueFraction")
    add("             + responseCost + emergencyInfrastructure + refundsMakeGoods + supportSurge")
    add("secondary  = (U3 < secondaryProbability) x (reputationLoss + partnerLegal)")
    add("loss       = material x (primary + secondary)")
    add("```")
    add("")
    add("Annual trial (other three scenarios): `attempts = PoissonInverseCDF(U1, threatEventFrequency)`, each attempt succeeds with "
        "`conditionalSuccess`, and `loss = successes x (primary + secondary indicator x secondary)`. Multiple events in one trial reuse "
        "that trial's sampled magnitudes (model assumption).")
    add("")
    add("Control economics: expected risk reduction = baseline mean - residual mean; net benefit = reduction - comparable-period cost; "
        "ROSI = net benefit / cost; cost of inaction = avoidable expected loss; tail-risk reduction = baseline P95 - residual P95. "
        f"Annualized cost = annual + one-time / {AMORTIZATION_YEARS} + per-launch x 1.")
    add("")
    add(f"Priority score (100 points): {', '.join(f'{k} {v}' for k, v in PRIORITY_WEIGHTS.items())}. "
        "60+ = Priority 1 (implement before launch), 40-59 = Priority 2 (implement next), below 40 = Priority 3 (evaluate or monitor). "
        "Scored on the first-year view (one launch event + one year of annual scenarios).")
    add("")

    add("## 2. Scenario results (baseline vs. recommended controls)")
    add("")
    add("| Scenario | Basis | Mean | P50 | P90 | P95 | P(loss) | Residual mean | Residual P95 | Control cost | Net benefit | ROSI |")
    add("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for scenario in SCENARIOS:
        result = package["scenarios"][scenario["id"]]["recommended"]
        b = result["baseline"]["metrics"]
        r = result["residual"]["metrics"]
        e = result["controlEconomics"]
        add(f"| {scenario['name']} | {TIME_BASES[scenario['timeBasis']]['short']} | {money(b['mean'])} | {money(b['p50'])} | {money(b['p90'])} | "
            f"{money(b['p95'])} | {pct(b['probabilityOfLoss'])} | {money(r['mean'])} | {money(r['p95'])} | {money(e['estimatedCost'])} | "
            f"{money(e['netBenefit'])} | {e['rosi']:.2f}x |")
    add("")
    for scenario in SCENARIOS:
        result = package["scenarios"][scenario["id"]]["recommended"]
        b = result["baseline"]["metrics"]
        r = result["residual"]["metrics"]
        add(f"**{scenario['name']}** ({TIME_BASES[scenario['timeBasis']]['label']}). Recommended controls: "
            f"{', '.join(result['controlEconomics']['selectedControlIds'])}.")
        add("")
        add("| Threshold | Baseline P(exceed) | Residual P(exceed) |")
        add("|---|---|---|")
        for index, item in enumerate(b["exceedance"]):
            add(f"| > {money(item['threshold'])} | {pct(item['probability'])} | {pct(r['exceedance'][index]['probability'])} |")
        add("")
        add("Top sensitivity drivers (Spearman rank correlation with baseline loss): "
            + "; ".join(f"{d['name']} ({d['correlation']:.2f})" for d in result["sensitivity"][:3]) + ".")
        add("")
        add("Largest low/high swings in expected loss: "
            + "; ".join(f"{t['name']} ({money(t['meanAtLow'])} to {money(t['meanAtHigh'])})" for t in result["tornado"][:3]) + ".")
        add("")

    add("## 3. Control priorities (first-year view)")
    add("")
    add("| # | Control | Priority | Score | Year-one loss avoided | First-year cost | Net benefit | ROSI | P95 reduction |")
    add("|---|---|---|---|---|---|---|---|---|")
    for row in sorted(package["priorities"]["controls"], key=lambda r: r["sequence"]):
        add(f"| {row['sequence']} | {row['name']}{' *' if row['elevated'] else ''} | {row['priorityLabel']} | {row['priorityScore']} | "
            f"{money(row['firstYearLossReduction'])} | {money(row['firstYearCost'])} | {money(row['firstYearNetBenefit'])} | "
            f"{row['firstYearRosi']:.2f}x | {money(row['p95ReductionTotal'])} |")
    add("")
    add("\\* Elevated as a prerequisite (resilience testing turns 'implemented' into 'implemented and tested').")
    add("")

    for label, key in (("All controls", "portfolioAllControls"), ("Priority 1 controls only", "portfolioPriority1")):
        p = package[key]
        e = p["controlEconomics"]
        add(f"**Portfolio, {label}** (first-year view): baseline {money(p['portfolio']['baselineMean'])}, residual "
            f"{money(p['portfolio']['residualMean'])}, loss avoided {money(e['lossesAvoided'])}, first-year cost {money(e['estimatedCost'])} "
            f"(range {money(e['costRange']['low'])}-{money(e['costRange']['high'])}), net benefit {money(e['netBenefit'])}, ROSI {e['rosi']:.2f}x.")
        add("")
    rc = package["readinessCurrent"]
    rp = package["readinessPriority1"]
    add(f"**Launch Protection Readiness Index:** {rc['current']['score']:.0f} now ({rc['current']['band']}); "
        f"{rp['proposed']['score']:.0f} with Priority 1 controls ({rp['proposed']['band']}). {READINESS_MODEL['note']}")
    add("")

    add("## 4. Model input table")
    add("")
    for scenario in SCENARIOS:
        add(f"### {scenario['name']} ({TIME_BASES[scenario['timeBasis']]['label']})")
        add("")
        add(f"_Loss event:_ {scenario['lossEventStatement']}")
        add("")
        add("| Factor | Low | Most likely | High | Unit | Evidence | Confidence | Sources | Rationale |")
        add("|---|---|---|---|---|---|---|---|---|")
        for item in scenario["inputs"]:
            add(f"| {item['label']} | {fmt_input(item, item['low'])} | {fmt_input(item, item['mode'])} | {fmt_input(item, item['high'])} | "
                f"{item['unit']} | {item['evidenceClass']} | {item['confidence']} | {', '.join(item['sourceIds'])} | {item['rationale']} |")
        add("")

    add("## 5. Control catalogue")
    add("")
    add("| Control | Group | NIST CSF 2.0 | Cost (basis) | Effects (likely, range) | Weeks | Confidence |")
    add("|---|---|---|---|---|---|---|")
    for control in CONTROLS:
        effects = "; ".join(
            f"{sid} {factor} -{eff['likely']:.0%} ({eff['low']:.0%}-{eff['high']:.0%})"
            for sid, factors in control["effects"].items()
            for factor, eff in factors.items()
        )
        add(f"| {control['name']} | {control['group']} | {', '.join(control['nist'])} | "
            f"{money(control['cost']['likely'])} ({control['costBasisLabel'].lower()}; {money(control['cost']['low'])}-{money(control['cost']['high'])}) | "
            f"{effects} | {control['implementationWeeks']['mode']} | {control['confidence']} |")
    add("")

    add("## 6. Attack paths")
    add("")
    for scenario in SCENARIOS:
        add(f"**{scenario['name']}:** " + " -> ".join(f"{step['number']} {step['title']}" for step in ATTACK_PATHS[scenario["id"]]))
        add("")

    add("## 7. Evidence register")
    add("")
    add("| ID | Source | Publisher | Date | Class | Reliability | Claim used |")
    add("|---|---|---|---|---|---|---|")
    for source in SOURCES:
        add(f"| {source['id']} | [{source['title']}]({source['url']}) | {source['publisher']} | {source['published']} | "
            f"{EVIDENCE_CLASSES.get(source['evidenceClass'], source['evidenceClass'])} | {source['reliability']} | {source['claim']} |")
    add("")

    add("## 8. Validation")
    add("")
    add("- `python3 -m unittest discover -s backend/tests -v` runs model, API, and data-integrity tests.")
    add("- Independent check: for every scenario the 200,000-trial Monte Carlo mean is within 4% of a closed-form expectation computed "
        "from triangular means (E[frequency] x E[success] x (E[primary] + E[secondary probability] x E[secondary])).")
    add("- Common random numbers: residual loss is never above baseline loss in any trial, for every scenario with every applicable control on.")
    add("- Reproducibility: the same seed returns identical metrics, histograms, and sensitivity results.")
    add("- Integrity: every input has a source, evidence class, rationale, confidence, owner, and reviewer; every control effect targets a real input; "
        "attack steps and controls reference each other in both directions.")
    add("")
    add("## 9. Limitations")
    add("")
    add("- Most loss magnitudes are team estimates anchored to public figures, not Take-Two data; ranges are wide on purpose.")
    add("- Inputs are sampled independently; real losses are correlated (a longer outage also raises refunds and support). This likely understates the tail.")
    add("- Control effectiveness ranges are team estimates informed by vendor and industry evidence, not measured Take-Two performance.")
    add("- Stacking controls multiplicatively assumes independent effects; overlapping controls may deliver less combined benefit.")
    add("- Launch-week observations (Nov 19-22, 2026) were used to calibrate revenue at risk and baseline capacity, so the DDoS figures are not a pure forecast.")
    add("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--samples", action="store_true", help="also write sampled inputs per scenario")
    args = parser.parse_args()
    package = build_package()
    RESULTS.mkdir(exist_ok=True)
    DOCS.mkdir(exist_ok=True)
    (RESULTS / "results_package.json").write_text(json.dumps(package, indent=2, default=float), encoding="utf-8")
    export_csvs(package)
    if args.samples:
        export_samples()
    (DOCS / "FAIR_MODEL.md").write_text(markdown(package), encoding="utf-8")
    print(f"Wrote {RESULTS.relative_to(ROOT)}/ and {DOCS.relative_to(ROOT)}/FAIR_MODEL.md")


if __name__ == "__main__":
    main()
