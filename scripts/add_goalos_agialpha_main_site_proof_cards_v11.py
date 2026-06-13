#!/usr/bin/env python3
from pathlib import Path
import argparse, html, json, re
CARDS = [
  {
    "id": "001",
    "slug": "buyer-rescue-workflow",
    "title": "Buyer Rescue Workflow",
    "tag": "First public proof loop",
    "level": "Customer trust",
    "problem": "A buyer cannot access a download or needs help after purchase. A normal AI answer may be polite, but it can miss access classification, refund boundaries, escalation, or evidence requirements.",
    "mission": "Improve a support workflow from v1.0 to v1.1, prove the improvement, and preserve a public-safe Proof Card without exposing buyer data.",
    "agialpha": "AGIALPHA coordinates mission posting, builder claim bond, proof submission bond, reviewer validation, proof-card action, credential action, and settlement.",
    "rsi": "The accepted support workflow can be reused in future support cases only after evidence, reviewer validation, and scoped upgrade approval.",
    "value": "Faster buyer rescue, less repeated support work, and a clearer foundation for the first public proof loop.",
    "claim": "Illustrative until completed with a live Evidence Docket."
  },
  {
    "id": "002",
    "slug": "sovereign-procurement-trust-room",
    "title": "Sovereign Procurement Trust Room",
    "tag": "Enterprise trust gateway",
    "level": "Procurement trust",
    "problem": "A serious buyer asks whether the AI workflow system can be evaluated, governed, audited, and trusted without exposing private data.",
    "mission": "Create a procurement trust-room response with evidence checklist, risk boundaries, reviewer rubric, and public-safe proof artifacts.",
    "agialpha": "AGIALPHA coordinates sponsor-funded proof work, builder bonds, reviewer bonds, proof-card registration, credential issuance, and reputation update.",
    "rsi": "The accepted trust-room response becomes a reusable procurement artifact for future due-diligence workflows after Selection Gate approval.",
    "value": "Reduces buyer uncertainty and turns procurement friction into a reusable trust asset.",
    "claim": "Illustrative until a live buyer/sponsor Evidence Docket is completed."
  },
  {
    "id": "003",
    "slug": "sovereign-ai-procurement-control-tower",
    "title": "Sovereign AI Procurement Control Tower",
    "tag": "Flagship institutional use case",
    "level": "Institutional control",
    "problem": "A sovereign or enterprise buyer asks: can this system be trusted, governed, audited, rolled back, and improved safely?",
    "mission": "Turn the procurement question into a proof mission: build the control-tower response, collect evidence, validate it, and register the resulting Proof Card.",
    "agialpha": "AGIALPHA coordinates the complete route: mission posting, builder claim bond, proof submission bond, reviewer bond, proof-card action, credential action, reputation, reward settlement, Evidence Docket anchoring, and upgrade rights.",
    "rsi": "The accepted control-tower artifact improves future procurement responses only if it survives evidence review, challenge window, monitoring, rollback readiness, and Selection Gate approval.",
    "value": "Creates a serious buyer-facing control plane for governance, diligence, and adoption decisions.",
    "claim": "Public-safe illustrative proof card until the real proof-work loop is executed."
  },
  {
    "id": "004",
    "slug": "persistent-intelligence-accumulation",
    "title": "Persistent Goal-Seeking Intelligence Accumulation Engine",
    "tag": "Meta-proof of compounding capability",
    "level": "Capability accumulation",
    "problem": "One-off AI outputs do not create durable institutional memory. The system needs to accumulate capabilities, evidence, and economic value over time.",
    "mission": "Show how GoalOS AGIALPHA Ascension accumulates validated artifacts, Evidence Dockets, credentials, reputation, and reusable capability across proof cycles.",
    "agialpha": "AGIALPHA coordinates repeated proof-settled work: missions, bonds, reviews, credentials, reputation-linked access, and settlement events that feed the Evidence Docket and Chronicle.",
    "rsi": "RSI is expressed as proof-backed upgrade rights: only proven artifacts influence future workflows, routing, evaluation, and institutional memory.",
    "value": "Turns scattered work into a durable evidence graph of reusable institutional intelligence.",
    "claim": "Experimental framework. Does not claim achieved AGI, guaranteed ROI, legal approval, tax approval, security approval, or mainnet deployment."
  },
  {
    "id": "005",
    "slug": "sovereign-rsi-value-to-capability-treasury",
    "title": "Sovereign RSI Value-to-Capability Treasury",
    "tag": "Capital-to-capability compounding loop",
    "level": "Economic compounding",
    "problem": "Accumulating capabilities and evidence is powerful, but the system becomes strategically exceptional only when verified value is reinvested into better future capability instead of being forgotten or spent blindly.",
    "mission": "Turn verified workflow value into governed reinvestment: measure the value created by accepted proof work, allocate a bounded capability budget, post higher-value proof missions, validate the outputs, and record how each cycle improves future work.",
    "agialpha": "AGIALPHA coordinates the value-to-capability loop: sponsor funding, reward vault allocation, builder claim bond, proof submission bond, reviewer bond, proof-card registration, credential issuance, reputation-linked access, settlement, AlphaWorkUnit metrology, TreasuryRouter records, and Chronicle memory.",
    "rsi": "RSI becomes economically efficient when the Selection Gate grants upgrade rights only to artifacts that prove value, safety, reproducibility, and rollback readiness. Accepted artifacts can influence future routing, budgeting, prompts, rubrics, procurement answers, and proof missions; rejected artifacts cannot.",
    "value": "Creates the missing compounding layer: verified value funds better missions; better missions create stronger artifacts; stronger artifacts improve future workflows; future workflows produce more proof-backed value.",
    "claim": "Experimental proof-card template. It does not claim token price appreciation, investment return, guaranteed ROI, legal approval, tax approval, security approval, achieved AGI, or Ethereum mainnet deployment."
  }
]
ROUTE = [
  "AEPGoalOSCommitRegistry",
  "AEPRunCommitmentRegistry",
  "JobRegistry",
  "JobClaimBondManager",
  "ProofSubmissionRegistry",
  "ReviewerBondRegistry",
  "ProofCardRegistry",
  "ProofCredentialRegistry",
  "ReputationRegistry",
  "AEPEvidenceDocketRegistry",
  "AEPSelectionGate",
  "AEPChronicleRegistry",
  "AlphaWorkUnitLedger",
  "AEPRewardVault",
  "TreasuryRouter",
  "CommercializationPerformanceVault"
]
START = '<!-- GOALOS_AGIALPHA_MAIN_SITE_PROOF_CARDS_V11_START -->'
END = '<!-- GOALOS_AGIALPHA_MAIN_SITE_PROOF_CARDS_V11_END -->'
AGIALPHA = '0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA'

