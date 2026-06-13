#!/usr/bin/env python3
from pathlib import Path
import argparse, json, html, re

CSS = """
:root{--navy:#07162f;--mid:#13284c;--gold:#b68a2e;--gold2:#e5c77d;--ivory:#f8f3ea;--ink:#172033;--muted:#5c6980;--line:#e3d6bd;--white:#fff;--green:#2d7d61}*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--ivory);color:var(--ink);font-family:Inter,ui-sans-serif,system-ui,-apple-system,Segoe UI,Arial,sans-serif;line-height:1.58}.gpc-nav{position:sticky;top:0;z-index:20;background:rgba(7,22,47,.98);padding:14px 24px;box-shadow:0 10px 30px rgba(7,22,47,.15)}.gpc-nav a{color:#fff;text-decoration:none;font-weight:850;margin-right:20px}.gpc-wrap{max-width:1220px;margin:auto}.gpc-hero{background:linear-gradient(135deg,#07162f 0%,#0c2344 55%,#2b2615 100%);color:#fff;padding:86px 24px 74px;border-bottom:6px solid var(--gold)}.gpc-kicker{color:var(--gold2);font-weight:900;letter-spacing:.17em;text-transform:uppercase;font-size:12px}.gpc-hero h1{font-size:clamp(42px,7vw,86px);line-height:.93;margin:14px 0 18px;letter-spacing:-.055em}.gpc-lead{font-size:20px;max-width:900px;color:#e8edf7}.gpc-actions{margin-top:28px;display:flex;gap:12px;flex-wrap:wrap}.gpc-btn{display:inline-block;background:var(--gold);color:#07162f;padding:12px 17px;border-radius:999px;text-decoration:none;font-weight:950}.gpc-btn.secondary{background:#fff;color:#07162f}.gpc-section{padding:56px 24px}.gpc-section h2{font-size:clamp(32px,4vw,54px);line-height:1;margin:0 0 16px;letter-spacing:-.04em}.gpc-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:18px}.gpc-card{background:#fff;border:1px solid var(--line);border-radius:24px;padding:22px;box-shadow:0 20px 52px rgba(7,22,47,.07)}.gpc-card.featured{border:2px solid var(--gold);background:linear-gradient(135deg,#fff,#fff7df)}.gpc-card h3{font-size:23px;line-height:1.1;margin:4px 0 10px}.gpc-badge{display:inline-block;background:#07162f;color:#fff;padding:6px 10px;border-radius:999px;font-size:12px;font-weight:900}.gpc-badge.gold{background:var(--gold);color:#07162f}.gpc-table{width:100%;border-collapse:separate;border-spacing:0;border:1px solid var(--line);border-radius:20px;overflow:hidden;background:#fff}.gpc-table th{background:#07162f;color:white;text-align:left;padding:13px;font-size:13px;text-transform:uppercase;letter-spacing:.08em}.gpc-table td{padding:14px;border-top:1px solid #eadfc8;vertical-align:top}.gpc-flow{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:11px}.gpc-step{background:#07162f;color:white;border-radius:17px;padding:14px;font-weight:800;min-height:80px}.gpc-step small{display:block;color:#d9c590;font-weight:800;margin-bottom:5px}.gpc-note{background:#fff7e7;border:1px solid #e4d2a4;border-radius:24px;padding:22px}.gpc-chart{display:grid;gap:10px}.gpc-bar{background:#f0e6d4;border-radius:999px;overflow:hidden;height:22px}.gpc-bar span{display:block;height:100%;background:linear-gradient(90deg,#07162f,#b68a2e)}.gpc-two{display:grid;grid-template-columns:1.1fr .9fr;gap:22px}.gpc-mono{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:13px;background:#07162f;color:#fff;padding:16px;border-radius:18px;overflow:auto}.gpc-footer{padding:44px 24px;background:#07162f;color:white}.gpc-detail{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:14px;margin-top:18px}.gpc-detail div{background:#fff;border:1px solid var(--line);border-radius:18px;padding:16px}.gpc-detail h4{margin:0 0 8px;color:#07162f}.gpc-list{margin:0;padding-left:20px}.gpc-timeline{border-left:4px solid var(--gold);padding-left:20px}.gpc-timeline p{margin:0 0 14px}.gpc-proofcard-head{padding:70px 24px 34px;background:linear-gradient(135deg,#fffaf0,#f8f3ea)}.gpc-proofcard-head h1{font-size:clamp(38px,6vw,72px);line-height:.95;margin:10px 0;letter-spacing:-.05em}.gpc-claim{background:#07162f;color:#fff;border-radius:26px;padding:28px;margin-top:22px}.gpc-claim strong{color:#f6dc8c}.gpc-page{padding:36px 24px 64px}.gpc-card-link{color:#07162f;text-decoration:none}.gpc-mini{font-size:13px;color:var(--muted)}@media(max-width:760px){.gpc-two{grid-template-columns:1fr}.gpc-nav a{display:inline-block;margin:4px 10px 4px 0}.gpc-section{padding:38px 18px}}
"""

