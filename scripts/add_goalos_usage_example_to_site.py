#!/usr/bin/env python3
"""Add the GoalOS AGIALPHA usage example to the generated GitHub Pages site.

This script is deliberately additive:
- it expects the main site builder to have already generated the site directory;
- it adds usage-example.html, proof-card-001.html, and data/usage-example-proof-card-001.json;
- it injects one small feature panel into index.html without deleting existing content;
- it updates sitemap.xml if present;
- it fails if the generated files are missing or if obvious private-key strings appear.
"""
from __future__ import annotations

import argparse, datetime, html, json, re
from pathlib import Path

AGIALPHA_TOKEN = "0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA"
REPO_URL = "https://github.com/MontrealAI/goalos-agialpha-ascension"
SITE_URL = "https://montrealai.github.io/goalos-agialpha-ascension/"
MARKER_START = "<!-- GOALOS_USAGE_EXAMPLE_START -->"
MARKER_END = "<!-- GOALOS_USAGE_EXAMPLE_END -->"

BASE_CSS = """
<style>
  :root{--navy:#101a2d;--ink:#172033;--ivory:#fffdf7;--panel:#f6f1e6;--line:#c9b98b;--gold:#9f7a25;--green:#2f6f4e;--muted:#647084;}
  body.usage-page{margin:0;background:var(--ivory);color:var(--ink);font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;line-height:1.55;}
  .usage-wrap{max-width:1120px;margin:0 auto;padding:38px 22px 64px;}
  .usage-hero{background:linear-gradient(135deg,#101a2d,#1c2b44);color:#fff;border:1px solid rgba(201,185,139,.7);border-radius:28px;padding:36px;box-shadow:0 26px 80px rgba(16,26,45,.28);}
  .usage-kicker{letter-spacing:.16em;text-transform:uppercase;color:#dcc78d;font-weight:800;font-size:.78rem;}
  .usage-hero h1{font-size:clamp(2.1rem,4vw,4.2rem);line-height:.97;margin:12px 0 18px;max-width:920px;}
  .usage-hero p{font-size:1.12rem;color:#e8edf7;max-width:880px;}
  .usage-actions{display:flex;flex-wrap:wrap;gap:12px;margin-top:22px;}
  .usage-btn{display:inline-block;text-decoration:none;border-radius:999px;padding:12px 18px;font-weight:800;border:1px solid rgba(255,255,255,.25);}
  .usage-btn.primary{background:#d9bd6a;color:#101a2d;}.usage-btn.secondary{color:#fff;background:rgba(255,255,255,.08);}
  .usage-grid{display:grid;grid-template-columns:repeat(12,1fr);gap:18px;margin-top:22px;}
  .usage-card{grid-column:span 6;background:#fff;border:1px solid #e4dbc5;border-radius:22px;padding:22px;box-shadow:0 16px 44px rgba(16,26,45,.08);}
  .usage-card.full{grid-column:1/-1}.usage-card.third{grid-column:span 4}
  .usage-card h2,.usage-card h3{margin:0 0 10px;color:#101a2d;line-height:1.15}.usage-card p{margin:0 0 12px}.usage-muted{color:var(--muted)}
  .proof-flow{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-top:14px;}
  .flow-step{background:#f8f4ea;border:1px solid #e1d5b8;border-radius:16px;padding:14px;font-weight:800;color:#1c2b44;}
  .number{font-size:2.2rem;font-weight:900;color:#9f7a25;line-height:1}.smallcaps{text-transform:uppercase;letter-spacing:.12em;font-size:.75rem;font-weight:900;color:#9f7a25}
  .boundary{background:#101a2d;color:#fff;border-radius:22px;padding:22px;border:1px solid #c9b98b}.boundary code{color:#ffe9a8}
  .usage-table{width:100%;border-collapse:collapse;font-size:.95rem}.usage-table th,.usage-table td{border:1px solid #e4dbc5;padding:10px;vertical-align:top}.usage-table th{background:#f6f1e6;text-align:left;color:#101a2d}
  .usage-callout{background:#f6f1e6;border:1px solid #d9c896;border-left:8px solid #9f7a25;border-radius:18px;padding:18px;margin:18px 0;}
  @media(max-width:850px){.usage-card,.usage-card.third{grid-column:1/-1}.proof-flow{grid-template-columns:1fr}.usage-hero{padding:26px}.usage-wrap{padding:20px 14px 44px}}
</style>
"""


