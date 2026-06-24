#!/usr/bin/env python3
"""Build the GoalOS AGIALPHA Ascension Sovereign Machine Economy additively."""
from __future__ import annotations
import argparse, hashlib, html, json, os, re, shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

RELEASE_TITLE="GoalOS AGIALPHA Ascension — Sovereign Machine Economy"
FEATURE_ID="sovereign-machine-economy"
PAGES=["sovereign-machine-economy.html","sovereign-machine-economy-architecture.html","sovereign-machine-economy-chronicle.html","sovereign-machine-economy-atlas.html"]
SHARED=["index.html","routes.json","sitemap.xml","site-status.json"]
COMPANIONS=[
 ("meta-agentic-alpha-agi-manifest.json","goalos.meta_agentic_alpha_agi.website_manifest.v2","META","meta-agentic-alpha-agi.html"),
 ("agi-alpha-node-v0-manifest.json","goalos.agi_alpha_node_v0.website_manifest.v2","NODE","agi-alpha-node-v0.html"),
 ("agi-jobs-v0-v2-manifest.json","goalos.agi_jobs_v0_v2.website_manifest.v3","JOBS","agi-jobs-v0-v2.html"),
]
STYLE_START="<!-- GOALOS_SOVEREIGN_MACHINE_ECONOMY_STYLE_START -->";STYLE_END="<!-- GOALOS_SOVEREIGN_MACHINE_ECONOMY_STYLE_END -->"
NAV_START="<!-- GOALOS_SOVEREIGN_MACHINE_ECONOMY_NAV_START -->";NAV_END="<!-- GOALOS_SOVEREIGN_MACHINE_ECONOMY_NAV_END -->"
HOME_START="<!-- GOALOS_SOVEREIGN_MACHINE_ECONOMY_HOME_START -->";HOME_END="<!-- GOALOS_SOVEREIGN_MACHINE_ECONOMY_HOME_END -->"
BASE_URL="https://montrealai.github.io/goalos-agialpha-ascension/"

def now()->datetime:
    epoch=os.environ.get("SOURCE_DATE_EPOCH")
    return datetime.fromtimestamp(int(epoch),tz=timezone.utc) if epoch else datetime.now(timezone.utc)
def iso(value:datetime)->str:return value.replace(microsecond=0).isoformat().replace("+00:00","Z")
def stable(value:Any)->str:return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(",",":"))
def digest(value:Any)->str:return hashlib.sha256((value if isinstance(value,bytes) else stable(value).encode("utf-8"))).hexdigest()
def file_digest(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):h.update(chunk)
    return h.hexdigest()
def load(path:Path)->dict[str,Any]:
    value=json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value,dict):raise ValueError(f"Expected object: {path}")
    return value
def dump(path:Path,value:Any)->None:
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def record(path:Path)->dict[str,Any]:return {"sha256":file_digest(path),"bytes":path.stat().st_size}

def validate_config(c:dict[str,Any])->None:
    errors=[]
    expected={"hero_metrics":6,"presets":5,"postures":4,"risk_profiles":4,"incidents":5,"gates":18,"artifacts":36,"guardians":7,"handoff_rules":6,"claim_boundary":6}
    if c.get("release_id")!="GOALOS-SOVEREIGN-MACHINE-ECONOMY-001":errors.append("release id")
    if c.get("version")!="1.0.0-civilization":errors.append("version")
    for key,count in expected.items():
        if not isinstance(c.get(key),list) or len(c[key])!=count:errors.append(f"{key} count")
    if [x.get("terminal") for x in c.get("incidents",[]) ]!=["HUMAN_SETTLEMENT_REVIEW","SAFE_HOLD","SAFE_HOLD","DISPUTE_OPEN","HUMAN_REVIEW_REQUIRED"]:errors.append("terminal constitution")
    if c.get("security",{}).get("external_authority")!="none":errors.append("authority")
    for key in ["external_dependencies","api_keys","wallet_connection","network_reads","network_writes","local_storage","live_compute","live_token_movement","credential_issuance"]:
        if c.get("security",{}).get(key) is not False:errors.append(f"security:{key}")
    if errors:raise ValueError("Invalid Sovereign Machine Economy config: "+", ".join(errors))

