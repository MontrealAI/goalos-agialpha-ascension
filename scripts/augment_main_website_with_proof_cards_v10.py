#!/usr/bin/env python3
from pathlib import Path
import argparse, json, html, re
from datetime import datetime, timezone

TOKEN = "0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA"
CARDS = [{"id": "001", "slug": "proof-card-001", "title": "Buyer Rescue Workflow", "subtitle": "Turn a buyer support problem into verified workflow improvement.", "problem": "A buyer cannot access a purchased file or needs a clear next step. A normal AI reply may be helpful, but it is not yet a reusable, reviewed workflow asset.", "mission": "Create and validate a support workflow that classifies the issue, drafts the reply, flags human review when needed, and records a public-safe proof summary.", "agialpha": "AGIALPHA coordinates the proof mission: sponsor posting, builder claim bond, proof submission bond, reviewer bond, proof-card registration, credential action, and reward settlement.", "rsi": "The accepted support workflow becomes a scoped reusable artifact for future support cases only after evidence, review, and Selection Gate acceptance.", "value": "Better buyer experience, lower repeated support work, clearer refund/access handling, and first public-safe proof that useful work can become reusable capability.", "status": "Illustrative until a live Evidence Docket is completed."}, {"id": "002", "slug": "proof-card-002", "title": "Sovereign Procurement Trust Room", "subtitle": "Convert buyer diligence into an auditable trust-room workflow.", "problem": "A serious buyer asks whether GoalOS AGIALPHA Ascension can be trusted, governed, audited, and explained without exposing private intelligence or private evidence.", "mission": "Assemble a procurement-ready trust room: claim boundary, security posture, evidence checklist, proof-card summary, reviewer rubric, and rollback path.", "agialpha": "AGIALPHA coordinates the sponsored trust-room mission and creates accountable commitments for builders and reviewers through bonds, proof actions, credentials, and reputation updates.", "rsi": "The accepted trust-room template improves future procurement responses because the system reuses only reviewed evidence structures and rejects unproven claims.", "value": "Shorter diligence cycles, stronger enterprise trust, safer public claims, better sponsor conversations, and a reusable due-diligence operating asset.", "status": "Illustrative until a live Evidence Docket is completed."}, {"id": "003", "slug": "proof-card-003", "title": "Sovereign AI Procurement Control Tower", "subtitle": "A flagship control tower for trust, evidence, rollout, rollback, and upgrade rights.", "problem": "A sovereign or enterprise buyer needs more than a demo: it needs a control plane for evaluating AI workflows, validating evidence, managing risk, and deciding what can improve future work.", "mission": "Build a procurement control tower with GoalOS commitments, run commitments, proof submissions, reviewer validation, Evidence Docket, Proof Card, credential, reputation, and Selection Gate path.", "agialpha": "AGIALPHA is used across the whole coordination route: mission posting, claim bonds, proof bonds, reviewer bonds, settlement, proof-card action, credential action, and reputation-linked access.", "rsi": "The control tower grants proof-backed upgrade rights only to procurement artifacts that survive evidence, evaluator review, scope control, monitoring, and rollback readiness.", "value": "An enterprise-grade route from buyer trust question to audited proof, making adoption legible to boards, procurement teams, risk owners, and sovereign institutions.", "status": "Illustrative until a live Evidence Docket is completed."}, {"id": "004", "slug": "proof-card-004", "title": "Persistent Goal-Seeking Intelligence Accumulation Engine", "subtitle": "Show how GoalOS AGIALPHA Ascension accumulates capability, evidence, and economic value over time.", "problem": "Most AI workflows disappear after use. The organization loses what worked, why it worked, who reviewed it, and whether it should improve future work.", "mission": "Demonstrate the persistent accumulation loop: goals become proof missions; proof missions create evidence; evidence creates credentials and reputation; accepted artifacts earn scoped upgrade rights; future work improves.", "agialpha": "AGIALPHA coordinates the economic accountability layer for the accumulation loop: posted missions, bonded participation, proof actions, reviewer accountability, settlement, credentialing, and reputation-linked access.", "rsi": "This is the meta-card: Recursive Self-Improvement becomes proof-backed accumulation. A capability shapes future work only after it passes evidence, evaluation, review, selection, monitoring, and rollback criteria.", "value": "A compounding evidence graph: validated workflows, rubrics, policies, proof templates, procurement answers, reviewer attestations, economic records, and reusable institutional intelligence.", "status": "Illustrative until repeated live Evidence Dockets prove accumulation over time."}]
ROUTE = [["AEPGoalOSCommitRegistry", "records the aim, scope, success metric, constraints, risk class and rollback expectations"], ["AEPRunCommitmentRegistry", "records the execution plan, tools, artifact versions, evaluator set and approval boundary"], ["JobRegistry", "posts the proof mission and its AGIALPHA reward"], ["JobClaimBondManager", "locks a builder claim bond so the mission is not casually abandoned"], ["ProofSubmissionRegistry", "receives the proof URI/hash and submission bond"], ["ReviewerBondRegistry", "binds reviewers to accountable validation and challenge windows"], ["ProofCardRegistry", "anchors the public-safe proof-card hash"], ["ProofCredentialRegistry", "issues a non-transferable proof credential for accepted work"], ["ReputationRegistry", "records approved proof and reviewer quality signals"], ["AEPEvidenceDocketRegistry", "anchors the evidence package that supports the public claim"], ["AEPSelectionGate", "decides whether the artifact earns scoped upgrade rights"], ["AEPChronicleRegistry", "preserves durable institutional memory for future work"]]