def esc(x): return html.escape(str(x), quote=True)


def page(title: str, body: str) -> str:
    return f"""<!doctype html>
<html lang='en'>
<head>
  <meta charset='utf-8'>
  <meta name='viewport' content='width=device-width, initial-scale=1'>
  <title>{esc(title)} - GoalOS AGIALPHA Ascension</title>
  <meta name='description' content='A clear non-technical usage example showing how GoalOS and AGIALPHA coordinate proof-based AI workflow work.'>
  {BASE_CSS}
</head>
<body class='usage-page'>
  <main class='usage-wrap'>
    {body}
  </main>
</body>
</html>"""


def usage_example_html() -> str:
    flow = ["Sponsor posts mission", "Builder claims", "Workflow improves", "Proof submitted", "Reviewer validates", "Proof Card registers", "Credential issues", "Reputation updates"]
    flow_html = "".join(f"<div class='flow-step'>{i+1}. {esc(step)}</div>" for i, step in enumerate(flow))
    body = f"""
<section class='usage-hero'>
  <div class='usage-kicker'>Usage Example / Proof Card 001</div>
  <h1>One support workflow becomes proof, reputation, and reusable capability.</h1>
  <p>A buyer needs help. GoalOS improves the support workflow. AGIALPHA coordinates the proof work between sponsor, builder, and reviewer. Ethereum records only public-safe proof anchors; private buyer data stays off-chain.</p>
  <div class='usage-actions'>
    <a class='usage-btn primary' href='proof-card-001.html'>View Proof Card 001</a>
    <a class='usage-btn secondary' href='{REPO_URL}'>View GitHub repository</a>
  </div>
</section>
<section class='usage-grid'>
  <article class='usage-card full'>
    <div class='smallcaps'>Plain-English example</div>
    <h2>Improve the Customer Support Reply Workflow</h2>
    <p>A customer buys a GoalOS product and asks for help with access, downloads, duplicate charge, or refund handling. A generic AI reply may be polite but miss policy classification or escalation. GoalOS turns that into a reusable workflow with a scorecard, diagnosis, improved v1.1 workflow, and public-safe proof note.</p>
    <div class='proof-flow'>{flow_html}</div>
  </article>
  <article class='usage-card'>
    <h3>What the buyer experiences</h3>
    <p>Faster and clearer support. No wallet required. No token required. The buyer simply gets a better answer and a clearer next step.</p>
  </article>
  <article class='usage-card'>
    <h3>Where AGIALPHA becomes useful</h3>
    <p>AGIALPHA is used when multiple parties coordinate proof work: posting the mission, bonding the claim, submitting proof, bonding review, registering the Proof Card, issuing a credential, and updating reputation.</p>
  </article>
  <article class='usage-card third'><div class='number'>1</div><h3>Proof Card</h3><p>A public-safe proof of what improved.</p></article>
  <article class='usage-card third'><div class='number'>2</div><h3>Credential</h3><p>A non-transferable record that a builder or reviewer completed approved proof work.</p></article>
  <article class='usage-card third'><div class='number'>3</div><h3>Reputation</h3><p>A route to better missions based on proof, not hype.</p></article>
  <article class='usage-card full'>
    <h2>Before / after</h2>
    <table class='usage-table'>
      <tr><th>Before</th><th>After GoalOS + AGIALPHA</th></tr>
      <tr><td>One-off support answer. Hard to reuse. Hard to verify. Little memory for the next job.</td><td>Versioned workflow, scorecard, reviewer validation, Proof Card, credential, reputation, and reusable support playbook.</td></tr>
      <tr><td>Trust depends on the author.</td><td>Trust depends on evidence, review, and proof history.</td></tr>
    </table>
  </article>
  <article class='usage-card full boundary'>
    <h2>Safe public boundary</h2>
    <p><code>GoalOS improves workflows. AGIALPHA coordinates proof work. Ethereum records public-safe proof anchors. The intelligence stays private. The proof becomes verifiable.</code></p>
    <p>This page is an illustrative usage example until a live Evidence Docket is filled from an executed proof mission. It does not claim investment return, achieved AGI, security approval, legal approval, tax approval, or mainnet deployment.</p>
  </article>
</section>
"""
    return page("Usage Example - Proof Card 001", body)