def build_sample(c:dict[str,Any],meta:dict[str,Any],node:dict[str,Any],jobs:dict[str,Any],companions:list[dict[str,Any]])->dict[str,Any]:
    mission=c["presets"][0]["mission"]
    mission_commitment=digest({"mission":mission,"posture":"evidence-first","risk":"critical"})
    selected={"id":"I01","name":"Aurelia Institution","topology":meta["candidate_engine"]["topologies"][0],"score":94.8}
    peers=sorted(node["peers"],key=lambda x:(x["base_reliability"]*.35+x["base_evidence"]*.31+(1-x["base_latency"]/200)*.18+(1-x["base_energy"])*.16),reverse=True)
    primary=[x["id"] for x in peers[:4]];shadow=[x["id"] for x in peers[4:7]]
    route_id="ROUTE-"+digest(primary+shadow)[:12].upper();work_unit_id="AWU-"+digest(mission_commitment+route_id)[12:28].upper()
    institutions=sorted(jobs["institutions"],key=lambda x:x["capability"]*.2+x["evidence"]*.2+x["reliability"]*.17+x["safety"]*.17+x["efficiency"]*.1+x["originality"]*.1+x["reputation"]*.06,reverse=True)
    coalition=[x["id"] for x in institutions[:5]];coalition_id="COUNCIL-"+digest(coalition)[:12].upper()
    institution_seal=digest({"mission_commitment":mission_commitment,"selected":selected})
    node_seal=digest({"institution_seal":institution_seal,"route_id":route_id,"work_unit_id":work_unit_id,"primary":primary,"shadow":shadow})
    market_seal=digest({"node_seal":node_seal,"coalition_id":coalition_id,"coalition":coalition})
    chain=[];previous="0"*64
    for item in c["artifacts"]:
        payload={"id":item["id"],"layer":item["layer"],"name":item["name"],"purpose":item["purpose"],"mission_commitment":mission_commitment,"institution_id":selected["id"],"route_id":route_id,"coalition_id":coalition_id,"terminal":"HUMAN_SETTLEMENT_REVIEW"}
        commitment=digest({"previous":previous,"payload":payload})
        chain.append({**item,"previous_commitment":previous,"commitment":commitment,"payload":payload});previous=commitment
    docket={
      "schema":"goalos.sovereign_machine_economy.docket.v1","release_id":c["release_id"],"version":c["version"],
      "mission":{"text":mission,"posture":"evidence-first","risk":"critical","incident":"none","commitment":mission_commitment},
      "meta":{"selected_institution":selected,"candidate_count":12,"pareto_review":"COMPLETE","constitution_seal":institution_seal},
      "node":{"route_id":route_id,"primary":primary,"shadow":shadow,"work_unit_id":work_unit_id,"evidence_seal":node_seal},
      "jobs":{"coalition_id":coalition_id,"coalition":coalition,"pareto_frontier":[x["id"] for x in institutions[:7]],"parliament":{"seats":9,"threshold":7,"pass":8,"dissent":1,"reject":0,"challenge_window":"336 hours"},"market_seal":market_seal},
      "handoffs":[{"id":"H01","from":"META","to":"NODE","commitment":institution_seal},{"id":"H02","from":"NODE","to":"JOBS","commitment":node_seal},{"id":"H03","from":"JOBS","to":"HUMAN","commitment":market_seal}],
      "companions":[{"layer":x["layer"],"release_id":x["release_id"],"version":x["version"]} for x in companions],
      "evidence":{"artifact_count":36,"expected_artifact_count":36,"chain_head":previous,"artifacts":chain},
      "authority":{"terminal_state":"HUMAN_SETTLEMENT_REVIEW","external_authority":"NONE_GRANTED","factual_correctness":"NOT_CERTIFIED","production_activation":"NOT_ACTIVATED","user_fund_authorization":"NO","external_actions":0,"network_requests":0,"wallet_connections":0,"live_token_movements":0,"memory_promotion":"NOT_AUTHORIZED"}
    }
    docket["run_commitment"]=digest(docket)
    return docket

