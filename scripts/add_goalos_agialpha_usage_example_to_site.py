#!/usr/bin/env python3
from pathlib import Path
import argparse, json, html, datetime, re

SITE_URL = "https://montrealai.github.io/goalos-agialpha-ascension/"
REPO_URL = "https://github.com/MontrealAI/goalos-agialpha-ascension"
AGIALPHA_TOKEN = "0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA"
MARKER_START = "<!-- GOALOS_USAGE_EXAMPLE_START -->"
MARKER_END = "<!-- GOALOS_USAGE_EXAMPLE_END -->"


def esc(v):
    return html.escape(str(v), quote=True)


def read_json(path, default=None):
    if default is None:
        default = {}
    p = Path(path)
    if not p.exists():
        return default
    return json.loads(p.read_text(encoding="utf-8"))


def write(path, text):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def card(title, body, kicker=""):
    return f"""
    <article class="ga-card">
      <div class="ga-kicker">{esc(kicker)}</div>
      <h3>{esc(title)}</h3>
      <p>{esc(body)}</p>
    </article>
    """


def css():
    return """
    <style>
    :root{--ga-ink:#071225;--ga-navy:#0a1733;--ga-blue:#12346d;--ga-gold:#b68b2c;--ga-ivory:#fbf7ef;--ga-line:#dbcda8;--ga-mint:#e9fff4;}
    .ga-usage{background:linear-gradient(135deg,#fbf7ef 0%,#f6efe1 48%,#edf4ff 100%);border:1px solid rgba(182,139,44,.45);border-radius:28px;padding:clamp(24px,4vw,54px);margin:42px auto;max-width:1180px;color:var(--ga-ink);box-shadow:0 28px 80px rgba(7,18,37,.16)}
    .ga-usage *{box-sizing:border-box}.ga-kicker{font-size:12px;letter-spacing:.22em;text-transform:uppercase;font-weight:800;color:#8a6a1d;margin-bottom:10px}.ga-usage h2{font-size:clamp(34px,6vw,72px);line-height:.95;margin:0 0 18px;color:var(--ga-navy);letter-spacing:-.055em}.ga-usage h3{font-size:22px;margin:0 0 10px;color:var(--ga-navy)}.ga-usage p{font-size:17px;line-height:1.6;color:#28364f}.ga-usage strong{color:#06142d}.ga-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:18px}.ga-card{background:rgba(255,255,255,.78);border:1px solid rgba(10,23,51,.12);border-radius:20px;padding:22px;box-shadow:0 14px 40px rgba(10,23,51,.08)}.ga-stage{display:flex;flex-wrap:wrap;gap:10px;margin:24px 0}.ga-pill{border:1px solid rgba(10,23,51,.12);background:#fff;border-radius:999px;padding:10px 14px;font-weight:800;color:var(--ga-navy);font-size:13px}.ga-cta-row{display:flex;flex-wrap:wrap;gap:12px;margin-top:24px}.ga-btn{display:inline-flex;align-items:center;text-decoration:none;border-radius:999px;padding:13px 18px;font-weight:900;border:1px solid var(--ga-navy);background:var(--ga-navy);color:#fff}.ga-btn.secondary{background:#fff;color:var(--ga-navy);border-color:rgba(10,23,51,.25)}.ga-proof{background:var(--ga-navy);color:#fff;border-radius:24px;padding:24px;margin-top:22px}.ga-proof p,.ga-proof li{color:#dce7ff}.ga-proof h3{color:#fff}.ga-two{display:grid;grid-template-columns:1.1fr .9fr;gap:22px}@media(max-width:850px){.ga-two{grid-template-columns:1fr}.ga-usage{border-radius:20px}}
    </style>
    """


def layout(title, subtitle, body, active="usage"):
    nav = """
    <nav class="ga-topnav" style="max-width:1180px;margin:22px auto 0;display:flex;gap:12px;flex-wrap:wrap;font-family:Inter,system-ui,sans-serif">
      <a href="index.html">Home</a>
      <a href="usage-example.html">Usage Example</a>
      <a href="proof-card-001.html">Proof Card 001</a>
      <a href="proof-mission-001.html">Proof Mission</a>
      <a href="share.html">Share</a>
      <a href="https://github.com/MontrealAI/goalos-agialpha-ascension">GitHub</a>
    </nav>
    <style>.ga-topnav a{color:#0a1733;text-decoration:none;font-weight:800;padding:8px 12px;border:1px solid #e2d6b8;border-radius:999px;background:#fff}.ga-topnav a:hover{border-color:#b68b2c}</style>
    """
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(subtitle)}">
  {css()}
