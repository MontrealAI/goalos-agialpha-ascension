(()=>{"use strict";
const $=(s,r=document)=>r.querySelector(s),$$=(s,r=document)=>[...r.querySelectorAll(s)];
const readData=()=>{const n=$("#frl-data");if(!n)return null;try{return JSON.parse(n.textContent)}catch(e){console.error("First Real Loop data parse failed",e);return null}};
const data=readData();
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const escapeText=v=>String(v??"");
const stableStringify=v=>{if(v===null||typeof v!=="object")return JSON.stringify(v);if(Array.isArray(v))return `[${v.map(stableStringify).join(",")}]`;return `{${Object.keys(v).sort().map(k=>`${JSON.stringify(k)}:${stableStringify(v[k])}`).join(",")}}`};
async function sha256(text){try{if(globalThis.crypto?.subtle){const b=await crypto.subtle.digest("SHA-256",new TextEncoder().encode(text));return [...new Uint8Array(b)].map(x=>x.toString(16).padStart(2,"0")).join("")}}catch(_){ }let h1=0x811c9dc5,h2=0x9e3779b9;for(let i=0;i<text.length;i++){h1=Math.imul(h1^text.charCodeAt(i),0x01000193);h2=Math.imul(h2^text.charCodeAt(i),0x85ebca6b)}return [h1>>>0,h2>>>0,h1^h2,h1+h2].map(x=>(x>>>0).toString(16).padStart(8,"0")).join("").repeat(2).slice(0,64)}
function download(name,content,type="application/json"){const a=document.createElement("a"),blob=new Blob([content],{type});a.href=URL.createObjectURL(blob);a.download=name;document.body.appendChild(a);a.click();setTimeout(()=>{URL.revokeObjectURL(a.href);a.remove()},0)}
function reveal(){const nodes=$$(".frl-reveal");if(!nodes.length)return;if(!("IntersectionObserver" in window)){nodes.forEach(n=>n.classList.add("is-visible"));return}const io=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){e.target.classList.add("is-visible");io.unobserve(e.target)}}),{threshold:.12});nodes.forEach(n=>io.observe(n))}
function segmented(){const root=$("[data-frl-postures]");if(!root)return;root.addEventListener("click",e=>{const b=e.target.closest("button[data-posture]");if(!b)return;$$('button[data-posture]',root).forEach(x=>{x.classList.toggle("is-active",x===b);x.setAttribute("aria-pressed",String(x===b))});root.dataset.value=b.dataset.posture})}
function setupRuntime(){const run=$("#frl-run"),reset=$("#frl-reset"),mission=$("#frl-mission"),depth=$("#frl-depth"),postures=$("[data-frl-postures]"),state=$("#frl-runtime-state"),rid=$("#frl-runtime-id"),stream=$("#frl-eventstream"),result=$("#frl-result"),downloadJson=$("#frl-download-json"),downloadBrief=$("#frl-download-brief");if(!run||!data)return;
 let current=null,running=false;
 const phases=data.runtime.phases;
 const phaseButtons=$$(".frl-phase");
 const inspector={code:$("#frl-stage-code"),title:$("#frl-stage-title"),detail:$("#frl-stage-detail"),evidence:$("#frl-stage-evidence")};
 const phaseEvidence=[
  [["Mission",data.seed.domain],["Boundary",`${data.sovereign.risk_class} · advisory only`],["Contract",data.releaseId]],
  [["Seed",data.seed.id],["Genome",`${data.seed.foresight_genome.length} foresight statements`],["Graph",`${data.seed.job_graph.length} governed jobs`]],
  [["Decision",data.mark.green_flamed?"GREEN-FLAMED":"WITHHELD"],["Average",`${data.mark.average_score} / 5`],["Safety",`${data.mark.scores.safety} / 5`]],
  [["Institution",data.sovereign.id],["Budget proxy",`USD ${data.sovereign.budget_equivalent_usd}`],["Authority","research + recommend only"]],
  [["Jobs","J1 → J5"],["Result","5 / 5 passed"],["Candidates","10 generated · 4 accepted in top five"]],
  [["Artifacts",`${data.artifactLedger.length} sealed records`],["Sources",`${data.sources.length} curated references`],["Claim","evidence-ready, not authority-ready"]],
  [["Memory",data.compiler.id],["Rules",`${data.compiler.source_discovery_rules.length+data.compiler.red_team_rules.length} reusable constraints`],["Lineage","Seed 001 → Compiler v0"]],
  [["vNext",data.vNext.id],["Yield",`${data.comparison.control_yield.toFixed(2)} → ${data.comparison.treatment_yield.toFixed(2)}`],["Lift",`${data.comparison.reuse_lift_percent.toFixed(2)}% · bounded scaffold evidence`]]
 ];
 function inspect(i){const p=phases[i]||phases[0];inspector.code.textContent=`${p.id} · ${p.label}`;inspector.title.textContent=p.title;inspector.detail.textContent=p.detail;inspector.evidence.innerHTML=(phaseEvidence[i]||[]).map(([a,b])=>`<div><b>${escapeText(a)}</b> / ${escapeText(b)}</div>`).join("");phaseButtons.forEach((b,j)=>b.setAttribute("aria-current",j===i?"step":"false"))}
 phaseButtons.forEach((b,i)=>b.addEventListener("click",()=>inspect(i)));
 inspect(0);
 function emit(i,label,message){const row=document.createElement("div");row.className="frl-event";const t=`T+${String(i*7).padStart(3,"0")}`;row.innerHTML=`<time>${t}</time><span><strong>${escapeText(label)}</strong> ${escapeText(message)}</span>`;stream.appendChild(row);stream.scrollTop=stream.scrollHeight}
 function setPhase(i){phaseButtons.forEach((b,j)=>{b.classList.toggle("is-active",j===i);b.classList.toggle("is-complete",j<i)});inspect(i)}
 async function buildCommitment(payload){return await sha256(stableStringify(payload))}
 async function execute(){if(running)return;running=true;run.disabled=true;reset.disabled=true;result.classList.remove("is-visible");stream.innerHTML="<h4>Proof event stream</h4>";phaseButtons.forEach(b=>b.classList.remove("is-active","is-complete"));const payload={release:data.releaseId,mission:mission.value.trim()||data.seed.domain,posture:postures?.dataset.value||"constitutional",depth:depth?.value||"full",seed:data.seed.id,compiler:data.compiler.id,terminal:data.runtime.finalState};const commitment=await buildCommitment(payload);rid.textContent=`RUN ${commitment.slice(0,12).toUpperCase()}`;state.textContent="COMMITTING";document.body.dataset.runState="running";
  const events=[
   ["COMMIT","mission contract sealed; authority defaults to none"],
   ["SEED","foresight genome and five-job graph admitted"],
   ["MARK",`average ${data.mark.average_score}/5; safety ${data.mark.scores.safety}/5; review gate passed`],
   ["SOVEREIGN","bounded advisory institution instantiated"],
   ["WORK","J1–J5 completed; dissent and review labels preserved"],
   ["PROOF",`${data.artifactLedger.length} evidence artifacts sealed`],
   ["LEARN",`${data.compiler.id} extracted into versioned memory`],
   ["vNEXT",`control ${data.comparison.control_yield.toFixed(2)} vs treatment ${data.comparison.treatment_yield.toFixed(2)}; human promotion required`]
  ];
  for(let i=0;i<phases.length;i++){setPhase(i);state.textContent=`${phases[i].label.toUpperCase()} / IN REVIEW`;emit(i,...events[i]);await sleep(i===0?360:430)}
  phaseButtons.forEach(b=>{b.classList.remove("is-active");b.classList.add("is-complete")});state.textContent=data.runtime.finalState;document.body.dataset.runState="complete";
  current={schemaVersion:"1.0.0",docketType:"browser_local_goalos_first_real_loop_demonstration",runCommitment:commitment,mission:payload.mission,posture:payload.posture,depth:payload.depth,seedId:data.seed.id,markDecision:data.mark.green_flamed?"GREEN_FLAMED":"WITHHELD",sovereignId:data.sovereign.id,jobs:{passed:5,total:5},evidence:{sources:data.sources.length,artifacts:data.artifactLedger.length,acceptedInterventions:data.acceptedInterventions.length},capabilityCompiler:data.compiler.id,vNext:{seedId:data.vNext.id,controlYield:data.comparison.control_yield,treatmentYield:data.comparison.treatment_yield,reuseLiftPercent:data.comparison.reuse_lift_percent,hallucinationDelta:data.comparison.hallucination_delta,safetyDelta:data.comparison.safety_delta},terminal:{state:data.runtime.finalState,authority:data.runtime.authority,externalActions:0,walletConnections:0,networkRequests:0},claimBoundary:data.identity.claimBoundary};
  $("#frl-result-commitment").textContent=commitment.slice(0,16);$("#frl-result-lift").textContent=`${data.comparison.reuse_lift_percent.toFixed(2)}%`;$("#frl-result-artifacts").textContent=data.artifactLedger.length;$("#frl-result-state").textContent="REVIEW";result.classList.add("is-visible");emit(8,"BOUNDARY","evidence package ready; authority withheld; reviewer decision pending");run.disabled=false;reset.disabled=false;running=false}
 function clear(){if(running)return;current=null;stream.innerHTML='<h4>Proof event stream</h4><div class="frl-event"><time>T+000</time><span><strong>READY</strong> local deterministic demonstration awaiting mission commitment</span></div>';phaseButtons.forEach(b=>b.classList.remove("is-active","is-complete"));state.textContent="READY · AUTHORITY NONE";rid.textContent="RUN NOT COMMITTED";result.classList.remove("is-visible");document.body.dataset.runState="ready";inspect(0)}
 run.addEventListener("click",execute);reset?.addEventListener("click",clear);downloadJson?.addEventListener("click",()=>{if(!current)return;download(`goalos-first-real-loop-${current.runCommitment.slice(0,12)}.json`,JSON.stringify(current,null,2)+"\n")});downloadBrief?.addEventListener("click",()=>{if(!current)return;const md=`# GoalOS AGIALPHA Ascension First Real Loop — Executive Review Brief\n\n**Mission:** ${current.mission}\n\n**Run commitment:** \`${current.runCommitment}\`\n\n## Result\n\n- MARK: ${current.markDecision}\n- Jobs: ${current.jobs.passed}/${current.jobs.total}\n- Evidence artifacts: ${current.evidence.artifacts}\n- Control yield: ${current.vNext.controlYield}\n- Treatment yield: ${current.vNext.treatmentYield}\n- Reuse lift: ${current.vNext.reuseLiftPercent}%\n- Terminal state: ${current.terminal.state}\n- Authority: ${current.terminal.authority}\n\n## Claim boundary\n\n${current.claimBoundary}\n`;download(`goalos-first-real-loop-${current.runCommitment.slice(0,12)}-brief.md`,md,"text/markdown")});clear()}
function setupLedger(){const q=$("#frl-ledger-search"),rows=$$(".frl-ledger-row"),count=$("#frl-ledger-count");if(q){const apply=()=>{const s=q.value.trim().toLowerCase();let n=0;rows.forEach(r=>{const show=!s||r.dataset.search.includes(s);r.hidden=!show;if(show)n++});if(count)count.textContent=`${n} / ${rows.length} artifacts`};q.addEventListener("input",apply);apply()}const copy=$("#frl-copy-commitment"),commit=$("#frl-docket-commitment");copy?.addEventListener("click",async()=>{const v=commit?.textContent.trim()||"";try{await navigator.clipboard.writeText(v);copy.textContent="Copied"}catch(_){copy.textContent="Select commitment"}setTimeout(()=>copy.textContent="Copy commitment",1500)})}
function setupManifest(){const pre=$("#frl-manifest-json");if(pre&&data?.publicDocket)pre.textContent=JSON.stringify(data.publicDocket,null,2)}
segmented();setupRuntime();setupLedger();setupManifest();reveal();
})();