def companion_info(site:Path)->list[dict[str,Any]]:
    result=[]
    for filename,schema,layer,primary in COMPANIONS:
        path=site/filename
        if not path.is_file():raise FileNotFoundError(f"Missing installed companion manifest: {path}")
        m=load(path)
        if m.get("schema")!=schema:raise ValueError(f"Unexpected companion schema: {filename}")
        result.append({"filename":filename,"schema":schema,"layer":layer,"release_id":m.get("release_id"),"release_title":m.get("release_title"),"version":m.get("version"),"primary_page":primary,"manifest_sha256":file_digest(path)})
    return result

def public_data(c:dict[str,Any],meta:dict[str,Any],node:dict[str,Any],jobs:dict[str,Any],companions:list[dict[str,Any]],mainnet:dict[str,Any])->dict[str,Any]:
    sample=build_sample(c,meta,node,jobs,companions)
    launches=[
      {"layer":"INTEGRATED","title":"Sovereign Machine Economy","href":"sovereign-machine-economy.html","description":"Run the complete institution → node → market proof cycle."},
      {"layer":"META","title":"Institution Foundry","href":"meta-agentic-alpha-agi.html","description":"Create, evolve, compare, and constitutionally select agent institutions."},
      {"layer":"NODE","title":"Sovereign Node Theatre","href":"agi-alpha-node-v0.html","description":"Execute bounded α‑Work Units through primary and shadow routes."},
      {"layer":"JOBS","title":"Sovereign Work Civilization","href":"agi-jobs-v0-v2.html","description":"Convene guild markets, proof parliament, dispute, and settlement review."},
      {"layer":"META","title":"META Architecture","href":"meta-agentic-alpha-agi-architecture.html","description":"Inspect the institution-formation constitution."},
      {"layer":"NODE","title":"Node Proof Ledger","href":"agi-alpha-node-v0-proof-ledger.html","description":"Inspect the sixteen-link node evidence standard."},
      {"layer":"JOBS","title":"Proof Parliament","href":"agi-jobs-v0-v2-proof.html","description":"Inspect validator judgments, dissent, challenge rights, and the Evidence Docket."},
      {"layer":"JOBS","title":"Settlement Constitution","href":"agi-jobs-v0-v2-settlement.html","description":"Inspect proof-conditioned settlement review and revocable memory."},
    ]
    return {**c,
      "meta":{"release_id":meta["release_id"],"release_title":meta["release_title"],"version":meta["version"],"agents":meta["agents"],"topologies":meta["candidate_engine"]["topologies"]},
      "node":{"release_id":node["release_id"],"release_title":node["release_title"],"version":node["version"],"peers":node["peers"],"validators":node["validators"],"guardians":node["guardians"]},
      "jobs":{"release_id":jobs["release_id"],"release_title":jobs["release_title"],"version":jobs["version"],"institutions":jobs["institutions"],"validators":jobs["validators"],"guardians":jobs["guardians"]},
      "companions":companions,"launch_surfaces":launches,"sample_docket":sample,
      "repository_evidence":{"network":mainnet.get("network"),"goalos_contracts":mainnet.get("goalosCreatedContractCount"),"operator_verified":mainnet.get("verification",{}).get("verified"),"operator_failed":mainnet.get("verification",{}).get("failed"),"production_activation":"NOT_ACTIVATED","user_fund_authorization":"NO"}
    }

def render(template:Path,data:dict[str,Any])->str:
    raw=template.read_text(encoding="utf-8")
    embedded=json.dumps(data,ensure_ascii=False,separators=(",",":")).replace("</script","<\\/script")
    raw=raw.replace("@@DATA_JSON@@",embedded).replace("@@SAMPLE_COMMITMENT@@",str(data["sample_docket"]["run_commitment"]))
    if "@@" in raw:raise ValueError(f"Unresolved template token in {template}")
    return raw

def replace_block(text:str,start:str,end:str,block:str)->str:
    if text.count(start)!=text.count(end):raise ValueError(f"Unbalanced markers: {start}")
    if start not in text:return text
    prefix,remainder=text.split(start,1);_,suffix=remainder.split(end,1);return prefix+block+suffix
