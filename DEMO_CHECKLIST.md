# Demo and submission checklist

## Before submission

- Review every evidence URL, access date, evidence classification, rationale, and confidence label.
- Prefer company filings, official frameworks, and MITRE pages over secondary reporting when a primary source is available.
- Keep team estimates explicitly labelled; do not describe them as observed company facts.
- Run `python3 -m unittest discover -s backend/tests -v` with the Python environment active.
- Run `npm --prefix frontend run build` from the project root.
- Open the Flask-served production application at `http://127.0.0.1:5000` and test all four routes.

## Live-demo walkthrough

1. Reset the demo and introduce the Executive Overview.
2. Explain that readiness is a team-designed index and is separate from FAIR financial loss.
3. Open Attack Paths and demonstrate the detailed Launch-Day DDoS pathway.
4. Point out the FAIR-variable links and then move to the Risk Simulator.
5. Explain low/most-likely/high triangular inputs, 10,000 trials, seed 243, baseline, residual, P50, P95, and P99.
6. Show why P50 can be zero when most periods contain no successful material event.
7. Open the Control Planner and distinguish pathway-preselected controls from the standalone financial priority ranking.
8. Show all-scenario portfolio mode, shared control cost, tail metrics, and the combined loss distribution.

## Emergency fallback

- Run every scenario and the portfolio once before presenting so matching results are saved in browser storage.
- Download one JSON scenario summary from the Risk Simulator.
- Capture screenshots of the Executive Overview, DDoS path, simulator distribution, and portfolio planner.
- Keep the screenshots and presentation available locally in case the development server or network is unavailable.

## Terms every presenter should be able to explain

- Threat event frequency
- Vulnerability or conditional success probability
- Primary and secondary loss
- Secondary-loss occurrence probability
- Triangular distribution
- Monte Carlo trial
- Fixed random seed
- Paired baseline/residual comparison
- Mean, P50, P90, P95, and P99
- Threshold probability
- Spearman rank sensitivity
- Tornado sensitivity
- Expected loss avoided, net benefit, and ROSI

