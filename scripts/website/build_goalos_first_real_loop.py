#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, html, json, re, shutil
from pathlib import Path

HOME_START='<!-- GOALOS_FIRST_REAL_LOOP_START -->'
HOME_END='<!-- GOALOS_FIRST_REAL_LOOP_END -->'
HOME_STYLE_START='<!-- GOALOS_FIRST_REAL_LOOP_STYLE_START -->'
HOME_STYLE_END='<!-- GOALOS_FIRST_REAL_LOOP_STYLE_END -->'
MISSION_008_END='<!-- GOALOS_PROOF_MISSION_008_END -->'
BASE_URL='https://montrealai.github.io/goalos-agialpha-ascension/'
PAGES=['first-real-loop.html','first-real-loop-architecture.html','first-real-loop-docket.html']


def load(path: Path): return json.loads(path.read_text(encoding='utf-8'))
def dump(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
def esc(value): return html.escape(str(value), quote=True)
def canonical(value): return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',',':'))
def digest_bytes(value: bytes): return hashlib.sha256(value).hexdigest()
def digest(value): return digest_bytes(canonical(value).encode('utf-8'))
def file_digest(path: Path): return digest_bytes(path.read_bytes())


def validate(content, mainnet):
    errors=[]
    if content.get('releaseId')!='GOALOS-AGIALPHA-FIRST-REAL-LOOP-001': errors.append('release identity mismatch')
    if content.get('schemaVersion')!='1.0.0': errors.append('schema version mismatch')
    if content.get('seed',{}).get('id')!='ColdChain-Energy-Seed-001': errors.append('seed identity mismatch')
    if content.get('mark',{}).get('green_flamed') is not True: errors.append('MARK result must be explicitly green-flamed')
    if len(content.get('jobs',[]))!=5 or not all(x.get('success') for x in content.get('jobs',[])): errors.append('five successful jobs required')
    if len(content.get('sources',[]))!=12: errors.append('twelve source records required')
    if len(content.get('acceptedInterventions',[]))!=4: errors.append('four accepted top-five interventions required')
    if content.get('comparison',{}).get('reuse_lift_percent')!=66.67: errors.append('bounded reuse lift must remain 66.67%')
    if content.get('comparison',{}).get('hallucination_delta')!=0 or content.get('comparison',{}).get('safety_delta')!=0: errors.append('comparison deltas mismatch')
    if len(content.get('artifactLedger',[]))!=12: errors.append('twelve-artifact ledger required')
    if len(content.get('runtime',{}).get('phases',[]))!=8: errors.append('eight proof phases required')
    if content.get('runtime',{}).get('finalState')!='HUMAN_REVIEW_REQUIRED': errors.append('terminal state must withhold authority')
    if content.get('runtime',{}).get('authority')!='NONE_GRANTED': errors.append('authority must be none')
    if mainnet.get('goalosCreatedContractCount')!=48: errors.append('Mainnet GoalOS contract record mismatch')
    ver=mainnet.get('verification',{})
    if ver.get('verified')!=48 or ver.get('failed')!=0: errors.append('Mainnet verification record mismatch')
    if not mainnet.get('notExternallyAudited'): errors.append('external audit boundary missing')
    forbidden=['guaranteed return','guaranteed roi','production authorized','user funds authorized']
    blob=canonical(content).lower()
    for phrase in forbidden:
        if phrase in blob: errors.append(f'forbidden claim framing: {phrase}')
    if errors: raise RuntimeError('; '.join(errors))


def make_public_docket(c, mainnet):
    docket={
        'schemaVersion':'1.0.0',
        'docketId':'GOALOS-FIRST-REAL-LOOP-DOCKET-001',
        'releaseId':c['releaseId'],
        'releaseDate':c['releaseDate'],
        'lineage':c['lineage'],
        'missionContract':{
            'seedId':c['seed']['id'],
            'domain':c['seed']['domain'],
            'foresightGenome':c['seed']['foresight_genome'],
            'jobGraph':c['seed']['job_graph'],
            'riskEnvelope':c['seed']['risk_envelope'],
            'promotionCriteria':c['seed']['promotion_criteria']},
        'mark':{
            'decision':'GREEN_FLAMED' if c['mark']['green_flamed'] else 'WITHHELD',
            'averageScore':c['mark']['average_score'],
            'scores':c['mark']['scores'],
            'reviewBoundary':'Internal structured demonstration; independent review remains required for external proof.'},
        'sovereign':c['sovereign'],
        'jobs':c['jobs'],
        'evidenceSummary':{
            'credibleSources':len(c['sources']),
            'acceptedInterventions':len(c['acceptedInterventions']),
            'artifactCount':len(c['artifactLedger']),
            'hallucinatedSourceDelta':c['comparison']['hallucination_delta'],
            'safetyDelta':c['comparison']['safety_delta']},
        'acceptedInterventions':c['acceptedInterventions'],
        'reusableConstruct':c['compiler'],
        'vNext':c['vNext'],
        'treatmentControl':c['comparison'],
        'successConditions':{
            'seedCommitted':True,'markReviewed':True,'fiveJobsPassed':True,'evidenceDocketSealed':True,
            'compilerExtracted':True,'vNextComparedWithControl':True,'humanPromotionPending':True},
        'goalosRecord':{
            'network':mainnet['network'],'goalosContracts':mainnet['goalosCreatedContractCount'],
            'operatorVerification':f"{mainnet['verification']['verified']}/{mainnet['verification']['goalosContracts']}",
            'productionActivation':'NOT_ACTIVATED','userFundAuthorization':'NO','externalAuditClaim':'NONE'},
        'terminal':{
            'state':c['runtime']['finalState'],'authority':c['runtime']['authority'],
            'externalActions':0,'walletConnections':0,'networkRequests':0},
        'claimBoundary':c['identity']['claimBoundary']}
    docket['runCommitment']=digest(docket)
    return docket