def esc(s): return html.escape(str(s), quote=True)

def load_cards():
    p=Path('data/proof-cards/proof-cards-v18.json')
    if not p.exists(): raise SystemExit('Missing data/proof-cards/proof-cards-v18.json')
    return json.loads(p.read_text(encoding='utf-8'))['cards']

def nav():
    return "<nav class='gpc-nav'><a href='index.html'>GoalOS AGIALPHA Ascension</a><a href='proof-cards.html'>Proof Cards</a><a href='proof-card-010.html'>Proof Card 010</a><a href='agialpha-ledger-route.html'>AGIALPHA Route</a><a href='sovereign-rsi-control-plane.html'>RSI</a><a href='evidence-docket.html'>Evidence</a></nav>"

def page(title, body):
    return f"<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'><title>{esc(title)}</title><style>{CSS}</style></head><body>{nav()}{body}<footer class='gpc-footer'><div class='gpc-wrap'><strong>GoalOS AGIALPHA Ascension</strong><p>Illustrative until a live Evidence Docket is completed. No investment, legal, tax, security, mainnet, or AGI/ASI achievement claim.</p></div></footer></body></html>"

def contract_explainer(name):
    if 'Cyber' in name or 'SBOM' in name or 'VEX' in name or 'Patch' in name or 'Security' in name or 'RedTeam' in name or 'Incident' in name:
        return 'Cyber-sovereign evidence module for authorized defensive scope, test, remediation, challenge, or rollback.'
    if 'Benchmark' in name or 'Experiment' in name or 'Autoresearch' in name:
        return 'Benchmark/autoresearch module for repeatable experiments, task manifests, evaluator harnesses, and portfolio learning.'
    if 'Staking' in name or 'CommitReveal' in name or 'Slashing' in name:
        return 'Accountability module for evaluator staking, sealed validation, and penalties for bad-faith review.'
    mapping={'AEPGoalOSCommitRegistry':'Records the aim, mandate, scope, constraints, risk class, and success conditions.','AEPRunCommitmentRegistry':'Records the intended run plan, agent roles, policies, artifacts, and rollback obligations.','JobRegistry':'Posts the proof mission so work can be claimed and tracked.','JobClaimBondManager':'Requires builders to bond against no-show or low-quality participation.','ProofSubmissionRegistry':'Receives the proof root, metadata URI, and submission record.','ReviewerBondRegistry':'Requires reviewers/red teams to put accountable weight behind validation.','ProofCardRegistry':'Registers the public-safe Proof Card artifact.','ProofCredentialRegistry':'Issues non-transferable proof credentials for accepted work.','ReputationRegistry':'Updates participant reputation from approved proof and review quality.','AEPEvidenceDocketRegistry':'Anchors the complete audit dossier for the claim.','AEPSelectionGate':'Decides whether an artifact earns scoped upgrade rights.','AEPChronicleRegistry':'Stores durable institutional memory for future missions.','AEPRewardVault':'Holds and routes reward budgets after proof conditions are met.','TreasuryRouter':'Routes verified value into governed capability budgets.','CommercializationPerformanceVault':'Links milestone evidence to commercialization-release logic.','AlphaWorkUnitLedger':'Measures proof-settled work units for value/capability accounting.','AEPRolloutRouter':'Controls scoped rollout of selected artifacts.','AEPRollbackRegistry':'Records rollback plans and recovery receipts.','AEPFalsificationRegistry':'Records falsification attempts, failed claims, and invalidated artifacts.','AEPConformanceRegistry':'Checks whether artifacts conform to AEP / GoalOS rules.','AEPClaimBoundaryRegistry':'Keeps public claims inside approved evidence boundaries.','AEPAgentRegistry':'Registers agent/operator identities and roles.','AEPArtifactRegistry':'Registers artifacts that may enter evidence or capability archives.'}
    return mapping.get(name,'Specialized registry or control module in the GoalOS AGIALPHA proof route.')