</head>
<body style="margin:0;background:#f6efe1;font-family:Inter,system-ui,-apple-system,Segoe UI,sans-serif;color:#071225">
{nav}
<main>
{body}
</main>
</body>
</html>"""


def add_homepage_panel(site, data):
    index = site / "index.html"
    if not index.exists():
        return
    block = f"""
{MARKER_START}
<section class="ga-usage" id="proof-card-001">
  {css()}
  <div class="ga-kicker">Public usage example</div>
  <div class="ga-two">
    <div>
      <h2>Proof Card 001<br>Support-to-Trust Workflow</h2>
      <p><strong>GoalOS turns AI work into proof:</strong> one support workflow improves, proof validates it, reputation compounds it.</p>
      <div class="ga-stage">
        <span class="ga-pill">Buyer support issue</span>
        <span class="ga-pill">GoalOS workflow</span>
        <span class="ga-pill">Builder proof</span>
        <span class="ga-pill">Reviewer validation</span>
        <span class="ga-pill">Proof Card</span>
        <span class="ga-pill">Credential</span>
        <span class="ga-pill">Reputation</span>
      </div>
      <div class="ga-cta-row">
        <a class="ga-btn" href="usage-example.html">See the example</a>
        <a class="ga-btn secondary" href="proof-card-001.html">Open Proof Card 001</a>
      </div>
    </div>
    <div class="ga-proof">
      <h3>The plain-English breakthrough</h3>
      <p>The buyer does not need crypto. Private data stays off-chain. AGIALPHA appears when multiple parties need to coordinate proof work: sponsor, builder, reviewer, credential, reputation, and better missions.</p>
      <p><strong>The intelligence stays private. The proof becomes verifiable.</strong></p>
    </div>
  </div>