CLAIM_BOUNDARY = "Illustrative public example until a live Evidence Docket is completed. No claim of achieved AGI, ASI, legal approval, tax approval, security approval, guaranteed return, or mainnet deployment is made by these pages."


def esc(x): return html.escape(str(x), quote=True)

def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8')

def read(path): return path.read_text(encoding='utf-8', errors='replace') if path.exists() else ''

def card_link(c): return f"{c['slug']}.html"

def route_html():
    return "\n".join(f"<article class='pc-route-step'><strong>{esc(name)}</strong><p>{esc(desc)}</p></article>" for name, desc in ROUTE)

def card_mini_html(c):
    return f"""
    <article class='pc-card pc-proof-card-{c['id']}'>
      <div class='pc-kicker'>Proof Card {c['id']}</div>
      <h3>{esc(c['title'])}</h3>
      <p>{esc(c['subtitle'])}</p>
      <div class='pc-meta-grid'>
        <span>AGIALPHA coordination</span>
        <span>Evidence Docket</span>
        <span>Sovereign RSI</span>
      </div>
      <a class='button primary' href='{card_link(c)}'>Open Proof Card {c['id']}</a>
    </article>"""

def card_page(c):
    title = f"Proof Card {c['id']} — {c['title']}"
    return page(title, f"""
    <section class='pc-hero pc-hero-card'>
      <div class='pc-eyebrow'>Proof Card {c['id']}</div>
      <h1>{esc(c['title'])}</h1>
      <p class='pc-subtitle'>{esc(c['subtitle'])}</p>
      <div class='pc-callout'><strong>{esc(c['status'])}</strong></div>
    </section>
    <section class='pc-section pc-grid-2'>
      <article class='pc-panel'><h2>Buyer / sponsor problem</h2><p>{esc(c['problem'])}</p></article>
      <article class='pc-panel'><h2>Proof mission</h2><p>{esc(c['mission'])}</p></article>
      <article class='pc-panel'><h2>Where AGIALPHA becomes useful</h2><p>{esc(c['agialpha'])}</p><p><code>{TOKEN}</code></p></article>
      <article class='pc-panel'><h2>RSI upgrade logic</h2><p>{esc(c['rsi'])}</p></article>
    </section>
    <section class='pc-section pc-panel pc-wide'>
      <h2>Smart-contract / registry route</h2>
      <p>Each useful workflow improvement moves through a public-safe proof route. Private evidence stays off-chain. Public anchors, credentials, reputation and selection outcomes are recorded as verifiable commitments.</p>
      <div class='pc-route'>{route_html()}</div>
    </section>
    <section class='pc-section pc-grid-2'>
      <article class='pc-panel'><h2>Evidence Docket checklist</h2><ul><li>GoalOS commitment</li><li>Run commitment</li><li>Before/after artifact</li><li>ProofBundle</li><li>Reviewer attestation</li><li>Proof Card hash</li><li>Credential receipt</li><li>Reputation update</li><li>Selection decision</li><li>Rollback notes</li></ul></article>
      <article class='pc-panel'><h2>Commercial value</h2><p>{esc(c['value'])}</p><h2>Claim boundary</h2><p class='pc-boundary'>{CLAIM_BOUNDARY}</p></article>
    </section>
    <section class='pc-section pc-actions'><a class='button primary' href='proof-cards.html'>View all Proof Cards</a><a class='button ghost' href='agialpha-ledger-route.html'>View AGIALPHA route</a><a class='button ghost' href='sovereign-rsi-control-plane.html'>View Sovereign RSI</a></section>
    """)