def artifact_payloads(c, docket, brief):
    return [
        docket,c['seed'],c['mark'],c['sovereign'],c['jobs'],c['sources'],c['acceptedInterventions'],c['compiler'],c['vNext'],c['comparison'],
        {'falsificationConditions':['reuse lift below 25%','hallucination delta above zero','safety delta above zero','fewer than three reviewer-accepted interventions','source identity or replay failure','authority boundary breach']},
        {'executiveBrief':brief}]


def executive_brief(c, docket):
    x=c['comparison']
    return f"""# GoalOS AGIALPHA Ascension First Real Loop — Executive Review Brief

**Release:** `{c['releaseId']}`  
**Run commitment:** `{docket['runCommitment']}`  
**Terminal state:** `{c['runtime']['finalState']}`  
**Authority:** `{c['runtime']['authority']}`

## Decision posture

The bounded first-loop demonstration completed its declared mechanics: Nova-Seed commitment, MARK review, Mini Sovereign formation, five proof-producing jobs, Evidence Docket assembly, capability-compiler extraction, and a vNext treatment/control challenge.

## Recorded result

- MARK average: **{c['mark']['average_score']} / 5**
- Jobs: **5 / 5 passed**
- Curated source records: **{len(c['sources'])}**
- Accepted interventions in the top five: **{len(c['acceptedInterventions'])}**
- Evidence artifacts: **{len(c['artifactLedger'])}**
- Control yield: **{x['control_yield']:.2f}**
- Treatment yield: **{x['treatment_yield']:.2f}**
- Deterministic scaffold reuse lift: **{x['reuse_lift_percent']:.2f}%**
- Hallucination delta: **{x['hallucination_delta']}**
- Safety delta: **{x['safety_delta']}**

## Review decision

**Evidence package ready for human review. Production authority remains withheld.** Independent reviewer replication, archived source verification, and domain-professional review remain prerequisites for stronger external claims or operational use.

## Claim boundary

{c['identity']['claimBoundary']}
"""


def embedded_data(c, docket, ledger):
    payload=dict(c)
    payload['publicDocket']=docket
    payload['artifactLedger']=ledger
    raw=json.dumps(payload,ensure_ascii=False,separators=(',',':')).replace('</script','<\\/script')
    return f'<script type="application/json" id="frl-data">{raw}</script>'


def common_head(title, description):
    return f'''<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#030607"><meta name="description" content="{esc(description)}"><title>{esc(title)}</title><link rel="icon" href="data:image/svg+xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 64 64%27%3E%3Crect width=%2764%27 height=%2764%27 rx=%2718%27 fill=%27%23030607%27/%3E%3Ccircle cx=%2732%27 cy=%2732%27 r=%2719%27 fill=%27none%27 stroke=%27%238fffd2%27 stroke-width=%274%27/%3E%3Cpath d=%27M32 13v38M13 32h38%27 stroke=%27%23fff0bd%27 stroke-width=%273%27/%3E%3C/svg%3E"><link rel="stylesheet" href="assets/goalos-v86-preserve.css"><style id="goalos-v86-critical">html{{background:#030607}}body{{min-height:100vh}}.frl-shell{{max-width:1240px;margin:auto}}</style><link rel="stylesheet" href="assets/first-real-loop/first-real-loop.css"><script defer src="assets/goalos-v86-dynamic-ai.js"></script><script defer src="assets/first-real-loop/first-real-loop.js"></script>'''


def nav(current='experience'):
    links=[('experience','first-real-loop.html','Experience'),('architecture','first-real-loop-architecture.html','Architecture'),('docket','first-real-loop-docket.html','Evidence Docket')]
    items=''.join(f'<a href="{href}"{(" aria-current=\"page\"" if key==current else "")}>{label}</a>' for key,href,label in links)
    return f'''<a class="frl-skip" href="#main">Skip to content</a><nav class="frl-nav" aria-label="First Real Loop navigation"><div class="frl-shell frl-navin"><a class="frl-brand" href="index.html"><span class="frl-brand-mark" aria-hidden="true"></span><span>GoalOS · First Real Loop</span></a><div class="frl-navlinks">{items}<a href="index.html">GoalOS Home</a></div></div></nav>'''


def footer(c):
    return f'''<footer class="frl-footer"><div class="frl-shell frl-footerin"><span>GoalOS AGIALPHA Ascension · {esc(c['releaseId'])}</span><span>Evidence-ready is not authority-ready · Human review required</span></div></footer>'''