def proof_card_html() -> str:
    body = """
<section class='usage-hero'>
  <div class='usage-kicker'>Public-safe proof card template</div>
  <h1>Proof Card 001 - Customer Support Reply Workflow</h1>
  <p>The first easy-to-understand demonstration of GoalOS AGIALPHA Ascension: useful workflow improvement converted into evidence, review, credential, and reputation.</p>
</section>
<section class='usage-grid'>
  <article class='usage-card'><h3>Mission</h3><p>Improve the Customer Support Reply Workflow for GoalOS digital-product buyers.</p></article>
  <article class='usage-card'><h3>Success metric</h3><p>Clearer classification, safer escalation, more reusable reply structure, and public-safe proof note.</p></article>
  <article class='usage-card'><h3>Builder output</h3><p>Workflow v1.0, scorecard, diagnosis, workflow v1.1, before/after comparison, proof note.</p></article>
  <article class='usage-card'><h3>Reviewer output</h3><p>Evidence validation, claim-boundary check, private-data exclusion check, approval or rejection.</p></article>
  <article class='usage-card full'>
    <h2>Why this matters</h2>
    <p>This card shows the product thesis in one example: AI work should not vanish after one task. It should become reusable capability after it is proven.</p>
    <div class='usage-callout'>No proof, no reputation. No verified value, no unlock.</div>
  </article>
  <article class='usage-card full boundary'>
    <h2>Public-safe statement</h2>
    <p><code>One workflow improved. Proof validated it. Reputation can now route better work.</code></p>
  </article>
</section>
"""
    return page("Proof Card 001", body)


def feature_panel() -> str:
    return f"""
{MARKER_START}
<section class='feature-panel' id='usage-example-proof-card-001' style='margin:32px auto;max-width:1120px;padding:0 22px;'>
  <div style='background:#fffdf7;color:#172033;border:1px solid #c9b98b;border-radius:24px;padding:24px;box-shadow:0 18px 56px rgba(16,26,45,.12);'>
    <div style='text-transform:uppercase;letter-spacing:.14em;font-weight:900;color:#9f7a25;font-size:.78rem;'>Featured usage example</div>
    <h2 style='margin:8px 0 10px;font-size:clamp(1.8rem,3vw,3rem);line-height:1.05;color:#101a2d;'>Proof Card 001: one support workflow becomes proof.</h2>
    <p style='font-size:1.05rem;max-width:880px;'>A simple non-technical demo: GoalOS improves a customer support workflow; AGIALPHA coordinates sponsor, builder, and reviewer proof work; the result becomes a Proof Card, credential, reputation, and a reusable capability.</p>
    <div style='display:flex;flex-wrap:wrap;gap:12px;margin-top:18px;'>
      <a href='usage-example.html' style='display:inline-block;background:#101a2d;color:white;padding:12px 18px;border-radius:999px;text-decoration:none;font-weight:800;'>See the usage example</a>
      <a href='proof-card-001.html' style='display:inline-block;background:#d9bd6a;color:#101a2d;padding:12px 18px;border-radius:999px;text-decoration:none;font-weight:800;'>Open Proof Card 001</a>
    </div>
  </div>
</section>
{MARKER_END}
"""


