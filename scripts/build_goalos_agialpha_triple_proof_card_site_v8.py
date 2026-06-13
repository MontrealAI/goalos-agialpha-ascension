
#!/usr/bin/env python3
from pathlib import Path
import argparse, json, html, shutil, re
from datetime import datetime, timezone
MARKER = 'GOALOS_AGIALPHA_TRIPLE_PROOF_CARD_DEMAND_CENTER_V8'
AGIALPHA = '0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA'
CARDS = [
  {
    "id": "001",
    "slug": "buyer-rescue-workflow",
    "title": "Buyer Rescue Workflow",
    "subtitle": "A simple buyer support problem becomes a proof-backed workflow upgrade.",
    "audience": "Digital product buyers, support teams, first-time operators",
    "problem": "A buyer cannot access a file, receives a generic reply, and needs a clear path to resolution without exposing private order data.",
    "mission": "Improve the support reply workflow from v1.0 to v1.1 so it classifies access, refund, duplicate charge, corrupted file, and human-review cases more reliably.",
    "why_it_matters": "This is the lowest-friction proof that GoalOS can turn everyday AI work into reusable institutional memory.",
    "agialpha_use": "AGIALPHA coordinates mission posting, builder claim bond, proof submission bond, reviewer bond, proof-card action, credential action, reward settlement, and reputation-linked access.",
    "proof_output": "Public-safe Proof Card showing what improved, what was reviewed, and what can be reused next.",
    "credential": "GoalOS Proof Builder - Buyer Rescue Workflow",
    "rsi_upgrade": "The accepted support classification rubric becomes a scoped upgrade candidate for future support workflows.",
    "status": "Illustrative until live Evidence Docket is completed.",
    "evidence_items": [
      "Workflow v1.0 prompt/spec",
      "Private buyer scenario redacted",
      "v1.0 output",
      "Scorecard and diagnosis",
      "Workflow v1.1 prompt/spec",
      "v1.1 output",
      "Before/after comparison",
      "Reviewer attestation",
      "Proof Card hash",
      "Rollback note"
    ],
    "public_line": "A buyer problem becomes a proof-backed support upgrade."
  },
  {
    "id": "002",
    "slug": "sovereign-procurement-trust-room",
    "title": "Sovereign Procurement Trust Room",
    "subtitle": "A procurement question becomes an auditable trust package.",
    "audience": "Departments, agencies, enterprise buyers, procurement teams",
    "problem": "A serious buyer asks whether the AI workflow system can be evaluated without leaking private data or relying on unsupported claims.",
    "mission": "Build a procurement-grade trust room with claim boundary, evidence checklist, reviewer rubric, proof-card summary, and private/public evidence split.",
    "why_it_matters": "Procurement is where promising AI tools often stall. This use case turns trust review into a repeatable proof mission.",
    "agialpha_use": "AGIALPHA coordinates sponsor-funded trust-room missions, builder claim bonds, proof evidence submission, reviewer validation, proof-card registration, credential issuance, reward settlement, and reputation updates.",
    "proof_output": "Public-safe Proof Card that summarizes the trust room while keeping private procurement evidence off-chain.",
    "credential": "GoalOS Trust Room Builder - Procurement Evidence",
    "rsi_upgrade": "The accepted trust-room template becomes a reusable artifact for future buyers, sponsors, and enterprise pilots.",
    "status": "Illustrative until live Evidence Docket is completed.",
    "evidence_items": [
      "Procurement question",
      "Claim boundary",
      "Trust room checklist",
      "Risk classification",
      "Public/private evidence split",
      "Reviewer rubric",
      "Red-team concerns",
      "Proof Card draft",
      "Credential decision",
      "Selection Gate note"
    ],
    "public_line": "A buyer trust question becomes an auditable proof room."
  },
  {
    "id": "003",
    "slug": "sovereign-ai-procurement-control-tower",
    "title": "Sovereign AI Procurement Control Tower",
    "subtitle": "A high-stakes AI adoption decision becomes a proof-governed control tower.",
    "audience": "Sovereign institutions, regulated enterprises, strategic procurement, AI governance offices",
    "problem": "A sovereign or enterprise buyer asks: can this AI workflow system be trusted, governed, audited, rolled back, and improved safely across departments?",
    "mission": "Create a control tower that converts procurement due diligence into GoalOS commitments, proof missions, reviewer attestations, Evidence Dockets, Proof Cards, credentials, reputation, and Selection Gate decisions.",
    "why_it_matters": "This is the flagship use case because it speaks to the buyer with the largest willingness to pay: the institution that needs trustworthy AI adoption at scale.",
    "agialpha_use": "AGIALPHA coordinates the entire proof-settled work route: sponsor mission posting, builder bonds, proof bonds, reviewer bonds, proof-card actions, credential actions, reward settlement, reputation-linked access, and future mission routing.",
    "proof_output": "Board-readable Proof Card and Evidence Docket showing the path from trust question to reusable procurement control artifact.",
    "credential": "GoalOS Sovereign AI Procurement Control Builder",
    "rsi_upgrade": "The accepted procurement control artifact earns scoped upgrade rights: future procurement workflows can reuse it only after proof, review, monitoring, and rollback checks.",
    "status": "Illustrative until live Evidence Docket is completed.",
    "evidence_items": [
      "Sovereign buyer question",
      "GoalOSCommit",
      "RunCommitment",
      "Proof mission specification",
      "Builder deliverables",
      "Reviewer attestation",
      "Risk and rollback plan",
      "Evidence Docket",
      "Proof Card",
      "SelectionCertificate",
      "Chronicle entry"
    ],
    "public_line": "Sovereign AI procurement becomes proof, confidence, and reusable capability."
  }
]
CONTRACTS = [
  [
    "AEPGoalOSCommitRegistry",
    "Records aim, authority, constraints, risk, budget, evaluator set and rollback duty."
  ],
  [
    "AEPRunCommitmentRegistry",
    "Records the selected run path, policy set, tools, artifacts and approvals."
  ],
  [
    "JobRegistry",
    "Posts the public proof mission and stores public-safe mission metadata."
  ],
  [
    "JobClaimBondManager",
    "Locks a builder claim bond so serious work is distinguishable."
  ],
  [
    "ProofSubmissionRegistry",
    "Stores proof submission hash and proof-card candidate hash."
  ],
  [
    "ReviewerBondRegistry",
    "Bonds reviewer accountability and challenge-window discipline."
  ],
  [
    "ProofCardRegistry",
    "Anchors public-safe Proof Card hash and URI."
  ],
  [
    "ProofCredentialRegistry",
    "Issues non-transferable credentials for accepted proof work."
  ],
  [
    "ReputationRegistry",
    "Records accepted proof, reviewer quality and future routing signals."
  ],
  [
    "AEPEvidenceDocketRegistry",
    "Anchors the Evidence Docket that makes claims auditable."
  ],
  [
    "AEPSelectionGate",
    "Decides whether an artifact earns scoped upgrade rights."
  ],
  [
    "AEPChronicleRegistry",
    "Records durable memory for future routing and learning."
  ]
]