def page(title, body):
    nav = """
    <header class='topbar'><div class='shell topbar-inner'><a class='brand' href='index.html'><span class='brand-mark'>α</span><span>GoalOS AGIALPHA Ascension</span></a><nav aria-label='Primary navigation'><a href='index.html'>Home</a><a href='proof-cards.html'>Proof Cards</a><a href='agialpha-ledger-route.html'>AGIALPHA</a><a href='sovereign-rsi-control-plane.html'>Sovereign RSI</a><a href='evidence-docket.html'>Evidence</a></nav></div></header>
    """
    return f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'><title>{esc(title)} · GoalOS AGIALPHA Ascension</title><meta name='description' content='GoalOS AGIALPHA Ascension proof-card demand center'><link rel='stylesheet' href='assets/site.css'><link rel='icon' href='assets/og.svg' type='image/svg+xml'></head><body><canvas class='mesh' aria-hidden='true'></canvas>{nav}<main class='shell pc-main'>{body}</main><footer class='footer'><div class='shell'><strong>Publication-safe boundary:</strong> {CLAIM_BOUNDARY}<br>Generated from repository evidence at <code>{datetime.now(timezone.utc).replace(microsecond=0).isoformat()}</code>.</div></footer><script src='assets/site.js'></script></body></html>"""

def proof_cards_page():
    cards = "\n".join(card_mini_html(c) for c in CARDS)
    return page('Proof Card Command Center', f"""
      <section class='pc-hero'><div class='pc-eyebrow'>Main website proof gallery</div><h1>Four Proof Cards for GoalOS AGIALPHA Ascension</h1><p class='pc-subtitle'>A clear public route from useful AI workflow work to evidence, credentials, reputation and proof-backed recursive self-improvement.</p></section>
      <section class='pc-section'><div class='pc-proof-grid'>{cards}</div></section>
      <section class='pc-section pc-panel pc-wide'><h2>What the four cards prove together</h2><p>Proof Card 001 shows simple buyer value. Proof Card 002 shows enterprise trust. Proof Card 003 shows sovereign procurement control. Proof Card 004 shows persistent accumulation of capability, evidence and economic value over time.</p></section>
    """)

def agialpha_page():
    return page('Where AGIALPHA becomes useful', f"""
    <section class='pc-hero'><div class='pc-eyebrow'>AGIALPHA ledger route</div><h1>Where AGIALPHA becomes useful</h1><p class='pc-subtitle'>AGIALPHA is the coordination asset for proof-settled AI workflow work: missions, bonds, review, credentials, reputation and settlement.</p><div class='pc-token'>{TOKEN}</div></section>
    <section class='pc-section pc-panel pc-wide'><h2>Smart-contract / registry route</h2><div class='pc-route'>{route_html()}</div></section>
    <section class='pc-section pc-grid-2'><article class='pc-panel'><h2>Used for</h2><ul><li>Mission posting</li><li>Builder claim bond</li><li>Proof submission bond</li><li>Reviewer bond</li><li>Proof-card action</li><li>Credential action</li><li>Reward settlement</li><li>Reputation-linked access</li></ul></article><article class='pc-panel'><h2>Not used for</h2><ul><li>Investment promises</li><li>Yield claims</li><li>Revenue-share claims</li><li>Private buyer data</li><li>Private evidence storage</li><li>Ungated mainnet claims</li></ul></article></section>
    """)

