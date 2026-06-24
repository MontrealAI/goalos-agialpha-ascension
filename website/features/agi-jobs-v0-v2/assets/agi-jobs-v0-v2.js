(() => {
  "use strict";
  const doc = document;
  const root = doc.documentElement;
  const body = doc.body;
  const pageName = body?.dataset.ajPage || "exchange";
  const dataNode = doc.getElementById("agi-jobs-data");
  if (!dataNode) return;
  const data = JSON.parse(dataNode.textContent || "{}");
  const $ = (selector, scope = doc) => scope.querySelector(selector);
  const $$ = (selector, scope = doc) => Array.from(scope.querySelectorAll(selector));
  const esc = (value) => String(value ?? "").replace(/[&<>'"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;","'":"&#39;",'"':"&quot;"}[c]));
  const clamp = (value, min = 0, max = 1) => Math.max(min, Math.min(max, value));
  const fmt = (value, digits = 0) => Number(value).toLocaleString("en-US", {maximumFractionDigits: digits, minimumFractionDigits: digits});
  const riskOrder = {low:0, medium:1, high:2, critical:3};
  const reducedMotion = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const SVG = "http://www.w3.org/2000/svg";

  function stable(value) {
    if (Array.isArray(value)) return `[${value.map(stable).join(",")}]`;
    if (value && typeof value === "object") return `{${Object.keys(value).sort().map(key => `${JSON.stringify(key)}:${stable(value[key])}`).join(",")}}`;
    return JSON.stringify(value);
  }

  function sha256(text) {
    const K = [
      0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,
      0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,
      0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,
      0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,
      0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,
      0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,
      0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,
      0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2
    ];
    const H = [0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19];
    const bytes = new TextEncoder().encode(String(text));
    const length = bytes.length;
    const paddedLength = Math.ceil((length + 9) / 64) * 64;
    const message = new Uint8Array(paddedLength);
    message.set(bytes); message[length] = 0x80;
    const view = new DataView(message.buffer);
    const bits = length * 8;
    view.setUint32(paddedLength - 8, Math.floor(bits / 0x100000000), false);
    view.setUint32(paddedLength - 4, bits >>> 0, false);
    const w = new Uint32Array(64);
    const rotr = (x, n) => (x >>> n) | (x << (32 - n));
    for (let offset = 0; offset < paddedLength; offset += 64) {
      for (let i = 0; i < 16; i++) w[i] = view.getUint32(offset + i * 4, false);
      for (let i = 16; i < 64; i++) {
        const s0 = rotr(w[i-15],7) ^ rotr(w[i-15],18) ^ (w[i-15] >>> 3);
        const s1 = rotr(w[i-2],17) ^ rotr(w[i-2],19) ^ (w[i-2] >>> 10);
        w[i] = (w[i-16] + s0 + w[i-7] + s1) >>> 0;
      }
      let [a,b,c,d,e,f,g,h] = H;
      for (let i = 0; i < 64; i++) {
        const S1 = rotr(e,6) ^ rotr(e,11) ^ rotr(e,25);
        const ch = (e & f) ^ (~e & g);
        const t1 = (h + S1 + ch + K[i] + w[i]) >>> 0;
        const S0 = rotr(a,2) ^ rotr(a,13) ^ rotr(a,22);
        const maj = (a & b) ^ (a & c) ^ (b & c);
        const t2 = (S0 + maj) >>> 0;
        h=g; g=f; f=e; e=(d+t1)>>>0; d=c; c=b; b=a; a=(t1+t2)>>>0;
      }
      H[0]=(H[0]+a)>>>0; H[1]=(H[1]+b)>>>0; H[2]=(H[2]+c)>>>0; H[3]=(H[3]+d)>>>0;
      H[4]=(H[4]+e)>>>0; H[5]=(H[5]+f)>>>0; H[6]=(H[6]+g)>>>0; H[7]=(H[7]+h)>>>0;
    }
    return H.map(x => x.toString(16).padStart(8,"0")).join("");
  }

  const findBy = (list, id) => list.find(item => item.id === id) || list[0];
  const riskAllows = (limit, risk) => (riskOrder[limit] ?? 0) >= (riskOrder[risk] ?? 0);
  const classFit = (institution, jobClass) => {
    const wanted = new Set(jobClass.skills || []);
    const overlap = (institution.capabilities || []).filter(skill => wanted.has(skill)).length;
    return overlap / Math.max(1, wanted.size);
  };

  function institutionScore(institution, posture, jobClass) {
    let weighted = 0;
    for (const [key, weight] of Object.entries(posture.weights)) weighted += Number(institution[key] || 0) * Number(weight);
    const fit = classFit(institution, jobClass);
    const reputation = Number(institution.reputation || 0);
    const capacity = Number(institution.capacity || 0) / 100;
    return clamp(weighted * .86 + fit * .07 + reputation * .045 + capacity * .025);
  }

  function isDominated(candidate, all) {
    const dims = ["capability","evidence","reliability","efficiency","latency","safety","originality"];
    return all.some(other => other.id !== candidate.id && dims.every(dim => Number(other[dim]) >= Number(candidate[dim])) && dims.some(dim => Number(other[dim]) > Number(candidate[dim])));
  }

  function marketSnapshot(jobClassId, postureId, riskId) {
    const jobClass = findBy(data.job_classes, jobClassId);
    const posture = findBy(data.postures, postureId);
    const admissible = data.institutions.filter(item => riskAllows(item.risk_limit, riskId));
    const rows = data.institutions.map(item => {
      const score = institutionScore(item, posture, jobClass);
      const admitted = admissible.some(x => x.id === item.id);
      const evidenceAxis = (item.evidence + item.safety + item.reliability) / 3;
      const utilityAxis = (item.capability + item.efficiency + item.latency + item.originality) / 4;
      return {...item, score, admitted, evidenceAxis, utilityAxis, fit:classFit(item, jobClass)};
    });
    const active = rows.filter(item => item.admitted);
    const frontier = active.filter(item => !isDominated(item, active));
    const sorted = [...rows].sort((a,b) => (b.admitted-a.admitted) || b.score-a.score || a.name.localeCompare(b.name));
    return {jobClass, posture, risk:findBy(data.risk_profiles,riskId), rows:sorted, active, frontier, leader:sorted.find(x=>x.admitted)};
  }

  function chooseDistinct(candidates, used, metric) {
    const pool = candidates.filter(item => !used.has(item.id));
    pool.sort((a,b) => metric(b)-metric(a) || b.score-a.score || a.name.localeCompare(b.name));
    const chosen = pool[0] || candidates.find(item => !used.has(item.id)) || candidates[0];
    if (chosen) used.add(chosen.id);
    return chosen;
  }

  function constituteCouncil(snapshot) {
    const candidates = snapshot.rows.filter(item => item.admitted);
    const used = new Set();
    const prime = candidates[0]; used.add(prime.id);
    const evidence = chooseDistinct(candidates, used, item => item.evidence + item.reliability + item.fit);
    const assurance = chooseDistinct(candidates, used, item => item.safety + item.evidence + item.reputation);
    const delivery = chooseDistinct(candidates, used, item => item.efficiency + item.latency + item.capacity/100);
    const shadow = chooseDistinct(candidates, used, item => item.originality + item.evidence + item.safety);
    const reserves = candidates.filter(item => !used.has(item.id)).slice(0,2);
    return {prime,evidence,assurance,delivery,shadow,reserves, id:`COUNCIL-${sha256([prime,evidence,assurance,delivery,shadow].map(x=>x.id).join("|")).slice(0,12).toUpperCase()}`};
  }

  function commissionFromInputs() {
    const preset = findBy(data.presets, $("#aj-preset")?.value || data.presets[0].id);
    const mission = $("#aj-mission")?.value.trim() || preset.mission;
    const jobClass = findBy(data.job_classes, $("#aj-job-class")?.value || preset.job_class);
    const posture = findBy(data.postures, $("#aj-posture")?.value || preset.posture);
    const risk = findBy(data.risk_profiles, $("#aj-risk")?.value || preset.risk);
    const reward = Math.max(500, Math.min(100000, Number($("#aj-reward")?.value || preset.reward_units)));
    const incident = findBy(data.incidents, $("#aj-incident")?.value || "none");
    return {preset,mission,jobClass,posture,risk,reward,incident};
  }

  function workGraph(council) {
    const owners = [council.prime,council.evidence,council.prime,council.delivery,council.assurance,council.shadow,council.delivery,council.evidence];
    return data.work_packages.map((item,index) => ({...item, owner:owners[index]?.name || council.prime.name, role:["prime","evidence","prime","delivery","assurance","shadow","delivery","evidence"][index], status:"COMPLETE"}));
  }

  function validatorJudgments(commission, council, snapshot) {
    const seats = commission.risk.validator_seats;
    const selected = data.validators.slice(0,seats);
    const quality = Math.round((council.prime.score * .55 + council.evidence.evidence * .15 + council.assurance.safety * .15 + snapshot.leader.reliability * .15) * 100);
    return selected.map((validator,index) => {
      let verdict = index === selected.length - 1 ? "DISSENT" : "PASS";
      let score = Math.max(55, Math.min(99, quality - (index % 4) * 2 + (index===0?3:0)));
      let rationale = `${validator.focus}; evidence package is sufficient for human review with stated boundaries.`;
      if (verdict === "DISSENT") { score = Math.max(62, quality - 11); rationale = "Minority view: narrow external claims, preserve unresolved assumptions, and require independent replication before reliance."; }
      if (commission.incident.effect === "validation" && index < Math.ceil(seats/3)) { verdict = index===0?"REJECT":"ABSTAIN"; score = 34 + index*4; rationale = "Correlated reveal pattern and conflict signal require a capture investigation."; }
      if (["identity","evidence","goal"].includes(commission.incident.effect) && index < 2) { verdict="REJECT"; score=28+index*5; rationale = `Material ${commission.incident.effect} breach invalidates continuation.`; }
      if (commission.incident.effect === "rights" && (index===0 || index===seats-1)) { verdict="DISSENT"; score=52; rationale="Source-rights conflict requires dispute and clearance before reuse or settlement readiness."; }
      if (commission.incident.effect === "budget" && index===seats-1) { verdict="DISSENT"; score=58; rationale="Resource envelope exceeded; require human repricing and scope reduction."; }
      const salt = sha256(`${commission.mission}|${validator.id}|${score}|${verdict}`).slice(0,16);
      const commitment = sha256(stable({validator:validator.id,verdict,score,salt}));
      return {...validator,verdict,score,rationale,salt,commitment,conflict:"NONE_DECLARED"};
    });
  }

  function guardianStatus(commission) {
    return data.guardians.map(guardian => {
      const map = {identity:"H01", evidence:"H02", rights:"H03", budget:"H04", validation:"H05", goal:"H06"};
      const veto = map[commission.incident.effect] === guardian.id;
      return {...guardian,status:veto?"VETO":"CLEAR"};
    });
  }

  function artifactPayload(artifact, context) {
    const base = {artifact_id:artifact.id,name:artifact.name,plane:artifact.plane,purpose:artifact.purpose,run_id:context.runId,release_id:data.release_id};
    const summary = {
      intent:{mission:context.commission.mission,risk:context.commission.risk.id,posture:context.commission.posture.id},
      identity:{council:Object.fromEntries(Object.entries(context.council).filter(([k,v]) => v && v.id).map(([k,v])=>[k,{id:v.id,name:v.name,identity:v.identity}]))},
      rights:{mode:"synthetic-demonstration-only",external_sources:0,live_data:0},
      economics:{reward_units:context.commission.reward,live_token_movement:0,authority:"NONE_GRANTED"},
      market:{leader:context.snapshot.leader.id,frontier:context.snapshot.frontier.map(x=>x.id),admitted:context.snapshot.active.map(x=>x.id)},
      selection:{council_id:context.council.id,prime:context.council.prime.id,shadow:context.council.shadow.id},
      planning:{packages:context.graph.map(x=>({id:x.id,owner:x.owner,proof:x.proof}))},
      execution:{mode:"deterministic-browser-local",external_actions:0,network_requests:0},
      proof:{artifact_count:data.artifacts.length,claim_boundary:data.claim_boundary.slice(0,3)},
      evaluation:{evidence_floor:context.commission.risk.evidence_floor,leader_score:Number(context.snapshot.leader.score.toFixed(4))},
      validation:{judgments:context.validators.map(x=>({id:x.id,verdict:x.verdict,score:x.score,commitment:x.commitment})),threshold:context.commission.risk.validator_threshold},
      challenge:{incident:context.commission.incident.id,terminal:context.terminal},
      memory:{status:"CANDIDATE_ONLY",expiry:"90_DAYS_AFTER_HUMAN_REVIEW",revocable:true},
      credential:{status:"HUMAN_APPROVAL_PENDING",transferable:false},
      settlement:{policy:data.settlement_policy,live_movement:0},
      "human-review":{terminal:context.terminal,authority:"NONE_GRANTED",external_actions:0}
    };
    return {...base,record:summary[artifact.plane] || {terminal:context.terminal,incident:context.commission.incident.id}};
  }

  function terminalFor(incident) { return incident.terminal || "HUMAN_SETTLEMENT_REVIEW"; }

  function compileDocket(commission, snapshot, council, graph, validators, guardians) {
    const runId = `AJ-${sha256(stable({mission:commission.mission,posture:commission.posture.id,risk:commission.risk.id,reward:commission.reward,incident:commission.incident.id,release:data.release_id})).slice(0,16).toUpperCase()}`;
    const terminal = terminalFor(commission.incident);
    const context = {commission,snapshot,council,graph,validators,guardians,runId,terminal};
    let previous = "0".repeat(64);
    const artifacts = data.artifacts.map(item => {
      const payload = artifactPayload(item,context);
      const commitment = sha256(stable({previous,payload}));
      const row = {...item,previous_commitment:previous,commitment,payload}; previous=commitment; return row;
    });
    const pass = validators.filter(x=>x.verdict==="PASS").length;
    const reject = validators.filter(x=>x.verdict==="REJECT").length;
    const dissent = validators.filter(x=>x.verdict==="DISSENT").length;
    const abstain = validators.filter(x=>x.verdict==="ABSTAIN").length;
    const allocation = data.settlement_policy.allocations.map(item => ({...item,units:Number((commission.reward*item.pct/100).toFixed(2))}));
    const docket = {
      schema:"goalos.agi_jobs_v0_v2.evidence_docket.v3",
      release_id:data.release_id,
      release_title:data.release_title,
      version:data.version,
      run_id:runId,
      work_constitution:{mission:commission.mission,preset:commission.preset.id,job_class:commission.jobClass.id,posture:commission.posture.id,risk:commission.risk.id,reward_units:commission.reward,deliverables:commission.preset.deliverables,forbidden_runtime_actions:["wallet connection","token movement","network request","external action","autonomous authorization"]},
      market:{leader:snapshot.leader.id,frontier:snapshot.frontier.map(x=>x.id),ranking:snapshot.rows.map(x=>({id:x.id,admitted:x.admitted,score:Number(x.score.toFixed(5)),fit:Number(x.fit.toFixed(3))})),council:{id:council.id,prime:council.prime.id,evidence:council.evidence.id,assurance:council.assurance.id,delivery:council.delivery.id,shadow:council.shadow.id,reserves:council.reserves.map(x=>x.id)}},
      work_graph:graph,
      parliament:{seats:validators.length,threshold:commission.risk.validator_threshold,pass,reject,dissent,abstain,judgments:validators},
      guardians,
      incident:commission.incident,
      evidence:{artifact_count:artifacts.length,chain_head:previous,artifacts},
      settlement:{mode:data.settlement_policy.mode,unit:data.settlement_policy.unit,allocation,conditions_precedent:data.settlement_policy.conditions_precedent,live_token_movement:0,wallet_connections:0,settlement_authority:"NONE_GRANTED"},
      memory:{reputation_delta_candidate:{prime:+3,evidence_partner:+2,assurance_partner:+2,delivery_partner:+2,shadow:+1,validators:"scope-bounded"},capability_passport_candidate:{institution:council.prime.id,status:"HUMAN_APPROVAL_PENDING",scope:commission.jobClass.label,skills:council.prime.capabilities,expiry:"90_DAYS_AFTER_HUMAN_REVIEW",revocable:true,transferable:false}},
      authority:{terminal_state:terminal,external_authority:"NONE_GRANTED",production_activation:"NOT_ACTIVATED",user_fund_authorization:"NO",external_actions:0,network_requests:0,wallet_connections:0,live_token_movements:0,factual_correctness:"NOT_CERTIFIED"},
      claim_boundary:data.claim_boundary
    };
    docket.run_commitment = sha256(stable(docket));
    return docket;
  }

  function option(value,label,selected=false){return `<option value="${esc(value)}"${selected?" selected":""}>${esc(label)}</option>`;}
  function populateSelect(node,list,valueLabel,selected){ if (!node) return; node.innerHTML=list.map(item=>option(item.id,valueLabel(item),item.id===selected)).join(""); }

  function renderMetrics(){ const node=$("#aj-hero-metrics"); if(node) node.innerHTML=data.hero_metrics.map(item=>`<div class="aj-metric-card"><strong>${esc(item.value)}</strong><span>${esc(item.label)}</span></div>`).join(""); }
  function renderThesis(){ const node=$("#aj-thesis-grid"); if(node) node.innerHTML=data.thesis.map((item,i)=>`<article class="aj-doctrine-card"><b>0${i+1}</b><h3>${esc(item.title)}</h3><p>${esc(item.detail)}</p><i></i></article>`).join(""); }

  function updateCharter() {
    const c=commissionFromInputs();
    if($("#aj-mission") && !$("#aj-mission").value.trim()) $("#aj-mission").value=c.preset.mission;
    const mission=$("#aj-mission")?.value.trim()||c.mission;
    if($("#aj-charter-mission")) $("#aj-charter-mission").textContent=mission;
    if($("#aj-charter-grid")) $("#aj-charter-grid").innerHTML=[
      ["WORK CLASS",c.jobClass.label],["POSTURE",c.posture.name],["RISK",c.risk.label],["PARLIAMENT",`${c.risk.validator_seats} seats · ${c.risk.validator_threshold} threshold`],["EVIDENCE FLOOR",`${Math.round(c.risk.evidence_floor*100)}%`],["REWARD MODEL",`${fmt(c.reward)} αU · demonstration`]
    ].map(([a,b])=>`<div><small>${esc(a)}</small><strong>${esc(b)}</strong></div>`).join("");
    if($("#aj-charter-deliverables")) $("#aj-charter-deliverables").innerHTML=c.preset.deliverables.map(x=>`<span>${esc(x)}</span>`).join("");
    if($("#aj-charter-id")) $("#aj-charter-id").textContent=`DRAFT-${sha256(mission).slice(0,8).toUpperCase()}`;
  }

  function renderGates(docket=null,activeIndex=-1) {
    const node=$("#aj-gate-rail"); if(!node) return;
    const terminal=docket?.authority?.terminal_state;
    const incidentEffect=docket?.incident?.effect;
    const blockIndex={identity:1,rights:2,budget:3,validation:11,evidence:9,goal:8}[incidentEffect] ?? 99;
    node.innerHTML=data.lifecycle.map((gate,index)=>{
      let cls="";
      if(docket){ if(index<activeIndex) cls=" is-complete"; else if(index===activeIndex) cls= terminal==="SAFE_HOLD"&&index>=blockIndex?" is-blocked":" is-active"; else if(index>blockIndex&&["SAFE_HOLD","DISPUTE_OPEN","HUMAN_REVIEW_REQUIRED"].includes(terminal)) cls=" is-blocked"; }
      return `<button type="button" class="aj-gate${cls}" data-gate="${index}"><small>${esc(gate.id)} · ${esc(gate.label)}</small><strong>${esc(gate.title)}</strong><span>${docket&&index<activeIndex?"COMPLETE":docket&&index===activeIndex?terminal||gate.state:"PENDING"}</span></button>`;
    }).join("");
    $$(".aj-gate",node).forEach(button=>button.addEventListener("click",()=>inspectGate(Number(button.dataset.gate),docket)));
  }

  function inspectGate(index,docket){ const gate=data.lifecycle[index]; const inspector=$("#aj-gate-inspector"); if(!gate||!inspector)return; inspector.innerHTML=`<span>${esc(gate.id)} · ${esc(gate.label)}</span><h3>${esc(gate.title)}</h3><p>${esc(gate.detail)}</p><code>STATE · ${esc(docket&&index<15?gate.state:(docket?.authority?.terminal_state||gate.state))}</code>`; }

  function renderMarket(snapshot,council=null) {
    const node=$("#aj-market-table"); if(node) node.innerHTML=snapshot.rows.map((item,index)=>`<div class="aj-market-row${snapshot.frontier.some(x=>x.id===item.id)?" is-frontier":""}${council&&council.prime.id===item.id?" is-selected":""}"><span class="rank">${String(index+1).padStart(2,"0")}</span><div><b>${esc(item.name)}</b><small>${item.admitted?`${esc(item.guild)} · ${esc(item.risk_limit.toUpperCase())}`:"NOT ADMITTED FOR RISK"}</small></div><span class="score">${item.admitted?fmt(item.score*100,1):"—"}</span><span>${fmt(item.evidence*100,0)} E</span><span>${fmt(item.safety*100,0)} S</span></div>`).join("");
    if($("#aj-frontier-count")) $("#aj-frontier-count").textContent=`${snapshot.frontier.length} PARETO GUILDS`;
    if(council) renderCouncil(council);
  }

  function renderCouncil(council){ if($("#aj-council-id")) $("#aj-council-id").textContent=council.id; const node=$("#aj-council-roles"); if(!node)return; const roles=[
    ["PRIME GUILD",council.prime],["EVIDENCE PARTNER",council.evidence],["ASSURANCE PARTNER",council.assurance],["DELIVERY PARTNER",council.delivery],["SHADOW INSTITUTION",council.shadow]
  ]; node.innerHTML=roles.map(([role,item])=>`<div class="aj-council-role"><small>${esc(role)}</small><strong>${esc(item.name)}</strong></div>`).join(""); }

  function renderWorkGraph(graph=null){ const node=$("#aj-work-graph"); if(!node)return; const rows=graph||data.work_packages.map(item=>({...item,owner:"AWAITING COUNCIL",status:"PENDING"})); node.innerHTML=rows.map(item=>`<article class="aj-work-package${item.status==="COMPLETE"?" is-complete":""}"><small>${esc(item.id)} · ${esc(item.role||"UNASSIGNED")}</small><h3>${esc(item.name)}</h3><p>${esc(item.proof)}</p><code>DEPENDS · ${esc(item.dependency||"ROOT")}</code><span class="owner">${esc(item.owner)}</span></article>`).join(""); }

  function seatPosition(index,total){ const angle=(-90 + index*(360/total))*Math.PI/180; return {left:50+39*Math.cos(angle),top:50+39*Math.sin(angle)}; }
  function renderParliament(validators=[],threshold=0){ const ring=$("#aj-validator-ring"); if(!ring)return; $$(".aj-validator-seat",ring).forEach(x=>x.remove()); validators.forEach((v,i)=>{const pos=seatPosition(i,validators.length); const div=doc.createElement("div");div.className=`aj-validator-seat ${v.verdict?`is-${v.verdict.toLowerCase()}`:""}`;div.style.left=`calc(${pos.left}% - 62px)`;div.style.top=`calc(${pos.top}% - 51px)`;div.innerHTML=`<small>${esc(v.id)}</small><strong>${esc(v.name)}</strong><span>${esc(v.verdict||"AWAITING")}${v.score?` · ${v.score}`:""}</span>`;ring.appendChild(div)}); const pass=validators.filter(x=>x.verdict==="PASS").length; if($("#aj-quorum"))$("#aj-quorum").textContent=`${pass} / ${threshold||validators.length}`; if($("#aj-parliament-state"))$("#aj-parliament-state").textContent=validators.length?(pass>=threshold?"THRESHOLD RECORDED":"THRESHOLD WITHHELD"):"AWAITING COMMIT"; const dissent=validators.find(x=>x.verdict==="DISSENT")||validators.find(x=>x.verdict==="REJECT"); if($("#aj-dissent-title"))$("#aj-dissent-title").textContent=dissent?`${dissent.name} · ${dissent.verdict}`:"No judgment revealed."; if($("#aj-dissent-copy"))$("#aj-dissent-copy").textContent=dissent?.rationale||"The minority seat remains structurally protected."; }

  function renderArtifacts(docket=null){ const node=$("#aj-artifact-constellation"); if(!node)return; const artifacts=docket?.evidence?.artifacts||data.artifacts; node.innerHTML=artifacts.map(item=>`<article class="aj-artifact${item.commitment?" is-sealed":""}"><small>${esc(item.id)}</small><strong>${esc(item.name)}</strong><span>${esc(item.plane)}</span><code>${esc(item.commitment||"NOT SEALED")}</code></article>`).join(""); if($("#aj-artifact-count"))$("#aj-artifact-count").textContent=`${docket?artifacts.length:0} / ${data.artifacts.length}`; if($("#aj-chain-head"))$("#aj-chain-head").textContent=docket?.evidence?.chain_head||"NOT SEALED"; if($("#aj-run-commitment"))$("#aj-run-commitment").textContent=docket?.run_commitment||"NOT SEALED"; }

  function renderTerminal(docket=null){ const state=docket?.authority?.terminal_state||"AWAITING COMMISSION"; if($("#aj-terminal-state"))$("#aj-terminal-state").textContent=state; const copies={HUMAN_SETTLEMENT_REVIEW:"The constitutional work cycle is evidence-ready for an authorized human settlement review. No external authority has been granted.",HUMAN_REVIEW_REQUIRED:"A material resource or scope condition requires human revision before the system may claim settlement readiness.",DISPUTE_OPEN:"A rights or challenge condition remains unresolved. The docket is preserved and settlement readiness is withheld.",SAFE_HOLD:"A severe constitutional breach forced a safe hold. Evidence remains available for investigation; continuation is denied.","AWAITING COMMISSION":"The system has not produced a review package."}; if($("#aj-terminal-copy"))$("#aj-terminal-copy").textContent=copies[state]||copies["AWAITING COMMISSION"]; const facts=$("#aj-terminal-facts"); if(facts){ const values=docket?[["FACTUAL CORRECTNESS",docket.authority.factual_correctness],["PRODUCTION",docket.authority.production_activation],["USER FUNDS",docket.authority.user_fund_authorization],["LIVE TOKEN MOVEMENT",String(docket.authority.live_token_movements)],["EXTERNAL ACTIONS",String(docket.authority.external_actions)],["AUTHORITY",docket.authority.external_authority]]:[["FACTUAL CORRECTNESS","NOT CERTIFIED"],["PRODUCTION","NOT ACTIVATED"],["USER FUNDS","NOT AUTHORIZED"],["LIVE TOKEN MOVEMENT","0"],["EXTERNAL ACTIONS","0"],["AUTHORITY","NONE_GRANTED"]]; facts.innerHTML=values.map(([a,b])=>`<div><small>${esc(a)}</small><strong>${esc(b)}</strong></div>`).join(""); } ["#aj-download-docket","#aj-download-brief","#aj-copy-summary"].forEach(sel=>{const el=$(sel);if(el)el.disabled=!docket}); }

  function download(name,type,content){ const blob=new Blob([content],{type});const url=URL.createObjectURL(blob);const a=doc.createElement("a");a.href=url;a.download=name;doc.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000); }
  function executiveBrief(docket){return `# ${data.release_title} — Executive Human Review Brief\n\n**Run:** \`${docket.run_id}\`  \n**Commitment:** \`${docket.run_commitment}\`  \n**Terminal:** \`${docket.authority.terminal_state}\`  \n**Authority:** \`${docket.authority.external_authority}\`\n\n## Work constitution\n\n${docket.work_constitution.mission}\n\n## Market\n\n- Prime guild: **${docket.market.council.prime}**\n- Pareto frontier: ${docket.market.frontier.join(", ")}\n- Parliament: ${docket.parliament.pass} PASS, ${docket.parliament.dissent} DISSENT, ${docket.parliament.reject} REJECT, ${docket.parliament.abstain} ABSTAIN\n- Evidence artifacts: ${docket.evidence.artifact_count}\n\n## Decision boundary\n\nNo wallet connection, token movement, production activation, user-fund authorization, credential issuance, legal reliance, or external action occurred. A sealed docket is a review object, not permission.\n`;}

  async function runFlight(event){ event?.preventDefault(); const runButton=$("#aj-run"); if(runButton)runButton.disabled=true; const commission=commissionFromInputs(); const snapshot=marketSnapshot(commission.jobClass.id,commission.posture.id,commission.risk.id); const council=constituteCouncil(snapshot); const graph=workGraph(council); const validators=validatorJudgments(commission,council,snapshot); const guardians=guardianStatus(commission); const docket=compileDocket(commission,snapshot,council,graph,validators,guardians); window.__AGI_JOBS_STATE__={running:true,commission,snapshot,council,graph,validators,guardians,docket}; renderMarket(snapshot,council);renderWorkGraph(graph);renderParliament(validators,commission.risk.validator_threshold);renderArtifacts(docket);renderTerminal(docket); const terminalIndex=15; const incidentIndex={identity:1,rights:12,budget:14,validation:11,evidence:9,goal:8}[commission.incident.effect]??terminalIndex; const stopAt=commission.incident.id==="none"?terminalIndex:incidentIndex; for(let i=0;i<=stopAt;i++){renderGates(docket,i);inspectGate(i,docket);await new Promise(resolve=>setTimeout(resolve,reducedMotion?0:42));} renderGates(docket,stopAt);inspectGate(stopAt,docket); if($("#aj-charter-id"))$("#aj-charter-id").textContent=docket.run_id; window.__AGI_JOBS_STATE__.running=false; if(runButton)runButton.disabled=false; }

  function initExchange(){ renderMetrics();renderThesis(); const preset=data.presets[0]; populateSelect($("#aj-preset"),data.presets,x=>x.name,preset.id);populateSelect($("#aj-job-class"),data.job_classes,x=>x.label,preset.job_class);populateSelect($("#aj-posture"),data.postures,x=>x.name,preset.posture);populateSelect($("#aj-risk"),data.risk_profiles,x=>x.label,preset.risk);populateSelect($("#aj-incident"),data.incidents,x=>x.label,"none"); if($("#aj-mission"))$("#aj-mission").value=preset.mission;if($("#aj-reward"))$("#aj-reward").value=preset.reward_units; ["#aj-mission","#aj-job-class","#aj-posture","#aj-risk","#aj-reward","#aj-incident"].forEach(sel=>$(sel)?.addEventListener("input",updateCharter)); $("#aj-preset")?.addEventListener("change",()=>{const p=findBy(data.presets,$("#aj-preset").value);$("#aj-mission").value=p.mission;$("#aj-job-class").value=p.job_class;$("#aj-posture").value=p.posture;$("#aj-risk").value=p.risk;$("#aj-reward").value=p.reward_units;updateCharter();}); $("#aj-job-form")?.addEventListener("submit",runFlight); $("#aj-reset")?.addEventListener("click",()=>{window.__AGI_JOBS_STATE__={running:false};$("#aj-preset").value=preset.id;$("#aj-mission").value=preset.mission;$("#aj-job-class").value=preset.job_class;$("#aj-posture").value=preset.posture;$("#aj-risk").value=preset.risk;$("#aj-reward").value=preset.reward_units;$("#aj-incident").value="none";updateCharter();renderGates();renderWorkGraph();renderParliament();renderArtifacts();renderTerminal();}); $("#aj-download-docket")?.addEventListener("click",()=>{const d=window.__AGI_JOBS_STATE__?.docket;if(d)download(`agi-jobs-${d.run_id.toLowerCase()}-evidence-docket.json`,"application/json",JSON.stringify(d,null,2)+"\n")}); $("#aj-download-brief")?.addEventListener("click",()=>{const d=window.__AGI_JOBS_STATE__?.docket;if(d)download(`agi-jobs-${d.run_id.toLowerCase()}-executive-brief.md`,"text/markdown",executiveBrief(d))}); $("#aj-copy-summary")?.addEventListener("click",async()=>{const d=window.__AGI_JOBS_STATE__?.docket;if(!d)return;const text=`${data.release_title}\n${d.run_id}\n${d.authority.terminal_state}\nAuthority: ${d.authority.external_authority}\nRun commitment: ${d.run_commitment}`;try{await navigator.clipboard.writeText(text)}catch{const ta=doc.createElement("textarea");ta.value=text;doc.body.appendChild(ta);ta.select();doc.execCommand("copy");ta.remove()}$("#aj-copy-summary").textContent="Copied";setTimeout(()=>$("#aj-copy-summary").textContent="Copy review summary",1200)}); updateCharter();renderGates();renderWorkGraph();renderParliament();renderArtifacts();renderTerminal(); window.__AGI_JOBS_STATE__={running:false}; }

  function renderMarketPage(){ const p=data.postures[0], c=data.job_classes[0], r=data.risk_profiles[2];populateSelect($("#aj-market-posture"),data.postures,x=>x.name,p.id);populateSelect($("#aj-market-class"),data.job_classes,x=>x.label,c.id);populateSelect($("#aj-market-risk"),data.risk_profiles,x=>x.label,r.id); const update=()=>{const s=marketSnapshot($("#aj-market-class").value,$("#aj-market-posture").value,$("#aj-market-risk").value);renderMarketObservatory(s)}; ["#aj-market-posture","#aj-market-class","#aj-market-risk"].forEach(sel=>$(sel)?.addEventListener("change",update)); if($("#aj-guild-grid"))$("#aj-guild-grid").innerHTML=data.institutions.map(item=>`<article class="aj-guild-card" data-sigil="${esc(item.sigil)}"><div class="aj-guild-meta"><span>${esc(item.guild.toUpperCase())}</span><span>${esc(item.risk_limit.toUpperCase())} RISK</span></div><h3>${esc(item.name)}</h3><p>“${esc(item.doctrine)}”</p><div class="aj-guild-skills">${item.capabilities.map(x=>`<span>${esc(x)}</span>`).join("")}</div><div class="aj-guild-bars">${[["CAPABILITY",item.capability],["EVIDENCE",item.evidence],["SAFETY",item.safety],["ORIGINALITY",item.originality]].map(([a,b])=>`<div class="aj-guild-bar"><small>${a} · ${fmt(b*100)}</small><i style="--value:${b*100}%"></i></div>`).join("")}</div></article>`).join(""); if($("#aj-archetype-grid"))$("#aj-archetype-grid").innerHTML=data.job_archetypes.map(item=>`<article class="aj-archetype"><small>${esc(item.id)} · ${esc(item.class.toUpperCase())}</small><h3>${esc(item.name)}</h3><p>${esc(item.proof)}</p></article>`).join(""); update(); }

  function renderMarketObservatory(snapshot){ if($("#aj-market-leader"))$("#aj-market-leader").textContent=snapshot.leader?.name||"NONE";if($("#aj-market-leader-score"))$("#aj-market-leader-score").textContent=snapshot.leader?`${fmt(snapshot.leader.score*100,1)} / 100 weighted score`:"No admissible institution";if($("#aj-market-frontier-label"))$("#aj-market-frontier-label").textContent=`${snapshot.frontier.length} FRONTIER`; const ranking=$("#aj-market-ranking");if(ranking)ranking.innerHTML=snapshot.rows.map((item,i)=>`<div class="aj-market-row${snapshot.frontier.some(x=>x.id===item.id)?" is-frontier":""}${i===0&&item.admitted?" is-selected":""}"><span class="rank">${String(i+1).padStart(2,"0")}</span><div><b>${esc(item.name)}</b><small>${item.admitted?esc(item.guild):"NOT ADMITTED"}</small></div><span class="score">${item.admitted?fmt(item.score*100,1):"—"}</span></div>`).join(""); const svg=$("#aj-pareto-chart");if(!svg)return;svg.innerHTML=""; for(let n=0;n<=5;n++){const x=70+n*125,y=450-n*82;const vl=doc.createElementNS(SVG,"line");vl.setAttribute("x1",x);vl.setAttribute("x2",x);vl.setAttribute("y1",40);vl.setAttribute("y2",450);vl.setAttribute("class","aj-chart-grid");svg.append(vl);const hl=doc.createElementNS(SVG,"line");hl.setAttribute("x1",70);hl.setAttribute("x2",695);hl.setAttribute("y1",450-n*82);hl.setAttribute("y2",450-n*82);hl.setAttribute("class","aj-chart-grid");svg.append(hl)} const ax=doc.createElementNS(SVG,"line");ax.setAttribute("x1",70);ax.setAttribute("x2",710);ax.setAttribute("y1",450);ax.setAttribute("y2",450);ax.setAttribute("class","aj-chart-axis");svg.append(ax);const ay=doc.createElementNS(SVG,"line");ay.setAttribute("x1",70);ay.setAttribute("x2",70);ay.setAttribute("y1",30);ay.setAttribute("y2",450);ay.setAttribute("class","aj-chart-axis");svg.append(ay); const xl=doc.createElementNS(SVG,"text");xl.setAttribute("x",390);xl.setAttribute("y",500);xl.setAttribute("text-anchor","middle");xl.setAttribute("class","aj-chart-label");xl.textContent="UTILITY + ORIGINALITY →";svg.append(xl);const yl=doc.createElementNS(SVG,"text");yl.setAttribute("x",18);yl.setAttribute("y",250);yl.setAttribute("transform","rotate(-90 18 250)");yl.setAttribute("text-anchor","middle");yl.setAttribute("class","aj-chart-label");yl.textContent="EVIDENCE + SAFETY →";svg.append(yl); snapshot.rows.filter(x=>x.admitted).forEach(item=>{const g=doc.createElementNS(SVG,"g");g.setAttribute("class",`aj-chart-point${snapshot.frontier.some(x=>x.id===item.id)?" is-frontier":""}${snapshot.leader?.id===item.id?" is-leader":""}`);const x=70+clamp((item.utilityAxis-.55)/.45)*625;const y=450-clamp((item.evidenceAxis-.55)/.45)*410;const circle=doc.createElementNS(SVG,"circle");circle.setAttribute("cx",x);circle.setAttribute("cy",y);circle.setAttribute("r",snapshot.leader?.id===item.id?14:10);const label=doc.createElementNS(SVG,"text");label.setAttribute("x",x+15);label.setAttribute("y",y+4);label.textContent=item.sigil;g.append(circle,label);g.addEventListener("mouseenter",()=>{if($("#aj-market-leader"))$("#aj-market-leader").textContent=item.name;if($("#aj-market-leader-score"))$("#aj-market-leader-score").textContent=`${fmt(item.score*100,1)} score · ${snapshot.frontier.some(x=>x.id===item.id)?"PARETO FRONTIER":"ADMISSIBLE"}`});svg.append(g)}); }

  function renderProofPage(){ const d=data.sample_docket; const validators=d.parliament.judgments;if($("#aj-proof-parliament-grid"))$("#aj-proof-parliament-grid").innerHTML=validators.map((v,i)=>`<article class="aj-proof-validator${v.verdict==="DISSENT"?" dissent":""}"><div class="seat"><span>${esc(v.id)} · SEAT ${i+1}</span><strong>${esc(v.verdict)}</strong></div><h3>${esc(v.name)}</h3><p>${esc(v.rationale)}</p><footer><span>${esc(v.focus)}</span><strong>${v.score} / 100</strong></footer></article>`).join("");if($("#aj-proof-commit-sample"))$("#aj-proof-commit-sample").textContent=validators[0].commitment;if($("#aj-proof-reveal-sample"))$("#aj-proof-reveal-sample").textContent=`${validators[0].verdict} · ${validators[0].score} · conflict ${validators[0].conflict}`;if($("#aj-proof-quorum-sample"))$("#aj-proof-quorum-sample").textContent=`${d.parliament.pass} PASS / threshold ${d.parliament.threshold} / ${d.parliament.dissent} DISSENT`;renderLedger(d.evidence.artifacts);if($("#aj-threat-theatre"))$("#aj-threat-theatre").innerHTML=data.threats.map(item=>`<article class="aj-threat-card"><small>${esc(item.disposition)}</small><h3>${esc(item.title)}</h3><p>${esc(item.control)}</p><strong>FAIL-CLOSED CONTROL</strong></article>`).join("");if($("#aj-docket-json"))$("#aj-docket-json").textContent=JSON.stringify(d,null,2); }

  function renderLedger(artifacts){const node=$("#aj-ledger");if(!node)return;node.innerHTML=artifacts.map(item=>`<article class="aj-ledger-row" data-search="${esc(`${item.id} ${item.name} ${item.plane} ${item.purpose}`.toLowerCase())}"><span class="aj-ledger-id">${esc(item.id)}</span><div><strong>${esc(item.name)}</strong><small>${esc(item.purpose)}</small></div><span class="aj-ledger-plane">${esc(item.plane)}</span><code class="aj-ledger-hash" title="${esc(item.commitment)}">${esc(item.commitment)}</code></article>`).join("");const search=$("#aj-ledger-search");const count=$("#aj-ledger-count");search?.addEventListener("input",()=>{const q=search.value.trim().toLowerCase();let visible=0;$$('.aj-ledger-row',node).forEach(row=>{const show=!q||row.dataset.search.includes(q);row.classList.toggle("is-hidden",!show);if(show)visible++});if(count)count.textContent=`${visible} / ${artifacts.length} artifacts`})}

  function renderSettlementPage(){ const render=()=>{const reward=Math.max(500,Math.min(100000,Number($("#aj-settlement-reward")?.value||24000)));if($("#aj-settlement-total"))$("#aj-settlement-total").textContent=`${fmt(reward)} αU`;if($("#aj-settlement-grid"))$("#aj-settlement-grid").innerHTML=data.settlement_policy.allocations.map(item=>`<article class="aj-settlement-allocation"><span class="pct">${item.pct}%</span><h3>${esc(item.label)}</h3><p>${esc(item.condition)}</p><strong>${fmt(reward*item.pct/100,2)} αU</strong></article>`).join("")};$("#aj-settlement-reward")?.addEventListener("input",render);render();if($("#aj-condition-grid"))$("#aj-condition-grid").innerHTML=data.settlement_policy.conditions_precedent.map((item,i)=>`<article class="aj-condition-card"><i>${String(i+1).padStart(2,"0")}</i><h3>${esc(item)}</h3><p>Must be affirmatively reviewed. No condition is inferred from silence.</p></article>`).join("");const passport=data.sample_docket.memory.capability_passport_candidate;const institution=findBy(data.institutions,passport.institution);if($("#aj-passport-name"))$("#aj-passport-name").textContent=institution.name;if($("#aj-passport-scope"))$("#aj-passport-scope").textContent=`Candidate scope: ${passport.scope}. Evidence chain: ${data.sample_docket.run_commitment.slice(0,18)}…`;if($("#aj-passport-skills"))$("#aj-passport-skills").innerHTML=passport.skills.map(x=>`<span>${esc(x)}</span>`).join("");if($("#aj-memory-deltas"))$("#aj-memory-deltas").innerHTML=Object.entries(data.sample_docket.memory.reputation_delta_candidate).map(([k,v])=>`<div class="aj-memory-delta"><strong>${esc(k.replaceAll("_"," ").toUpperCase())}</strong><span>${esc(v)}</span></div>`).join(""); }

  function renderArchitecturePage(){ if($("#aj-module-stack"))$("#aj-module-stack").innerHTML=data.modules.map(item=>`<article class="aj-module-card"><small>${esc(item.id)} · ${esc(item.authority.toUpperCase())}</small><h3>${esc(item.name)}</h3><p>${esc(item.purpose)}</p><code>BOUNDED AUTHORITY · ${esc(item.authority)}</code></article>`).join("");if($("#aj-translation-table"))$("#aj-translation-table").innerHTML=data.architecture_translation.map(item=>`<article class="aj-translation-row"><strong>${esc(item.original)}</strong><b>${esc(item.goalos)}</b><p>${esc(item.translation)}</p></article>`).join("");if($("#aj-principle-grid"))$("#aj-principle-grid").innerHTML=data.governance_principles.map((item,i)=>`<article class="aj-principle-card"><small>${String(i+1).padStart(2,"0")}</small><h3>${esc(item.title)}</h3><p>${esc(item.detail)}</p></article>`).join("");if($("#aj-threat-grid"))$("#aj-threat-grid").innerHTML=data.threats.map(item=>`<article class="aj-threat-arch-card"><small>${esc(item.disposition)}</small><h3>${esc(item.title)}</h3><p>${esc(item.control)}</p><strong>CONSTITUTIONAL DISPOSITION</strong></article>`).join("");if($("#aj-lineage-table"))$("#aj-lineage-table").innerHTML=data.lineage_fingerprints.map((item,i)=>`<article class="aj-lineage-row"><span>${String(i+1).padStart(2,"0")}</span><strong>${esc(item.path)}</strong><code title="${esc(item.sha256)}">${esc(item.sha256)}</code><small>${fmt(item.bytes)} B</small></article>`).join("");const m=data.mainnet_record||{};if($("#aj-mainnet-context"))$("#aj-mainnet-context").innerHTML=[["NETWORK",m.network],["GOALOS CONTRACTS",m.contracts],["OPERATOR VERIFICATION",m.verification],["PHASE-B GRANTS",m.phase_b_grants],["PRODUCTION",m.production_activation],["USER FUNDS",m.user_fund_authorization]].map(([a,b])=>`<div><small>${esc(a)}</small><strong>${esc(b??"UNKNOWN")}</strong></div>`).join("");if($("#aj-claim-list"))$("#aj-claim-list").innerHTML=data.claim_boundary.map(x=>`<li>${esc(x)}</li>`).join(""); }

  try {
    if (pageName === "exchange") initExchange();
    else if (pageName === "market") renderMarketPage();
    else if (pageName === "proof") renderProofPage();
    else if (pageName === "settlement") renderSettlementPage();
    else if (pageName === "architecture") renderArchitecturePage();
    root.dataset.ajReady = "true";
  } catch (error) {
    root.dataset.ajReady = "error";
    root.dataset.ajError = String(error?.message || error);
    console.error(error);
  }
})();