def insert_after(text:str,marker:str,block:str)->str|None:
    pos=text.find(marker)
    if pos<0:return None
    pos+=len(marker);return text[:pos]+"\n"+block+text[pos:]

def patch_homepage(path:Path)->None:
    text=path.read_text(encoding="utf-8")
    style=f'{STYLE_START}\n<link rel="stylesheet" href="assets/sovereign-machine-economy.css" data-goalos-sovereign-machine-economy>\n{STYLE_END}'
    nav=f'{NAV_START}<a href="sovereign-machine-economy.html">Machine Economy</a>{NAV_END}'
    home=f'''{HOME_START}
<section class="sme-home-gateway" id="sovereign-machine-economy" data-goalos-feature="sovereign-machine-economy" aria-labelledby="sme-home-title">
  <div class="sme-home-grid">
    <div class="sme-home-copy"><small>GOALOS AGIALPHA ASCENSION · THE COMPLETE MACHINE-ECONOMY STACK</small><h2 id="sme-home-title">THE SOVEREIGN <span>MACHINE ECONOMY</span></h2><p><strong>A mind that builds minds. A node that turns intelligence into proof. A market that turns proof into accountable value.</strong> Form the institution through META‑AGENTIC α‑AGI, execute through AGI Alpha Node, coordinate value through AGI Jobs, and stop at the human authority boundary.</p><div class="sme-home-metrics"><div><strong>3</strong><span>sovereign layers</span></div><div><strong>18</strong><span>constitutional gates</span></div><div><strong>36</strong><span>proof artifacts</span></div><div><strong>0</strong><span>unearned authority</span></div></div><div class="sme-home-actions"><a href="sovereign-machine-economy.html">Enter the Machine Economy →</a><a href="sovereign-machine-economy-architecture.html">Read the Constitution</a><a href="sovereign-machine-economy-chronicle.html">Inspect the Proof Chronicle</a><a href="sovereign-machine-economy-atlas.html">Open the Civilization Atlas</a></div><div class="sme-home-stack"><span>META‑AGENTIC α‑AGI 👁️✨</span><i>→</i><span>AGI Alpha Node v0 ⚡️✨</span><i>→</i><span>AGI Jobs v0 (v2) ✨</span></div></div>
    <div class="sme-home-monument" aria-hidden="true"><div class="sme-home-orbit o1"><b>META</b></div><div class="sme-home-orbit o2"><b>NODE</b></div><div class="sme-home-orbit o3"><b>JOBS</b></div><div class="sme-home-core"><small>GOALOS</small><strong>αΩ</strong><span>PROOF EARNS<br>PERMISSION</span></div></div>
  </div>
</section>
{HOME_END}'''
    text=replace_block(text,STYLE_START,STYLE_END,style)
    if STYLE_START not in text:
        if "</head>" not in text:raise ValueError("Homepage missing </head>")
        text=text.replace("</head>",style+"\n</head>",1)
    text=replace_block(text,NAV_START,NAV_END,nav)
    if NAV_START not in text:
        inserted=insert_after(text,"<!-- GOALOS_AGI_JOBS_V0_V2_NAV_END -->",nav)
        if inserted is None:
            if "</nav>" not in text:raise ValueError("Homepage missing </nav>")
            inserted=text.replace("</nav>",nav+"\n</nav>",1)
        text=inserted
    text=replace_block(text,HOME_START,HOME_END,home)
    if HOME_START not in text:
        inserted=insert_after(text,"<!-- GOALOS_AGI_JOBS_V0_V2_HOME_END -->",home)
        if inserted is None:
            for marker in ["<!-- GOALOS_FIRST_REAL_LOOP_END -->","<!-- GOALOS_AGI_ALPHA_NODE_V0_HOME_END -->","<!-- GOALOS_META_AGENTIC_ALPHA_AGI_HOME_END -->"]:
                inserted=insert_after(text,marker,home)
                if inserted is not None:break
        if inserted is None:
            if "</main>" not in text:raise ValueError("Homepage missing </main>")
            inserted=text.replace("</main>",home+"\n</main>",1)
        text=inserted
    path.write_text(text,encoding="utf-8")