def rsi_page():
    return page('Sovereign RSI Control Plane', """
    <section class='pc-hero'><div class='pc-eyebrow'>Recursive Self-Improvement</div><h1>Sovereign RSI through proof-backed upgrade rights</h1><p class='pc-subtitle'>The system improves efficiently because future work can reuse only artifacts that survived evidence, evaluation, review, scope control, monitoring and rollback readiness.</p></section>
    <section class='pc-section pc-grid-3'>
      <article class='pc-panel'><h2>Observe</h2><p>A workflow weakness, procurement gap, support defect or trust bottleneck is identified.</p></article>
      <article class='pc-panel'><h2>Improve</h2><p>A builder produces a better artifact, workflow, rubric, policy, template or route.</p></article>
      <article class='pc-panel'><h2>Prove</h2><p>The artifact is packaged into a ProofBundle and Evidence Docket.</p></article>
      <article class='pc-panel'><h2>Review</h2><p>Reviewers validate evidence through a bonded, challengeable process.</p></article>
      <article class='pc-panel'><h2>Select</h2><p>The Selection Gate decides whether the artifact earns scoped upgrade rights.</p></article>
      <article class='pc-panel'><h2>Propagate</h2><p>Accepted artifacts improve future work; unsafe artifacts do not propagate.</p></article>
    </section>
    <section class='pc-section pc-panel pc-wide'><h2>Efficient RSI loop</h2><div class='pc-flow'>Weak artifact → Improved artifact → Proof → Review → Selection → Scoped upgrade → Better future work → Chronicle</div></section>
    """)

def evidence_page():
    return page('Evidence Docket', """
    <section class='pc-hero'><div class='pc-eyebrow'>Evidence Docket</div><h1>How claims become auditable</h1><p class='pc-subtitle'>Every serious public claim should have a proof room: commitments, artifacts, evidence, review, selection, settlement and rollback notes.</p></section>
    <section class='pc-section pc-grid-2'><article class='pc-panel'><h2>public-safe evidence</h2><ul><li>Claim</li><li>GoalOSCommit hash</li><li>RunCommitment hash</li><li>ProofBundle hash</li><li>Proof Card hash</li><li>Reviewer attestation</li><li>Selection decision</li></ul></article><article class='pc-panel'><h2>private evidence</h2><ul><li>Buyer identity</li><li>Private support tickets</li><li>Private prompts</li><li>Confidential policies</li><li>Internal review notes</li><li>Legal or tax material</li></ul></article></section>
    """)

def season_page():
    rows = ''.join(f"<tr><td>PC-{c['id']}</td><td>{esc(c['title'])}</td><td>{esc(c['subtitle'])}</td></tr>" for c in CARDS)
    return page('Season 001', f"""
    <section class='pc-hero'><div class='pc-eyebrow'>Season 001</div><h1>First proof missions</h1><p class='pc-subtitle'>Season 001 should produce the first live Evidence Dockets that turn illustrative proof cards into executed proof.</p></section>
    <section class='pc-section pc-panel pc-wide'><h2>Proof mission catalogue</h2><div class='table-wrap'><table><thead><tr><th>Card</th><th>Mission</th><th>Why it matters</th></tr></thead><tbody>{rows}</tbody></table></div></section>
    """)

def share_page():
    return page('Share', """
    <section class='pc-hero'><div class='pc-eyebrow'>Share kit</div><h1>Explain the system in one minute</h1><p class='pc-subtitle'>GoalOS turns AI adoption into proof. AGIALPHA coordinates proof work. Evidence Dockets make claims auditable. Sovereign RSI reuses only what proved itself.</p></section>
    <section class='pc-section pc-panel pc-wide'><h2>Public line</h2><p class='pc-quote'>GoalOS AGIALPHA Ascension accumulates what proved itself: capability, evidence, reputation and reusable institutional intelligence.</p></section>
    """)