def loop_svg():
    nodes=[('COMMIT',310,36),('SEED',500,112),('MARK',584,310),('SOVEREIGN',500,508),('WORK',310,584),('PROOF',120,508),('LEARN',36,310),('vNEXT',120,112)]
    rays=''.join(f'<line class="frl-loop-ray" x1="310" y1="310" x2="{x}" y2="{y}"/>' for _,x,y in nodes)
    ns=''.join(f'<g class="frl-loop-node"><circle cx="{x}" cy="{y}" r="35"/><text x="{x}" y="{y+4}">{esc(n)}</text></g>' for n,x,y in nodes)
    return f'''<svg class="frl-loop-svg" viewBox="0 0 620 620" role="img" aria-label="Eight-phase First Real Loop proof cycle"><defs><linearGradient id="frlLoopGradient"><stop stop-color="#fff0bd"/><stop offset=".48" stop-color="#8fffd2"/><stop offset="1" stop-color="#73eaff"/></linearGradient><radialGradient id="frlCoreGradient"><stop stop-color="#fff"/><stop offset=".28" stop-color="#fff0bd"/><stop offset=".66" stop-color="#8fffd2"/><stop offset="1" stop-color="#123d2e"/></radialGradient><filter id="frlGlow"><feGaussianBlur stdDeviation="7" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs><circle class="frl-loop-track" cx="310" cy="310" r="274"/><circle class="frl-loop-inner" cx="310" cy="310" r="205"/><circle class="frl-loop-inner" cx="310" cy="310" r="142"/>{rays}{ns}<circle class="frl-loop-core" cx="310" cy="310" r="104"/><text class="frl-loop-coretext" x="310" y="292">FIRST</text><text class="frl-loop-coretext" x="310" y="316">REAL</text><text class="frl-loop-coretext" x="310" y="340">LOOP</text><circle class="frl-tracer" cx="310" cy="75" r="7"/></svg>'''