def esc(x): return html.escape(str(x), quote=True)
CSS = '''
:root{--ink:#071327;--muted:#4a5872;--line:#d8d1c4;--ivory:#f8f3ea;--paper:#fffaf0;--navy:#08152b;--gold:#b98a2c;--gold2:#e8d59d;--sage:#dfe9dc;--blue:#dde8f6;--card:#ffffff;}
*{box-sizing:border-box} body{margin:0;background:var(--ivory);color:var(--ink);font-family:Inter,ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif;line-height:1.55} a{color:inherit}.top{position:sticky;top:0;z-index:5;background:rgba(8,21,43,.97);color:#fff;border-bottom:1px solid rgba(255,255,255,.08)}.nav{max-width:1180px;margin:0 auto;padding:15px 22px;display:flex;gap:20px;align-items:center;justify-content:space-between}.brand{font-weight:850;letter-spacing:-.02em}.navlinks{display:flex;gap:18px;flex-wrap:wrap}.navlinks a{font-weight:750;font-size:13px;text-decoration:none;color:#f8f3ea}.hero{background:linear-gradient(135deg,#f8f3ea 0,#fffaf0 45%,#e9dfcc 100%);border-bottom:1px solid var(--line)}.wrap{max-width:1180px;margin:0 auto;padding:54px 22px}.eyebrow{font-size:12px;letter-spacing:.18em;text-transform:uppercase;color:var(--gold);font-weight:900}.hero h1{font-size:clamp(44px,6vw,82px);line-height:.94;margin:14px 0 18px;letter-spacing:-.065em;max-width:1050px}.lead{font-size:20px;color:var(--muted);max-width:890px}.cta{display:flex;gap:14px;flex-wrap:wrap;margin-top:28px}.btn{border:1px solid var(--navy);padding:12px 18px;border-radius:999px;background:var(--navy);color:#fff;text-decoration:none;font-weight:850}.btn.alt{background:transparent;color:var(--navy)}.grid{display:grid;gap:18px}.cards3{grid-template-columns:repeat(3,minmax(0,1fr))}.cards2{grid-template-columns:repeat(2,minmax(0,1fr))}.card{background:rgba(255,255,255,.78);border:1px solid var(--line);border-radius:22px;padding:22px;box-shadow:0 18px 45px rgba(8,21,43,.06)}.card.dark{background:var(--navy);color:#fff;border-color:#112345}.card h3{font-size:24px;line-height:1.04;margin:8px 0 10px;letter-spacing:-.035em}.card p{color:var(--muted);margin:0}.card.dark p{color:#d7dfeb}.num{font-size:13px;letter-spacing:.14em;text-transform:uppercase;color:var(--gold);font-weight:900}.section{padding:44px 0;border-top:1px solid var(--line)}.section h2{font-size:clamp(32px,4vw,54px);line-height:1;margin:0 0 18px;letter-spacing:-.055em}.section p{font-size:17px;color:var(--muted);max-width:920px}.flow{display:grid;gap:10px;margin-top:18px}.step{display:grid;grid-template-columns:52px 1fr;gap:14px;align-items:start;background:#fff;border:1px solid var(--line);border-radius:18px;padding:14px}.step b{display:block}.badge{width:40px;height:40px;border-radius:50%;display:flex;align-items:center;justify-content:center;background:var(--navy);color:#fff;font-weight:900}.table{width:100%;border-collapse:separate;border-spacing:0;border:1px solid var(--line);border-radius:20px;overflow:hidden;background:#fff}.table th,.table td{padding:14px;text-align:left;border-bottom:1px solid var(--line);vertical-align:top}.table th{background:#f0e6d7;font-size:12px;text-transform:uppercase;letter-spacing:.12em;color:#72551d}.table tr:last-child td{border-bottom:0}.proof-header{background:linear-gradient(135deg,var(--navy),#142645);color:#fff;border-radius:28px;padding:34px;margin-top:22px}.proof-header p{color:#dfe7f4}.status{font-size:12px;text-transform:uppercase;letter-spacing:.12em;color:var(--gold2);font-weight:900}.footer{padding:36px 22px;border-top:1px solid var(--line);color:var(--muted);font-size:13px}.mono{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:13px;background:#fff;border:1px solid var(--line);border-radius:16px;padding:14px;overflow:auto}.notice{background:#fff7da;border:1px solid #e1c86e;border-radius:18px;padding:16px;color:#493b12}@media(max-width:900px){.cards3,.cards2{grid-template-columns:1fr}.hero h1{font-size:44px}.wrap{padding:38px 18px}.nav{align-items:flex-start;flex-direction:column}.step{grid-template-columns:1fr}}
'''
def page(filename, title, body, out):
    doc=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)}</title><meta name="description" content="GoalOS AGIALPHA triple Proof Card demand center."><style>{CSS}</style></head><body data-build="{MARKER}" data-proof-card-count="3"><header class="top"><div class="nav"><div class="brand">GoalOS AGIALPHA Ascension</div><nav class="navlinks"><a href="index.html">Home</a><a href="proof-cards.html">Proof Cards</a><a href="agialpha-ledger-route.html">AGIALPHA Route</a><a href="sovereign-rsi-control-plane.html">Sovereign RSI</a><a href="evidence-docket.html">Evidence Docket</a></nav></div></header>{body}<footer class="footer"><div class="wrap" style="padding-top:0;padding-bottom:0">Illustrative public demand center until live Evidence Dockets are completed. No investment, legal, tax, security, AGI, ASI, ROI, or mainnet-deployment claim.</div></footer></body></html>'''
    (out/filename).write_text(doc, encoding='utf-8')
def card_tile(c):
    return f'''<article class="card" data-proof-card-id="{esc(c['id'])}"><span class="num">Proof Card {esc(c['id'])}</span><h3>{esc(c['title'])}</h3><p>{esc(c['subtitle'])}</p><p style="margin-top:14px"><a class="btn alt" href="proof-card-{esc(c['id'])}.html">Open complete proof card</a></p></article>'''
def contract_table():
    rows=''.join(f'<tr><td><b>{esc(a)}</b></td><td>{esc(b)}</td></tr>' for a,b in CONTRACTS)
    return f'<table class="table"><thead><tr><th>Registry / contract</th><th>Role in proof route</th></tr></thead><tbody>{rows}</tbody></table>'
def evidence_list(c):
    return '<ul>' + ''.join(f'<li>{esc(x)}</li>' for x in c['evidence_items']) + '</ul>'
def proof_card_body(c):
    return f'''<main><section class="hero"><div class="wrap"><div class="eyebrow">Complete Proof Card {esc(c['id'])}</div><h1>{esc(c['title'])}</h1><p class="lead">{esc(c['subtitle'])}</p><div class="proof-header"><div class="status">{esc(c['status'])}</div><h2 style="margin:10px 0 12px;font-size:34px;letter-spacing:-.04em">{esc(c['public_line'])}</h2><p>{esc(c['why_it_matters'])}</p></div></div></section><div class="wrap"><section class="section"><h2>The buyer problem</h2><p>{esc(c['problem'])}</p></section><section class="section"><h2>The proof mission</h2><p>{esc(c['mission'])}</p><div class="notice"><b>Public-safe boundary:</b> private prompts, buyer data, procurement files, and internal evidence stay off-chain. Public anchors, proof-card hashes, credential decisions, and reputation signals can be recorded.</div></section><section class="section"><h2>Where AGIALPHA becomes useful</h2><p>{esc(c['agialpha_use'])}</p><div class="grid cards2"><div class="card"><span class="num">Coordination</span><h3>AGIALPHA is used when trust crosses parties.</h3><p>It coordinates sponsor, builder, reviewer, proof, credential, reputation and settlement actions.</p></div><div class="card"><span class="num">Token address</span><h3>Existing AGIALPHA asset.</h3><p class="mono">{AGIALPHA}</p></div></div></section><section class="section"><h2>Smart-contract / registry route</h2><p>The route below makes the contract suite explicit.</p>{contract_table()}</section><section class="section"><h2>Evidence Docket checklist</h2><p>The Proof Card is credible only when the Evidence Docket can support the public claim.</p>{evidence_list(c)}</section><section class="section"><h2>Sovereign RSI upgrade logic</h2><p>{esc(c['rsi_upgrade'])}</p><div class="flow"><div class="step"><div class="badge">1</div><div><b>Observe weakness</b> A weak workflow or trust artifact is identified.</div></div><div class="step"><div class="badge">2</div><div><b>Improve artifact</b> A builder creates a stronger workflow, control, rubric or proof package.</div></div><div class="step"><div class="badge">3</div><div><b>Prove change</b> Evidence, review notes and public-safe hashes are assembled.</div></div><div class="step"><div class="badge">4</div><div><b>Select carefully</b> Reviewer validation and Selection Gate decide whether scoped upgrade rights are earned.</div></div><div class="step"><div class="badge">5</div><div><b>Propagate only if proven</b> Future workflows reuse the accepted artifact; unsafe material cannot shape production paths.</div></div></div></section><section class="section"><h2>Claim boundary</h2><p>This page does not claim achieved AGI, ASI, superintelligence, investment return, legal approval, tax approval, security approval, customer result, or mainnet deployment. It is a public usage example until a live Evidence Docket is completed.</p></section></div></main>'''
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--out', default='site'); args=ap.parse_args(); out=Path(args.out)
    if out.exists(): shutil.rmtree(out)
    out.mkdir(parents=True); (out/'data').mkdir(); (out/'evidence').mkdir()
    card_grid=''.join(card_tile(c) for c in CARDS)
    index=f'''<main><section class="hero"><div class="wrap"><div class="eyebrow">Flagship Demand Center</div><h1>Three Proof Cards that make GoalOS AGIALPHA Ascension visible.</h1><p class="lead">GoalOS turns useful AI workflow work into proof. AGIALPHA coordinates proof-settled missions. Reviewers validate evidence. Proof Cards create confidence. Accepted artifacts earn scoped upgrade rights through sovereign RSI.</p><div class="cta"><a class="btn" href="proof-cards.html">View all three Proof Cards</a><a class="btn alt" href="agialpha-ledger-route.html">See AGIALPHA route</a><a class="btn alt" href="sovereign-rsi-control-plane.html">See RSI loop</a></div></div></section><div class="wrap"><section class="section"><h2>The three visible proof cards</h2><p>Proof Card 001 is simple and relatable. Proof Card 002 is enterprise-trust oriented. Proof Card 003 is the flagship sovereign procurement control tower.</p><div class="grid cards3">{card_grid}</div></section><section class="section"><h2>Why this creates demand</h2><div class="grid cards3"><div class="card dark"><span class="num">Buyer</span><h3>Trust becomes understandable.</h3><p>People can see what improved, what was reviewed and what remains private.</p></div><div class="card dark"><span class="num">Sponsor</span><h3>Demand becomes fundable.</h3><p>Proof missions give sponsors a concrete way to fund useful workflow improvement.</p></div><div class="card dark"><span class="num">Network</span><h3>Reputation compounds.</h3><p>Accepted proof creates credentials, reputation and better routing for future work.</p></div></div></section></div></main>'''
    page('index.html','GoalOS AGIALPHA Demand Center',index,out)
    rows=''.join(f'<tr><td><b>Proof Card {esc(c["id"])} - {esc(c["title"])}</b></td><td>{esc(c["audience"])}</td><td>{esc(c["proof_output"])}</td><td><a href="proof-card-{esc(c["id"])}.html">Open</a></td></tr>' for c in CARDS)
    page('proof-cards.html','Proof Cards',f'<main><section class="hero"><div class="wrap"><div class="eyebrow">Proof Card Gallery</div><h1>All three proof cards are visible, complete and linked.</h1><p class="lead">Each card includes buyer problem, mission, AGIALPHA use, contract route, Evidence Docket checklist, RSI upgrade logic and claim boundary.</p></div></section><div class="wrap"><section class="section"><table class="table"><thead><tr><th>Proof Card</th><th>Audience</th><th>Output</th><th>Page</th></tr></thead><tbody>{rows}</tbody></table></section></div></main>',out)
    for c in CARDS: page(f'proof-card-{c["id"]}.html', f'Proof Card {c["id"]}', proof_card_body(c), out)
    page('flagship-use-case.html','Flagship Use Case', proof_card_body(CARDS[-1]), out)
    uses=['Mission posting','Builder claim bond','Proof submission bond','Reviewer bond','Proof-card action','Credential action','Reward settlement','Reputation-linked access','Evidence Docket anchoring','Selection Gate upgrade rights','Chronicle memory']
    use_cards=''.join(f'<div class="card"><span class="num">Use</span><h3>{esc(x)}</h3><p>Used when multiple parties need accountable proof-work coordination.</p></div>' for x in uses)
    page('agialpha-ledger-route.html','AGIALPHA Ledger Route',f'<main><section class="hero"><div class="wrap"><div class="eyebrow">AGIALPHA Ledger Route</div><h1>Where AGIALPHA becomes useful.</h1><p class="lead">AGIALPHA is not required for ordinary buyers. It becomes useful when sponsors, builders, reviewers, proof cards, credentials, reputation and settlement need shared coordination.</p><div class="proof-header"><span class="status">Existing coordination asset</span><h2 style="font-size:28px">AGIALPHA token address</h2><p class="mono">{AGIALPHA}</p></div></div></section><div class="wrap"><section class="section"><h2>AGIALPHA coordinates these actions</h2><div class="grid cards3">{use_cards}</div></section><section class="section"><h2>Registry route</h2>{contract_table()}</section></div></main>',out)
    rsi='<main><section class="hero"><div class="wrap"><div class="eyebrow">Sovereign RSI Control Plane</div><h1>Sovereign RSI through proof-backed upgrade rights.</h1><p class="lead">GoalOS-native RSI is efficient because future work reuses only artifacts that survived evidence, evaluation, reviewer validation, scope control, challenge windows, monitoring and rollback readiness.</p></div></section><div class="wrap"><section class="section"><h2>The RSI loop</h2><div class="flow"><div class="step"><div class="badge">1</div><div><b>Detect</b> A weak workflow, response, trust package or control artifact is identified.</div></div><div class="step"><div class="badge">2</div><div><b>Improve</b> A builder creates a stronger artifact under a bounded GoalOS mission.</div></div><div class="step"><div class="badge">3</div><div><b>Prove</b> The artifact is supported by Evidence Docket material and public-safe hashes.</div></div><div class="step"><div class="badge">4</div><div><b>Review</b> A bonded reviewer validates the evidence under a rubric.</div></div><div class="step"><div class="badge">5</div><div><b>Select</b> The Selection Gate decides whether the artifact earns scoped upgrade rights.</div></div><div class="step"><div class="badge">6</div><div><b>Propagate</b> Only approved artifacts can improve future routing, templates, policies or workflows.</div></div></div></section><section class="section"><h2>Why it is efficient</h2><p>Instead of retraining or rewriting everything, the system turns accepted proof into reusable building blocks. That reduces repeated work, improves routing quality and creates institutional memory while keeping unproven artifacts out of production paths.</p></section></div></main>'
    page('sovereign-rsi-control-plane.html','Sovereign RSI',rsi,out)
    erows=''.join(f'<tr><td><b>Proof Card {esc(c["id"])}</b></td><td>{evidence_list(c)}</td></tr>' for c in CARDS)
    page('evidence-docket.html','Evidence Docket',f'<main><section class="hero"><div class="wrap"><div class="eyebrow">Evidence Docket</div><h1>Public confidence, private evidence.</h1><p class="lead">The Proof Card is public. The Evidence Docket is the auditable evidence room. Private data stays off-chain; public-safe hashes and summaries can be anchored.</p></div></section><div class="wrap"><section class="section"><h2>Evidence by proof card</h2><table class="table"><thead><tr><th>Card</th><th>Evidence checklist</th></tr></thead><tbody>{erows}</tbody></table></section></div></main>',out)
    page('season-001.html','Season 001',f'<main><section class="hero"><div class="wrap"><div class="eyebrow">Season 001</div><h1>From first proof to proof-work market.</h1><p class="lead">Season 001 launches with the three visible proof cards and extends them into sponsor-funded missions.</p></div></section><div class="wrap"><section class="section"><h2>First missions</h2><div class="grid cards3">{card_grid}</div></section><section class="section"><h2>Operating rule</h2><div class="proof-header"><h2>No proof, no upgrade rights.</h2><p>No evidence, no review, no credential, no reputation, no propagation.</p></div></section></div></main>',out)
    links=''.join(f'<li><a href="proof-card-{esc(c["id"])}.html">Proof Card {esc(c["id"])} - {esc(c["title"])}</a>: {esc(c["public_line"])}</li>' for c in CARDS)
    page('share.html','Share Kit',f'<main><section class="hero"><div class="wrap"><div class="eyebrow">Share Kit</div><h1>Share the demand center.</h1><p class="lead">GoalOS turns sovereign AI work into proof. AGIALPHA coordinates the mission. Reviewers validate evidence. Proof Cards create confidence. Only proven artifacts improve the next workflow.</p></div></section><div class="wrap"><section class="section"><h2>Shareable proof cards</h2><ul>{links}</ul></section><section class="section"><h2>Best line</h2><div class="proof-header"><h2>GoalOS turns AI adoption into proof.</h2><p>AGIALPHA coordinates proof work. Evidence Dockets make claims auditable. Sovereign RSI reuses only what proved itself.</p></div></section></div></main>',out)
    (out/'data'/'proof-cards.json').write_text(json.dumps({'build':MARKER,'generated_at':datetime.now(timezone.utc).isoformat(),'proof_cards':CARDS}, indent=2), encoding='utf-8')
    for c in CARDS:
        (out/'data'/f'proof-card-{c["id"]}.json').write_text(json.dumps(c, indent=2), encoding='utf-8')
        (out/'evidence'/f'proof-card-{c["id"]}-evidence-docket-template.json').write_text(json.dumps({'proof_card_id':c['id'],'title':c['title'],'status':'template','required_evidence':c['evidence_items'],'contract_route':[x[0] for x in CONTRACTS],'agialpha_token':AGIALPHA,'claim_boundary':'illustrative until live Evidence Docket is completed'}, indent=2), encoding='utf-8')
    (out/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join(f'<url><loc>https://montrealai.github.io/goalos-agialpha-ascension/{p.name}</loc></url>' for p in sorted(out.glob('*.html'))) + '</urlset>', encoding='utf-8')
    (out/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: https://montrealai.github.io/goalos-agialpha-ascension/sitemap.xml\n', encoding='utf-8')
    print(f'Built {MARKER} with {len(CARDS)} proof cards at {out}')
if __name__=='__main__': main()
