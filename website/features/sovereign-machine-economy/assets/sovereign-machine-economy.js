(() => {
  "use strict";
  const doc = document;
  const root = doc.documentElement;
  const body = doc.body;
  const pageName = body?.dataset.smePage || "experience";
  const dataNode = doc.getElementById("sme-data");
  if (!dataNode) return;
  const data = JSON.parse(dataNode.textContent || "{}");
  const $ = (selector, scope = doc) => scope.querySelector(selector);
  const $$ = (selector, scope = doc) => Array.from(scope.querySelectorAll(selector));
  const esc = value => String(value ?? "").replace(/[&<>'"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;","'":"&#39;",'"':"&quot;"}[c]));
  const reducedMotion = matchMedia("(prefers-reduced-motion: reduce)").matches;
  root.classList.add("sme-js");
  window.__SME_DATA__ = data;

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
    const message = new Uint8Array(paddedLength); message.set(bytes); message[length] = 0x80;
    const view = new DataView(message.buffer); const bits = length * 8;
    view.setUint32(paddedLength - 8, Math.floor(bits / 0x100000000), false); view.setUint32(paddedLength - 4, bits >>> 0, false);
    const w = new Uint32Array(64); const rotr = (x, n) => (x >>> n) | (x << (32 - n));
    for (let offset = 0; offset < paddedLength; offset += 64) {
      for (let i = 0; i < 16; i++) w[i] = view.getUint32(offset + i * 4, false);
      for (let i = 16; i < 64; i++) {
        const s0 = rotr(w[i-15],7) ^ rotr(w[i-15],18) ^ (w[i-15] >>> 3);
        const s1 = rotr(w[i-2],17) ^ rotr(w[i-2],19) ^ (w[i-2] >>> 10);
        w[i] = (w[i-16] + s0 + w[i-7] + s1) >>> 0;
      }
      let [a,b,c,d,e,f,g,h] = H;
      for (let i = 0; i < 64; i++) {
        const S1 = rotr(e,6) ^ rotr(e,11) ^ rotr(e,25); const ch = (e & f) ^ (~e & g);
        const t1 = (h + S1 + ch + K[i] + w[i]) >>> 0; const S0 = rotr(a,2) ^ rotr(a,13) ^ rotr(a,22);
        const maj = (a & b) ^ (a & c) ^ (b & c); const t2 = (S0 + maj) >>> 0;
        h=g; g=f; f=e; e=(d+t1)>>>0; d=c; c=b; b=a; a=(t1+t2)>>>0;
      }
      H[0]=(H[0]+a)>>>0; H[1]=(H[1]+b)>>>0; H[2]=(H[2]+c)>>>0; H[3]=(H[3]+d)>>>0;
      H[4]=(H[4]+e)>>>0; H[5]=(H[5]+f)>>>0; H[6]=(H[6]+g)>>>0; H[7]=(H[7]+h)>>>0;
    }
    return H.map(x => x.toString(16).padStart(8,"0")).join("");
  }

  const deepClone = value => JSON.parse(JSON.stringify(value));
  const pad = value => String(value).padStart(2, "0");
  const titleOf = (item, fallback) => item?.name || item?.title || item?.label || item?.id || fallback;
  const idOf = (item, fallback) => item?.id || item?.key || sha256(titleOf(item, fallback)).slice(0, 10).toUpperCase();
  const numeric = value => Number.isFinite(Number(value)) ? Number(value) : 0;

  function choose(items, seed, count, salt = "") {
    if (!Array.isArray(items) || !items.length) return [];
    return items.map((item, index) => ({item, score: parseInt(sha256(`${seed}|${salt}|${index}|${stable(item)}`).slice(0, 12), 16)}))
      .sort((a,b) => b.score - a.score).slice(0, Math.min(count, items.length)).map(x => x.item);
  }

  function score(seed, salt, floor = 70, span = 29) { return floor + (parseInt(sha256(`${seed}|${salt}`).slice(0, 8), 16) % (span + 1)); }

  function weightedScore(metrics, weights) {
    return Object.entries(weights || {}).reduce((sum, [key, weight]) => sum + numeric(metrics[key]) * numeric(weight), 0);
  }

  function paretoFrontier(items, keys) {
    return items.filter((candidate, index) => !items.some((other, j) => j !== index && keys.every(key => numeric(other.metrics[key]) >= numeric(candidate.metrics[key])) && keys.some(key => numeric(other.metrics[key]) > numeric(candidate.metrics[key]))));
  }

  function download(filename, content, type = "application/json") {
    const blob = new Blob([content], {type}); const link = doc.createElement("a");
    link.href = URL.createObjectURL(blob); link.download = filename; doc.body.appendChild(link); link.click();
    setTimeout(() => { URL.revokeObjectURL(link.href); link.remove(); }, 0);
  }

  function formOption(item) { return `<option value="${esc(item.id)}">${esc(item.label)}</option>`; }

  function buildCandidates(seed, commission) {
    const agents = data.dependencies.meta.agents || [];
    const adjectives = ["Aurelia","Civic","Apex","Helios","Concord","Veritas","Nexus","Sentinel","Polaris"];
    const nouns = ["Covenant","Assembly","Institution","Observatory","Directorate","Guild","Forum","Constellation","Accord"];
    const keys = ["evidence","safety","rights","utility","efficiency","novelty"];
    const candidates = Array.from({length:9}, (_, index) => {
      const candidateSeed = sha256(`${seed}|institution|${index}`);
      const roles = choose(agents, candidateSeed, Math.min(6, agents.length || 6), "roles");
      const metrics = Object.fromEntries(keys.map((key, metricIndex) => [key, score(candidateSeed, `${key}|${metricIndex}`, 70, 29)]));
      const weighted = weightedScore(metrics, commission.posture.weights);
      return {
        id:`INST-${candidateSeed.slice(0,12).toUpperCase()}`,
        name:`${adjectives[index]} ${commission.domain.split(" ")[0]} ${nouns[(index + parseInt(candidateSeed.slice(0,2),16)) % nouns.length]}`,
        metrics, weighted_score:Number(weighted.toFixed(3)),
        roles:roles.map((item, roleIndex) => ({id:idOf(item,`A${roleIndex+1}`),name:titleOf(item,`Constitutional Agent ${roleIndex+1}`),authority:item.boundary || item.mandate || "bounded specialist authority"})),
        lineage_root:sha256(stable({seed:candidateSeed,roles:roles.map(x=>idOf(x,"agent")),mission:commission.mission})),
        authority:"BOUNDED_AND_REVOCABLE"
      };
    });
    const frontier = paretoFrontier(candidates, keys);
    const selected = [...frontier].sort((a,b) => b.weighted_score - a.weighted_score || a.id.localeCompare(b.id))[0] || candidates[0];
    return {candidates, frontier, selected};
  }

  function buildInstitution(seed, commission) {
    const set = buildCandidates(seed, commission); const selected = deepClone(set.selected);
    selected.charter_commitment = sha256(stable({mission:commission.mission,posture:commission.posture.id,risk:commission.risk.id,selected:selected.id,lineage:selected.lineage_root}));
    selected.candidate_count = set.candidates.length; selected.frontier_count = set.frontier.length;
    selected.rejected_candidates = set.candidates.filter(x => x.id !== selected.id).map(x => ({id:x.id,name:x.name,weighted_score:x.weighted_score,frontier:set.frontier.some(f=>f.id===x.id)}));
    return selected;
  }

  function buildNode(seed, institution, commission) {
    const peers = data.dependencies.node.peers || [];
    const primary = choose(peers, seed, 4, "primary-route"); const primaryIds = new Set(primary.map(x => idOf(x,"peer")));
    const shadow = choose(peers.filter(x => !primaryIds.has(idOf(x,"peer"))), seed, 3, "shadow-route");
    const route = {primary:primary.map(x=>({id:idOf(x,"peer"),name:titleOf(x,"Peer"),region:x.region||"DECLARED"})),shadow:shadow.map(x=>({id:idOf(x,"peer"),name:titleOf(x,"Peer"),region:x.region||"DECLARED"}))};
    const envelope = {risk:commission.risk.id,multiplier:commission.risk.resource_multiplier,max_external_actions:0,network_requests:0,wallet_connections:0,live_token_movements:0};
    return {
      id:`NODE-${sha256(`${seed}|node`).slice(0,12).toUpperCase()}`,
      route_id:`ROUTE-${sha256(stable(route)).slice(0,12).toUpperCase()}`,
      primary:route.primary,shadow:route.shadow,
      identity_commitment:sha256(stable({institution:institution.id,lineage:institution.lineage_root,release:data.dependencies.node.version,route})),
      resource_constitution:envelope,
      resource_commitment:sha256(stable(envelope)),
      receipt_id:`AWU-${sha256(`${seed}|receipt`).slice(0,16).toUpperCase()}`,
      external_actions:0,wallet_connections:0,network_requests:0
    };
  }

  function institutionMetrics(item) {
    return {
      evidence:numeric(item.evidence || item.reputation || 80),
      safety:numeric(item.safety || item.reliability || 80),
      rights:numeric(item.reputation || item.safety || 80),
      utility:numeric(item.capability || item.capacity || 80),
      efficiency:numeric(item.efficiency || (100 - numeric(item.rate || 20)) || 80),
      novelty:numeric(item.originality || 80)
    };
  }

  function buildMarket(seed, commission, institution, node) {
    const catalog = data.dependencies.jobs.institutions || [];
    const scored = catalog.map(item => {
      const metrics = institutionMetrics(item); return {...item,metrics,weighted_score:Number(weightedScore(metrics,commission.posture.weights).toFixed(3))};
    });
    const keys=["evidence","safety","rights","utility","efficiency","novelty"];
    const frontier=paretoFrontier(scored,keys);
    const ranked=[...scored].sort((a,b)=>b.weighted_score-a.weighted_score || idOf(a,"guild").localeCompare(idOf(b,"guild")));
    const prime=ranked[0]; const remaining=ranked.filter(x=>x!==prime); const selected=[prime,...choose(remaining,seed,5,"coalition")].slice(0,6);
    const roles=["PRIME","EVIDENCE","ASSURANCE","DELIVERY","SHADOW","RESERVE"];
    const validatorCatalog=data.dependencies.jobs.validators||[];
    const dissentSeat=validatorCatalog.find(item=>String(item.id||"").toUpperCase()==="V09"||/independent dissent/i.test(titleOf(item,"")));
    const pool=validatorCatalog.filter(item=>item!==dissentSeat);
    const ordinary=choose(pool,seed,Math.max(0,commission.risk.validator_seats-(dissentSeat?1:0)),"validators");
    const validators=(dissentSeat?[...ordinary,dissentSeat]:choose(validatorCatalog,seed,commission.risk.validator_seats,"validators")).slice(0,commission.risk.validator_seats);
    const opinions=validators.map((validator,index)=>{
      const protectedDissent=dissentSeat?validator===dissentSeat:index===validators.length-1;
      const verdict=protectedDissent?"DISSENT":"PASS"; const value=protectedDissent?66:82+(parseInt(sha256(`${seed}|validator|${index}`).slice(0,2),16)%15);
      return {id:idOf(validator,`V${index+1}`),name:titleOf(validator,`Validator ${index+1}`),verdict,score:value,conflict:"NONE_DECLARED",commitment:sha256(stable({seed,index,verdict,value,validator:idOf(validator,"validator")}))};
    });
    return {
      id:`MARKET-${sha256(`${seed}|market`).slice(0,12).toUpperCase()}`,
      frontier:frontier.map(x=>({id:idOf(x,"guild"),name:titleOf(x,"Guild"),weighted_score:x.weighted_score})),
      coalition_id:`COALITION-${sha256(stable(selected.map(x=>idOf(x,"guild")))).slice(0,12).toUpperCase()}`,
      coalition:selected.map((item,index)=>({id:idOf(item,`G${index+1}`),name:titleOf(item,`Guild ${index+1}`),role:roles[index],weighted_score:item.weighted_score})),
      parliament:{seats:validators.length,threshold:commission.risk.threshold,pass:Math.max(0,validators.length-1),dissent:validators.length?1:0,reject:0,opinions},
      challenge_hours:commission.risk.challenge_hours,
      charter_commitment:sha256(stable({mission:commission.mission,institution:institution.id,node:node.id,coalition:selected.map(x=>idOf(x,"guild"))})),
      settlement:{status:"HUMAN_SETTLEMENT_REVIEW",live:false,wallet_connection:false,token_movement:false,external_actions:0}
    };
  }

  function buildHandoffs(seed, commission, institution, node, market) {
    let previous="0".repeat(64);
    return data.handoffs.map(item=>{
      const payload={id:item.id,from:item.from,to:item.to,name:item.name,mission:commission.mission,institution:institution.id,node:node.id,market:market.id,previous};
      const commitment=sha256(stable(payload)); const row={...item,previous_commitment:previous,commitment}; previous=commitment; return row;
    });
  }

  function buildArtifacts(seed, commission, institution, node, market, terminal) {
    let previous="0".repeat(64);
    return data.artifact_classes.map((meta,index)=>{
      const payload={id:`A${pad(index+1)}`,plane:meta.plane,name:meta.name,run_seed:seed,mission:commission.mission,institution:institution.id,node:node.id,market:market.id,terminal};
      const artifact_hash=sha256(stable(payload)); const commitment=sha256(stable({previous,payload,artifact_hash}));
      const row={id:`A${pad(index+1)}`,plane:meta.plane,name:meta.name,previous_commitment:previous,artifact_hash,commitment,payload}; previous=commitment; return row;
    });
  }

  function buildRun(commission, options={}) {
    const seed=sha256(stable({release:data.release_id,mission:commission.mission,preset:commission.preset.id,posture:commission.posture.id,risk:commission.risk.id,incident:commission.incident.id}));
    const institution=buildInstitution(seed,commission); const node=buildNode(seed,institution,commission); const market=buildMarket(seed,commission,institution,node);
    const terminal=commission.incident.terminal||"HUMAN_SETTLEMENT_REVIEW"; const handoffs=buildHandoffs(seed,commission,institution,node,market); const artifacts=buildArtifacts(seed,commission,institution,node,market,terminal);
    const evidenceRoot=artifacts.at(-1)?.commitment||"0".repeat(64);
    const memory={id:`MEM-${sha256(`${seed}|memory`).slice(0,12).toUpperCase()}`,status:"HUMAN_PROMOTION_REQUIRED",scope:commission.preset.domain,expiry:"90_DAYS_AFTER_APPROVAL",revocable:true,evidence_root:evidenceRoot,automatic_promotion:false,failure_memory_preserved:true};
    const review={status:"PENDING_HUMAN_REVIEW",selected_action:null,record:null,available_actions:deepClone(data.review_actions),authority_granted:false,settlement_authorized:false,memory_promoted:false};
    const docket={
      schema:"goalos.sovereign_machine_economy.docket.v2",release_id:data.release_id,run_id:`SME-${seed.slice(0,16).toUpperCase()}`,mission:commission,
      institution,node,market,handoffs,evidence:{artifact_count:artifacts.length,chain_head:evidenceRoot,artifacts},counterfactuals:[],review,memory,
      incident:{id:commission.incident.id,label:commission.incident.label,effect:commission.incident.effect,stop_gate:commission.incident.stop_gate},
      authority:{terminal_state:terminal,external_authority:"NONE_GRANTED",factual_correctness:"NOT_CERTIFIED",production_activation:"NOT_ACTIVATED",user_fund_authorization:"NO",automatic_memory_promotion:"NOT_AUTHORIZED",external_actions:0,network_requests:0,wallet_connections:0,live_token_movements:0},
      claim_boundary:data.claim_boundary
    };
    const state={seed,terminal,institution,node,market,handoffs,artifacts,memory,docket,running:false,logs:[]};
    if (options.includeUniverses) {
      state.universes=buildUniverses(commission);
      docket.counterfactuals=state.universes.map(item=>({id:item.id,label:item.label,promise:item.promise,posture:item.posture,institution:item.institution_id,route:item.route,coalition:item.coalition,terminal_state:item.terminal,authority:item.authority,external_actions:0,scores:item.scores,commitment:sha256(stable({seed,universe:item.id,posture:item.posture,institution:item.institution_id,route:item.route,coalition:item.coalition,scores:item.scores}))}));
    }
    docket.economy_root=sha256(stable({institution:institution.charter_commitment,node:node.identity_commitment,market:market.charter_commitment,handoffs:handoffs.at(-1)?.commitment,evidence:evidenceRoot,counterfactuals:docket.counterfactuals.map(item=>item.commitment),memory:memory.id,review:review.status,terminal}));
    docket.run_commitment=sha256(stable(docket));
    return state;
  }
  function buildUniverses(baseCommission) {
    return data.universes.map(universe=>{
      const posture=data.postures.find(item=>item.id===universe.posture)||data.postures[0];
      const commission={...baseCommission,posture,incident:data.incidents.find(item=>item.id==="none")};
      const state=buildRun(commission,{includeUniverses:false});
      const scores=state.institution.metrics;
      return {id:universe.id,label:universe.label,promise:universe.promise,posture:posture.id,institution:state.institution.name,institution_id:state.institution.id,route:state.node.route_id,coalition:state.market.coalition_id,parliament:`${state.market.parliament.seats} seats · ${state.market.parliament.threshold} threshold`,frontier:state.market.frontier.length,evidence_margin:Math.round((scores.evidence+scores.safety+scores.rights)/3),utility_margin:Math.round((scores.utility+scores.efficiency+scores.novelty)/3),economy_root:state.docket.economy_root,terminal:state.terminal,authority:"NONE_GRANTED",scores};
    });
  }

  function applyReviewAction(state, actionId) {
    const action=data.review_actions.find(item=>item.id===actionId); if (!action||!state?.docket) return state;
    const record=sha256(stable({run_id:state.docket.run_id,economy_root:state.docket.economy_root,action:action.id,status:action.record,previous:state.docket.run_commitment}));
    state.docket.review={...state.docket.review,status:action.record,selected_action:action.id,record,authority_granted:false,settlement_authorized:false,memory_promoted:false};
    if (action.id==="request-revision") state.terminal="HUMAN_REVIEW_REQUIRED";
    if (action.id==="open-dispute") state.terminal="DISPUTE_OPEN";
    if (action.id==="reject") state.terminal="SAFE_HOLD";
    state.docket.authority.terminal_state=state.terminal;
    state.docket.run_commitment=sha256(stable({...state.docket,run_commitment:undefined}));
    return state;
  }
  function reviewBrief(state) {
    const d=state.docket; const review=d.review?.status||"PENDING_HUMAN_REVIEW";
    return `# GoalOS Sovereign Machine Economy Ω — Executive Review Brief\n\n**Run:** \`${d.run_id}\`  \n**Economy root:** \`${d.economy_root}\`  \n**Terminal state:** \`${d.authority.terminal_state}\`  \n**External authority:** \`${d.authority.external_authority}\`  \n**Local review record:** \`${review}\`\n\n## Mission\n\n${d.mission.mission}\n\n## Constitutional civilization\n\n- Mind Foundry: ${d.institution.name} (${d.institution.frontier_count}/${d.institution.candidate_count} candidates on the constitutional frontier)\n- Proof Node: ${d.node.id}; primary route ${d.node.route_id}; ${d.node.primary.length} primary + ${d.node.shadow.length} shadow peers\n- Work Economy: ${d.market.coalition_id}; ${d.market.parliament.seats} validator seats; ${d.market.parliament.dissent} preserved dissent\n- Counterfactual Observatory: ${d.counterfactuals.length} constitutional universes compared\n\n## Proof\n\n- Typed handoffs: ${d.handoffs.length}\n- Chained artifacts: ${d.evidence.artifact_count}\n- Evidence root: \`${d.evidence.chain_head}\`\n- Run commitment: \`${d.run_commitment}\`\n\n## Human boundary\n\nExternal actions: 0  \nWallet connections: 0  \nNetwork requests: 0  \nLive token movement: 0  \nFactual correctness: NOT_CERTIFIED  \nProduction activation: NOT_ACTIVATED  \nMemory promotion: NOT_AUTHORIZED\n\n**The package is ready for accountable human review. No external authority has been granted.**\n`;
  }
  function renderCommon() {
    const metrics=$("#sme-hero-metrics"); if (metrics) metrics.innerHTML=data.hero_metrics.map(item=>`<div class="sme-metric"><strong>${esc(item.value)}</strong><span>${esc(item.label)}</span></div>`).join("");
    const sources=$("#sme-source-releases"); if (sources) sources.innerHTML=data.source_releases.map((item,index)=>`<article class="sme-source-card sme-reveal"><div class="sme-source-num"><span>0${index+1} · ${esc(item.layer)}</span><span>${esc(item.id)}</span></div><div class="sme-source-sigil">${esc(item.sigil)}</div><h3>${esc(item.title)}</h3><p>${esc(item.role)}</p><div class="sme-source-handoff"><strong>BOUNDARY CONTRACT</strong><br>${esc(item.handoff)}</div><div class="sme-source-links"><a href="${esc(item.page)}">Open experience</a><a href="${esc(item.architecture_page)}">Architecture</a></div></article>`).join("");
    const handoffs=$("#sme-handoff-grid"); if (handoffs) handoffs.innerHTML=data.handoffs.map(item=>`<article class="sme-handoff-card sme-reveal"><small>${esc(item.id)} · ${esc(item.from)} → ${esc(item.to)}</small><h3>${esc(item.name)}</h3><p>${esc(item.purpose)}</p><code data-handoff-id="${esc(item.id)}">commitment pending</code></article>`).join("");
    const boundary=$("#sme-boundary-grid"); if (boundary) {
      const entries=[["EXTERNAL AUTHORITY","NONE_GRANTED","No generated result becomes permission to act."],["FACTUAL CORRECTNESS","NOT_CERTIFIED","Evidence structure does not certify external truth."],["PRODUCTION","NOT_ACTIVATED","The experience is a local constitutional twin."],["USER FUNDS","NOT_AUTHORIZED","No wallet, payment, or value-movement path exists."],["MEMORY PROMOTION","HUMAN_REQUIRED","Capability memory remains a scoped, revocable candidate."],["EXTERNAL ACTIONS","0","No network write, transaction, credential, or execution occurs."]];
      boundary.innerHTML=entries.map(([a,b,c])=>`<article class="sme-boundary-card"><small>${a}</small><strong>${b}</strong><p>${c}</p></article>`).join("");
    }
    const preview=$("#sme-universe-preview"); if (preview) preview.innerHTML=data.universes.map((item,index)=>`<article class="sme-universe-card" style="--universe-glow:${["rgba(232,205,119,.22)","rgba(121,240,218,.22)","rgba(155,132,255,.22)"][index]}"><small>UNIVERSE 0${index+1}</small><h3>${esc(item.label)}</h3><p>${esc(item.promise)}</p><ul><li><span>Authority</span><strong>NONE_GRANTED</strong></li><li><span>Constitutional vetoes</span><strong>UNCHANGED</strong></li><li><span>Outcome</span><strong>POSTURE-DEPENDENT</strong></li></ul></article>`).join("");
  }

  function renderParliament(market) {
    const node=$("#sme-parliament"); if (!node) return;
    const opinions=market.parliament.opinions; const radius=70; const cx=95,cy=95;
    const seats=opinions.map((item,index)=>{const angle=(-Math.PI/2)+(index/opinions.length)*Math.PI*2; const x=cx+Math.cos(angle)*radius; const y=cy+Math.sin(angle)*radius; return `<div class="sme-seat ${item.verdict.toLowerCase()}" style="left:${x}px;top:${y}px" title="${esc(item.name)} · ${esc(item.verdict)}">${esc(item.id)}<br>${esc(item.verdict)}</div>`;}).join("");
    node.innerHTML=`${seats}<div class="sme-parliament-core">${market.parliament.pass} PASS<br>${market.parliament.dissent} DISSENT</div>`;
    const summary=$("#sme-parliament-summary"); if (summary) summary.textContent=`${market.parliament.seats} seats · ${market.parliament.threshold} threshold`;
  }

  function renderRun(state) {
    window.__SME_STATE__=state;
    const setText=(id,value)=>{const node=$(id);if(node)node.textContent=value;};
    setText("#sme-terminal-state",state.terminal); setText("#sme-institution-name",state.institution.name);
    setText("#sme-institution-detail",`${state.institution.roles.length} bounded roles · ${state.institution.frontier_count}/${state.institution.candidate_count} candidates on the constitutional frontier.`);
    setText("#sme-node-route",state.node.route_id); setText("#sme-node-detail",`${state.node.primary.length} primary peers · ${state.node.shadow.length} shadow peers · receipt ${state.node.receipt_id}.`);
    setText("#sme-coalition-name",state.market.coalition_id); setText("#sme-coalition-detail",`${state.market.coalition.length} guild council · ${state.market.parliament.pass} PASS · ${state.market.parliament.dissent} DISSENT.`);
    setText("#sme-economy-root",`${state.docket.economy_root.slice(0,18)}…`); setText("#sme-root-detail",`${state.artifacts.length} artifacts · ${state.handoffs.length} handoffs · commitment ${state.docket.run_commitment.slice(0,12)}…`);
    const decision=$("#sme-decision"); if (decision) decision.classList.toggle("is-hold",state.terminal!=="HUMAN_SETTLEMENT_REVIEW");
    setText("#sme-decision-copy",state.terminal==="HUMAN_SETTLEMENT_REVIEW"?"Proof-ready work awaits human settlement review. Evidence does not move value by itself.":`${state.docket.incident.label}: ${state.docket.incident.effect} Terminal state ${state.terminal}; authority remains withheld.`);
    $$('[data-handoff-id]').forEach((node,index)=>{if(state.handoffs[index])node.textContent=`${state.handoffs[index].commitment.slice(0,18)}…`;});
    const live=$("#sme-live-handoffs"); if(live) live.innerHTML=state.handoffs.map(item=>`<div class="sme-live-handoff"><span>${esc(item.id)}</span><strong>${esc(item.from)} → ${esc(item.to)} · ${esc(item.name)}</strong><code>${esc(item.commitment.slice(0,12))}…</code></div>`).join("");
    setText("#sme-handoff-summary",`${state.handoffs.length} / ${data.handoffs.length} sealed`);
    const spark=$("#sme-evidence-spark"); if(spark)spark.innerHTML=state.artifacts.map(item=>`<i class="sme-evidence-dot is-sealed" title="${esc(item.id)} · ${esc(item.name)}"></i>`).join("");
    setText("#sme-artifact-summary",`${state.artifacts.length} / ${data.artifact_classes.length} sealed`); renderParliament(state.market);
    ["sme-download-json","sme-download-md","sme-copy-summary"].forEach(id=>{const node=$(`#${id}`);if(node)node.disabled=false;});
    $$("#sme-review-actions button").forEach(button=>button.disabled=false);
    const review=state.docket.review; const reviewNode=$("#sme-review-record"); if(reviewNode){reviewNode.querySelector("span").textContent=review.status; reviewNode.querySelector("code").textContent=review.record||"—";}
  }

  async function animateRun(state) {
    const gates=$$(".sme-gate"); const statuses=$$(".sme-engine-status-card"); gates.forEach(node=>node.className="sme-gate"); statuses.forEach(node=>node.className="sme-engine-status-card");
    const stopIndex=Math.max(0,Math.min(gates.length-1,numeric(state.docket.incident.stop_gate))); const delay=reducedMotion?0:55;
    for(let i=0;i<gates.length;i++){
      if(i<stopIndex)gates[i].classList.add("is-complete"); else if(i===stopIndex)gates[i].classList.add(state.terminal==="HUMAN_SETTLEMENT_REVIEW"?"is-active":"is-held");
      const engineIndex=i<7?0:i<14?1:2; statuses.forEach((node,index)=>{node.classList.toggle("is-active",index===engineIndex);if(index<engineIndex)node.classList.add("is-complete");});
      if(delay)await new Promise(resolve=>setTimeout(resolve,delay)); if(i===stopIndex&&state.terminal!=="HUMAN_SETTLEMENT_REVIEW")break;
    }
    statuses.forEach((node,index)=>{node.classList.remove("is-active");if(state.terminal==="HUMAN_SETTLEMENT_REVIEW"||index<(stopIndex<7?0:stopIndex<14?1:2))node.classList.add("is-complete");}); renderRun(state);
  }

  function currentCommission(fields) {
    const preset=data.mission_presets.find(x=>x.id===fields.preset.value)||data.mission_presets[0];
    return {mission:fields.mission.value.trim(),preset,domain:preset.domain,posture:data.postures.find(x=>x.id===fields.posture.value)||data.postures[0],risk:data.risk_profiles.find(x=>x.id===fields.risk.value)||data.risk_profiles[0],incident:data.incidents.find(x=>x.id===fields.incident.value)||data.incidents[0]};
  }

  function updateCommissionPreview(riskId) {
    const risk=data.risk_profiles.find(x=>x.id===riskId)||data.risk_profiles[0]; const nodes=$$("#sme-commission-preview>div strong");
    if(nodes[0])nodes[0].textContent=`${data.artifact_classes.length} predecessor-linked artifacts`; if(nodes[1])nodes[1].textContent=`${risk.validator_seats} seats · ${risk.threshold} threshold`; if(nodes[2])nodes[2].textContent=`${risk.challenge_hours} hours`;
  }

  function renderExperience() {
    renderCommon();
    const fields={preset:$("#sme-preset"),mission:$("#sme-mission"),posture:$("#sme-posture"),risk:$("#sme-risk"),incident:$("#sme-incident")}; if(!Object.values(fields).every(Boolean))return;
    fields.preset.innerHTML=data.mission_presets.map(formOption).join(""); fields.posture.innerHTML=data.postures.map(formOption).join(""); fields.risk.innerHTML=data.risk_profiles.map(formOption).join(""); fields.incident.innerHTML=data.incidents.map(formOption).join(""); fields.posture.value="balanced";fields.risk.value="high";fields.incident.value="none";
    const setPreset=()=>{const item=data.mission_presets.find(x=>x.id===fields.preset.value)||data.mission_presets[0];fields.mission.value=item.mission;const draft=$("#sme-draft-id");if(draft)draft.textContent=`DRAFT-${sha256(item.mission).slice(0,8).toUpperCase()}`;};
    fields.preset.addEventListener("change",setPreset); fields.mission.addEventListener("input",()=>{const draft=$("#sme-draft-id");if(draft)draft.textContent=`DRAFT-${sha256(fields.mission.value).slice(0,8).toUpperCase()}`;}); fields.risk.addEventListener("change",()=>updateCommissionPreview(fields.risk.value)); setPreset();updateCommissionPreview(fields.risk.value);
    const status=$("#sme-engine-status"); status.innerHTML=data.source_releases.map(item=>`<article class="sme-engine-status-card"><small>${esc(item.layer)}</small><strong>${esc(item.id.toUpperCase())}</strong></article>`).join("");
    $("#sme-gate-groups").innerHTML="<span>FORMATION · G01–G07</span><span>EXECUTION · G08–G14</span><span>ACCOUNTABLE VALUE · G15–G21</span>";
    $("#sme-gate-rail").innerHTML=data.gates.map(item=>`<button class="sme-gate" type="button" data-engine="${esc(item.engine)}" data-label="${esc(item.id)} · ${esc(item.label)}" title="${esc(item.id)} · ${esc(item.title)}" aria-label="${esc(item.id)} ${esc(item.title)}"></button>`).join("");
    $("#sme-review-actions").innerHTML=data.review_actions.map(item=>`<button type="button" data-review-action="${esc(item.id)}" disabled>${esc(item.label)}</button>`).join("");
    $("#sme-mission-form").addEventListener("submit",async event=>{event.preventDefault();const commission=currentCommission(fields);if(!commission.mission){fields.mission.focus();return;}const button=$("#sme-convene");button.disabled=true;button.textContent="Constituting…";const state=buildRun(commission,{includeUniverses:true});state.running=true;window.__SME_STATE__=state;await animateRun(state);state.running=false;window.__SME_STATE__=state;button.disabled=false;button.textContent="Convene Sovereign Economy";});
    $("#sme-reset").addEventListener("click",()=>{setPreset();fields.posture.value="balanced";fields.risk.value="high";fields.incident.value="none";updateCommissionPreview("high");$$(".sme-gate").forEach(node=>node.className="sme-gate");$$(".sme-engine-status-card").forEach(node=>node.className="sme-engine-status-card");["#sme-terminal-state","#sme-institution-name","#sme-node-route","#sme-coalition-name","#sme-economy-root"].forEach((id,index)=>{const values=["AWAITING COMMISSION","Not formed","Not admitted","Not convened","—"];if($(id))$(id).textContent=values[index];});["sme-download-json","sme-download-md","sme-copy-summary"].forEach(id=>$("#"+id).disabled=true);$$("#sme-review-actions button").forEach(b=>b.disabled=true);$("#sme-live-handoffs").innerHTML="";$("#sme-evidence-spark").innerHTML="";$("#sme-parliament").innerHTML="";$("#sme-review-record span").textContent="NO REVIEW RECORDED";$("#sme-review-record code").textContent="—";window.__SME_STATE__={running:false,terminal:"AWAITING_COMMISSION"};});
    $$('[data-view]').forEach(button=>button.addEventListener("click",()=>{$$('[data-view]').forEach(x=>x.classList.remove("is-active"));button.classList.add("is-active");$(".sme-runtime").dataset.view=button.dataset.view;}));
    $("#sme-review-actions").addEventListener("click",event=>{const button=event.target.closest("button[data-review-action]");const state=window.__SME_STATE__;if(!button||!state?.docket)return;applyReviewAction(state,button.dataset.reviewAction);renderRun(state);});
    $("#sme-download-json").addEventListener("click",()=>{const state=window.__SME_STATE__;if(state?.docket)download(`sovereign-machine-economy-${state.docket.run_id}.json`,JSON.stringify(state.docket,null,2)+"\n");});
    $("#sme-download-md").addEventListener("click",()=>{const state=window.__SME_STATE__;if(state?.docket)download(`sovereign-machine-economy-${state.docket.run_id}-brief.md`,reviewBrief(state),"text/markdown");});
    $("#sme-copy-summary").addEventListener("click",async()=>{const state=window.__SME_STATE__;if(!state?.docket)return;const text=`${data.release_title}\n${state.docket.run_id}\n${state.docket.authority.terminal_state}\nEconomy root: ${state.docket.economy_root}\nReview: ${state.docket.review.status}\nAuthority: NONE_GRANTED`;try{await navigator.clipboard.writeText(text);}catch{const area=doc.createElement("textarea");area.value=text;doc.body.append(area);area.select();doc.execCommand("copy");area.remove();}});
    window.__SME_STATE__={running:false,terminal:"AWAITING_COMMISSION"};
  }

  function renderArchitecture() {
    const stack=$("#sme-architecture-stack"); if(stack){const layers=[["L01","MISSION PRINCIPAL","Declares purpose, success, exclusions, rights, risk, and budget.","COMMISSION · CHALLENGE · REVIEW","#ffffff"],["L02","META-AGENTIC α‑AGI","Forms, compares, and constitutes bounded institutions.","PROPOSE · SELECT · CONSTITUTE","#e8cd77"],["L03","AGI Alpha Node v0","Admits identity, routes work, executes locally, and seals receipts.","ADMIT · ROUTE · EXECUTE · PROVE","#79f0da"],["L04","AGI Jobs v0 (v2)","Forms markets, parliament, challenge, and settlement review.","COMMISSION · VALIDATE · CHALLENGE · REVIEW","#9b84ff"],["L05","REVOCABLE MEMORY","Returns scoped lessons without inheriting authority.","PROPOSE · EXPIRE · REVOKE · REPLAY","#62dff6"],["L06","HUMAN AUTHORITY","Approves, revises, rejects, disputes, authorizes, or revokes outside the twin.","DELIBERATE · AUTHORIZE · REVOKE","#ffffff"]];stack.innerHTML=layers.map(([id,title,detail,authority,color])=>`<article class="sme-stack-layer" style="--layer-color:${color}"><div class="sme-stack-id">${id}</div><div><h3>${esc(title)}</h3><p>${esc(detail)}</p></div><div class="sme-stack-authority">${esc(authority)}</div></article>`).join("");}
    const rights=$("#sme-rights-grid");if(rights)rights.innerHTML=data.constitutional_rights.map((item,index)=>`<article class="sme-right-card"><span>${pad(index+1)}</span><div><h3>${esc(item.right)}</h3><p>${esc(item.duty)}</p></div></article>`).join("");
    const gates=$("#sme-architecture-gates");if(gates)gates.innerHTML=data.gates.map(item=>`<li><small>${esc(item.engine)} · ${esc(item.id)} · ${esc(item.label)}</small><h3>${esc(item.title)}</h3><p>${esc(item.description)}</p><strong>${esc(item.evidence)}</strong></li>`).join("");
    const matrix=$("#sme-authority-matrix");if(matrix){const rows=[["Authority","Principal","Mind Foundry","Proof Node","Work Economy","Memory","Human"],["Declare mission","YES","INPUT","INPUT","COMMISSION","NO","REVIEW"],["Form institution","NO","BOUNDED","NO","INPUT","INPUT","OVERRIDE"],["Execute work","NO","NO","BOUNDED","COMMISSION","NO","AUTHORIZE"],["Validate proof","CHALLENGE","SUBMIT","SUBMIT","PARLIAMENT","REPLAY","OVERRIDE"],["Prepare settlement","NO","NO","NO","REVIEW","NO","AUTHORIZE"],["Promote memory","PROPOSE","CANDIDATE","EVIDENCE","RECOMMEND","PENDING","APPROVE"],["Move value","NO","NO","NO","NO","NO","EXTERNAL ONLY"]];matrix.innerHTML=rows.map((row,index)=>`<div class="sme-authority-row${index===0?" sme-authority-head":""}">${row.map((value,i)=>i===0?`<strong>${esc(value)}</strong>`:`<span class="sme-authority-value ${/YES|BOUNDED|PARLIAMENT|CANDIDATE|PENDING|APPROVE|AUTHORIZE|OVERRIDE|EXTERNAL/.test(value)?"review":"no"}">${esc(value)}</span>`).join("")}</div>`).join("");}
    const threats=$("#sme-threat-grid");if(threats)threats.innerHTML=data.threats.map(item=>`<article class="sme-threat-card"><small>${esc(item.id)} · ${esc(item.disposition)}</small><h3>${esc(item.title)}</h3><p>${esc(item.control)}</p></article>`).join("");
    const lineage=$("#sme-lineage-table");if(lineage)lineage.innerHTML=data.lineage_fingerprints.map((item,index)=>`<article class="sme-lineage-row"><span>${pad(index+1)}</span><strong>${esc(item.path)}</strong><code title="${esc(item.sha256)}">${esc(item.sha256)}</code><small>${Number(item.bytes).toLocaleString()} B</small></article>`).join("");
    if($("#sme-lineage-root"))$("#sme-lineage-root").textContent=`root ${data.lineage_root}`;if($("#sme-lineage-count"))$("#sme-lineage-count").textContent=`${data.lineage_fingerprints.length} fingerprints`;
  }

  function renderLedger() {
    const sample=data.sample_docket; const integrity=$("#sme-integrity-grid");if(integrity){const entries=[["HANDOFFS",sample.handoffs.length,"predecessor-linked"],["ARTIFACTS",sample.evidence.artifact_count,"16 Mind · 16 Node · 16 Market"],["DISSENT",sample.market.parliament.dissent,"preserved"],["CHAIN HEAD",sample.evidence.chain_head.slice(0,12)+"…","SHA-256"],["AUTHORITY",sample.authority.external_authority,"fail-closed"]];integrity.innerHTML=entries.map(([a,b,c])=>`<article class="sme-integrity-card"><small>${esc(a)}</small><strong>${esc(b)}</strong><span>${esc(c)}</span></article>`).join("");}
    const handoffs=$("#sme-ledger-handoffs");if(handoffs)handoffs.innerHTML=sample.handoffs.map(item=>`<article class="sme-ledger-handoff"><span>${esc(item.id)}</span><div><h3>${esc(item.name)}</h3><p>${esc(item.from)} → ${esc(item.to)} · ${esc(item.purpose)}</p></div><code title="${esc(item.commitment)}">${esc(item.commitment)}</code></article>`).join("");
    let plane="ALL",query=""; const ledger=$("#sme-artifact-ledger");
    const renderRows=()=>{const items=sample.evidence.artifacts.filter(item=>(plane==="ALL"||item.plane===plane)&&`${item.id} ${item.plane} ${item.name}`.toLowerCase().includes(query.toLowerCase()));ledger.innerHTML=items.map(item=>`<article class="sme-artifact-row"><span>${esc(item.id)}</span><small>${esc(item.plane)}</small><strong>${esc(item.name)}</strong><code title="${esc(item.commitment)}">${esc(item.commitment)}</code></article>`).join("");$("#sme-ledger-count").textContent=`${items.length} / ${sample.evidence.artifacts.length} artifacts`;};
    renderRows();$("#sme-ledger-search")?.addEventListener("input",event=>{query=event.target.value;renderRows();});$("#sme-ledger-filters")?.addEventListener("click",event=>{const button=event.target.closest("button[data-plane]");if(!button)return;plane=button.dataset.plane;$$("#sme-ledger-filters button").forEach(x=>x.classList.toggle("is-active",x===button));renderRows();});
    const json=$("#sme-sample-json");if(json)json.textContent=JSON.stringify(sample,null,2);$("#sme-copy-docket")?.addEventListener("click",async()=>{const text=JSON.stringify(sample,null,2);try{await navigator.clipboard.writeText(text);}catch{const area=doc.createElement("textarea");area.value=text;doc.body.append(area);area.select();doc.execCommand("copy");area.remove();}});
  }

  function renderMemory() {
    const steps=[["Proven Work","A complete evidence chain reaches human settlement review.","SOURCE · CHAIN ROOT"],["Candidate Extraction","Reusable structure is isolated without inheriting live authority.","SCOPE · EXCLUSIONS"],["Counterfactual Replay","The candidate is tested against a control and falsification criteria.","CONTROL · DELTA"],["Rights and Failure Memory","Dissent, incidents, externalities, and failure conditions travel with success.","DISSENT · RIGHTS"],["Human Tribunal","Reviewers approve, restrict, defer, or reject promotion conditions.","DECISION · EXPIRY"],["Return to Foundry","Approved memory becomes bounded input to future institution design.","REVOCABLE · TRACEABLE"]];
    const cycle=$("#sme-memory-cycle");if(cycle)cycle.innerHTML=steps.map(([title,detail,strong])=>`<article class="sme-memory-step"><h3>${esc(title)}</h3><p>${esc(detail)}</p><strong>${esc(strong)}</strong></article>`).join("");
    const rules=$("#sme-memory-rules");if(rules)rules.innerHTML=data.memory_rules.map((item,index)=>`<article class="sme-memory-rule"><span>${pad(index+1)}</span><p>${esc(item)}</p></article>`).join("");
    const questions=[["Evidence integrity","Does the candidate preserve its complete source evidence root?"],["Measured advantage","Did counterfactual replay demonstrate a bounded improvement?"],["Failure memory","Are incidents, dissent, rejected alternatives, and negative evidence preserved?"],["Scope control","Is the candidate restricted to a declared domain and task family?"],["Expiry","Does it expire automatically unless deliberately renewed?"],["Revocation","Can counterevidence or governance review revoke it immediately?"],["Rights and policy","Did guardian review find unresolved conflicts or externalities?"],["Authority separation","Does the candidate avoid inheriting execution or settlement authority?"],["Human decision","Has an accountable reviewer explicitly recorded promotion conditions?"]];const tribunal=$("#sme-tribunal");if(tribunal)tribunal.innerHTML=questions.map(([title,detail],index)=>`<article class="sme-tribunal-card"><small>QUESTION ${pad(index+1)}</small><h3>${esc(title)}</h3><p>${esc(detail)}</p></article>`).join("");
    const rollback=$("#sme-rollback-flow");if(rollback){const flow=[["01","TRIGGER","Counterevidence, expiry, incident, rights conflict, or human revocation."],["02","FREEZE","The candidate becomes unavailable to new institution formation."],["03","TRACE","Affected institutions, missions, and evidence roots are enumerated."],["04","REPLAY","Counterfactual and historical impact are re-evaluated."],["05","DECIDE","Human governance revokes, restricts, repairs, or renews."],["06","PRESERVE","The revocation remains permanent institutional memory."]];rollback.innerHTML=flow.map(([id,title,detail])=>`<article class="sme-rollback-step"><small>${id}</small><strong>${esc(title)}</strong><p>${esc(detail)}</p></article>`).join("");}
  }

  function renderUniverseCards(universes) {
    const colors=["rgba(232,205,119,.25)","rgba(121,240,218,.25)","rgba(155,132,255,.25)"];
    const grid=$("#sme-universe-grid");if(grid)grid.innerHTML=universes.map((u,index)=>`<article class="sme-universe-result" style="--universe-glow:${colors[index]}"><header><small>${esc(u.label.toUpperCase())}</small><code>${esc(u.economy_root.slice(0,10))}…</code></header><h3>${esc(u.institution)}</h3><dl><dt>Node route</dt><dd>${esc(u.route)}</dd><dt>Coalition</dt><dd>${esc(u.coalition)}</dd><dt>Parliament</dt><dd>${esc(u.parliament)}</dd><dt>Market frontier</dt><dd>${esc(u.frontier)} institutions</dd><dt>Terminal</dt><dd>${esc(u.terminal)}</dd><dt>Authority</dt><dd>${esc(u.authority)}</dd></dl><div class="sme-score-bars">${Object.entries(u.scores).map(([key,value])=>`<div class="sme-score-bar"><span>${esc(key)}</span><i style="--score:${value}%"></i><strong>${value}</strong></div>`).join("")}</div></article>`).join("");
    const table=$("#sme-comparison-table");if(table){const rows=[["Dimension",...universes.map(x=>x.label.replace(" Universe",""))],["Selected institution",...universes.map(x=>x.institution)],["Node route",...universes.map(x=>x.route)],["Coalition",...universes.map(x=>x.coalition)],["Evidence margin",...universes.map(x=>String(x.evidence_margin))],["Utility margin",...universes.map(x=>String(x.utility_margin))],["Economy root",...universes.map(x=>x.economy_root.slice(0,14)+"…")],["External authority",...universes.map(x=>x.authority)]];table.innerHTML=rows.map((row,index)=>`<div class="sme-comparison-row${index===0?" head":""}">${row.map(value=>`<span>${esc(value)}</span>`).join("")}</div>`).join("");}
  }

  function renderObservatory() {
    const preset=$("#sme-observatory-preset"),mission=$("#sme-observatory-mission"),risk=$("#sme-observatory-risk");preset.innerHTML=data.mission_presets.map(formOption).join("");risk.innerHTML=data.risk_profiles.map(formOption).join("");risk.value="high";const setPreset=()=>{mission.value=(data.mission_presets.find(x=>x.id===preset.value)||data.mission_presets[0]).mission;};preset.addEventListener("change",setPreset);setPreset();
    const runUniverses=()=>{const p=data.mission_presets.find(x=>x.id===preset.value)||data.mission_presets[0];const commission={mission:mission.value.trim(),preset:p,domain:p.domain,posture:data.postures[0],risk:data.risk_profiles.find(x=>x.id===risk.value)||data.risk_profiles[0],incident:data.incidents[0]};const universes=buildUniverses(commission);window.__SME_UNIVERSES__=universes;renderUniverseCards(universes);};$("#sme-run-universes").addEventListener("click",runUniverses);runUniverses();
    const invariant=$("#sme-invariant-grid");if(invariant){const cards=[["AUTHORITY","NONE_GRANTED","No posture grants execution, settlement, production, or external authority."],["DISSENT","PRESERVED","The independent dissent seat remains protected in every universe."],["CHALLENGE","OPEN","Rights, falsification, and appeal paths do not disappear under frontier posture."],["MEMORY","HUMAN_REQUIRED","No universe may automatically promote capability memory."]];invariant.innerHTML=cards.map(([a,b,c])=>`<article class="sme-invariant-card"><small>${a}</small><strong>${b}</strong><p>${c}</p></article>`).join("");}
  }

  function glyphBits(rootValue) { return rootValue.split("").flatMap(hex=>parseInt(hex,16).toString(2).padStart(4,"0").split("")); }

  function renderPassport(docket) {
    const rootValue=docket.economy_root||docket.evidence?.chain_head||"0".repeat(64); const glyph=$("#sme-passport-glyph");if(glyph)glyph.innerHTML=glyphBits(rootValue).map(bit=>`<i class="sme-passport-pixel${bit==="1"?" on":""}"></i>`).join("");
    if($("#sme-passport-root"))$("#sme-passport-root").textContent=rootValue;if($("#sme-passport-mission"))$("#sme-passport-mission").textContent=docket.mission?.mission||"Unnamed mission";if($("#sme-passport-state"))$("#sme-passport-state").textContent=docket.authority?.terminal_state||"UNKNOWN";
    const fields=[["RUN ID",docket.run_id],["ECONOMY ROOT",rootValue],["RUN COMMITMENT",docket.run_commitment],["EVIDENCE ROOT",docket.evidence?.chain_head],["HANDOFFS",String(docket.handoffs?.length||0)],["ARTIFACTS",String(docket.evidence?.artifact_count||0)],["EXTERNAL AUTHORITY",docket.authority?.external_authority],["PRODUCTION",docket.authority?.production_activation]];$("#sme-passport-fields").innerHTML=fields.map(([a,b])=>`<article class="sme-passport-field"><small>${esc(a)}</small>${String(b||"").length>28?`<code>${esc(b||"—")}</code>`:`<strong>${esc(b||"—")}</strong>`}</article>`).join("");
    const engines=[["MIND FOUNDRY",docket.institution?.name,`${docket.institution?.frontier_count||0}/${docket.institution?.candidate_count||0} frontier candidates · ${docket.institution?.roles?.length||0} roles`],["PROOF NODE",docket.node?.id,`${docket.node?.primary?.length||0} primary · ${docket.node?.shadow?.length||0} shadow · ${docket.node?.receipt_id||"—"}`],["WORK ECONOMY",docket.market?.coalition_id,`${docket.market?.parliament?.seats||0} seats · ${docket.market?.parliament?.dissent||0} dissent · ${docket.market?.settlement?.status||"—"}`]];$("#sme-passport-engines").innerHTML=engines.map(([a,b,c])=>`<article class="sme-passport-engine"><small>${esc(a)}</small><h3>${esc(b||"—")}</h3><p>${esc(c)}</p></article>`).join("");
    const review=docket.review||{status:"PENDING_HUMAN_REVIEW",record:null};$("#sme-passport-review").innerHTML=`<div><small>LOCAL REVIEW ARTIFACT</small><strong>${esc(review.status||"PENDING_HUMAN_REVIEW")}</strong></div><code>${esc(review.record||"—")}</code>`;
    const artifacts=docket.evidence?.artifacts||[];const picks=[artifacts[0],artifacts[15],artifacts[23],artifacts[31],artifacts.at(-1)].filter(Boolean);$("#sme-passport-chain").innerHTML=picks.map(item=>`<article class="sme-passport-chain-card"><small>${esc(item.id)} · ${esc(item.plane)}</small><strong>${esc(item.name)}</strong><code>${esc(item.commitment)}</code></article>`).join("");
    const interpretation=[["WHAT IT ESTABLISHES","The docket has an internally consistent mission identity, engine handoffs, evidence chain, review state, and authority boundary."],["WHAT IT DOES NOT ESTABLISH","It does not independently certify external facts, outcomes, scientific validity, legal compliance, production readiness, or authorization."],["WHAT MAY HAPPEN NEXT","Accountable humans may deliberate, request revision, open a dispute, reject the package, or separately authorize a bounded next step."],["WHAT CAN NEVER HAPPEN HERE","The browser experience cannot connect a wallet, move funds, call an external service, execute production work, or grant itself authority."]];$("#sme-passport-interpretation").innerHTML=interpretation.map(([a,b])=>`<article class="sme-interpretation-card"><small>${a}</small><h3>${a.split(" ").slice(1).join(" ")}</h3><p>${b}</p></article>`).join("");
  }

  function renderPassportPage() {
    const sample=deepClone(data.sample_docket);renderPassport(sample);$("#sme-passport-sample").addEventListener("click",()=>renderPassport(deepClone(sample)));$("#sme-passport-file").addEventListener("change",event=>{const file=event.target.files?.[0];if(!file)return;const reader=new FileReader();reader.addEventListener("load",()=>{try{const parsed=JSON.parse(String(reader.result||"{}"));if(parsed.schema!=="goalos.sovereign_machine_economy.docket.v2")throw new Error("Unsupported docket schema");renderPassport(parsed);}catch(error){console.error("Mission Passport could not open the selected docket",error);}});reader.readAsText(file);});
  }

  function activateReveals() {
    const nodes=$$(".sme-reveal");if(!("IntersectionObserver" in window)||reducedMotion){nodes.forEach(node=>node.classList.add("is-visible"));return;}const observer=new IntersectionObserver(entries=>entries.forEach(entry=>{if(entry.isIntersecting){entry.target.classList.add("is-visible");observer.unobserve(entry.target);}}),{threshold:.12});nodes.forEach(node=>observer.observe(node));
  }

  window.__SME_ENGINE__={stable,sha256,buildRun,buildUniverses,applyReviewAction};
  try {
    if(pageName==="experience")renderExperience();
    if(pageName==="architecture")renderArchitecture();
    if(pageName==="ledger")renderLedger();
    if(pageName==="memory")renderMemory();
    if(pageName==="observatory")renderObservatory();
    if(pageName==="passport")renderPassportPage();
    activateReveals(); root.dataset.smeReady="true";
  } catch(error) { root.dataset.smeReady="error"; console.error("Sovereign Machine Economy initialization failed",error); }
})();