def update_shared(site:Path,c:dict[str,Any],sample:dict[str,Any])->None:
    routes_path=site/"routes.json";routes=load(routes_path) if routes_path.exists() else {"version":"unknown","routes":[]}
    if not isinstance(routes.get("routes"),list):raise ValueError("routes array missing")
    routes["routes"]=sorted(set(map(str,routes["routes"])).union(PAGES))
    routes["sovereign_machine_economy"]={"release_id":c["release_id"],"version":c["version"],"pages":PAGES,"integration":"additive-post-build","runtime":"deterministic-browser-local-constitutional-machine-economy","external_actions":0}
    dump(routes_path,routes)
    sitemap_path=site/"sitemap.xml";text=sitemap_path.read_text(encoding="utf-8") if sitemap_path.exists() else "<?xml version='1.0'?><urlset></urlset>"
    for page in PAGES:
        url=BASE_URL+page
        if url not in text:
            if "</urlset>" not in text:raise ValueError("Invalid sitemap")
            text=text.replace("</urlset>",f"<url><loc>{html.escape(url)}</loc></url></urlset>",1)
    sitemap_path.write_text(text,encoding="utf-8")
    status_path=site/"site-status.json";status=load(status_path) if status_path.exists() else {}
    status["root_html_pages"]=len(list(site.glob("*.html")));status["published_html_pages_including_resources"]=len(list(site.rglob("*.html")))
    status["sovereign_machine_economy"]={"release":c["release_id"],"version":c["version"],"pages":PAGES,"constitutional_gates":18,"proof_artifacts":36,"terminal_state":"HUMAN_SETTLEMENT_REVIEW","authority":"NONE_GRANTED","sample_run_commitment":sample["run_commitment"]}
    dump(status_path,status)

def reconcile(site:Path,c:dict[str,Any],built_at:str)->list[str]:
    reconciled=[]
    # Order matters: downstream manifests hash upstream manifests.
    for filename,schema,_,_ in COMPANIONS:
        path=site/filename;m=load(path)
        if m.get("schema")!=schema:raise ValueError(f"Unexpected schema: {filename}")
        files=m.get("files")
        if not isinstance(files,dict) or not all(name in files for name in SHARED):raise ValueError(f"Missing shared files: {filename}")
        for name in SHARED:files[name]=record(site/name)
        # Refresh declared companion-manifest dependencies after upstream updates.
        for dep,_,_,_ in COMPANIONS:
            if dep in files and (site/dep).is_file():files[dep]=record(site/dep)
        integration=m.setdefault("integration",{});history=integration.setdefault("reconciliations",[])
        if not isinstance(history,list):raise ValueError(f"Invalid reconciliation history: {filename}")
        history[:]=[item for item in history if not isinstance(item,dict) or item.get("release_id")!=c["release_id"]]
        history.append({"release_id":c["release_id"],"version":c["version"],"built_at":built_at,"reason":"shared additive website surfaces were extended by the Sovereign Machine Economy","files":SHARED})
        dump(path,m);reconciled.append(filename)
    return reconciled