</section>
{MARKER_END}
"""
    text = index.read_text(encoding="utf-8", errors="replace")
    if MARKER_START in text and MARKER_END in text:
        text = re.sub(re.escape(MARKER_START)+r".*?"+re.escape(MARKER_END), block.strip(), text, flags=re.S)
    elif "</main>" in text:
        text = text.replace("</main>", block + "\n</main>", 1)
    elif "</body>" in text:
        text = text.replace("</body>", block + "\n</body>", 1)
    else:
        text += block
    index.write_text(text, encoding="utf-8")


def build_pages(site, data, share):
    site.mkdir(parents=True, exist_ok=True)
    (site / "data").mkdir(parents=True, exist_ok=True)
    generated_at = datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

    # Copy source JSON to public data.
    public_data = dict(data)
    public_data["generatedAt"] = generated_at
    write(site / "data/usage-example-proof-card-001.json", json.dumps(public_data, indent=2))

    stages = "".join(f"<span class='ga-pill'>{esc(x)}</span>" for x in data.get("loop", []))
    roles = "".join(card(r["role"], r["plainEnglish"], "role") for r in data.get("roles", []))
    public_proof = "".join(f"<li>{esc(x)}</li>" for x in data.get("publicProof", []))
    private_evidence = "".join(f"<li>{esc(x)}</li>" for x in data.get("privateEvidence", []))

    body = f"""
    <section class="ga-usage">
      <div class="ga-kicker">GoalOS AGIALPHA Ascension usage example</div>
      <h2>{esc(data['title'])}</h2>
      <p><strong>{esc(data['oneLine'])}</strong></p>
      <p>{esc(data['plainEnglish'])}</p>
      <p><strong>The intelligence stays private. The proof becomes verifiable.</strong></p>
      <div class="ga-stage">{stages}</div>
      <div class="ga-cta-row">
        <a class="ga-btn" href="proof-card-001.html">Open Proof Card</a>
        <a class="ga-btn secondary" href="proof-mission-001.html">See the mission</a>
        <a class="ga-btn secondary" href="share.html">Share this</a>
      </div>
    </section>
    <section class="ga-usage">
      <div class="ga-kicker">Why AGIALPHA matters</div>
      <h2>AGIALPHA is for proof coordination, not buyer friction.</h2>
      <p>A normal buyer does not need AGIALPHA. AGIALPHA becomes useful when a sponsor, builder, and reviewer need a shared coordination rail for proof-settled work.</p>
      <div class="ga-grid">{roles}</div>
    </section>
    <section class="ga-usage">
      <div class="ga-two">
        <div class="ga-card"><div class="ga-kicker">Public proof anchor</div><h3>What the public can see</h3><ul>{public_proof}</ul></div>
        <div class="ga-card"><div class="ga-kicker">Private evidence boundary</div><h3>What stays private</h3><ul>{private_evidence}</ul></div>
      </div>
    </section>
    """
    write(site / "usage-example.html", layout("Proof Card 001 usage example", data['oneLine'], body))

    proof_body = f"""
    <section class="ga-usage">
      <div class="ga-kicker">Proof Card 001</div>
      <h2>Support-to-Trust Workflow</h2>
      <p><strong>Public example status:</strong> illustrative until replaced by a live Evidence Docket.</p>
      <div class="ga-proof">
        <h3>Proof statement</h3>
        <p>A customer support workflow can be improved from v1.0 to v1.1, reviewed against evidence, and published as a public-safe Proof Card without exposing private buyer data.</p>
      </div>
      <div class="ga-grid">
        {card('Before', 'One support reply is created and forgotten.', 'workflow v1.0')}
        {card('After', 'The workflow improves, proof is reviewed, a credential is issued, and reputation updates.', 'workflow v1.1')}
        {card('Why it compounds', 'Future support work can start from a reviewed and reusable workflow improvement.', 'RSI signal')}
      </div>
    </section>
    """
    write(site / "proof-card-001.html", layout("Proof Card 001", "Support-to-Trust Workflow", proof_body))

    mission_body = f"""
    <section class="ga-usage" id="sponsor">
      <div class="ga-kicker">Proof Mission 001</div>
      <h2>Sponsor a useful mission.</h2>
      <p>Sponsor a mission to improve a real support workflow. The output is not just a response; it is a reviewed improvement with a public-safe Proof Card.</p>
      <div class="ga-grid">
        {card('Sponsor', 'Funds the proof mission and defines the outcome.', 'step 1')}
        {card('Builder', 'Improves the workflow and submits proof.', 'step 2')}
        {card('Reviewer', 'Validates evidence and claim boundaries.', 'step 3')}
        {card('Network', 'Records proof, credential, and reputation.', 'step 4')}
      </div>
    </section>
    <section class="ga-usage" id="builder"><div class="ga-kicker">Builder path</div><h2>Become the builder.</h2><p>Use GoalOS to turn a support scenario into a reusable workflow improvement. Submit proof, earn a credential, and build reputation.</p></section>
    <section class="ga-usage" id="reviewer"><div class="ga-kicker">Reviewer path</div><h2>Review what matters.</h2><p>Validate whether the evidence supports the claim and whether the public Proof Card is safe to show.</p></section>
    """
    write(site / "proof-mission-001.html", layout("Proof Mission 001", "Sponsor, build, review, and prove the first workflow mission", mission_body))

    share_body = f"""
    <section class="ga-usage">
      <div class="ga-kicker">Share kit</div>
      <h2>Help people understand GoalOS in one useful example.</h2>
      <div class="ga-card"><h3>Short post</h3><p>{esc(share.get('shortPost',''))}</p></div>
      <div class="ga-card"><h3>Long post</h3><p>{esc(share.get('longPost',''))}</p></div>
      <div class="ga-proof"><h3>Founder line</h3><p>{esc(share.get('founderLine',''))}</p></div>
      <p><strong>Boundary:</strong> {esc(share.get('safeBoundary',''))}</p>
    </section>
    """
    write(site / "share.html", layout("Share GoalOS Proof Card 001", "Public copy for the GoalOS AGIALPHA usage example", share_body))

    # Sitemap additive.
    sitemap = site / "sitemap.xml"
    additions = ["usage-example.html", "proof-card-001.html", "proof-mission-001.html", "share.html"]
    if sitemap.exists():
        text = sitemap.read_text(encoding="utf-8", errors="replace")
        for page in additions:
            loc = f"<url><loc>{SITE_URL}{page}</loc></url>"
            if f"{SITE_URL}{page}" not in text:
                text = text.replace("</urlset>", f"  {loc}\n</urlset>") if "</urlset>" in text else text + "\n" + loc
        sitemap.write_text(text, encoding="utf-8")
    else:
        urls = "\n".join(f"  <url><loc>{SITE_URL}{p}</loc></url>" for p in additions)
        write(sitemap, f"<?xml version='1.0' encoding='UTF-8'?><urlset xmlns='http://www.sitemaps.org/schemas/sitemap/0.9'>\n{urls}\n</urlset>\n")

    manifest = {
        "schema": "goalos.agialpha.usage_example_site_manifest.v2",
        "generatedAt": generated_at,
        "pages": additions,
        "source": "docs/examples/proof-card-001-support-to-trust-workflow.md",
        "data": "data/examples/proof-card-001-support-to-trust-workflow.json",
        "claimBoundary": data.get("claimBoundary", {})
    }
    write(site / "data/usage-example-site-manifest.json", json.dumps(manifest, indent=2))

    add_homepage_panel(site, data)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--site", default="site")
    args = ap.parse_args()
    site = Path(args.site)
    data = read_json("data/examples/proof-card-001-support-to-trust-workflow.json")
    share = read_json("data/examples/proof-card-001-share-kit.json")
    if not data:
        raise SystemExit("Missing data/examples/proof-card-001-support-to-trust-workflow.json")
    build_pages(site, data, share)
    print("Proof Card 001 usage example pages added to", site)

if __name__ == "__main__":
    main()