def card_grid(cards):
    out="<div class='gpc-grid'>"
    for c in cards:
        cls='gpc-card featured' if c['id']=='010' else 'gpc-card'
        out += f"<article class='{cls}'><span class='gpc-badge {'gold' if c['id']=='010' else ''}'>Proof Card {esc(c['id'])}</span><h3>{esc(c['title'])}</h3><p><strong>{esc(c['level'])}</strong></p><p>{esc(c['thesis'])}</p><p><a class='gpc-btn' href='proof-card-{esc(c['id'])}.html'>Open Proof Card {esc(c['id'])}</a></p></article>"
    return out+"</div>"

def home_section(cards):
    return f"""<!-- GOALOS_PROOF_CARDS_V18_START --><section id='proof-card-command-center' class='gpc-section'><div class='gpc-wrap'><div class='gpc-kicker'>Proof Card Command Center</div><h2>Ten proof cards, one compounding evidence graph.</h2><p class='gpc-lead'>GoalOS-native alpha-AGI Ascension turns AI work into auditable institutional capability. AGIALPHA coordinates proof-settled work, Evidence Dockets make claims inspectable, and RSI reuses only what proved itself.</p>{card_grid(cards)}<div class='gpc-actions'><a class='gpc-btn' href='proof-cards.html'>Open full proof-card gallery</a><a class='gpc-btn secondary' href='proof-card-010.html'>Open latest execution-moat card</a></div></div></section><!-- GOALOS_PROOF_CARDS_V18_END -->"""

def portfolio_ladder(active, cards):
    h="<div class='gpc-chart'>"
    for i,c in enumerate(cards,1):
        pct=20+i*8
        if c['id']==active: pct=100
        h += f"<div><strong>Proof Card {esc(c['id'])} - {esc(c['title'])}</strong><div class='gpc-bar'><span style='width:{min(pct,100)}%'></span></div></div>"
    return h+'</div>'