def esc(x): return html.escape(str(x), quote=True)
def write(path, text):
    path=Path(path); path.parent.mkdir(parents=True, exist_ok=True); path.write_text(text, encoding='utf-8')
def css_text():
    return '\n:root{--navy:#061126;--navy2:#0a1730;--ink:#0b1730;--muted:#5e6e86;--gold:#b88927;--gold2:#e6c164;--paper:#fbf7ef;--card:#ffffff;--line:#e7dcc8;--green:#1d7f5b}\n*{box-sizing:border-box}body.proof-body{margin:0;background:radial-gradient(circle at top left,#fff8ea 0,#fbf7ef 28%,#f7efe2 100%);color:var(--ink);font-family:Inter,ui-sans-serif,system-ui,-apple-system,Segoe UI,sans-serif}.proof-nav{display:flex;justify-content:space-between;gap:18px;align-items:center;padding:18px 32px;background:var(--navy);color:white;position:sticky;top:0;z-index:10;box-shadow:0 16px 40px rgba(3,11,24,.22)}.proof-nav a{color:white;text-decoration:none;font-weight:850}.proof-nav nav{display:flex;gap:16px;flex-wrap:wrap}.proof-nav nav a{opacity:.9}main{max-width:1220px;margin:0 auto;padding:64px 28px}.eyebrow{font-size:12px;letter-spacing:.18em;text-transform:uppercase;color:var(--gold);font-weight:900}h1{font-size:clamp(42px,6vw,78px);line-height:.94;margin:10px 0 18px;letter-spacing:-.06em}h2{font-size:clamp(30px,4vw,52px);line-height:1.02;margin:10px 0 18px;letter-spacing:-.045em}h3{font-size:24px;line-height:1.05;margin:10px 0}.section-lead{font-size:20px;line-height:1.55;color:#26364d;max-width:950px}.proof-card-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(245px,1fr));gap:18px;margin:28px 0}.proof-card-tile,.panel{background:rgba(255,255,255,.92);border:1px solid var(--line);border-radius:24px;padding:24px;box-shadow:0 22px 70px rgba(5,18,40,.08)}.proof-card-tile{display:flex;flex-direction:column;gap:10px}.proof-card-005{border:2px solid var(--gold);box-shadow:0 26px 90px rgba(184,137,39,.22)}.card-number{font-size:12px;text-transform:uppercase;letter-spacing:.16em;color:var(--gold);font-weight:950}.muted{color:var(--muted)}.button{display:inline-block;background:var(--navy);color:white!important;text-decoration:none;padding:11px 15px;border-radius:999px;font-weight:900;margin-top:auto}.button.ghost{background:white;color:var(--navy)!important;border:1px solid var(--line)}.proof-card-main-section{background:linear-gradient(135deg,#fffaf1 0%,#fff 100%);border:1px solid #eadcc2;border-radius:28px;padding:34px;margin:40px auto}.proof-route-box{background:#f5efe4;border:1px solid #eadcc2;border-radius:18px;padding:18px;margin:14px 0}.route,.rsi-loop{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:12px;margin:24px 0}.route div,.rsi-loop div{background:#fff;border-left:4px solid var(--gold);border-radius:14px;padding:16px;border-top:1px solid var(--line);border-right:1px solid var(--line);border-bottom:1px solid var(--line);font-weight:750}.rsi-loop div{border-left-color:var(--green)}.claim{font-size:15px;background:white;border:1px dashed #c7b68e;border-radius:18px;padding:16px}.proof-footer{text-align:center;color:var(--muted);padding:40px}.chip-row{display:flex;gap:8px;flex-wrap:wrap}.chip-row span{font-size:12px;border:1px solid #eadcc2;background:#fff9ec;padding:6px 9px;border-radius:999px;font-weight:800}.next-links{display:flex;gap:12px;flex-wrap:wrap;margin:26px 0}.hero{padding:20px 0 30px}.proof-hero{border-bottom:1px solid var(--line);margin-bottom:22px}@media(max-width:720px){.proof-nav{align-items:flex-start;flex-direction:column}.proof-nav nav{gap:10px}main{padding:42px 18px}h1{font-size:44px}.proof-card-main-section{padding:22px}}\n'