def experience_page(c,docket,ledger):
    metrics=[('12','credible sources'),('5 / 5','jobs passed'),('12','evidence artifacts'),('66.67%','bounded reuse lift'),('0','hallucination delta'),('NONE','authority granted')]
    metric_html=''.join(f'<div class="frl-ribbon-card"><strong>{a}</strong><span>{esc(b)}</span></div>' for a,b in metrics)
    phase_buttons=''.join(f'<button class="frl-phase" type="button" data-phase="{i}" aria-label="Inspect {esc(p["title"])}"><i></i><span>{esc(p["label"])}</span></button>' for i,p in enumerate(c['runtime']['phases']))
    jobs=''.join(f'''<article class="frl-job frl-reveal"><strong>{esc(j['id'])} · PASS</strong><h3>{esc(j['name'])}</h3><div class="frl-jobmetric">{esc(j['metric'])}</div><p>{esc(j['detail'])}</p><p>{esc(j['proof'])}</p></article>''' for j in c['jobs'])
    interventions=''.join(f'''<article class="frl-intervention frl-reveal"><div class="frl-intervention-head"><span class="frl-num">{esc(x['id'])} · {esc(x['red_team_verdict'])}</span><span class="frl-score">QUALITY {x['quality_score']:.2f}</span></div><h3>{esc(x['title'])}</h3><div class="frl-tags"><span class="frl-tag">{esc(x['capex_bucket'])}</span><span class="frl-tag">{len(x['source_ids'])} traces</span><span class="frl-tag">{esc(x['risk_tier'])}</span></div><p>{esc(x['mechanism'])}</p></article>''' for x in c['acceptedInterventions'])
    laws=''.join(f'<article class="frl-law frl-reveal"><strong>{esc(x["title"])}</strong><p>{esc(x["detail"])}</p></article>' for x in c['invariants'])
    return f'''<!doctype html><html lang="en"><head>{common_head(c['identity']['title'],c['identity']['thesis'])}</head><body class="frl-body" data-run-state="ready">{nav('experience')}<main id="main"><section class="frl-hero"><div class="frl-shell frl-hero-grid"><div><div class="frl-kicker">{esc(c['identity']['kicker'])}</div><h1>THE FIRST<br><span>REAL LOOP</span></h1><div class="frl-hero-line">{esc(c['identity']['heroLine'])}</div><p class="frl-thesis">{esc(c['identity']['thesis'])}</p><div class="frl-doctrine">{esc(c['identity']['doctrine'])}</div><div class="frl-actions"><a class="frl-btn primary" href="#flight-deck">Run the governed loop</a><a class="frl-btn" href="first-real-loop-docket.html">Inspect the Evidence Docket</a></div><div class="frl-status-pill">{esc(c['identity']['status'])}</div></div><div><div class="frl-oracle">{loop_svg()}</div><div class="frl-hero-metrics"><div class="frl-hero-metric"><strong>5 / 5</strong><span>proof-producing jobs</span></div><div class="frl-hero-metric"><strong>66.67%</strong><span>deterministic reuse lift</span></div><div class="frl-hero-metric"><strong>0</strong><span>external actions</span></div></div></div></div></section>
<section class="frl-section void"><div class="frl-shell"><div class="frl-heading frl-reveal"><div class="frl-eyebrow">The recursion contract</div><h2>One loop. Every consequence visible.</h2><p>The original First Real Loop is preserved as a causal institution: one Nova-Seed is judged, bounded, worked, challenged, remembered, and transferred into vNext. GoalOS adds explicit authority states, artifact commitments, replay posture, falsification conditions, and a terminal human gate.</p></div><div class="frl-metric-ribbon">{metric_html}</div></div></section>
<section class="frl-section void" id="flight-deck"><div class="frl-shell"><div class="frl-heading frl-reveal"><div class="frl-eyebrow">Local proof-cycle command theatre</div><h2>Ignite a bounded mission.</h2><p>This browser-local demonstration makes no network request and performs no external action. It composes a deterministic Evidence Docket around your mission language, then stops before authority.</p></div><div class="frl-console"><aside class="frl-control"><div class="frl-console-head"><div><span>MISSION CONTRACT</span><h3>Declare the loop</h3></div><span>LOCAL ONLY</span></div><div class="frl-field"><label for="frl-mission">Mission</label><textarea id="frl-mission">Identify a bounded, evidence-backed operational improvement and extract only the reusable rules that survive review.</textarea></div><fieldset class="frl-field" style="border:0;padding:0"><legend>Constitutional posture</legend><div class="frl-segmented" data-frl-postures data-value="constitutional"><button type="button" data-posture="conservative" aria-pressed="false">Conservative</button><button class="is-active" type="button" data-posture="constitutional" aria-pressed="true">Constitutional</button><button type="button" data-posture="frontier" aria-pressed="false">Frontier</button></div></fieldset><div class="frl-field"><label for="frl-depth">Evidence depth</label><select id="frl-depth"><option value="full">Full loop · 8 phases · 12 artifacts</option><option value="review">Review emphasis · stronger falsification</option><option value="lineage">Lineage emphasis · deeper vNext trace</option></select></div><p class="frl-compact-law">No Evidence Docket, no promotion. No human review, no authority. No hidden mutation, no institutional memory.</p><button class="frl-btn primary" id="frl-run" type="button">Ignite governed loop</button><button class="frl-btn" id="frl-reset" type="button">Reset</button><div class="frl-result-banner" id="frl-result" aria-live="polite"><strong>Evidence package ready. Authority withheld.</strong><div class="frl-result-grid"><div><b id="frl-result-commitment">—</b><span>commitment</span></div><div><b id="frl-result-lift">—</b><span>reuse lift</span></div><div><b id="frl-result-artifacts">—</b><span>artifacts</span></div><div><b id="frl-result-state">—</b><span>decision</span></div></div></div></aside><section class="frl-runtime" aria-label="First Real Loop runtime"><div class="frl-runtime-top"><span class="frl-runtime-id" id="frl-runtime-id">RUN NOT COMMITTED</span><span class="frl-runtime-state" id="frl-runtime-state">READY · AUTHORITY NONE</span></div><div class="frl-phasebar">{phase_buttons}</div><div class="frl-runtime-body"><div class="frl-stage-inspector"><span class="frl-stage-code" id="frl-stage-code"></span><h3 id="frl-stage-title"></h3><p id="frl-stage-detail"></p><div class="frl-stage-evidence" id="frl-stage-evidence"></div></div><div class="frl-eventstream" id="frl-eventstream"><h4>Proof event stream</h4></div></div><div class="frl-runtime-foot"><span class="frl-boundary">External actions 0 · wallet connections 0 · network requests 0</span><div class="frl-runtime-actions"><button class="frl-btn small" id="frl-download-json" type="button">Download Docket JSON</button><button class="frl-btn small" id="frl-download-brief" type="button">Download Review Brief</button></div></div></section></div></div></section>
<section class="frl-section paper"><div class="frl-shell"><div class="frl-heading frl-reveal"><div class="frl-eyebrow">Causal sequence</div><h2>From intent to institutional memory.</h2><p>The loop is not “agent runs task.” It is a chain of admissibility, bounded authority, evidence production, explicit challenge, memory extraction, and comparative transfer.</p></div><div class="frl-cycle">{''.join(f'<article class="frl-cycle-card frl-reveal"><i>{i+1}</i><h3>{esc(p["title"])}</h3><p>{esc(p["detail"])}</p></article>' for i,p in enumerate(c['runtime']['phases']))}</div></div></section>
<section class="frl-section void"><div class="frl-shell"><div class="frl-heading frl-reveal"><div class="frl-eyebrow">Five proof-producing jobs</div><h2>Work becomes inspectable.</h2><p>Every stage exposes its success criterion and proof boundary. Passing the job graph means the package is reviewable—not that its recommendations are authorized for real-world execution.</p></div><div class="frl-jobs">{jobs}</div></div></section>
<section class="frl-section paper2"><div class="frl-shell"><div class="frl-comparison"><div class="frl-heading frl-reveal"><div class="frl-eyebrow">vNext treatment / control</div><h2>Learning must beat a baseline.</h2><p>Seed 002 reuses the extracted ColdChain-Energy-Compiler-v0 against an explicit control. Yield improves from 0.30 to 0.50 at the same cost units. The result remains deterministic scaffold evidence pending independent replay and archived source verification.</p><div class="frl-proof-list"><div class="frl-proof-item"><i>✓</i><div><strong>No added hallucination delta</strong><span>Both control and treatment record zero hallucinated sources.</span></div></div><div class="frl-proof-item"><i>✓</i><div><strong>No added safety delta</strong><span>Treatment does not increase recorded safety flags.</span></div></div><div class="frl-proof-item"><i>!</i><div><strong>External proof remains pending</strong><span>Independent reviewer replication and source snapshots remain required.</span></div></div></div></div><div class="frl-chart frl-reveal"><div class="frl-num">PRIMARY METRIC · ACCEPTED USEFUL INTERVENTIONS / COST UNITS</div><div class="frl-bars"><div class="frl-bar-row control"><span>Control</span><div class="frl-bar-track"><div class="frl-bar-fill" style="--value:60%"></div></div><b>0.30</b></div><div class="frl-bar-row"><span>Treatment</span><div class="frl-bar-track"><div class="frl-bar-fill" style="--value:100%"></div></div><b>0.50</b></div></div><div class="frl-lift"><strong>+66.67%</strong><p><b>Bounded reuse lift.</b><br>Not an empirical SOTA claim, production result, guaranteed outcome, or facility-specific savings estimate.</p></div></div></div></div></section>
<section class="frl-section void"><div class="frl-shell"><div class="frl-heading frl-reveal"><div class="frl-eyebrow">Accepted evidence objects</div><h2>Recommendations with memory.</h2><p>The top accepted interventions retain mechanism, source traces, causal chain, preconditions, failure modes, risk tier, quality score, and reviewer label.</p></div><div class="frl-interventions">{interventions}</div></div></section>
<section class="frl-section void"><div class="frl-shell"><div class="frl-heading frl-reveal"><div class="frl-eyebrow">Constitutional invariants</div><h2>Recursion without self-coronation.</h2><p>GoalOS separates intelligence, evidence, and authority. The loop can earn a stronger case for reuse; it cannot appoint itself, move funds, operate equipment, or convert a scaffold result into an external claim.</p></div><div class="frl-law-grid">{laws}</div></div></section>
<section class="frl-section gold"><div class="frl-shell"><div class="frl-grid3"><article class="frl-card"><span class="frl-num">Repository record</span><h3>48 / 48 operator verification</h3><p>GoalOS’s recorded contract set is represented as configured evidence. Production activation remains not activated.</p></article><article class="frl-card"><span class="frl-num">Authority boundary</span><h3>User-fund authorization: no</h3><p>No wallet connection, settlement, token movement, or blockchain transaction occurs in this experience.</p></article><article class="frl-card"><span class="frl-num">Audit boundary</span><h3>No external-audit claim</h3><p>Source-identity reproducibility remains pending in the repository release boundary.</p></article></div></div></section>
<section class="frl-final"><div class="frl-shell"><div class="frl-eyebrow">Terminal state</div><h2>Proof that becomes <span>memory.</span><br>Memory that must still earn permission.</h2><p>{esc(c['identity']['claimBoundary'])}</p><div class="frl-actions" style="justify-content:center"><a class="frl-btn primary" href="first-real-loop-docket.html">Open the sealed docket</a><a class="frl-btn" href="first-real-loop-architecture.html">Enter the architecture</a></div></div></section></main>{footer(c)}{embedded_data(c,docket,ledger)}</body></html>'''