def proof_page(c,cards):
    def lis(xs): return ''.join(f"<li>{esc(x)}</li>" for x in xs)
    metric_rows=''.join(f"<tr><td><strong>{esc(a)}</strong></td><td>{esc(b)}</td><td>{esc(d)}</td></tr>" for a,b,d in c.get('metrics',[]))
    contract_rows=''.join(f"<tr><td>{i+1}</td><td><code>{esc(x)}</code></td><td>{esc(contract_explainer(x))}</td></tr>" for i,x in enumerate(c['contracts']))
    route=' -> '.join(c['contracts'][:9]) + (' -> ...' if len(c['contracts'])>9 else '')
    body=f"""
<header class='gpc-proofcard-head'><div class='gpc-wrap'><div class='gpc-kicker'>Proof Card {esc(c['id'])} · {esc(c['domain'])}</div><h1>{esc(c['title'])}</h1><p class='gpc-lead'>{esc(c['thesis'])}</p><div class='gpc-claim'><strong>Proof mission.</strong> {esc(c['mission'])}</div><div class='gpc-actions'><a class='gpc-btn' href='proof-cards.html'>All Proof Cards</a><a class='gpc-btn secondary' href='agialpha-ledger-route.html'>AGIALPHA Route</a><a class='gpc-btn secondary' href='sovereign-rsi-control-plane.html'>RSI Control Plane</a></div></div></header>
<main class='gpc-page'><div class='gpc-wrap'>
<section class='gpc-section'><h2>Why this card matters</h2><div class='gpc-two'><div class='gpc-note'><p><strong>Problem.</strong> {esc(c['problem'])}</p><p><strong>Why now.</strong> {esc(c['why'])}</p></div><div class='gpc-card'><h3>Where AGIALPHA becomes useful</h3><p>{esc(c['agialpha'])}</p></div></div></section>
<section class='gpc-section'><h2>Execution graph</h2><div class='gpc-flow'><div class='gpc-step'><small>01</small>GoalOSCommit</div><div class='gpc-step'><small>02</small>RunCommitment</div><div class='gpc-step'><small>03</small>AGIALPHA-funded mission</div><div class='gpc-step'><small>04</small>Specialist agents</div><div class='gpc-step'><small>05</small>ProofBundle</div><div class='gpc-step'><small>06</small>Review + red-team</div><div class='gpc-step'><small>07</small>Evidence Docket</div><div class='gpc-step'><small>08</small>Selection Gate</div><div class='gpc-step'><small>09</small>Credential + reputation</div><div class='gpc-step'><small>10</small>Chronicle memory</div></div></section>
<section class='gpc-section'><h2>Skills, plans, and goals used</h2><div class='gpc-grid'><div class='gpc-card'><h3>Skills used</h3><ul class='gpc-list'>{lis(c['skills'])}</ul></div><div class='gpc-card'><h3>Plans used</h3><ul class='gpc-list'>{lis(c['plans'])}</ul></div><div class='gpc-card'><h3>Goals used</h3><ul class='gpc-list'>{lis(c['goals'])}</ul></div></div></section>
<section class='gpc-section'><h2>Smart-contract / registry route</h2><p>The proof path is a registry route that turns work into auditable institutional memory.</p><div class='gpc-mono'>{esc(route)}</div><table class='gpc-table' style='margin-top:18px'><tr><th>#</th><th>Contract / registry</th><th>What it contributes</th></tr>{contract_rows}</table></section>
<section class='gpc-section'><h2>Evidence Docket checklist</h2><div class='gpc-two'><div class='gpc-card'><ul class='gpc-list'>{lis(c['evidence'])}</ul></div><div class='gpc-note'><h3>Claim boundary</h3><p>This card is an experimental proof template until a live Evidence Docket is completed. It does not claim achieved AGI, achieved superintelligence, guaranteed financial return, legal/tax/security approval, offensive cyber capability, Ethereum mainnet deployment, or Kardashev Type II achievement.</p></div></div></section>
<section class='gpc-section'><h2>Measured improvement logic</h2><table class='gpc-table'><tr><th>Dimension</th><th>Before</th><th>After proof-gated upgrade</th></tr>{metric_rows}</table></section>
<section class='gpc-section'><h2>RSI upgrade logic</h2><div class='gpc-note'><p>{esc(c['rsi'])}</p><p><strong>Operating principle:</strong> unproven work cannot become future operating context; replayed, reviewed, and selected work can.</p></div></section>
<section class='gpc-section'><h2>Proof-card portfolio position</h2>{portfolio_ladder(c['id'], cards)}</section>
</div></main>
"""
    return page(f"Proof Card {c['id']} - {c['title']}", body)

def support_page(name,title,content):
    body=f"<main class='gpc-section'><div class='gpc-wrap'><h1>{esc(title)}</h1>{content}</div></main>"
    return page(title, body)