def card_tile(c):
    return f"""<article class='proof-card-tile proof-card-{esc(c['id'])}'><div class='card-number'>Proof Card {esc(c['id'])}</div><h3>{esc(c['title'])}</h3><p class='muted'>{esc(c['tag'])}</p><p>{esc(c['mission'])}</p><div class='chip-row'><span>{esc(c['level'])}</span><span>AGIALPHA</span><span>Sovereign RSI</span></div><a class='button' href='proof-card-{esc(c['id'])}.html'>Open Proof Card {esc(c['id'])}</a></article>"""
def homepage_section():
    tiles=''.join(card_tile(c) for c in CARDS)
    return f"""\n{START}\n<section class='proof-card-main-section' id='proof-cards'><p class='eyebrow'>GoalOS AGIALPHA Proof Card Command Center</p><h2>Five proof cards make the system visible: trust, procurement, control, persistence, and value-to-capability compounding.</h2><p class='section-lead'>GoalOS turns AI adoption into proof. AGIALPHA coordinates proof-settled work. Evidence Dockets make claims auditable. Sovereign RSI reuses only what proved itself.</p><div class='proof-card-grid'>{tiles}</div><div class='proof-route-box'><strong>Proof Card 005 upgrades the sequence:</strong> verified value becomes a governed capability budget, then funds better missions, stronger artifacts, and more valuable future work.</div><div class='proof-route-box'><strong>AGIALPHA route:</strong> mission posting -> builder claim bond -> proof submission bond -> reviewer bond -> Proof Card -> credential -> reputation -> reward vault -> Selection Gate -> Chronicle.</div><div class='proof-route-box'><strong>Sovereign RSI:</strong> weak artifact -> improved artifact -> proof -> review -> selection -> scoped upgrade rights -> value-to-capability reinvestment -> better future work.</div></section>\n{END}\n"""