def home_section():
    cards = "\n".join(card_mini_html(c) for c in CARDS)
    return f"""
<!-- GOALOS_PROOF_CARDS_MAIN_SITE_START -->
<section class='section pc-home-section' id='proof-cards'>
  <div class='section-header'>
    <div>
      <div class='eyebrow'>Proof Card Command Center</div>
      <h2>Four visible proof cards: useful work, trusted evidence, compounding intelligence</h2>
    </div>
    <p>Added to the main website. These cards explain where AGIALPHA becomes useful and how Sovereign RSI works through proof-backed upgrade rights.</p>
  </div>
  <div class='pc-proof-grid'>
    {cards}
  </div>
  <article class='card wide lux pc-home-rsi'>
    <h3>What this proves as a system</h3>
    <p>GoalOS sets the aim. AGIALPHA coordinates proof-settled work. Evidence Dockets make claims auditable. The Selection Gate decides which artifacts earn scoped upgrade rights. Future work improves only by reusing what proved itself.</p>
    <div class='badge-row'><span class='badge gold'>AGIALPHA route</span><span class='badge cyan'>Evidence Docket</span><span class='badge mint'>Sovereign RSI</span><span class='badge violet'>Proof-backed upgrade rights</span></div>
    <div class='actions'><a class='button primary' href='proof-cards.html'>Open Proof Card Command Center</a><a class='button ghost' href='agialpha-ledger-route.html'>AGIALPHA ledger route</a><a class='button ghost' href='sovereign-rsi-control-plane.html'>Sovereign RSI control plane</a></div>
  </article>
</section>
<!-- GOALOS_PROOF_CARDS_MAIN_SITE_END -->
"""

def append_css(site):
    css_path = site/'assets'/'site.css'
    css = read(css_path)
    marker = '/* GOALOS PROOF CARD MAIN WEBSITE V10 */'
    if marker in css:
        return
    css += """

/* GOALOS PROOF CARD MAIN WEBSITE V10 */
.pc-main { padding-bottom: 90px; }
.pc-home-section { margin-top: 46px; }
.pc-hero { padding: 82px 0 38px; }
.pc-hero h1 { font-size: clamp(2.7rem, 7vw, 5.8rem); line-height: .94; letter-spacing: -.065em; max-width: 980px; margin: 0 0 22px; }
.pc-subtitle { max-width: 900px; color: var(--muted); font-size: 1.22rem; }
.pc-eyebrow { color: var(--gold); text-transform: uppercase; letter-spacing: .22em; font-weight: 950; font-size: .84rem; margin-bottom: 18px; }
.pc-proof-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 18px; }
.pc-card, .pc-panel { background: linear-gradient(145deg, rgba(255,255,255,.095), rgba(255,255,255,.035)); border: 1px solid rgba(255,255,255,.16); border-radius: 24px; padding: 24px; box-shadow: 0 25px 80px rgba(0,0,0,.25); }
.pc-card { min-height: 350px; display: flex; flex-direction: column; justify-content: space-between; }
.pc-card h3 { font-size: 1.45rem; margin: 10px 0; line-height: 1.05; }
.pc-card p, .pc-panel p { color: var(--muted); }
.pc-kicker { color: var(--gold); font-size: .78rem; font-weight: 950; letter-spacing: .16em; text-transform: uppercase; }
.pc-meta-grid { display: flex; flex-wrap: wrap; gap: 8px; margin: 16px 0; }
.pc-meta-grid span { border: 1px solid rgba(255,214,107,.28); border-radius: 999px; padding: 6px 10px; font-size: .76rem; color: #ffe8a3; background: rgba(255,214,107,.06); }
.pc-grid-2 { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 18px; }
.pc-grid-3 { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 18px; }
.pc-section { margin: 34px 0; }
.pc-wide { grid-column: 1 / -1; }
.pc-route { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; margin-top: 18px; }
.pc-route-step { border: 1px solid rgba(99,232,255,.19); background: rgba(99,232,255,.055); border-radius: 16px; padding: 14px; }
.pc-route-step strong { color: var(--cyan); }
.pc-route-step p { margin: 6px 0 0; font-size: .88rem; color: var(--muted); }
.pc-callout, .pc-token, .pc-flow, .pc-quote { background: rgba(255,214,107,.095); border: 1px solid rgba(255,214,107,.32); color: #fff3c2; border-radius: 18px; padding: 18px; margin: 18px 0; font-weight: 750; }
.pc-token { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; word-break: break-all; }
.pc-boundary { border-left: 3px solid var(--gold); padding-left: 14px; color: #d9e6ff !important; }
.pc-actions { display: flex; flex-wrap: wrap; gap: 12px; }
.pc-home-rsi { margin-top: 18px; }
@media (max-width: 1100px) { .pc-proof-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } .pc-route { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 760px) { .pc-proof-grid, .pc-grid-2, .pc-grid-3, .pc-route { grid-template-columns: 1fr; } .pc-hero { padding-top: 44px; } }
"""
    write(css_path, css)