def architecture_page(c,docket,ledger):
    layers=[
        ('L0','Human Intent Root','Mission purpose, protected boundaries, success conditions, and final authority remain human-defined.','RATIFICATION'),
        ('L1','Nova-Seed Contract','Foresight genome, work graph, risk envelope, and promotion criteria become committed inputs.','COMMITTED'),
        ('L2','MARK Admissibility Kernel','Coherence, evidence, usefulness, safety, reusability, and executability are scored before work.','GATED'),
        ('L3','Mini Sovereign Institution','A bounded work organ receives only the authority required for advisory evidence production.','BOUNDED'),
        ('L4','Five-Job Execution Graph','Source discovery, modeling, generation, causal red-team, and ranking produce explicit artifacts.','OBSERVABLE'),
        ('L5','ProofBundle + Evidence Docket','Sources, outputs, dissent, failures, scores, risks, and decisions become one replayable package.','SEALED'),
        ('L6','Capability Compiler Memory','Only schemas, rubrics, source rules, and red-team constraints that survived review are versioned.','VERSIONED'),
        ('L7','vNext Falsification Trial','Parent-linked mutation competes against a declared control under yield, hallucination, and safety metrics.','CHALLENGED'),
        ('L8','Human Promotion Boundary','Evidence may support a recommendation; only an authorized human process may promote or deploy.','WITHHELD')]
    layer_html=''.join(f'<article class="frl-layer frl-reveal" id="layer-{i}"><div class="frl-layer-code">{esc(code)}</div><div><h3>{esc(name)}</h3><p>{esc(detail)}</p></div><span class="frl-layer-state">{esc(state)}</span></article>' for i,(code,name,detail,state) in enumerate(layers))
    index=''.join(f'<a href="#layer-{i}">{esc(code)} · {esc(name)}</a>' for i,(code,name,_,_) in enumerate(layers))
    mapping=[
        ('Nova-Seed','Committed mission contract','Intent and risk become replayable inputs.'),('MARK','Admissibility policy kernel','Judgment becomes explicit before execution.'),('Mini Sovereign','Bounded agent institution','Authority is enumerated and default-deny.'),('AGI Jobs','Evidence-gated action graph','Every stage has success and proof conditions.'),('Evidence Docket','Artifact manifest + provenance root','Outputs, dissent, and risk remain inspectable.'),('Compiler v0','Versioned capability memory','Only reviewed reusable rules may transfer.'),('Seed 002','Parent-linked mutation','vNext declares what changed and what was inherited.'),('Treatment / control','Falsification evaluation','Learning must outperform a baseline without worsening safety.'),('Reviewer','Human authority root','Promotion, deployment, and stronger claims stay external to the loop.')]
    left=''.join(f'<div class="frl-map-item"><strong>{esc(a)}</strong><span>Original First Real Loop</span></div>' for a,_,_ in mapping)
    right=''.join(f'<div class="frl-map-item"><strong>{esc(b)}</strong><span>{esc(d)}</span></div>' for _,b,d in mapping)
    threats=''.join(f'<article class="frl-threat frl-reveal"><strong>{esc(x["disposition"])}</strong><h3>{esc(x["title"])}</h3><p>{esc(x["control"])}</p></article>' for x in c['threats'])
    return f'''<!doctype html><html lang="en"><head>{common_head('Architecture · '+c['identity']['title'],'Constitutional architecture of the GoalOS First Real Loop.')}</head><body class="frl-body">{nav('architecture')}<main id="main"><header class="frl-arch-hero"><div class="frl-shell"><div class="frl-kicker">Constitutional systems architecture</div><h1 class="frl-page-title">THE LOOP<br>BEHIND THE LOOP</h1><p class="frl-page-lead">The GoalOS reimplementation treats recursion as an institution, not a slogan. Nine layers separate intent, judgment, execution, proof, memory, mutation, falsification, and authority so that no subsystem can silently promote itself.</p><div class="frl-status-pill">9 layers · 8 invariants · 6 threat controls · authority withheld</div></div></header>
<section class="frl-section paper"><div class="frl-shell"><div class="frl-heading frl-reveal"><div class="frl-eyebrow">Constitutional stack</div><h2>Every power has a boundary.</h2><p>The stack makes causal responsibility legible. Inputs are committed before work, outputs are sealed before learning, and learning is challenged before promotion.</p></div><div class="frl-architecture"><nav class="frl-arch-index" aria-label="Architecture layers">{index}</nav><div class="frl-arch-stack">{layer_html}</div></div></div></section>
<section class="frl-section paper2"><div class="frl-shell"><div class="frl-heading frl-reveal"><div class="frl-eyebrow">Lineage translation</div><h2>Original spirit. GoalOS-grade control.</h2><p>No concept is discarded. Each original mechanism is translated into a more explicit proof, governance, or authority primitive.</p></div><div class="frl-map"><div class="frl-map-col">{left}</div><div class="frl-map-arrow" aria-hidden="true">→</div><div class="frl-map-col">{right}</div></div></div></section>
<section class="frl-section void"><div class="frl-shell"><div class="frl-heading frl-reveal"><div class="frl-eyebrow">Threat and failure atlas</div><h2>The loop is designed to be challenged.</h2><p>Safety is not represented by a decorative badge. Each failure class has a disposition that can withhold, reject, stop, or route the system to human review.</p></div><div class="frl-threats">{threats}</div></div></section>
<section class="frl-section paper"><div class="frl-shell"><div class="frl-heading frl-reveal"><div class="frl-eyebrow">Proof state machine</div><h2>No shortcut to memory.</h2><p>The valid route is linear in authority but recursive in learning: commit → seed → judge → bound → work → prove → learn → challenge → review. A failed gate does not disappear; it becomes a preserved negative artifact.</p></div><div class="frl-cycle">{''.join(f'<article class="frl-cycle-card frl-reveal"><i>{i}</i><h3>{esc(x[1])}</h3><p>{esc(x[2])}</p></article>' for i,x in enumerate(layers))}</div></div></section>
<section class="frl-section gold"><div class="frl-shell"><div class="frl-heading"><div class="frl-eyebrow">Final constitutional equation</div><h2>Capability ≠ authority.</h2><p>Capability may produce evidence. Evidence may justify a recommendation. A recommendation may enter human review. None of those states autonomously authorizes production execution, user-fund movement, external settlement, or a stronger empirical claim.</p></div><div class="frl-terminal"><div class="frl-terminal-card"><strong>CAPABILITY STATE</strong><span>EVIDENCE_READY</span></div><div class="frl-terminal-card"><strong>AUTHORITY STATE</strong><span>NONE_GRANTED</span></div><div class="frl-terminal-card"><strong>TERMINAL STATE</strong><span>HUMAN_REVIEW_REQUIRED</span></div></div></div></section></main>{footer(c)}{embedded_data(c,docket,ledger)}</body></html>'''


