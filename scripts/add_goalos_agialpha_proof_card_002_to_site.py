#!/usr/bin/env python3
from pathlib import Path
import argparse, json, html, re

AGIALPHA = "0xA61a3B3a130a9c20768EEBF97E21515A6046a1fA"

def esc(x): return html.escape(str(x), quote=True)

def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8')

def base_css():
    return """
    <style>
      :root{--navy:#07152b;--blue:#0d2546;--gold:#b99035;--ivory:#fbf7ef;--paper:#fffdf8;--muted:#5e6b7a;--line:#d8d2c4;--green:#0b7a53;}
      *{box-sizing:border-box} body{margin:0;background:var(--ivory);color:#122033;font-family:Inter,ui-sans-serif,system-ui,-apple-system,Segoe UI,Arial,sans-serif;line-height:1.55}
      a{color:#0d4d8b;text-decoration:none} a:hover{text-decoration:underline}
      .wrap{max-width:1180px;margin:0 auto;padding:32px 22px}.hero{background:linear-gradient(135deg,#07152b,#102c52);color:white;border-bottom:6px solid var(--gold)}
      .eyebrow{letter-spacing:.16em;text-transform:uppercase;color:#f5d276;font-weight:800;font-size:.78rem}.hero h1{font-size:clamp(2rem,5vw,4.7rem);line-height:.95;margin:.35em 0}.hero p{max-width:820px;font-size:1.12rem;color:#e8eef7}.button{display:inline-block;background:#f4c95d;color:#07152b;font-weight:900;border-radius:999px;padding:.8rem 1.05rem;margin:.25rem .4rem .25rem 0}.button.secondary{background:transparent;color:#fff;border:1px solid rgba(255,255,255,.35)}
      .card{background:rgba(255,255,255,.92);border:1px solid var(--line);border-radius:22px;padding:22px;box-shadow:0 18px 50px rgba(7,21,43,.08);margin:18px 0}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:18px}.metric{background:#fff;border-left:5px solid var(--gold);border-radius:16px;padding:18px}.metric b{display:block;color:var(--blue);font-size:1.15rem}.kicker{font-weight:900;color:var(--gold);letter-spacing:.12em;text-transform:uppercase;font-size:.74rem}.section h2{font-size:2rem;color:var(--blue);margin-top:1.4rem}.flow{display:grid;gap:12px}.step{background:#fff;border:1px solid var(--line);border-radius:18px;padding:16px}.step strong{color:var(--blue)} code{background:#f3ead8;color:#081a30;border-radius:7px;padding:.12rem .35rem} table{width:100%;border-collapse:collapse;background:#fff;border-radius:16px;overflow:hidden} th{background:#0d2546;color:white;text-align:left} th,td{padding:12px;border:1px solid #ded7c8;vertical-align:top} .notice{background:#fff8df;border:1px solid #e1c36c;border-radius:18px;padding:16px;color:#3c2d03}.footer{padding:30px;text-align:center;color:#6b7280}.pill{display:inline-block;border:1px solid #d8d2c4;border-radius:999px;padding:.35rem .7rem;background:#fff;margin:.25rem}.rsibox{border:2px solid var(--gold);background:#0d2546;color:#fff;border-radius:24px;padding:22px}.rsibox h3{color:#f4c95d;margin-top:0}.mono{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:.9rem;word-break:break-all}.small{font-size:.92rem;color:var(--muted)}
    </style>
    """

def shell(title, body):
    nav = """<div class='wrap' style='padding-top:14px;padding-bottom:14px'><a href='index.html'><b>GoalOS AGIALPHA Ascension</b></a> &nbsp; <a href='proof-card-001.html'>Proof Card 001</a> &nbsp; <a href='proof-card-002.html'>Proof Card 002</a> &nbsp; <a href='agialpha-contract-flow.html'>AGIALPHA Flow</a> &nbsp; <a href='sovereign-rsi-loop.html'>Sovereign RSI</a> &nbsp; <a href='proof-mission-002.html'>Sponsor Mission</a></div>"""
    return "<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>"+esc(title)+"</title>"+base_css()+"</head><body>"+nav+body+"<div class='footer'>GoalOS sets the aim. AGIALPHA coordinates proof-settled work. Evidence Dockets make claims auditable.</div></body></html>"