def update_index(site):
    idx = site/'index.html'
    htmltxt = read(idx)
    if not htmltxt:
        raise SystemExit('site/index.html not found. Build the main site first.')
    # nav link
    if "proof-cards.html" not in htmltxt:
        htmltxt = htmltxt.replace("<a href=\"sovereign-rsi.html\">Sovereign RSI</a>", "<a href=\"sovereign-rsi.html\">Sovereign RSI</a>\n  <a href=\"proof-cards.html\">Proof Cards</a>")
    section = home_section()
    pattern = re.compile(r"\n?<!-- GOALOS_PROOF_CARDS_MAIN_SITE_START -->.*?<!-- GOALOS_PROOF_CARDS_MAIN_SITE_END -->\n?", re.S)
    htmltxt = re.sub(pattern, "\n"+section+"\n", htmltxt)
    if 'GOALOS_PROOF_CARDS_MAIN_SITE_START' not in htmltxt:
        # place immediately after hero if possible, before live status section
        marker = "<section class=\"section\">\n  <div class=\"section-header\">\n    <div>\n      <div class=\"eyebrow\">Live public status</div>"
        if marker in htmltxt:
            htmltxt = htmltxt.replace(marker, section + "\n" + marker, 1)
        else:
            htmltxt = htmltxt.replace("</main>", section + "\n</main>")
    write(idx, htmltxt)

def update_sitemap(site):
    pages = ['proof-cards.html','proof-card-001.html','proof-card-002.html','proof-card-003.html','proof-card-004.html','agialpha-ledger-route.html','sovereign-rsi-control-plane.html','evidence-docket.html','season-001.html','share.html']
    sitemap = site/'sitemap.xml'
    base = 'https://montrealai.github.io/goalos-agialpha-ascension/'
    if sitemap.exists():
        text = read(sitemap)
        for p in pages:
            loc = f'<loc>{base}{p}</loc>'
            if loc not in text:
                text = text.replace('</urlset>', f'  <url><loc>{base}{p}</loc></url>\n</urlset>')
        write(sitemap, text)
    else:
        urls = ''.join(f'  <url><loc>{base}{p}</loc></url>\n' for p in ['index.html']+pages)
        write(sitemap, f"<?xml version='1.0' encoding='UTF-8'?><urlset xmlns='http://www.sitemaps.org/schemas/sitemap/0.9'>\n{urls}</urlset>\n")

def write_data(site):
    data = {'generatedAt': datetime.now(timezone.utc).replace(microsecond=0).isoformat(), 'agialphaToken': TOKEN, 'proofCards': CARDS, 'contractRoute': [{'name': n, 'purpose': d} for n,d in ROUTE], 'claimBoundary': CLAIM_BOUNDARY}
    write(site/'data'/'proof-cards'/'proof-cards-index.json', json.dumps(data, indent=2))
    for c in CARDS:
        docket = {'proofCard': c['id'], 'title': c['title'], 'status': c['status'], 'claimBoundary': CLAIM_BOUNDARY, 'requiredEvidence': ['GoalOSCommit','RunCommitment','ProofBundle','ReviewerAttestation','ProofCardHash','CredentialReceipt','ReputationUpdate','SelectionDecision','RollbackNotes'], 'agialphaToken': TOKEN}
        write(site/'evidence'/'examples'/f"proof-card-{c['id']}-evidence-docket-template.json", json.dumps(docket, indent=2))

def build(site):
    site = Path(site)
    if not (site/'index.html').exists():
        raise SystemExit(f'{site}/index.html not found. This script must run after the main website builder.')
    append_css(site)
    update_index(site)
    write(site/'proof-cards.html', proof_cards_page())
    for c in CARDS:
        write(site/f"{c['slug']}.html", card_page(c))
    write(site/'agialpha-ledger-route.html', agialpha_page())
    write(site/'sovereign-rsi-control-plane.html', rsi_page())
    write(site/'evidence-docket.html', evidence_page())
    write(site/'season-001.html', season_page())
    write(site/'share.html', share_page())
    write_data(site)
    update_sitemap(site)
    print('Main website augmented with four proof cards.')
    print(site.resolve())

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--site', default='site')
    args = ap.parse_args()
    build(args.site)