def docket_page(c,docket,ledger):
    rows=''.join(f'''<article class="frl-ledger-row" data-search="{esc((x['id']+' '+x['name']+' '+x['class']+' '+x['purpose']).lower())}"><span class="frl-ledger-id">{esc(x['id'])}</span><div><strong>{esc(x['name'])}</strong><small>{esc(x['purpose'])}</small></div><span class="frl-ledger-class">{esc(x['class'])}</span><span class="frl-ledger-hash" title="{esc(x['sha256'])}">{esc(x['sha256'])}</span></article>''' for x in ledger)
    accepted=''.join(f'<article class="frl-card"><span class="frl-num">{esc(x["id"])} · {esc(x["risk_tier"])}</span><h3>{esc(x["title"])}</h3><p>{esc(x["mechanism"])}</p><p><b>Evidence traces:</b> {", ".join(map(esc,x["source_ids"]))} · <b>Reviewer:</b> {esc(x["reviewer_label"])}</p></article>' for x in c['acceptedInterventions'])
    return f'''<!doctype html><html lang="en"><head>{common_head('Evidence Docket · '+c['identity']['title'],'Sealed artifact ledger and public review docket for the GoalOS First Real Loop.')}</head><body class="frl-body">{nav('docket')}<main id="main"><header class="frl-docket-hero"><div class="frl-shell"><div class="frl-kicker">Sealed public review package</div><h1 class="frl-page-title">THE EVIDENCE<br>DOCKET</h1><p class="frl-page-lead">Twelve artifacts bind the mission, judgment, bounded authority, work graph, provenance, decisions, reusable construct, vNext mutation, falsification criteria, and terminal human gate into one inspectable record.</p><div class="frl-status-pill">Run commitment · <span id="frl-docket-commitment">{esc(docket['runCommitment'])}</span></div><div class="frl-actions"><a class="frl-btn primary" href="downloads/first-real-loop/first-real-loop-evidence-docket.json" download>Download canonical Docket JSON</a><a class="frl-btn" href="downloads/first-real-loop/first-real-loop-executive-brief.md" download>Download Executive Brief</a><button class="frl-btn" id="frl-copy-commitment" type="button">Copy commitment</button></div></div></header>
<section class="frl-section paper"><div class="frl-shell"><div class="frl-heading frl-reveal"><div class="frl-eyebrow">Artifact ledger</div><h2>Every claim has a record.</h2><p>Search the sealed ledger by artifact name, class, identifier, or purpose. Hashes are generated from canonical JSON payloads in the autonomous build.</p></div><div class="frl-ledger-tools"><input class="frl-search" id="frl-ledger-search" type="search" placeholder="Search artifacts, classes, or controls" aria-label="Search Evidence Docket artifacts"><strong id="frl-ledger-count">12 / 12 artifacts</strong></div><div class="frl-ledger">{rows}</div></div></section>
<section class="frl-section void"><div class="frl-shell"><div class="frl-heading frl-reveal"><div class="frl-eyebrow">Canonical public manifest</div><h2>One commitment. No hidden promotion.</h2><p>The public manifest records a green-flamed internal demonstration, five passed jobs, twelve evidence artifacts, a versioned compiler, a treatment/control result, and a terminal state that withholds authority.</p></div><div class="frl-manifest"><div class="frl-manifest-head"><strong>first-real-loop-evidence-docket.json</strong><span class="frl-runtime-id">SHA-256 · {esc(docket['runCommitment'])[:18]}…</span></div><pre id="frl-manifest-json"></pre></div></div></section>
<section class="frl-section paper2"><div class="frl-shell"><div class="frl-heading frl-reveal"><div class="frl-eyebrow">Accepted intervention register</div><h2>Evidence objects, not prescriptions.</h2><p>These four entries were accepted within the original deterministic top-five review. They remain advisory, source-linked, risk-labeled, and subject to facility-professional review.</p></div><div class="frl-grid2">{accepted}</div></div></section>
<section class="frl-section void"><div class="frl-shell"><div class="frl-heading frl-reveal"><div class="frl-eyebrow">Terminal disposition</div><h2>The docket closes at the human boundary.</h2></div><div class="frl-terminal"><div class="frl-terminal-card"><strong>FACTUAL CORRECTNESS</strong><span>NOT EXTERNALLY CERTIFIED</span></div><div class="frl-terminal-card"><strong>PRODUCTION</strong><span>NOT_ACTIVATED</span></div><div class="frl-terminal-card"><strong>USER FUNDS</strong><span>NOT AUTHORIZED</span></div><div class="frl-terminal-card"><strong>EXTERNAL ACTIONS</strong><span>0</span></div><div class="frl-terminal-card"><strong>AUTHORITY</strong><span>NONE_GRANTED</span></div><div class="frl-terminal-card"><strong>FINAL STATE</strong><span>HUMAN_REVIEW_REQUIRED</span></div></div></div></section>
<section class="frl-section gold"><div class="frl-shell"><div class="frl-heading"><div class="frl-eyebrow">Claim boundary</div><h2>Evidence first. Promotion later.</h2><p>{esc(c['identity']['claimBoundary'])}</p></div></div></section></main>{footer(c)}{embedded_data(c,docket,ledger)}</body></html>'''