def main()->int:
    root=Path(__file__).resolve().parents[2]
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument("--site",type=Path,default=root/"site");ap.add_argument("--root",type=Path,default=root);ap.add_argument("--content",type=Path,default=root/"content/sovereign-machine-economy.json")
    args=ap.parse_args();site=args.site.resolve();repo=args.root.resolve();content_path=args.content.resolve()
    if not site.is_dir():raise FileNotFoundError(f"Missing generated site: {site}")
    required=[site/"index.html",site/"meta-agentic-alpha-agi.html",site/"agi-alpha-node-v0.html",site/"agi-jobs-v0-v2.html",site/"agi-jobs-v0-v2-manifest.json",site/"routes.json",site/"sitemap.xml",site/"site-status.json"]
    missing=[str(x) for x in required if not x.is_file() or x.stat().st_size==0]
    if missing:raise FileNotFoundError("Build META-Agentic, Alpha Node, and AGI Jobs first: "+", ".join(missing))
    c=load(content_path);validate_config(c)
    meta=load(repo/"content/meta-agentic-alpha-agi.json");node=load(repo/"content/agi-alpha-node-v0.json");jobs=load(repo/"content/agi-jobs-v0-v2.json");mainnet=load(repo/"data/mainnet/v4.4.0-mainnet-2026-06-21.json")
    companions=companion_info(site);data=public_data(c,meta,node,jobs,companions,mainnet);built_at=iso(now())
    before={str(p.relative_to(site)):file_digest(p) for p in site.rglob("*") if p.is_file()}
    feature=repo/"website/features/sovereign-machine-economy";asset_out=site/"assets";asset_out.mkdir(parents=True,exist_ok=True)
    shutil.copy2(feature/"assets/sovereign-machine-economy.css",asset_out/"sovereign-machine-economy.css");shutil.copy2(feature/"assets/sovereign-machine-economy.js",asset_out/"sovereign-machine-economy.js")
    templates=feature/"templates"
    for page in PAGES:(site/page).write_text(render(templates/page,data),encoding="utf-8")
    patch_homepage(site/"index.html");update_shared(site,c,data["sample_docket"]);reconciled=reconcile(site,c,built_at)
    data["companions"]=companion_info(site) # public data records final reconciled manifest hashes
    # Re-render after reconciliation so lineage hashes are final.
    data["sample_docket"]=build_sample(c,meta,node,jobs,data["companions"])
    for page in PAGES:(site/page).write_text(render(templates/page,data),encoding="utf-8")
    data_out=site/"data/sovereign-machine-economy.json";dump(data_out,data)
    download=site/"downloads/sovereign-machine-economy/sample-sovereign-economy-docket.json";dump(download,data["sample_docket"])
    own_files=[*PAGES,"assets/sovereign-machine-economy.css","assets/sovereign-machine-economy.js","data/sovereign-machine-economy.json","downloads/sovereign-machine-economy/sample-sovereign-economy-docket.json",*SHARED,*[x[0] for x in COMPANIONS]]
    manifest={"schema":"goalos.sovereign_machine_economy.website_manifest.v1","release_id":c["release_id"],"release_title":c["release_title"],"constellation_title":c["constellation_title"],"version":c["version"],"built_at":built_at,"experience":{"sovereign_layers":3,"constitutional_gates":18,"proof_artifacts":36,"rival_entities":36,"public_surfaces":4,"normal_terminal":"HUMAN_SETTLEMENT_REVIEW","external_authority":"NONE_GRANTED"},"integration":{"mode":"additive-post-build","canonical_v86_source_modified":False,"homepage_markers":[STYLE_START,NAV_START,HOME_START],"existing_outputs_allowed_to_change":[*SHARED,*[x[0] for x in COMPANIONS]],"companion_manifests_reconciled":reconciled},"companions":data["companions"],"sample_run_commitment":data["sample_docket"]["run_commitment"],"files":{name:record(site/name) for name in own_files}}
    dump(site/"sovereign-machine-economy-manifest.json",manifest)
    after={str(p.relative_to(site)):file_digest(p) for p in site.rglob("*") if p.is_file()}
    removed=sorted(before.keys()-after.keys())
    report={"schema":"goalos.sovereign_machine_economy.build_report.v1","status":"PASS","release_title":RELEASE_TITLE,"version":c["version"],"built_at":built_at,"site":str(site),"pages":PAGES,"sample_run_commitment":data["sample_docket"]["run_commitment"],"declared_new_outputs":sorted([*PAGES,"sovereign-machine-economy-manifest.json","assets/sovereign-machine-economy.css","assets/sovereign-machine-economy.js","data/sovereign-machine-economy.json","downloads/sovereign-machine-economy/sample-sovereign-economy-docket.json","qa/sovereign-machine-economy-build.json"]),"declared_integration_surfaces":sorted([*SHARED,*[x[0] for x in COMPANIONS]]),"files_removed":removed,"companion_manifests_reconciled":reconciled,"authority":"NONE_GRANTED","external_actions":0}
    dump(site/"qa/sovereign-machine-economy-build.json",report)
    print(json.dumps(report,ensure_ascii=False,indent=2));return 0
if __name__=="__main__":raise SystemExit(main())