CONTRACTS = [
    ('AEPGoalOSCommitRegistry','Creates the institutional commitment: objective, constraints, metric, risk class, evidence, rollback expectation.'),
    ('AEPRunCommitmentRegistry','Commits the actual run plan: work packages, builders, reviewers, tools, deadlines, artifact roots.'),
    ('JobRegistry','Posts the proof mission with AGIALPHA reward and public-safe metadata.'),
    ('JobClaimBondManager','Builder claims the mission with an AGIALPHA bond.'),
    ('ProofSubmissionRegistry','Builder submits proof hashes and a proof-card candidate.'),
    ('ReviewerBondRegistry','Reviewer bonds AGIALPHA and validates the proof under a rubric.'),
    ('ProofCardRegistry','Registers the public-safe Proof Card.'),
    ('ProofCredentialRegistry','Issues non-transferable proof credentials.'),
    ('ReputationRegistry','Records approved proof and review quality.'),
    ('AEPEvidenceDocketRegistry','Anchors the Evidence Docket root and public/private boundary.'),
    ('AEPSelectionGate','Promotes only artifacts that pass proof, scope, rollout, and rollback gates.'),
    ('AEPChronicleRegistry','Records accepted artifacts and their upgrade lineage.')
]

def add_home_feature(site):
    idx=site/'index.html'
    if not idx.exists():
        raise SystemExit('site/index.html not found. Refusing to create fallback site because preservation is required.')
    html_text=idx.read_text(encoding='utf-8',errors='replace')
    marker='GOALOS_PROOF_CARD_002_FEATURE'
    if marker in html_text:
        return
    panel=f"""
    <section id='{marker}' class='section card' style='margin:28px auto;max-width:1120px'>
      <div class='kicker'>New elite usage example</div>
      <h2>Proof Card 002 - Sovereign Procurement Trust Room</h2>
      <p>A serious buyer needs to trust an AI workflow vendor. GoalOS decomposes procurement into proof missions; AGIALPHA coordinates sponsor, builder, and reviewer work; approved evidence becomes a Proof Card, credential, reputation signal, and reusable RSI artifact.</p>
      <p><a class='button' href='proof-card-002.html'>View Proof Card 002</a> <a class='button secondary' style='color:#0d2546;border-color:#d8d2c4' href='agialpha-contract-flow.html'>See AGIALPHA contract flow</a> <a class='button secondary' style='color:#0d2546;border-color:#d8d2c4' href='sovereign-rsi-loop.html'>See Sovereign RSI loop</a></p>
    </section>
    """
    if '</main>' in html_text:
        html_text=html_text.replace('</main>', panel+'</main>', 1)
    elif '</body>' in html_text:
        html_text=html_text.replace('</body>', panel+'</body>', 1)
    else:
        html_text += panel
    idx.write_text(html_text,encoding='utf-8')