def replace_marked(raw,start,end,replacement):
    if raw.count(start)!=1 or raw.count(end)!=1: raise RuntimeError(f'marker count mismatch: {start}')
    return re.sub(re.escape(start)+r'.*?'+re.escape(end),replacement,raw,count=1,flags=re.S)


def home_section(c):
    return f'''{HOME_START}<section class="frl-home-gateway" id="first-real-loop" data-goalos-feature="first-real-loop"><div class="frl-home-in"><div><small>GOALOS AGIALPHA ASCENSION · RECURSIVE EVIDENCE INSTITUTION</small><h2>THE FIRST <span>REAL LOOP</span></h2><p><strong>Where intelligence earns memory.</strong> One Nova-Seed becomes a bounded Sovereign, five proof-producing jobs, a twelve-artifact Evidence Docket, a reusable capability compiler, and a vNext treatment/control challenge—without granting itself authority.</p><div class="frl-home-stats"><div class="frl-home-stat"><strong>5 / 5</strong><span>jobs passed</span></div><div class="frl-home-stat"><strong>12</strong><span>sealed artifacts</span></div><div class="frl-home-stat"><strong>+66.67%</strong><span>bounded reuse lift</span></div><div class="frl-home-stat"><strong>NONE</strong><span>authority granted</span></div></div><div class="frl-home-actions"><a href="first-real-loop.html">Enter the First Real Loop</a><a href="first-real-loop-docket.html">Inspect the Docket</a><a href="first-real-loop-architecture.html">Open the Architecture</a></div></div><div class="frl-home-orbit" aria-label="First Real Loop gateway emblem"><div class="frl-home-node n1">SEED</div><div class="frl-home-node n2">PROOF</div><div class="frl-home-node n3">vNEXT</div><div class="frl-home-node n4">MARK</div><div class="frl-home-core">FIRST<br>REAL<br>LOOP</div></div></div></section>{HOME_END}'''


def inject_home(path: Path, c):
    raw=path.read_text(encoding='utf-8')
    style=f'{HOME_STYLE_START}<link rel="stylesheet" href="assets/first-real-loop/first-real-loop.css" data-goalos-first-real-loop>{HOME_STYLE_END}'
    if HOME_STYLE_START in raw: raw=replace_marked(raw,HOME_STYLE_START,HOME_STYLE_END,style)
    else:
        if '</head>' not in raw: raise RuntimeError('homepage lacks </head>')
        raw=raw.replace('</head>',style+'\n</head>',1)
    section=home_section(c)
    if HOME_START in raw: raw=replace_marked(raw,HOME_START,HOME_END,section)
    elif MISSION_008_END in raw: raw=raw.replace(MISSION_008_END,MISSION_008_END+'\n'+section,1)
    elif '</main>' in raw: raw=raw.replace('</main>',section+'\n</main>',1)
    elif '</body>' in raw: raw=raw.replace('</body>',section+'\n</body>',1)
    else: raise RuntimeError('no safe homepage insertion point')
    path.write_text(raw,encoding='utf-8')