def wrap(title, body):
    return f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'><title>{esc(title)} | GoalOS AGIALPHA Ascension</title><meta name='description' content='GoalOS AGIALPHA Ascension Proof Card Command Center'><link rel='stylesheet' href='assets/proof-cards-main.css'></head><body class='proof-body'><header class='proof-nav'><a href='index.html'>GoalOS AGIALPHA Ascension</a><nav><a href='index.html'>Home</a><a href='proof-cards.html'>Proof Cards</a><a href='proof-card-005.html'>Proof Card 005</a><a href='agialpha-ledger-route.html'>AGIALPHA Route</a><a href='sovereign-rsi-control-plane.html'>Sovereign RSI</a><a href='evidence-docket.html'>Evidence Docket</a></nav></header><main>{body}</main><footer class='proof-footer'>Illustrative until live Evidence Docket is completed. Private intelligence stays off-chain. Public proof becomes verifiable.</footer></body></html>"""
def card_page(c):
    route=''.join(f'<div>{esc(x)}</div>' for x in ROUTE)
    checklist_items=['GoalOSCommit','RunCommitment','ProofBundle','Evaluator or reviewer attestation','Proof Card hash','Credential record','Reputation update','Settlement / reward record','Selection Gate decision','Rollback boundary','Chronicle entry','Claim boundary']
    checklist=''.join(f'<div>{esc(x)}</div>' for x in checklist_items)
    return wrap(f"Proof Card {c['id']} - {c['title']}", f"""<section class='hero proof-hero'><p class='eyebrow'>Proof Card {esc(c['id'])}</p><h1>{esc(c['title'])}</h1><p class='section-lead'>{esc(c['tag'])}</p><div class='proof-route-box'><strong>Canonical use:</strong> {esc(c['value'])}</div></section><section class='panel'><h2>Problem</h2><p>{esc(c['problem'])}</p></section><section class='panel'><h2>Proof mission</h2><p>{esc(c['mission'])}</p></section><section class='panel'><h2>Where AGIALPHA becomes useful</h2><p>{esc(c['agialpha'])}</p><div class='route'>{route}</div></section><section class='panel'><h2>Sovereign RSI upgrade logic</h2><p>{esc(c['rsi'])}</p><div class='rsi-loop'><div>Observe weakness</div><div>Improve artifact</div><div>Prove change</div><div>Review evidence</div><div>Select</div><div>Grant scoped upgrade rights</div><div>Reinvest verified value</div><div>Chronicle result</div></div></section><section class='panel'><h2>Evidence Docket checklist</h2><div class='route'>{checklist}</div></section><section class='panel'><h2>Claim boundary</h2><p class='claim'>{esc(c['claim'])}</p></section><div class='next-links'><a class='button' href='proof-cards.html'>View all Proof Cards</a><a class='button ghost' href='agialpha-ledger-route.html'>View AGIALPHA route</a><a class='button ghost' href='sovereign-rsi-control-plane.html'>View Sovereign RSI</a></div>""")