def integrate(site):
    cards=load_cards()
    site.mkdir(parents=True, exist_ok=True)
    index=site/'index.html'
    if not index.exists(): raise SystemExit('Existing main site did not build site/index.html; refusing destructive fallback.')
    html=index.read_text(encoding='utf-8', errors='replace')
    block=home_section(cards)
    html=re.sub(r"<!-- GOALOS_PROOF_CARDS_V18_START -->.*?<!-- GOALOS_PROOF_CARDS_V18_END -->", block, html, flags=re.S)
    if 'GOALOS_PROOF_CARDS_V18_START' not in html:
        html=html.replace('</body>', block+'</body>') if '</body>' in html else html+block
    index.write_text(html, encoding='utf-8')
    gallery=f"<main class='gpc-section'><div class='gpc-wrap'><div class='gpc-kicker'>Proof Card Gallery</div><h1>Substantial proof-card portfolio</h1><p class='gpc-lead'>Each Proof Card is a stable, public-safe page with problem, mission, AGIALPHA route, contracts, skills, plans, goals, Evidence Docket requirements, RSI logic, and claim boundary.</p>{card_grid(cards)}</div></main>"
    (site/'proof-cards.html').write_text(page('Proof Cards - GoalOS AGIALPHA Ascension', gallery), encoding='utf-8')
    for c in cards:
        (site/f"proof-card-{c['id']}.html").write_text(proof_page(c,cards), encoding='utf-8')
    (site/'agialpha-ledger-route.html').write_text(support_page('agialpha-ledger-route.html','Where AGIALPHA becomes useful',"<p>AGIALPHA coordinates proof-settled work: mission budgets, builder claim bonds, proof submission bonds, reviewer and red-team bonds, proof-card registration, credential issuance, reputation-linked routing, reward-vault settlement, treasury reinvestment, and Chronicle memory.</p><div class='gpc-mono'>GoalOSCommit -> RunCommitment -> JobRegistry -> ClaimBond -> ProofSubmission -> ReviewerBond -> ProofCard -> Credential -> Reputation -> EvidenceDocket -> SelectionGate -> Chronicle</div>"), encoding='utf-8')
    (site/'sovereign-rsi-control-plane.html').write_text(support_page('sovereign-rsi-control-plane.html','RSI as proof-backed upgrade rights',"<p>RSI means recursive self-improvement through evidence, evaluation, reviewer validation, scope control, challenge windows, monitoring, rollback readiness, Selection Gate approval, and Chronicle memory.</p><div class='gpc-flow'><div class='gpc-step'>observe weakness</div><div class='gpc-step'>improve artifact</div><div class='gpc-step'>prove</div><div class='gpc-step'>review</div><div class='gpc-step'>select</div><div class='gpc-step'>grant scoped upgrade rights</div><div class='gpc-step'>chronicle</div></div>"), encoding='utf-8')
    (site/'evidence-docket.html').write_text(support_page('evidence-docket.html','Evidence Docket',"<p>Every serious claim needs a docket: claim, baseline, task manifest, run trace, artifacts, evaluator report, reviewer attestation, red-team result, cost ledger, safety ledger, SelectionCertificate, rollback path, Chronicle entry, and delayed-outcome update.</p>"), encoding='utf-8')
    (site/'season-001.html').write_text(support_page('season-001.html','Season 001 proof missions',"<p>Season 001 should begin with narrow, authorized, defensible proof missions: buyer rescue, procurement trust, control tower, accumulation engine, value-to-capability treasury, sovereign enterprise OS, autoresearch reactor, corporate capability foundry, cyber-sovereign execution moat, and cyber-sovereign proof benchmark market.</p>"), encoding='utf-8')
    (site/'share.html').write_text(support_page('share.html','Share kit',"<p>GoalOS turns AI adoption into proof. AGIALPHA coordinates proof-settled work. Evidence Dockets make claims auditable. RSI reuses only what proved itself.</p>"), encoding='utf-8')
    # Remove legacy capitalized startup-like wording from any generated main-site page.
    # Lowercase 'recursive self-improvement' is a concept; capitalized branding-like usage is avoided.
    for html_file in site.rglob('*.html'):
        txt = html_file.read_text(encoding='utf-8', errors='replace')
        txt = txt.replace('Sovereign Recursive Self-Improvement', 'Sovereign RSI')
        txt = txt.replace('Recursive Self-Improvement', 'RSI')
        html_file.write_text(txt, encoding='utf-8')

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--site', default='site'); args=ap.parse_args()
    integrate(Path(args.site))
    print('Integrated substantial Proof Cards 001-010 into canonical main website root.')
if __name__=='__main__': main()
