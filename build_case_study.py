import csv
import html
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parent
CSV_PATH = ROOT / "outputs" / "final_audit.csv"
OUT = ROOT / "index.html"

def esc(value):
    return html.escape(str(value or ""))

with CSV_PATH.open("r", encoding="utf-8-sig", newline="") as f:
    rows = list(csv.DictReader(f))

total = len(rows)
review = sum(r.get("verification_status") == "needs_review" for r in rows)
verified = total - review
source_accessible = sum(str(r.get("api_source_accessible", "")).lower() == "true" for r in rows)
composio_available = sum(r.get("composio_status") == "available" for r in rows)
composio_not_found = sum(r.get("composio_status") == "not_found" for r in rows)
low_conf = sum(r.get("confidence") == "low" for r in rows)

cat = Counter(r.get("category", "") for r in rows)
cat_review = Counter(r.get("category", "") for r in rows if r.get("verification_status") == "needs_review")

sample_candidates = [
    r for r in rows
    if r.get("composio_status") == "available"
    and str(r.get("composio_tool_count", "")).isdigit()
]
sample = sorted(sample_candidates, key=lambda r: int(r.get("composio_tool_count", "0")), reverse=True)[:5]
sample += [r for r in rows if r.get("verification_status") == "needs_review"][:5]

table_rows = []
for r in rows:
    docs = "Yes" if str(r.get("api_source_accessible", "")).lower() == "true" else "No"
    table_rows.append(
        "<tr>"
        f"<td><strong>{esc(r.get('app_name'))}</strong></td>"
        f"<td>{esc(r.get('category'))}</td>"
        f"<td>{docs}</td>"
        f"<td>{esc(r.get('composio_status'))}</td>"
        f"<td>{esc(r.get('composio_tool_count'))}</td>"
        f"<td><span class=\"badge {esc(r.get('verification_status'))}\">{esc(r.get('verification_status'))}</span></td>"
        f"<td>{esc(r.get('confidence'))}</td>"
        "</tr>"
    )

sample_rows = []
for r in sample:
    try:
        tools = int(r.get("composio_tool_count", "0") or 0)
    except ValueError:
        tools = 0
    status = "HIT" if r.get("composio_status") == "available" and tools > 0 else "MISS / REVIEW"
    sample_rows.append(
        "<tr>"
        f"<td>{esc(r.get('app_name'))}</td>"
        f"<td>{esc(r.get('composio_toolkit'))}</td>"
        f"<td>{esc(r.get('composio_status'))}</td>"
        f"<td>{esc(r.get('composio_tool_count'))}</td>"
        f"<td><b>{status}</b></td>"
        "</tr>"
    )

cat_rows = "".join(
    f"<tr><td>{esc(k)}</td><td>{v}</td><td>{cat_review.get(k, 0)}</td></tr>"
    for k, v in cat.most_common()
)

template = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Composio 100-App Integration Audit - Case Study</title>
<style>
:root {--bg:#0b1020;--panel:#121a2d;--panel2:#18223a;--text:#eef3ff;--muted:#9eabc5;--line:#2a3652;--accent:#77e0c1;--warn:#ffcc66}
* {box-sizing:border-box}
body {margin:0;background:linear-gradient(180deg,#09101f,#0e1526 40%,#0a1020);color:var(--text);font:15px/1.55 Inter,Segoe UI,Arial,sans-serif}
main {max-width:1180px;margin:auto;padding:42px 24px 70px}
.eyebrow {color:var(--accent);font-weight:800;letter-spacing:.12em;text-transform:uppercase;font-size:12px}
h1 {font-size:44px;line-height:1.05;margin:10px 0 14px;max-width:900px}
h2 {font-size:25px;margin:0 0 14px}
p {color:var(--muted);max-width:900px}
.hero {padding:34px;border:1px solid var(--line);background:radial-gradient(circle at 90% 0,#1c3154 0,transparent 38%),var(--panel);border-radius:24px}
.headline {font-size:20px;color:#fff;max-width:920px;margin:0 0 22px}
.grid {display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:22px 0}
.card {background:var(--panel2);border:1px solid var(--line);border-radius:16px;padding:18px}
.num {font-size:30px;font-weight:850}
.label {color:var(--muted);font-size:13px}
section {margin-top:34px}
.panel {background:rgba(18,26,45,.88);border:1px solid var(--line);border-radius:18px;padding:22px}
.cols {display:grid;grid-template-columns:1fr 1fr;gap:16px}
.steps {display:grid;grid-template-columns:repeat(5,1fr);gap:10px}
.step {background:var(--panel2);padding:16px;border-radius:14px;border:1px solid var(--line)}
.step b {display:block;color:var(--accent);margin-bottom:5px}
table {width:100%;border-collapse:collapse;font-size:13px}
th,td {padding:10px 9px;border-bottom:1px solid var(--line);text-align:left}
th {color:#cbd6ee;position:sticky;top:0;background:#121a2d}
tbody tr:hover {background:#18233b}
.badge {display:inline-block;padding:3px 8px;border-radius:999px;font-size:11px;font-weight:800}
.verified_with_source_limitation {background:#244a45;color:#9ff1dc}
.needs_review {background:#4a3a25;color:#ffd98a}
.controls {display:flex;gap:10px;flex-wrap:wrap;margin:14px 0}
input,select {background:#0d1527;border:1px solid var(--line);color:white;padding:10px;border-radius:10px}
.small {font-size:12px;color:var(--muted)}
code {background:#0b1323;padding:3px 6px;border-radius:6px;color:#bdefff}
pre {background:#080e1b;border:1px solid var(--line);padding:16px;border-radius:12px;overflow:auto;color:#dce7ff}
a {color:var(--accent)}
.honest {border-left:4px solid var(--warn);padding-left:16px}
.good {border-left:4px solid var(--accent);padding-left:16px}
@media(max-width:800px) {h1 {font-size:34px}.grid {grid-template-columns:1fr 1fr}.cols,.steps {grid-template-columns:1fr}}
</style>
</head>
<body>
<main>
<div class="hero">
<div class="eyebrow">Composio - AI Product Ops Case Study</div>
<h1>Auditing 100 apps for agent-ready integrations</h1>
<p class="headline"><b>Headline:</b> A two-pass research + verification agent turned a 100-app integration audit into a structured evidence trail - while explicitly separating confirmed findings from source-limited and review-needed cases.</p>
<p>This page is the reviewer-facing deliverable. It shows the output, workflow, what the agent automated, where human review remains necessary, and the honest failure modes.</p>
</div>

<div class="grid">
<div class="card"><div class="num">__TOTAL__</div><div class="label">apps audited</div></div>
<div class="card"><div class="num">__VERIFIED__</div><div class="label">verified / source-limited</div></div>
<div class="card"><div class="num">__REVIEW__</div><div class="label">need review</div></div>
<div class="card"><div class="num">__COMPOSIO__</div><div class="label">Composio toolkits found</div></div>
</div>

<section><div class="panel">
<h2>What the audit found</h2>
<p class="good"><b>Pattern 1:</b> Composio toolkit discovery is the strongest machine-verifiable signal in this run: a toolkit returning tools gives concrete integration evidence.</p>
<p class="honest"><b>Pattern 2:</b> Documentation access is a separate problem from API existence. Blocked or JS-heavy pages are recorded as source-access limitations, not treated as proof of "no API".</p>
<p class="honest"><b>Pattern 3:</b> __REVIEW__ apps remain in <b>needs_review</b>; the system intentionally does not turn uncertainty into a false positive.</p>
<p class="small">Run-level signals: official documentation fetched for __SOURCE_ACCESSIBLE__/__TOTAL__; Composio returned tools for __COMPOSIO__/__TOTAL__; __NOT_FOUND__ supplied toolkit lookups returned no tools; __LOW_CONF__ rows had low research confidence.</p>
</div></section>

<section><h2>The agent / workflow</h2>
<div class="steps">
<div class="step"><b>01 - Load</b>Read the 100-app dataset and research configuration.</div>
<div class="step"><b>02 - Research</b>Fetch official docs and inspect Composio toolkit availability.</div>
<div class="step"><b>03 - Structure</b>Store source access, tool counts, confidence and limitations as JSON.</div>
<div class="step"><b>04 - Verify</b>Check required fields, source access, toolkit results and confidence.</div>
<div class="step"><b>05 - Publish</b>Generate the final CSV + JSON audit and this case study.</div>
</div>
</section>

<section class="cols">
<div class="panel"><h2>What the agent automated</h2>
<ul>
<li>100-app batch processing</li>
<li>Official documentation fetching</li>
<li>Composio toolkit discovery</li>
<li>Retry on toolkit lookup failure</li>
<li>Confidence and verification classification</li>
<li>Structured JSON + CSV output</li>
</ul></div>
<div class="panel"><h2>Where a human is still needed</h2>
<ul>
<li>Review apps with blocked or inaccessible documentation.</li>
<li>Resolve ambiguous or fuzzy toolkit mappings.</li>
<li>Confirm authentication requirements where provider-specific setup is gated.</li>
<li>Spot-check important claims against current first-party sources.</li>
<li>Decide whether a source limitation is acceptable for production use.</li>
</ul></div>
</section>

<section><div class="panel">
<h2>Verification: sample spot-check</h2>
<p>This sample is an <b>output-consistency spot-check</b>, not a fabricated accuracy percentage. A "HIT" means the audit row itself reports a live Composio toolkit with a non-zero tool count. "MISS / REVIEW" means the row needs human/source review.</p>
<table><thead><tr><th>App</th><th>Toolkit</th><th>Observed status</th><th>Tools</th><th>Check</th></tr></thead><tbody>__SAMPLE_ROWS__</tbody></table>
<p class="small">For a true external accuracy score, expected labels must be independently established before comparing them with agent output. This implementation does not invent that ground truth.</p>
</div></section>

<section><div class="panel">
<h2>Category matrix</h2>
<table><thead><tr><th>Category</th><th>Apps</th><th>Needs review</th></tr></thead><tbody>__CATEGORY_ROWS__</tbody></table>
</div></section>

<section><div class="panel">
<h2>Full 100-app audit</h2>
<div class="controls"><input id="q" placeholder="Search app..." oninput="filterRows()"><select id="status" onchange="filterRows()"><option value="">All statuses</option><option>verified_with_source_limitation</option><option>needs_review</option></select></div>
<div style="max-height:520px;overflow:auto"><table id="audit"><thead><tr><th>App</th><th>Category</th><th>Docs fetched</th><th>Composio</th><th>Tools</th><th>Verification</th><th>Confidence</th></tr></thead><tbody>__TABLE_ROWS__</tbody></table></div>
</div></section>

<section class="cols">
<div class="panel"><h2>Proof / runnable trigger</h2>
<p>The research agent is runnable locally from the source repository:</p>
<pre>python -m app.agents.orchestrator
python -m app.agents.verifier
python outputs\final_audit.py</pre>
<p>The final artifacts are <code>outputs/final_audit.csv</code> and <code>outputs/final_audit.json</code>.</p>
</div>
<div class="panel"><h2>Source & reproducibility</h2>
<p>Source repository: <a href="REPLACE_REPO_URL" target="_blank">GitHub repository - replace this link</a></p>
<p>Setup is documented in <code>README.md</code>. Secrets are kept outside the repository in <code>.env</code>.</p>
</div>
</section>

<section><div class="panel">
<h2>What I would improve next</h2>
<ul>
<li>Replace simple keyword scanning with structured extraction from first-party API docs.</li>
<li>Add independent ground-truth labels for a statistically meaningful sample accuracy score.</li>
<li>Add browser-based research for JS-rendered documentation.</li>
<li>Use stricter verification for fuzzy toolkit matches before classifying them as confirmed.</li>
<li>Add checkpointing and concurrency for faster 100+ app audits.</li>
</ul>
</div></section>

<p class="small">Generated from the project's final_audit.csv. No claim of API absence is made solely from a failed HTTP fetch.</p>
</main>

<script>
function filterRows() {
    const q = document.getElementById('q').value.toLowerCase();
    const s = document.getElementById('status').value;
    document.querySelectorAll('#audit tbody tr').forEach(function(row) {
        const text = row.innerText.toLowerCase();
        const okQ = !q || text.includes(q);
        const okS = !s || row.cells[5].innerText.trim() === s;
        row.style.display = okQ && okS ? '' : 'none';
    });
}
</script>
</body>
</html>'''

html_doc = template
replacements = {
    "__TOTAL__": str(total),
    "__VERIFIED__": str(verified),
    "__REVIEW__": str(review),
    "__COMPOSIO__": str(composio_available),
    "__SOURCE_ACCESSIBLE__": str(source_accessible),
    "__NOT_FOUND__": str(composio_not_found),
    "__LOW_CONF__": str(low_conf),
    "__SAMPLE_ROWS__": "".join(sample_rows),
    "__CATEGORY_ROWS__": cat_rows,
    "__TABLE_ROWS__": "".join(table_rows),
}
for key, value in replacements.items():
    html_doc = html_doc.replace(key, value)

OUT.write_text(html_doc, encoding="utf-8")
print(f"Created: {OUT}")
print(f"Apps: {total}")
print(f"Verified/source-limited: {verified}")
print(f"Needs review: {review}")
print(f"Composio toolkits found: {composio_available}")
