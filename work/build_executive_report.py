from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "outputs" / "report" / "Cyber_Attack_Decision_Workbench_Executive_Report_Draft.docx"

NAVY = "17365D"
LIGHT_BLUE = "DCE6F1"
PALE_BLUE = "F2F6FA"
LIGHT_GRAY = "F3F3F3"
BORDER = "D9D9D9"


def shade(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)


def set_cell_margins(cell, top=90, start=100, bottom=90, end=100):
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    tc_mar = tc_pr.first_child_found_in("w:tcMar")
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar")
        tc_pr.append(tc_mar)
    for margin, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = tc_mar.find(qn(f"w:{margin}"))
        if node is None:
            node = OxmlElement(f"w:{margin}")
            tc_mar.append(node)
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")


def set_cell_border(cell, color=BORDER, size="4"):
    tc_pr = cell._tc.get_or_add_tcPr()
    borders = tc_pr.first_child_found_in("w:tcBorders")
    if borders is None:
        borders = OxmlElement("w:tcBorders")
        tc_pr.append(borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        tag = qn(f"w:{edge}")
        node = borders.find(tag)
        if node is None:
            node = OxmlElement(f"w:{edge}")
            borders.append(node)
        node.set(qn("w:val"), "single")
        node.set(qn("w:sz"), size)
        node.set(qn("w:color"), color)


def prevent_row_split(row):
    tr_pr = row._tr.get_or_add_trPr()
    cant_split = OxmlElement("w:cantSplit")
    tr_pr.append(cant_split)


def keep_with_next(paragraph):
    paragraph.paragraph_format.keep_with_next = True


def add_table(doc, headers, rows, widths=None, font_size=8.5, repeat_header=True):
    table = doc.add_table(rows=1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    table.style = "Table Grid"
    header = table.rows[0]
    if repeat_header:
        tr_pr = header._tr.get_or_add_trPr()
        tbl_header = OxmlElement("w:tblHeader")
        tbl_header.set(qn("w:val"), "true")
        tr_pr.append(tbl_header)
    for i, text in enumerate(headers):
        cell = header.cells[i]
        shade(cell, NAVY)
        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        set_cell_margins(cell)
        set_cell_border(cell)
        if widths:
            cell.width = Inches(widths[i])
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(str(text))
        r.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)
        r.font.size = Pt(font_size)
    for row_index, values in enumerate(rows):
        row = table.add_row()
        prevent_row_split(row)
        for i, value in enumerate(values):
            cell = row.cells[i]
            if row_index % 2:
                shade(cell, PALE_BLUE)
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            set_cell_margins(cell)
            set_cell_border(cell)
            if widths:
                cell.width = Inches(widths[i])
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if i > 0 and len(str(value)) < 35 else WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(str(value))
            r.font.size = Pt(font_size)
    doc.add_paragraph().paragraph_format.space_after = Pt(0)
    return table


def add_caption(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(3)
    p.paragraph_format.space_after = Pt(8)
    r = p.add_run(text)
    r.bold = True
    r.font.size = Pt(9)
    return p


def add_figure_placeholder(doc, number, instruction, caption):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run(f"[Insert Figure {number} here: {instruction}]")
    r.italic = True
    r.font.color.rgb = RGBColor(89, 89, 89)
    add_caption(doc, f"Figure {number}  {caption}")


def add_bullets(doc, items):
    for item in items:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.24)
        p.paragraph_format.first_line_indent = Inches(-0.16)
        p.add_run("• ")
        p.add_run(item)


def add_numbered(doc, items):
    for item in items:
        p = doc.add_paragraph(style="List Number")
        p.add_run(item)


def add_heading(doc, text, level=1):
    p = doc.add_heading(text, level=level)
    keep_with_next(p)
    return p


def add_para(doc, text, bold_lead=None):
    p = doc.add_paragraph()
    if bold_lead and text.startswith(bold_lead):
        p.add_run(bold_lead).bold = True
        p.add_run(text[len(bold_lead):])
    else:
        p.add_run(text)
    return p


doc = Document()
section = doc.sections[0]
section.page_width = Inches(8.5)
section.page_height = Inches(11)
section.top_margin = Inches(0.72)
section.bottom_margin = Inches(0.72)
section.left_margin = Inches(0.75)
section.right_margin = Inches(0.75)

styles = doc.styles
styles["Normal"].font.name = "Aptos"
styles["Normal"].font.size = Pt(10.5)
styles["Normal"].paragraph_format.space_after = Pt(6)
styles["Normal"].paragraph_format.line_spacing = 1.08
styles["Title"].font.name = "Aptos Display"
styles["Title"].font.size = Pt(28)
styles["Title"].font.bold = True
styles["Title"].font.color.rgb = RGBColor(0, 0, 0)
title_ppr = styles["Title"].element.get_or_add_pPr()
title_border = title_ppr.find(qn("w:pBdr"))
if title_border is not None:
    title_ppr.remove(title_border)
for style_name, size in (("Heading 1", 17), ("Heading 2", 13), ("Heading 3", 11)):
    style = styles[style_name]
    style.font.name = "Aptos Display"
    style.font.size = Pt(size)
    style.font.bold = True
    style.font.color.rgb = RGBColor(0, 0, 0)
    style.paragraph_format.space_before = Pt(12 if style_name != "Heading 1" else 18)
    style.paragraph_format.space_after = Pt(5)
styles["List Bullet"].font.name = "Aptos"
styles["List Bullet"].font.size = Pt(10.5)
styles["List Number"].font.name = "Aptos"
styles["List Number"].font.size = Pt(10.5)

for sec in doc.sections:
    header = sec.header.paragraphs[0]
    header.text = "Cyber Attack Decision Workbench"
    header.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    header.runs[0].font.size = Pt(8)
    header.runs[0].font.color.rgb = RGBColor(102, 102, 102)
    footer = sec.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = footer.add_run("Page ")
    run.font.size = Pt(8)
    field = OxmlElement("w:fldSimple")
    field.set(qn("w:instr"), "PAGE")
    footer._p.append(field)

# Cover
p = doc.add_paragraph(style="Title")
p.alignment = WD_ALIGN_PARAGRAPH.LEFT
p.add_run("Cyber Attack Decision Workbench")
subtitle = doc.add_paragraph()
subtitle.paragraph_format.space_before = Pt(8)
subtitle.paragraph_format.space_after = Pt(24)
r = subtitle.add_run("Executive Cyber Risk Analysis for a Major Rockstar Games Launch")
r.font.size = Pt(15)
r.bold = True

meta = [
    ("Course", "Cyber Risk Modeling"),
    ("Prepared by", "Member 1  Member 2  Member 3"),
    ("Date", "24 November 2026"),
    ("Deliverable", "Working web application and executive decision report"),
]
table = doc.add_table(rows=0, cols=2)
table.alignment = WD_TABLE_ALIGNMENT.LEFT
table.autofit = False
for label, value in meta:
    cells = table.add_row().cells
    cells[0].width = Inches(1.4)
    cells[1].width = Inches(5.6)
    cells[0].paragraphs[0].add_run(label).bold = True
    cells[1].paragraphs[0].add_run(value)
    for cell in cells:
        set_cell_margins(cell, top=70, bottom=70)

doc.add_paragraph()
opening = doc.add_paragraph()
opening.paragraph_format.space_before = Pt(18)
opening.paragraph_format.line_spacing = 1.15
opening.add_run(
    "A major Rockstar Games launch is more than a software release. It is a concentrated business event in which online availability, customer trust, intellectual property, and brand reputation are exposed at the same time. The Cyber Attack Decision Workbench turns that high-stakes scenario into an executive decision: what could happen, what could it cost, and which controls are worth funding before launch?"
)

doc.add_page_break()

add_heading(doc, "Executive Summary", 1)
add_para(doc, "The Cyber Attack Decision Workbench was designed around a compelling executive question: how should Take-Two and Rockstar prepare for cyberattacks surrounding a major game launch? A launch concentrates extraordinary demand, public attention, and revenue-sensitive services into a narrow window. A successful attack could prevent players from connecting, expose source code or builds, exploit trusted insiders, or use the excitement around the release to distribute fake downloads and phishing campaigns. The workbench makes these four threats visible as connected business decisions rather than separate technical problems.")
add_para(doc, "The tool's main contribution is its ability to move from attack story to investment decision in one place. STRIDE identifies the security failure, MITRE ATT&CK shows how an adversary could act, and a FAIR-style model translates event frequency, conditional success, and loss magnitude into a financial distribution. Executives can then switch controls on or off and see how the expected loss, severe tail outcomes, implementation cost, net benefit, and return on security investment change. This connects course concepts to a decision that security, finance, and leadership can discuss together [1, 3, 4].")
add_para(doc, "The Python model performs 10,000 Monte Carlo trials with fixed seed 243. Each trial samples uncertain low, most-likely, and high estimates, determines whether threat events and successful loss events occur, and calculates primary and possible secondary loss. The application reports mean loss, P50, P90, P95, P99, threshold probabilities, sensitivity, and baseline-versus-residual comparisons. Repeated random sampling is appropriate because cyber frequency and impact are uncertain and point estimates hide the range of plausible outcomes [4, 5].")
add_para(doc, "The evidence-anchored model estimates baseline expected loss of $5.70 million for Launch-Day DDoS, $3.84 million for source-code theft, $1.91 million for insider leak, and $8.91 million for fake downloads and phishing. With the controls selected for each path, the corresponding residual means fall to $1.52 million, $0.80 million, $0.47 million, and $1.44 million. These are reproducible model outputs, not audited predictions, and the workbench shows the assumptions behind them.")
add_para(doc, "Across all four scenarios, the modeled portfolio produces the report's clearest decision result. Nine controls with an expected combined cost of $3.57 million reduce modeled mean loss from $20.18 million to $2.29 million. This represents $17.90 million in expected loss avoided, $14.33 million in net benefit, and a modeled ROSI of 4.01. The analysis prioritizes phishing-resistant multifactor authentication and incident drills across scenarios, while identifying CDN scrubbing as essential for launch availability and brand monitoring as a high-value response to fake downloads. The result is not simply a list of security tools; it is a defensible order for spending a limited security budget.")

add_figure_placeholder(doc, 1, "Executive Overview with Launch-Day DDoS selected, baseline and residual metrics, readiness dimensions, and the scenario heat map", "Executive view of modeled exposure and team readiness")

add_heading(doc, "1 The Launch Decision", 1)
add_heading(doc, "1.1 What Executives Must Decide", 2)
add_para(doc, "The scenario places the reader in the weeks before a major Rockstar Games launch. Demand is expected to surge, attention from attackers and imitators is increasing, and every proposed safeguard competes for time and budget. Executives must decide which controls need to be in place before launch, which risks can be accepted, and whether the expected protection justifies the cost. Answering only that DDoS or phishing is 'high risk' is not enough to support those choices.")
add_para(doc, "The workbench answers the decision through an interactive chain of reasoning. It shows how an attack could unfold, where a control interrupts it, how that control changes frequency, conditional success, or loss magnitude, and what the change means financially. It is intended for security leaders, technical teams, risk analysts, finance partners, and executives who need a shared view of the same decision.")
add_para(doc, "The course material emphasizes that measurement should serve a decision and that useful precision is more important than perfect measurement [6]. We therefore limited the scope to four decision-relevant scenarios and nine controls. The workbench does not attempt to predict every cyber incident, reproduce an official FAIR assessment, or calculate an audited valuation of Take-Two Interactive. It is a transparent decision-support model built from public evidence, derived values, and clearly labelled team assumptions.")

add_heading(doc, "1.2 Four Ways a Major Launch Can Be Disrupted", 2)
add_table(doc,
    ["Scenario", "Business concern", "Natural analysis period"],
    [
        ["Launch-Day DDoS", "Loss of availability during concentrated demand can interrupt access, purchases, support, and launch operations.", "Launch event"],
        ["Build and Source Code Theft", "Compromised development access can expose code, secrets, builds, and intellectual property.", "Annual"],
        ["Insider or Contractor Leak", "Trusted access can be misused to disclose confidential product, partner, customer, or employee information.", "Annual"],
        ["Fake Downloads and Phishing", "Brand impersonation can distribute malware, steal credentials, generate support costs, and reduce customer trust.", "Annual"],
    ],
    widths=[1.55, 4.45, 1.15], font_size=8.5)
add_para(doc, "Launch-Day DDoS receives the deepest treatment because it creates an immediate and visible test of launch readiness. If players cannot connect at the moment of peak demand, the problem moves quickly from network operations to customer experience, support, public communication, and revenue recovery. Cloudflare provides current industry context on DDoS activity, while the 2014 PlayStation Network disruption provides a historical sector precedent for a multi-day outage [23, 25]. Neither source proves a company-specific attack probability; the frequency and vulnerability ranges remain clearly labelled team assumptions.")

add_heading(doc, "2 How the Attacks Could Unfold", 1)
add_heading(doc, "2.1 Use of STRIDE and MITRE ATT and CK", 2)
add_para(doc, "STRIDE gives the team a consistent set of failure categories: Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, and Elevation of Privilege. MITRE ATT&CK provides technique-level descriptions of adversary behavior. Course Lecture 8 explains that STRIDE is useful for system-level threat identification, while ATT&CK supports technique mapping, detection analysis, and operational planning [3]. We used STRIDE across all scenarios and ATT&CK to build each four-stage attack path.")
add_table(doc,
    ["Scenario", "Main STRIDE categories", "Representative ATT and CK techniques"],
    [
        ["Launch-Day DDoS", "Information Disclosure, Spoofing, Denial of Service", "T1595 Active Scanning; T1584 Compromise Infrastructure; T1498 Network DoS; T1499 Endpoint DoS [9-12]"],
        ["Source Code Theft", "Spoofing, Elevation of Privilege, Information Disclosure, Repudiation", "T1078 Valid Accounts; T1083 File and Directory Discovery; T1005 Data from Local System; T1567 Exfiltration Over Web Service [13-16]"],
        ["Insider Leak", "Elevation of Privilege, Repudiation, Information Disclosure", "T1078; T1083; T1005; T1567 [13-16]"],
        ["Fake Downloads", "Spoofing, Tampering, Information Disclosure", "T1583.001 Domains; T1608.001 Upload Malware; T1566.002 Spearphishing Link; T1204.002 Malicious File [17-20]"],
    ], widths=[1.35, 2.35, 3.45], font_size=8.1)

add_heading(doc, "2.2 Launch Day Under Attack", 2)
add_table(doc,
    ["Stage", "Attacker activity", "Business effect", "Control interruption"],
    [
        ["1 Reconnaissance", "Scan public services, DNS, APIs, and exposed origins using T1595.", "Identifies high-value endpoints and capacity limits.", "Rate limiting, monitoring, and incident escalation."],
        ["2 Botnet preparation", "Acquire distributed infrastructure and test traffic using T1584.", "Creates capacity to bypass simple source blocking.", "Pre-provisioned scrubbing and rehearsed routing changes."],
        ["3 Traffic flood", "Generate network and application traffic using T1498.", "Saturates edge, network, or origin capacity.", "CDN scrubbing and adaptive rate limiting."],
        ["4 Business disruption", "Sustain exhaustion of customer-facing services using T1499.", "Failed access and transactions create response, recovery, and possible stakeholder loss.", "Incident drills, service prioritization, communication, and recovery."],
    ], widths=[1.2, 2.25, 2.1, 1.65], font_size=8.1)
add_para(doc, "This path is the project's central threat story. An attacker first identifies exposed services, prepares distributed infrastructure, and launches a traffic flood at the moment demand is already high. The immediate technical effect is service exhaustion; the business effect is failed player access, disrupted transactions, emergency response, and possible longer-term stakeholder loss. The workbench lets the reader open each stage and see its STRIDE category, ATT&CK technique, indicators, evidence, business effect, and control interruption point.")
add_para(doc, "The same path drives the financial model. Reconnaissance and botnet preparation influence frequency and vulnerability. CDN scrubbing and adaptive rate limiting reduce conditional success. Faster detection, service prioritization, communication, and recovery reduce primary loss. Customer, partner, contractual, and reputation consequences are treated as secondary loss because they may follow a disruption but do not occur every time.")
add_figure_placeholder(doc, 2, "Attack Paths page with the DDoS technical flow and the Traffic flood stage expanded to show indicators, FAIR links, controls, and executive decision", "Detailed Launch-Day DDoS attack path")

add_heading(doc, "3 What the Model Knows and Assumes", 1)
add_heading(doc, "3.1 Evidence Classification", 2)
add_para(doc, "The application separates four kinds of information. Public facts come from filings, framework pages, and technique references. Derived values are calculated from cited figures. Team estimates express uncertain values that public evidence cannot directly provide. Model assumptions define how the simulation behaves. This distinction prevents a methodology source from being presented as evidence for a numeric estimate.")
add_para(doc, "The strongest financial source is Take-Two's Q2 FY2027 earnings release filed with the SEC, which provides the guidance used to calculate average daily net bookings [21]. The FY2026 Form 10-K provides organizational context but does not directly prove the insider-loss range [22]. The reported $5 million Rockstar recovery cost is secondary reporting and is used only as an anchor for a wider source-theft range [24]. Open FAIR and NIST CSF support the model and control structure, not the numeric estimates [7, 8].")

add_heading(doc, "3.2 Evidence-Anchored Model Inputs", 2)
add_table(doc,
    ["Scenario", "Frequency low likely high", "Vulnerability low likely high", "Primary loss low likely high", "Secondary loss low likely high", "Secondary occurrence"],
    [
        ["DDoS", "0.60 / 0.85 / 0.97 per launch", "4% / 12% / 35%", "$0.84M / $9.70M / $80.62M", "$3.43M / $13.70M / $85.63M", "35%"],
        ["Source theft", "0.6 / 1.5 / 3.0 per year", "3% / 10% / 25%", "$2.80M / $5.00M / $25.00M", "$1.00M / $6.00M / $60.00M", "30%"],
        ["Insider leak", "0.3 / 0.8 / 1.5 per year", "5% / 15% / 35%", "$1.50M / $4.90M / $18.00M", "$0.50M / $5.00M / $40.00M", "25%"],
        ["Fake downloads", "4 / 12 / 30 per year", "2% / 6% / 15%", "$0.50M / $3.00M / $12.00M", "$0.50M / $4.00M / $30.00M", "20%"],
    ], widths=[1.0, 1.3, 1.25, 1.35, 1.35, 0.85], font_size=7.4)
add_para(doc, "Low, most-likely, and high values define triangular distributions. We used triangular distributions because the available evidence supports bounded judgment ranges but is not sufficient to fit a reliable empirical severity distribution. Lecture 5 distinguishes event-count distributions such as Poisson from positive severity distributions, and Lecture 10 recommends ranges, distributions, and Monte Carlo simulation when cyber data is incomplete [2, 4]. A more mature organization could replace the triangular severity distributions with fitted lognormal or other distributions after collecting enough loss data.")

add_heading(doc, "3.3 DDoS Primary Loss Derivation", 2)
add_para(doc, "DDoS primary loss is derived instead of entered as one unexplained amount. The formula is:")
equation = doc.add_paragraph()
equation.alignment = WD_ALIGN_PARAGRAPH.CENTER
equation.add_run("Outage days × average daily net bookings × launch uplift × online-dependent share × unrecovered share + response cost").bold = True
add_table(doc,
    ["Component", "Low", "Most likely", "High", "Basis"],
    [
        ["Outage duration", "0.25 day", "1 day", "3 days", "Historical sector precedent and team range [23]"],
        ["Average daily net bookings", "$36.41M", "$37.23M", "$38.04M", "Q3 guidance divided by 92 days [21]"],
        ["Launch uplift", "1.0×", "1.5×", "2.5×", "Team estimate"],
        ["Online-dependent share", "25%", "40%", "55%", "Team estimate"],
        ["Unrecovered share", "15%", "30%", "45%", "Team estimate"],
        ["Response cost", "$0.50M", "$3.00M", "$10.00M", "Team estimate"],
        ["Derived primary loss", "$0.84M", "$9.70M", "$80.62M", "Calculated from the six components"],
    ], widths=[1.45, 1.0, 1.0, 1.0, 2.75], font_size=8.2)
add_para(doc, "Secondary DDoS loss uses 0.1%, 0.4%, and 2.5% of a $3.425 billion reference figure, producing $3.425 million, $13.70 million, and $85.625 million. These percentages are team assumptions. The model applies secondary loss in 35% of successful DDoS events rather than adding it automatically to every event.")
add_figure_placeholder(doc, 3, "Risk Simulator evidence register showing the DDoS loss formula, component values, evidence types, confidence, and source links", "Transparent DDoS loss derivation and evidence register")

add_heading(doc, "4 Turning Uncertainty into Financial Risk", 1)
add_heading(doc, "4.1 FAIR-Style Structure", 2)
add_para(doc, "The application uses a FAIR-style structure rather than claiming an official certified FAIR assessment. FAIR organizes risk around the frequency and magnitude of loss [7]. Our implementation uses threat event frequency, vulnerability or conditional success probability, primary loss, secondary loss, and secondary-loss occurrence probability. The model equation is:")
equation = doc.add_paragraph()
equation.alignment = WD_ALIGN_PARAGRAPH.CENTER
equation.add_run("Loss = successful events × primary loss + secondary-loss events × secondary loss").bold = True
add_para(doc, "For a launch event, the model treats threat occurrence and successful disruption as probability tests. For annual scenarios, the number of threat events is sampled from a Poisson distribution, and successful events are sampled conditionally. Poisson is appropriate for discrete event counts under its assumptions, which the course addresses in Lecture 5 [2].")

add_heading(doc, "4.2 Monte Carlo Process", 2)
add_numbered(doc, [
    "Select the scenario, natural analysis period, evidence profile, controls, trial count, and seed.",
    "Sample frequency, vulnerability, primary loss, and secondary loss from their triangular ranges.",
    "Sample threat-event count, conditional success, and whether secondary loss occurs.",
    "Calculate baseline loss without controls.",
    "Reuse the same random values and apply control multipliers to calculate residual loss.",
    "Repeat the process 10,000 times and summarize the resulting distributions.",
])
add_para(doc, "This is Monte Carlo simulation: repeated random sampling produces a distribution of possible results instead of a single point estimate [5]. A fixed seed of 243 makes identical inputs reproducible. Baseline and residual results use paired random draws, so the difference is caused by the controls rather than by two lucky or unlucky random samples.")
add_para(doc, "Annual event counts are not capped. The Python model can produce any count supported by the sampled Poisson distribution. The browser receives 30 histogram bins rather than all 10,000 raw losses, which keeps the interface responsive while preserving the distribution shape.")

add_heading(doc, "4.3 Metrics and Sensitivity", 2)
add_bullets(doc, [
    "Mean is the average modeled loss across all trials, including zero-loss trials.",
    "P50 is the median. A P50 of $0 means at least half the simulated periods had no successful material loss event.",
    "P90, P95, and P99 describe increasingly severe tail outcomes. P95 is exceeded in about 5% of trials; P99 is exceeded in about 1%.",
    "Threshold probabilities measure how often simulated loss exceeds $10 million, $25 million, $50 million, or $100 million.",
    "Spearman rank sensitivity measures whether larger sampled inputs are associated with larger losses without requiring a linear relationship.",
    "Tornado sensitivity moves one input from its low to high estimate while reusing the same trials, showing the change in expected loss.",
])
add_para(doc, "Sensitivity matters because the output is only as useful as its assumptions. It identifies which uncertain inputs deserve better evidence or management attention. Lecture 10 identifies sensitivity analysis as a way to test model robustness under uncertainty [4].")
add_figure_placeholder(doc, 4, "Risk Simulator showing the model-run summary, baseline and residual metrics, loss distribution, and sensitivity views", "Monte Carlo results and sensitivity analysis")

add_heading(doc, "5 How the Workbench Delivers the Analysis", 1)
add_para(doc, "The workbench is not a static report with fixed answers. It is a working web application that allows the user to move between the executive view, technical attack paths, financial simulation, and control planning without losing the selected scenario or controls. This design is important because an executive can see the recommendation, while an analyst can inspect the assumptions and a technical team can trace the control back to the attack stage it is intended to stop.")
add_heading(doc, "5.1 System Architecture", 2)
add_table(doc,
    ["Layer", "Technology", "Purpose"],
    [
        ["Frontend", "React JavaScript", "Builds reusable pages and components for the four decision views."],
        ["Build and development", "Vite", "Runs the development server and creates the optimized production bundle."],
        ["Navigation", "React Router", "Provides four real routes and shared layout."],
        ["Shared state", "React Context", "Keeps scenario, controls, mode, results, readiness, and evidence profile consistent across pages."],
        ["Charts", "Plotly", "Renders loss distributions, sensitivity, portfolio results, and the heat map."],
        ["API", "Flask", "Returns configuration and runs scenario or portfolio simulations."],
        ["Quantitative model", "Python NumPy and SciPy", "Samples distributions, calculates percentiles, and performs correlation analysis."],
        ["Production delivery", "Flask plus Vite build", "Serves the React production files and API as one application."],
    ], widths=[1.25, 1.55, 4.3], font_size=8.3)

add_heading(doc, "5.2 Main Application Pages", 2)
add_bullets(doc, [
    "Executive Overview shows the selected scenario, readiness, baseline and residual loss, expected loss avoided, P90, and a qualitative heat map.",
    "Attack Paths shows all four scenarios. DDoS includes technical flow, response timeline, substeps, indicators, FAIR links, decisions, MITRE techniques, STRIDE tags, evidence, and control interruption points.",
    "Risk Simulator exposes assumptions, analysis period, evidence profile, secondary-loss probability, distribution metrics, thresholds, charts, sensitivity, and evidence. It can export a JSON summary.",
    "Control Investment Planner supports selected-scenario and all-scenario views. It shows cost ranges, model effects, implementation time, confidence, coverage, standalone priority, net benefit, ROSI, and portfolio tail risk.",
])

add_heading(doc, "5.3 API and Shared Calculation Flow", 2)
add_table(doc,
    ["Endpoint", "Input or output", "Role"],
    [
        ["GET /api/health", "Service status", "Confirms that the Flask calculation service is available."],
        ["GET /api/config", "Scenarios, controls, paths, sources, methodology", "Keeps model configuration and evidence centralized in Python."],
        ["POST /api/simulate", "Scenario, controls, period, trials, seed, profile, optional custom inputs", "Returns baseline and residual metrics, histograms, economics, priorities, and sensitivity."],
        ["POST /api/portfolio", "Controls, trials, seed, profile", "Combines scenario trials using each scenario's natural period and counts shared control cost once."],
    ], widths=[1.45, 3.0, 2.65], font_size=8.2)
add_para(doc, "React sends a simulation request whenever shared scenario, control, mode, profile, or applied assumptions change. Exact-match browser caching provides a demonstration fallback after a calculation has run. Flask remains the calculation authority; the website does not run from Excel. The team used the workbook as an evidence and reconciliation artifact, then transferred the stronger assumptions into Python to avoid spreadsheet drift and hidden formulas.")

add_heading(doc, "5.4 Verification", 2)
add_para(doc, "The backend test suite contains 22 automated tests covering reproducibility, assumption validation, control applicability, secondary-loss probability, profile differences, all four scenarios, portfolio periods, expected control cost, attack-path references, and API responses. The frontend production build is also verified with Vite. The tests do not prove that team estimates are correct; they confirm that the implemented model follows its stated rules consistently.")

add_heading(doc, "6 What the Analysis Found", 1)
add_heading(doc, "6.1 Scenario Risk Results", 2)
add_table(doc,
    ["Scenario", "Basis", "Baseline mean", "Residual mean", "Baseline P95", "Residual P95"],
    [
        ["Launch-Day DDoS", "Launch", "$5.70M", "$1.52M", "$47.91M", "$0.00M"],
        ["Source Code Theft", "Annual", "$3.84M", "$0.80M", "$25.26M", "$4.15M"],
        ["Insider Leak", "Annual", "$1.91M", "$0.47M", "$13.34M", "$2.64M"],
        ["Fake Downloads", "Annual", "$8.91M", "$1.44M", "$33.71M", "$8.21M"],
    ], widths=[1.65, 0.75, 1.2, 1.2, 1.2, 1.2], font_size=8.5)
add_para(doc, "The four scenarios do not produce the same answer, which is exactly why the workbench is useful. Fake downloads create the highest baseline mean in this model because they can occur repeatedly across the year. DDoS has a lower mean but a highly concentrated launch-day tail: its baseline P95 reaches $47.91 million. Each residual mean uses the controls selected for that attack path. A residual DDoS P95 of $0 means at least 95% of controlled launch trials contain no material modeled loss, but the $52.77 million residual P99 shows that a rare severe launch failure remains possible.")
add_table(doc,
    ["Scenario", "Selected controls", "Expected cost", "Loss avoided", "Net benefit", "ROSI"],
    [
        ["Launch-Day DDoS", "CDN scrubbing; rate limiting", "$1.14M", "$4.19M", "$3.04M", "2.66×"],
        ["Source Code Theft", "Repository hardening; least privilege", "$0.90M", "$3.05M", "$2.14M", "2.37×"],
        ["Insider Leak", "Least privilege; DLP monitoring", "$0.77M", "$1.45M", "$0.67M", "0.87×"],
        ["Fake Downloads", "Brand monitoring; phishing-resistant MFA", "$0.80M", "$7.47M", "$6.67M", "8.30×"],
    ], widths=[1.45, 2.25, 0.95, 0.95, 0.9, 0.65], font_size=8.2)
add_para(doc, "Expected cost is the mean of each control's triangular low, most-likely, and high cost range. Loss avoided equals baseline mean minus residual mean. Net benefit subtracts expected control cost from modeled loss avoided. ROSI divides net benefit by control cost. A ROSI of 2.66 means the modeled net benefit is 2.66 times the expected control cost; it does not mean the control guarantees a financial return.")

add_heading(doc, "6.2 Portfolio Results", 2)
add_table(doc,
    ["Measure", "Baseline", "All controls", "Interpretation"],
    [
        ["Mean", "$20.18M", "$2.29M", "Average combined modeled loss."],
        ["P50", "$11.49M", "$0.00M", "Median combined loss."],
        ["P95", "$71.34M", "$9.92M", "Severe outcome exceeded in about 5% of trials."],
        ["P99", "$110.54M", "$40.30M", "Extreme tail outcome exceeded in about 1% of trials."],
        ["Probability above $50M", "11.38%", "0.57%", "Share of trials above the threshold."],
        ["Probability above $100M", "1.64%", "0.00%", "No selected-control trial exceeded $100M in this fixed run."],
    ], widths=[1.55, 1.0, 1.0, 3.55], font_size=8.4)
add_para(doc, "The portfolio view reveals the value of treating launch security as one connected problem. All nine controls have an expected combined cost of $3.57 million. The model estimates $17.90 million of loss avoided, leaving $14.33 million net benefit and a ROSI of 4.01. More importantly, the probability of loss above $50 million falls from 11.38% to 0.57%, while P99 falls from $110.54 million to $40.30 million. The portfolio is a decision comparison rather than a conventional annual forecast because it combines one launch-event DDoS exposure with annual exposures for the other scenarios.")
add_figure_placeholder(doc, 5, "Control Planner in all-scenario portfolio mode showing investment, net benefit, ROSI, P95, P99, distribution, and scenario table", "All-scenario control portfolio and tail-risk reduction")

add_heading(doc, "7 Which Controls Should Be Funded", 1)
add_heading(doc, "7.1 Portfolio Ranking", 2)
add_para(doc, "The ranking below tests each control alone across every scenario it covers. Priority is based on standalone expected net benefit, with loss avoided as the tie-breaker. This avoids a hidden weighted score. The ranking does not mean controls should be implemented without architecture review; it is a financial comparison under the stated assumptions.")
add_table(doc,
    ["Rank", "Control", "Expected cost", "Loss avoided", "Net benefit", "ROSI"],
    [
        ["1", "Phishing-resistant MFA", "$0.51M", "$7.89M", "$7.38M", "14.57×"],
        ["2", "Incident drills", "$0.13M", "$6.11M", "$5.98M", "45.99×"],
        ["3", "Brand monitoring and takedown", "$0.30M", "$4.96M", "$4.66M", "15.71×"],
        ["4", "CDN and DDoS scrubbing", "$0.87M", "$3.58M", "$2.71M", "3.13×"],
        ["5", "Least-privilege access reviews", "$0.33M", "$3.00M", "$2.66M", "7.99×"],
        ["6", "DLP and behavior monitoring", "$0.44M", "$3.09M", "$2.65M", "6.03×"],
        ["7", "Repository and CI CD hardening", "$0.57M", "$2.39M", "$1.82M", "3.19×"],
        ["8", "Adaptive rate limiting", "$0.28M", "$1.92M", "$1.64M", "5.93×"],
        ["9", "Contractor offboarding automation", "$0.15M", "$1.09M", "$0.94M", "6.18×"],
    ], widths=[0.45, 2.45, 1.05, 1.05, 1.05, 0.75], font_size=8.2)
add_table(doc,
    ["Control", "Implementation range", "Confidence", "Scenario coverage"],
    [
        ["Phishing-resistant MFA", "4 to 14 weeks; 8 likely", "High", "Source theft; fake downloads"],
        ["Incident drills", "1 to 4 weeks; 2 likely", "Medium", "All four scenarios"],
        ["Brand monitoring", "2 to 6 weeks; 4 likely", "Medium", "Fake downloads"],
        ["CDN and DDoS scrubbing", "2 to 7 weeks; 4 likely", "High", "DDoS"],
        ["Least privilege", "3 to 10 weeks; 6 likely", "Medium", "Source theft; insider leak"],
        ["DLP monitoring", "5 to 14 weeks; 8 likely", "Medium", "Source theft; insider leak"],
        ["Repository hardening", "4 to 12 weeks; 7 likely", "Medium", "Source theft"],
        ["Adaptive rate limiting", "2 to 5 weeks; 3 likely", "Medium", "DDoS"],
        ["Contractor offboarding", "2 to 7 weeks; 4 likely", "Medium", "Insider leak"],
    ], widths=[2.15, 1.85, 0.85, 2.35], font_size=7.4)

add_heading(doc, "7.2 Recommended Investment Order", 2)
add_para(doc, "The order is produced by a repeatable financial comparison rather than by team preference or an unexplained weighted score. The model first calculates the four-scenario baseline using DDoS on a launch-event basis and the other scenarios on an annual basis. It then tests each control by itself, applying the control only to the scenarios it covers while leaving every other scenario at baseline. The same 10,000 paired trials and fixed seed are reused so that the measured difference comes from the control rather than a different random sample.")
add_para(doc, "For each standalone test, loss avoided equals the portfolio baseline mean minus the mean with that control. Expected cost is the mean of the control's triangular low, most-likely, and high cost estimates: (low + most likely + high) / 3. Net benefit equals loss avoided minus expected cost. The model ranks controls from highest to lowest net benefit, using loss avoided only to break a tie. ROSI is also reported as net benefit divided by cost, but it does not determine the order because a low-cost control can have a high percentage return while preventing fewer dollars of loss. Confidence, implementation time, and scenario coverage remain visible as decision context rather than hidden score weights.")
add_para(doc, "A worked example shows the calculation. MFA has cost estimates of $0.32 million, $0.48 million, and $0.72 million, so its expected cost is ($0.32M + $0.48M + $0.72M) / 3 = $0.51 million after rounding. The baseline portfolio mean is $20.18 million. With MFA applied by itself, the modeled portfolio mean is approximately $12.29 million, so loss avoided is $20.18M - $12.29M = $7.89 million. Subtracting the $0.51 million expected cost gives $7.38 million net benefit. This is the largest standalone net benefit, so MFA receives rank 1.")
add_para(doc, "The complete ordering follows directly from the descending net-benefit results: MFA $7.38 million; incident drills $5.98 million; brand monitoring $4.66 million; CDN and DDoS scrubbing $2.71 million; least privilege $2.66 million; DLP monitoring $2.65 million; repository hardening $1.82 million; adaptive rate limiting $1.64 million; and contractor offboarding $0.94 million. Because $7.38M > $5.98M > $4.66M and so on, these become ranks 1 through 9. No separate weighted priority formula is used.")
add_para(doc, "This method places phishing-resistant MFA first. Its expected standalone cost is $0.51 million, while it avoids $7.89 million of modeled loss across source-code theft and fake-download scenarios, producing the largest net benefit at $7.38 million. Incident drills rank second: their $0.13 million expected cost and coverage of all four scenarios produce $6.11 million of loss avoided, $5.98 million net benefit, and the highest ROSI at 45.99. Drills do not rank first because the primary ordering measure is total net benefit, not ROSI. Their modeled value should still be validated through exercise performance data because it depends on assumed response and recovery effects.")
add_para(doc, "Brand monitoring and takedown ranks third with $4.66 million net benefit because fake downloads have the largest baseline mean and the control reduces both recurring attempts and downstream loss. CDN and DDoS scrubbing ranks fourth with $2.71 million net benefit. Although fourth across the portfolio, it remains the primary launch-specific investment because it is the strongest direct interruption point for DDoS frequency, conditional success, and outage loss. Portfolio rank therefore supports budget sequencing; it does not replace scenario-specific operational judgment.")
add_para(doc, "Least-privilege reviews, DLP monitoring, and repository hardening form the next identity and data-protection layer. Adaptive rate limiting and contractor offboarding remain positive, comparatively inexpensive investments and should be scheduled with the related application and identity work. These standalone results cannot simply be added together: when controls affect the same risk factors, their benefits overlap. The combined nine-control portfolio is therefore simulated separately.")
add_para(doc, "Finally, the cost model represents expected implementation expenditure but does not fully quantify indirect costs such as training, process friction, staffing, or adoption. Lecture 10 distinguishes direct, indirect, and organizational control costs [4]. Before a real purchase, the organization should replace team estimates with vendor quotes and internal labor estimates, then rerun the workbench to confirm whether the order changes.")

add_heading(doc, "8 Limitations and Interpretation", 1)
add_bullets(doc, [
    "The model is FAIR-style decision support, not an official Open FAIR assessment or audited financial forecast.",
    "Public evidence is limited. Many frequency, vulnerability, loss, control-effectiveness, cost, and implementation-time values are team estimates.",
    "Triangular distributions are transparent but may underrepresent skewed severity compared with a fitted lognormal or other empirical distribution.",
    "Annual Poisson counts assume event independence and a stable sampled rate within a trial. Coordinated or correlated attacks may violate that assumption.",
    "Control multipliers are applied multiplicatively. Interactions, implementation failure, control dependencies, and attacker adaptation are simplified.",
    "The portfolio uses independent deterministic random streams for each scenario and does not model common-cause or correlated losses. Lecture 10 notes that correlated risk can amplify losses [4].",
    "The mixed-basis portfolio combines a launch event with three annual scenarios, so it is best used to compare investments rather than as a literal annual total.",
    "A P50 of zero is plausible when most trials contain no successful material event. It does not imply zero risk because mean and tail losses remain positive.",
    "The readiness index is a team-designed average of Prevent, Detect, Respond, and Recover dimensions. It is separate from the financial model and is not an official NIST score.",
    "The qualitative heat map provides a communication aid. Its positions are team assessments and should not be confused with the Monte Carlo probabilities.",
])
add_para(doc, "These limitations are visible in the interface through evidence classifications, rationales, confidence labels, source notes, assumption profiles, model disclaimers, and the evidence register. The existing original-team estimates are retained as a comparison profile, while evidence-anchored assumptions are the default.")

add_heading(doc, "9 Final Decision", 1)
add_para(doc, "A major game launch creates a rare concentration of technical dependence, commercial value, and public attention. The team's contribution is a workbench that makes that risk explorable. It follows an attack from adversary behavior to business interruption, quantifies a range of possible financial outcomes, and shows how a control changes both the attack path and the investment case.")
add_para(doc, "The main decision is to fund phishing-resistant MFA and incident drills as cross-scenario priorities, while treating CDN scrubbing as essential for the launch-specific DDoS scenario and brand monitoring as a high-value response to fake downloads. Least privilege, DLP, repository hardening, rate limiting, and offboarding complete the layered control plan. The results justify these recommendations under the current assumptions, but the values should be recalibrated with internal telemetry, incident data, vendor quotes, staffing estimates, and exercise results before real deployment.")
add_para(doc, "The workbench's selling point is therefore not one dramatic loss figure. It is the ability to connect a launch-day threat, its evidence and uncertainty, the control that interrupts it, and the financial reason to act. That turns cyber risk from a technical warning into a decision executives can examine, challenge, and fund.")

add_heading(doc, "References", 1)
references = [
    "[1] Mattarock, M. Cyber Risk Modeling Introduction and Course Overview. Course Lecture 1, 25 August 2025.",
    "[2] Mattarock, M. Cyber Risk Modeling Class 5. Probability Distributions. Course Lecture 5, 8 September 2026.",
    "[3] Mattarock, M. Cyber Risk Modeling Class 8. STRIDE, DREAD, MITRE ATT and CK, and FAIR-Compatible Integration. Course Lecture 8, 17 September 2026.",
    "[4] Mattarock, M. Cyber Risk Modeling Class 10. Limitations of FAIR, Uncertainty, Systemic Risk, and Control Costs. Course Lecture 10, 24 September 2026.",
    "[5] Mattarock, M. Cyber Risk Modeling Class 11 Monte Carlo Analysis. Course Lecture 11, 30 September 2025.",
    "[6] Mattarock, M. Cyber Risk Modeling Class 12. Measurement, Loss Event Frequency, and Frequency and Magnitude. Course Lecture 12, 1 October 2026.",
    "[7] The Open Group. Open FAIR. https://www.opengroup.org/open-fair. Accessed 20 November 2026.",
    "[8] National Institute of Standards and Technology. Cybersecurity Framework 2.0. https://www.nist.gov/cyberframework. Accessed 21 November 2026.",
    "[9] MITRE. Active Scanning T1595. https://attack.mitre.org/techniques/T1595/. Accessed 21 November 2026.",
    "[10] MITRE. Compromise Infrastructure T1584. https://attack.mitre.org/techniques/T1584/. Accessed 21 November 2026.",
    "[11] MITRE. Network Denial of Service T1498. https://attack.mitre.org/techniques/T1498/. Accessed 21 November 2026.",
    "[12] MITRE. Endpoint Denial of Service T1499. https://attack.mitre.org/techniques/T1499/. Accessed 21 November 2026.",
    "[13] MITRE. Valid Accounts T1078. https://attack.mitre.org/techniques/T1078/. Accessed 24 November 2026.",
    "[14] MITRE. File and Directory Discovery T1083. https://attack.mitre.org/techniques/T1083/. Accessed 24 November 2026.",
    "[15] MITRE. Data from Local System T1005. https://attack.mitre.org/techniques/T1005/. Accessed 24 November 2026.",
    "[16] MITRE. Exfiltration Over Web Service T1567. https://attack.mitre.org/techniques/T1567/. Accessed 24 November 2026.",
    "[17] MITRE. Acquire Infrastructure Domains T1583.001. https://attack.mitre.org/techniques/T1583/001/. Accessed 24 November 2026.",
    "[18] MITRE. Stage Capabilities Upload Malware T1608.001. https://attack.mitre.org/techniques/T1608/001/. Accessed 24 November 2026.",
    "[19] MITRE. Phishing Spearphishing Link T1566.002. https://attack.mitre.org/techniques/T1566/002/. Accessed 24 November 2026.",
    "[20] MITRE. User Execution Malicious File T1204.002. https://attack.mitre.org/techniques/T1204/002/. Accessed 24 November 2026.",
    "[21] Take-Two Interactive Software. Q2 Fiscal Year 2027 Earnings Release. U.S. Securities and Exchange Commission. https://www.sec.gov/Archives/edgar/data/946581/000162828026072175/ttwo2q27earningsrelease.htm. Accessed 9 November 2026.",
    "[22] Take-Two Interactive Software. Fiscal Year 2026 Form 10-K. https://ir.take2games.com/static-files/31b9a69d-016e-4d72-9d91-b911f1313bed. Accessed 20 November 2026.",
    "[23] The Register. PlayStation clambers back online after DDoS disruption. https://www.theregister.com/2014/12/27/playstation_clambers_back_online/. Accessed 20 November 2026.",
    "[24] GamesRadar. Report on the cost and staff time associated with the Rockstar leak. https://www.gamesradar.com/the-gta-6-leak-cost-rockstar-dollar5-million-and-thousands-of-hours-of-staff-time/. Accessed 20 November 2026.",
    "[25] Cloudflare. DDoS Threat Report 2026 Q3. https://blog.cloudflare.com/ddos-threat-report-2026-q3/. Accessed 20 November 2026.",
]
for reference in references:
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Inches(0.2)
    p.paragraph_format.first_line_indent = Inches(-0.2)
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run(reference)
    r.font.size = Pt(7.8)

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
doc.save(OUTPUT)
print(OUTPUT)