def build_pages(site):
    site=Path(site); (site/'assets').mkdir(parents=True, exist_ok=True)
    write(site/'assets/proof-cards-main.css', css_text())
    tiles=''.join(card_tile(c) for c in CARDS)
    write(site/'proof-cards.html', wrap('Proof Cards', f"<section><p class='eyebrow'>Proof Card Command Center</p><h1>Five proof cards make GoalOS AGIALPHA Ascension legible.</h1><p class='section-lead'>The sequence moves from buyer rescue to procurement trust, institutional control, persistent intelligence accumulation, and value-to-capability reinvestment.</p></section><div class='proof-card-grid'>{tiles}</div>"))
    for c in CARDS: write(site/f"proof-card-{c['id']}.html", card_page(c))
    route=''.join(f'<div>{esc(x)}</div>' for x in ROUTE)
    write(site/'agialpha-ledger-route.html', wrap('AGIALPHA Ledger Route', f"<section><p class='eyebrow'>AGIALPHA Ledger Route</p><h1>Where AGIALPHA becomes useful.</h1><p class='section-lead'>AGIALPHA is useful when proof work needs sponsors, builders, reviewers, bonds, credentials, reputation, reward settlement, and auditable public anchors.</p></section><section class='panel'><h2>Registry and settlement route</h2><div class='route'>{route}</div></section>"))
    write(site/'sovereign-rsi-control-plane.html', wrap('Sovereign RSI Control Plane', "<section><p class='eyebrow'>Sovereign RSI</p><h1>Recursive self-improvement through proof-backed upgrade rights.</h1><p class='section-lead'>The system improves efficiently by reusing only artifacts that survived evidence, evaluation, reviewer validation, scope control, challenge window, monitoring, and rollback readiness.</p></section><section class='panel'><div class='rsi-loop'><div>Observe weakness</div><div>Improve artifact</div><div>Prove change</div><div>Review evidence</div><div>Select</div><div>Grant scoped upgrade rights</div><div>Reinvest verified value</div><div>Chronicle result</div></div></section>"))
    write(site/'evidence-docket.html', wrap('Evidence Docket', "<section><p class='eyebrow'>Evidence Docket</p><h1>The proof room for serious buyers and reviewers.</h1><p class='section-lead'>Evidence Dockets collect claims, missions, ProofBundles, reviewer attestations, proof-card hashes, credentials, reputation updates, selection decisions, value records, and rollback boundaries.</p></section>"))
    write(site/'season-001.html', wrap('Season 001', f"<section><p class='eyebrow'>Season 001</p><h1>Proof missions that convert trust into capability.</h1><p class='section-lead'>Start with clear missions, validate evidence, publish proof cards, issue credentials, update reputation, and reinvest verified value into stronger missions.</p></section><div class='proof-card-grid'>{tiles}</div>"))
    write(site/'share.html', wrap('Share Kit', "<section><p class='eyebrow'>Share Kit</p><h1>GoalOS turns AI adoption into proof.</h1><p class='section-lead'>AGIALPHA coordinates proof work. Evidence Dockets make claims auditable. Sovereign RSI reuses only what proved itself. Proof Card 005 shows how verified value funds stronger future capability.</p></section>"))
    for c in CARDS:
        write(site/'data/examples'/f"proof-card-{c['id']}-{c['slug']}.json", json.dumps(c, indent=2))
        docket={'proof_card_id':f"PC-{c['id']}",'title':c['title'],'status':'template_until_live_evidence_docket_completed','agialpha_token':AGIALPHA,'required_evidence':['GoalOSCommit','RunCommitment','ProofBundle','Reviewer attestation','Proof Card hash','Credential record','Reputation update','Selection Gate decision','Rollback boundary','Chronicle entry'],'claim_boundary':c['claim']}
        if c['id']=='005': docket['additional_value_to_capability_evidence']=['verified value record','AlphaWorkUnit measurement','reward vault allocation','treasury routing note','reinvestment mission post','future-work improvement comparison']
        write(site/'evidence/examples'/f"proof-card-{c['id']}-evidence-docket-template.json", json.dumps(docket, indent=2))
def inject_home(index_path):
    s=Path(index_path).read_text(encoding='utf-8', errors='replace')
    s=re.sub(r'<!-- GOALOS_AGIALPHA_MAIN_SITE_PROOF_CARDS_V\d+_START -->.*?<!-- GOALOS_AGIALPHA_MAIN_SITE_PROOF_CARDS_V\d+_END -->','',s,flags=re.S)
    s=re.sub(re.escape(START)+r'.*?'+re.escape(END),'',s,flags=re.S)
    section=homepage_section()
    if '</main>' in s: s=s.replace('</main>', section+'\n</main>',1)
    elif '</body>' in s: s=s.replace('</body>', section+'\n</body>',1)
    else: s+=section
    if 'proof-cards-main.css' not in s and '</head>' in s: s=s.replace('</head>',"<link rel='stylesheet' href='assets/proof-cards-main.css'>\n</head>",1)
    Path(index_path).write_text(s, encoding='utf-8')
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--site', required=True); args=ap.parse_args(); site=Path(args.site); index=site/'index.html'
    if not index.exists(): raise SystemExit(f'ERROR: {index} does not exist. Build the main website first; this script is additive only.')
    build_pages(site); inject_home(index); print('Added Proof Cards 001-005 to existing main website without deleting existing pages.')
if __name__=='__main__': main()