def update_sitemap(path: Path):
    raw=path.read_text(encoding='utf-8') if path.exists() else "<?xml version='1.0' encoding='UTF-8'?><urlset xmlns='http://www.sitemaps.org/schemas/sitemap/0.9'></urlset>"
    for page in PAGES:
        url=BASE_URL+page
        if url not in raw:
            if '</urlset>' not in raw: raise RuntimeError('invalid sitemap')
            raw=raw.replace('</urlset>',f'<url><loc>{url}</loc></url></urlset>',1)
    path.write_text(raw,encoding='utf-8')


def update_status(path: Path, docket):
    status=load(path) if path.exists() else {}
    status['first_real_loop']={'release':'GOALOS-AGIALPHA-FIRST-REAL-LOOP-001','pages':PAGES,'run_commitment':docket['runCommitment'],'terminal_state':'HUMAN_REVIEW_REQUIRED','authority':'NONE_GRANTED'}
    dump(path,status)


def main():
    ap=argparse.ArgumentParser(description='Build GoalOS AGIALPHA Ascension First Real Loop additively')
    ap.add_argument('--site',default='site');ap.add_argument('--content',default='content/goalos-first-real-loop.json');ap.add_argument('--mainnet',default='data/mainnet/v4.4.0-mainnet-2026-06-21.json');ap.add_argument('--assets',default='website/first_real_loop')
    a=ap.parse_args();site=Path(a.site);cp=Path(a.content);mp=Path(a.mainnet);assets=Path(a.assets)
    if not site.is_dir(): raise RuntimeError(f'missing built site: {site}')
    required=[site/'index.html',site/'proof-mission-008.html',site/'ethereum-mainnet.html',site/'sitemap.xml',site/'site-status.json',assets/'first-real-loop.css',assets/'first-real-loop.js']
    missing=[str(x) for x in required if not x.is_file() or x.stat().st_size==0]
    if missing: raise RuntimeError('Build the preserved website, Proof Missions 001–008, and Mainnet record first: '+', '.join(missing))
    c=load(cp);mainnet=load(mp);validate(c,mainnet);docket=make_public_docket(c,mainnet);brief=executive_brief(c,docket)
    payloads=artifact_payloads(c,docket,brief);ledger=[]
    for item,payload in zip(c['artifactLedger'],payloads):
        row=dict(item);row['sha256']=digest(payload);ledger.append(row)
    before={str(p.relative_to(site)):file_digest(p) for p in site.rglob('*') if p.is_file()}
    asset_out=site/'assets/first-real-loop';asset_out.mkdir(parents=True,exist_ok=True)
    shutil.copy2(assets/'first-real-loop.css',asset_out/'first-real-loop.css');shutil.copy2(assets/'first-real-loop.js',asset_out/'first-real-loop.js')
    (site/PAGES[0]).write_text(experience_page(c,docket,ledger),encoding='utf-8')
    (site/PAGES[1]).write_text(architecture_page(c,docket,ledger),encoding='utf-8')
    (site/PAGES[2]).write_text(docket_page(c,docket,ledger),encoding='utf-8')
    inject_home(site/'index.html',c);update_sitemap(site/'sitemap.xml');update_status(site/'site-status.json',docket)
    dl=site/'downloads/first-real-loop';dl.mkdir(parents=True,exist_ok=True)
    dump(dl/'first-real-loop-evidence-docket.json',docket)
    dump(dl/'first-real-loop-artifact-ledger.json',{'schemaVersion':'1.0.0','runCommitment':docket['runCommitment'],'artifacts':ledger})
    dump(dl/'first-real-loop-replay-manifest.json',{'schemaVersion':'1.0.0','releaseId':c['releaseId'],'sourceCommit':c['lineage']['sourceCommit'],'goalosSnapshotCommit':c['lineage']['goalosSnapshotCommit'],'contentSha256':file_digest(cp),'mainnetSha256':file_digest(mp),'runCommitment':docket['runCommitment'],'replay':'Rebuild the canonical site, Proof Missions 001–008, Mainnet record, then run build_goalos_first_real_loop.py and verify_goalos_first_real_loop.py.'})
    (dl/'first-real-loop-executive-brief.md').write_text(brief,encoding='utf-8')
    after={str(p.relative_to(site)):file_digest(p) for p in site.rglob('*') if p.is_file()}
    allowed_existing={'index.html','sitemap.xml','site-status.json'}
    unexpected=[p for p,h in before.items() if p not in allowed_existing and after.get(p)!=h]
    removed=[p for p in before if p not in after]
    if unexpected or removed: raise RuntimeError(f'unexpected existing-site changes: {unexpected}; removed: {removed}')
    qa={'status':'PASS','releaseId':c['releaseId'],'pages':PAGES,'runCommitment':docket['runCommitment'],'artifactCount':len(ledger),'sourceCount':len(c['sources']),'jobsPassed':sum(1 for x in c['jobs'] if x['success']),'reuseLiftPercent':c['comparison']['reuse_lift_percent'],'existingFilesChanged':sorted(allowed_existing),'unexpectedExistingChanges':unexpected,'removedFiles':removed,'externalActions':0,'walletConnections':0,'productionActivation':'NOT_ACTIVATED','authority':'NONE_GRANTED','terminalState':'HUMAN_REVIEW_REQUIRED','contentSha256':file_digest(cp),'mainnetSha256':file_digest(mp)}
    dump(site/'qa/first-real-loop-build.json',qa);print(json.dumps(qa,indent=2));return 0

if __name__=='__main__': raise SystemExit(main())