def inject_index(index_path: Path):
    if not index_path.exists():
        index_path.write_text(page("GoalOS AGIALPHA Ascension", "<section class='usage-hero'><h1>GoalOS AGIALPHA Ascension</h1><p>GoalOS improves workflows. AGIALPHA coordinates proof work.</p></section>" + feature_panel()), encoding='utf-8')
        return
    text = index_path.read_text(encoding='utf-8', errors='replace')
    text = re.sub(re.escape(MARKER_START) + r".*?" + re.escape(MARKER_END), "", text, flags=re.S)
    panel = feature_panel()
    if "</main>" in text:
        text = text.replace("</main>", panel + "\n</main>", 1)
    elif "</body>" in text:
        text = text.replace("</body>", panel + "\n</body>", 1)
    else:
        text += panel
    index_path.write_text(text, encoding='utf-8')


def update_sitemap(site: Path):
    sitemap = site / "sitemap.xml"
    urls = [SITE_URL + "usage-example.html", SITE_URL + "proof-card-001.html"]
    if sitemap.exists():
        text = sitemap.read_text(encoding='utf-8', errors='replace')
        for url in urls:
            if url not in text:
                text = text.replace("</urlset>", f"  <url><loc>{url}</loc></url>\n</urlset>")
        sitemap.write_text(text, encoding='utf-8')
    else:
        body = "\n".join(f"  <url><loc>{u}</loc></url>" for u in [SITE_URL] + urls)
        sitemap.write_text(f"<?xml version='1.0' encoding='UTF-8'?><urlset xmlns='http://www.sitemaps.org/schemas/sitemap/0.9'>\n{body}\n</urlset>\n", encoding='utf-8')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--site", default="site")
    args = ap.parse_args()
    site = Path(args.site)
    site.mkdir(parents=True, exist_ok=True)
    (site / "data").mkdir(exist_ok=True)
    (site / "usage-example.html").write_text(usage_example_html(), encoding='utf-8')
    (site / "proof-card-001.html").write_text(proof_card_html(), encoding='utf-8')
    (site / "data" / "usage-example-proof-card-001.json").write_text(json.dumps({
        "schema":"goalos.agialpha.public_usage_example.v1",
        "id":"proof-card-001-customer-support-reply-workflow",
        "generatedAt":datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z"),
        "agialphaToken":AGIALPHA_TOKEN,
        "buyerNeedsCrypto":False,
        "publicShareLine":"GoalOS turns AI work into proof: one support workflow improves, proof validates it, reputation compounds it.",
        "claimBoundary":{"illustrative":True,"achievedAGI":False,"investmentReturn":False,"mainnetDeploymentClaim":False}
    }, indent=2), encoding='utf-8')
    inject_index(site / "index.html")
    update_sitemap(site)
    # Verification
    required = ["index.html", "usage-example.html", "proof-card-001.html", "data/usage-example-proof-card-001.json"]
    missing = [p for p in required if not (site/p).exists()]
    if missing:
        raise SystemExit(f"Missing generated usage-example files: {missing}")
    text_all = "\n".join(p.read_text(encoding='utf-8', errors='ignore') for p in [site/"usage-example.html", site/"proof-card-001.html", site/"index.html"])
    banned = ["PRIVATE_KEY", "SEED_PHRASE", "MNEMONIC", "DEPLOYER_PRIVATE_KEY"]
    hits = [b for b in banned if b in text_all]
    if hits:
        raise SystemExit(f"Potential secret markers in usage example output: {hits}")
    print("GoalOS AGIALPHA usage example added to website artifact.")

if __name__ == "__main__":
    main()