def pages(site):
    flow_rows=''.join(f"<tr><td><code>{esc(c)}</code></td><td>{esc(d)}</td></tr>" for c,d in CONTRACTS)
    hero = """
    <section class='hero'><div class='wrap'><div class='eyebrow'>Proof Card 002</div><h1>Sovereign Procurement Trust Room</h1><p>A high-value GoalOS AGIALPHA use case: convert enterprise and sovereign AI procurement into proof missions, reviewed evidence, public Proof Cards, credentials, reputation, and reusable RSI artifacts.</p><p><a class='button' href='proof-card-002.html'>Read the Proof Card</a><a class='button secondary' href='agialpha-contract-flow.html'>AGIALPHA contract flow</a><a class='button secondary' href='sovereign-rsi-loop.html'>Sovereign RSI loop</a></p></div></section>
    """
    body=hero+"""
    <main class='wrap section'>
      <div class='grid'>
        <div class='metric'><b>Buyer pain</b>Procurement, security, privacy, legal, and operational trust evidence is slow to assemble and hard to verify.</div>
        <div class='metric'><b>GoalOS response</b>Decompose the trust problem into proof missions with evidence, review, Proof Cards, credentials, and reputation.</div>
        <div class='metric'><b>AGIALPHA role</b>Coordinates mission rewards, builder bonds, proof bonds, reviewer bonds, proof-card actions, credentials, and settlement.</div>
        <div class='metric'><b>RSI value</b>Only proven procurement artifacts can improve future missions through the Selection Gate.</div>
      </div>
      <div class='card'><h2>Why this is the larger example</h2><p>Proof Card 001 remains the simple buyer-support example. Proof Card 002 shows the institutional system: sponsor demand, multi-agent execution, AGIALPHA coordination, reviewer validation, Evidence Docket, proof-card publication, credentialing, reputation, and recursive improvement.</p></div>
    </main>"""
    write(site/'sovereign-procurement-trust-room.html', shell('Sovereign Procurement Trust Room', body))

    proof_body="""
    <section class='hero'><div class='wrap'><div class='eyebrow'>Public-safe proof card</div><h1>Proof Card 002</h1><p>Sovereign Procurement Trust Room: a sponsor-funded proof mission that turns buyer trust requirements into reviewed evidence and reusable RSI artifacts.</p></div></section>
    <main class='wrap section'>
      <div class='card'><h2>The story</h2><p>A serious buyer wants to adopt an AI workflow. Before adoption, the buyer needs security evidence, privacy boundaries, procurement answers, support readiness, cost/risk notes, claim safety, and rollback paths. GoalOS turns this into a proof mission. Builders create the evidence. Reviewers validate it. AGIALPHA coordinates the proof work. A public-safe Proof Card is registered without exposing private evidence.</p></div>
      <div class='grid'>
        <div class='card'><div class='kicker'>Sponsor</div><p>Funds the mission and receives a buyer-ready Evidence Docket.</p></div>
        <div class='card'><div class='kicker'>Builder</div><p>Creates evidence artifacts and submits proof hashes.</p></div>
        <div class='card'><div class='kicker'>Reviewer</div><p>Validates evidence under rubric, bond, and challenge window.</p></div>
        <div class='card'><div class='kicker'>Network</div><p>Reuses approved artifacts only after Selection Gate approval.</p></div>
      </div>
      <div class='notice'><b>Boundary:</b> This is a usage example and demand engine. It is a public-safe usage example, not a live customer result, approval statement, or Ethereum mainnet deployment announcement.</div>
    </main>"""
    write(site/'proof-card-002.html', shell('Proof Card 002', proof_body))

    contract_body=f"""
    <section class='hero'><div class='wrap'><div class='eyebrow'>AGIALPHA + smart contracts</div><h1>How the proof work is coordinated</h1><p>AGIALPHA is useful when multiple parties need a shared proof layer: sponsors, builders, reviewers, Proof Cards, credentials, reputation, and future routing.</p></div></section>
    <main class='wrap section'>
      <div class='card'><h2>AGIALPHA token</h2><p class='mono'>{AGIALPHA}</p><p>AGIALPHA coordinates proof work; it is not needed for a normal buyer to purchase a GoalOS product.</p></div>
      <table><thead><tr><th>Contract / registry</th><th>Role in Proof Card 002</th></tr></thead><tbody>{flow_rows}</tbody></table>
      <div class='rsibox'><h3>Private intelligence, public proof</h3><p>Buyer data, prompts, questionnaires, internal policy, and full review rationale stay off-chain. Public-safe hashes, credentials, reputation events, evidence roots, and selection certificates can be anchored for accountability.</p></div>
    </main>"""
    write(site/'agialpha-contract-flow.html', shell('AGIALPHA Contract Flow', contract_body))

    rsi_rows=''.join(f"<tr><td><b>{esc(p)}</b></td><td>{esc(m)}</td></tr>" for p,m in [
        ('Observe weakness','Procurement cycles repeatedly stall on the same evidence gaps.'),
        ('Improve artifact','Builders create reusable evidence indexes, answer libraries, claim boundaries, and review rubrics.'),
        ('Prove change','ProofBundles and reviewer attestations show what changed and why it is safer or more useful.'),
        ('Select upgrade','Selection Gate promotes only evidence-backed, scope-limited, rollback-ready artifacts.'),
        ('Propagate','Future missions route through accepted artifacts.'),
        ('Rollback','Unsafe or stale artifacts are paused, replaced, or rolled back with a visible receipt.')
    ])
    rsi_body=f"""
    <section class='hero'><div class='wrap'><div class='eyebrow'>Sovereign RSI</div><h1>Recursive self-improvement with proof-backed upgrade rights</h1><p>GoalOS-native RSI is efficient because future work reuses only artifacts that earned the right to propagate.</p></div></section>
    <main class='wrap section'>
      <div class='rsibox'><h3>RSI definition</h3><p>RSI = proof-backed upgrade rights. An artifact may shape future work only after evidence, evaluation, reviewer validation, scope control, challenge window, rollout readiness, monitoring, and rollback readiness.</p></div>
      <table><thead><tr><th>Phase</th><th>Meaning</th></tr></thead><tbody>{rsi_rows}</tbody></table>
    </main>"""
    write(site/'sovereign-rsi-loop.html', shell('Sovereign RSI Loop', rsi_body))

    missions=''.join(f"<tr><td><b>{esc(i)}</b></td><td>{esc(m)}</td><td>{esc(g)}</td><td>{esc(a)}</td></tr>" for i,m,g,a in [
        ('PM-002A','Trust Room Evidence Index','Create buyer-safe index of security, privacy, governance, product, and support evidence.','Evidence Docket root + Trust Room map'),
        ('PM-002B','Questionnaire Accelerator','Convert buyer questions into reviewed responses and evidence references.','Answer library + templates'),
        ('PM-002C','Claims Boundary Review','Prevent unsafe or unsupported claims before sponsor-facing use.','Approved language matrix'),
        ('PM-002D','Rollback Readiness','Define pause, replacement, and rollback paths.','Rollback plan + incident proof note'),
        ('PM-002E','Cost / Risk Docket','Record cost, latency, privacy, support, and monitoring responsibilities.','Risk-adjusted operating dossier')
    ])
    mission_body=f"""
    <section class='hero'><div class='wrap'><div class='eyebrow'>Sponsor-ready proof mission</div><h1>Mission 002</h1><p>Sponsor a Sovereign Procurement Trust Room: a bounded proof mission that creates buyer-ready evidence and reusable RSI artifacts.</p></div></section>
    <main class='wrap section'><table><thead><tr><th>ID</th><th>Mission</th><th>Goal</th><th>Artifact</th></tr></thead><tbody>{missions}</tbody></table></main>"""
    write(site/'proof-mission-002.html', shell('Proof Mission 002', mission_body))

    share_body="""
    <section class='hero'><div class='wrap'><div class='eyebrow'>Share page</div><h1>Public copy for Proof Card 002</h1><p>Copy/paste language for a safe public explanation of the new elite use case.</p></div></section>
    <main class='wrap section'><div class='card'><h2>Short post</h2><p>GoalOS AGIALPHA Ascension turns enterprise AI procurement into proof. Sponsors fund missions. Builders submit evidence. Reviewers validate. Proof Cards create trust. RSI reuses only what proved itself.</p></div><div class='card'><h2>One-line explanation</h2><p>GoalOS sets the mission, AGIALPHA coordinates proof work, and the Evidence Docket makes trust auditable.</p></div></main>"""
    write(site/'share-sovereign-trust-room.html', shell('Share Proof Card 002', share_body))


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--site', default='site')
    args=ap.parse_args()
    site=Path(args.site)
    if not site.exists():
        raise SystemExit('Site directory not found. Refusing fallback deployment.')
    add_home_feature(site)
    pages(site)

    pc001_body="""
    <section class='hero'><div class='wrap'><div class='eyebrow'>Proof Card 001</div><h1>Buyer Rescue Workflow</h1><p>A buyer cannot access a download. GoalOS improves the support workflow. AGIALPHA coordinates the proof work only where proof coordination is needed. A reviewer validates evidence. Private buyer data stays off-chain.</p></div></section>
    <main class='wrap section'>
      <div class='grid'>
        <div class='metric'><b>Problem</b>A support answer is helpful but incomplete.</div>
        <div class='metric'><b>GoalOS mission</b>Improve the support workflow from v1.0 to v1.1.</div>
        <div class='metric'><b>Proof</b>Submit before/after outputs, scorecard, proof note, and reviewer validation.</div>
        <div class='metric'><b>RSI value</b>Only the reviewed workflow upgrade may improve future support missions.</div>
      </div>
      <div class='notice'><b>Boundary:</b> This is the simple non-technical doorway use case. It remains included as Proof Card 001.</div>
    </main>"""
    if not (site/'proof-card-001.html').exists():
        write(site/'proof-card-001.html', shell('Proof Card 001', pc001_body))

    # copy json/evidence if available
    for src,dst in [
        (Path('data/examples/proof-card-002-sovereign-procurement-trust-room.json'), site/'data/proof-card-002-sovereign-trust-room.json'),
        (Path('data/examples/proof-card-002-share-kit.json'), site/'data/proof-card-002-share-kit.json'),
        (Path('evidence/examples/proof-card-002-evidence-docket-template.json'), site/'evidence/proof-card-002-evidence-docket-template.json')
    ]:
        if src.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_text(src.read_text(encoding='utf-8'), encoding='utf-8')
    print('Proof Card 002 pages added additively.')

if __name__ == '__main__':
    main()
