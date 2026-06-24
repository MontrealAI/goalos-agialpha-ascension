(() => {
  "use strict";
  const root = document.documentElement;
  const $ = (selector, scope = document) => scope.querySelector(selector);
  const $$ = (selector, scope = document) => [...scope.querySelectorAll(selector)];
  const dataNode = $("#sme-data");
  if (!dataNode) return;
  const DATA = JSON.parse(dataNode.textContent);
  const PAGE = root.dataset.smePage || "experience";
  const encoder = new TextEncoder();
  const reducedMotion = matchMedia("(prefers-reduced-motion: reduce)").matches;

  const escapeHTML = value => String(value).replace(/[&<>'"]/g, char => ({"&":"&amp;","<":"&lt;",">":"&gt;","'":"&#39;",'"':"&quot;"}[char]));
  const truncate = (value, length = 18) => String(value).length > length ? `${String(value).slice(0, length)}…` : String(value);
  const sleep = ms => new Promise(resolve => setTimeout(resolve, reducedMotion ? 0 : ms));
  const stable = value => {
    if (Array.isArray(value)) return `[${value.map(stable).join(",")}]`;
    if (value && typeof value === "object") return `{${Object.keys(value).sort().map(key => `${JSON.stringify(key)}:${stable(value[key])}`).join(",")}}`;
    return JSON.stringify(value);
  };
  function sha256Fallback(text) {
    const rightRotate = (value, amount) => (value >>> amount) | (value << (32 - amount));
    let mathPow = Math.pow, maxWord = mathPow(2, 32), lengthProperty = "length", i, j;
    let result = "", words = [], asciiBitLength = text[lengthProperty] * 8;
    let hash = sha256Fallback.h = sha256Fallback.h || [], k = sha256Fallback.k = sha256Fallback.k || [], primeCounter = k[lengthProperty];
    const isComposite = {};
    for (let candidate = 2; primeCounter < 64; candidate++) {
      if (!isComposite[candidate]) {
        for (i = 0; i < 313; i += candidate) isComposite[i] = candidate;
        hash[primeCounter] = (mathPow(candidate, .5) * maxWord) | 0;
        k[primeCounter++] = (mathPow(candidate, 1 / 3) * maxWord) | 0;
      }
    }
    text += "\x80"; while (text[lengthProperty] % 64 - 56) text += "\x00";
    for (i = 0; i < text[lengthProperty]; i++) { j = text.charCodeAt(i); if (j >> 8) throw new Error("SHA-256 fallback expects UTF-8 bytes"); words[i >> 2] |= j << ((3 - i) % 4) * 8; }
    words[words[lengthProperty]] = (asciiBitLength / maxWord) | 0; words[words[lengthProperty]] = asciiBitLength;
    for (j = 0; j < words[lengthProperty];) {
      const w = words.slice(j, j += 16), oldHash = hash.slice(0); hash = hash.slice(0, 8);
      for (i = 0; i < 64; i++) {
        const w15 = w[i - 15], w2 = w[i - 2], a = hash[0], e = hash[4];
        const temp1 = hash[7] + (rightRotate(e, 6) ^ rightRotate(e, 11) ^ rightRotate(e, 25)) + ((e & hash[5]) ^ ((~e) & hash[6])) + k[i] + (w[i] = i < 16 ? w[i] : (w[i - 16] + (rightRotate(w15, 7) ^ rightRotate(w15, 18) ^ (w15 >>> 3)) + w[i - 7] + (rightRotate(w2, 17) ^ rightRotate(w2, 19) ^ (w2 >>> 10))) | 0);
        const temp2 = (rightRotate(a, 2) ^ rightRotate(a, 13) ^ rightRotate(a, 22)) + ((a & hash[1]) ^ (a & hash[2]) ^ (hash[1] & hash[2]));
        hash = [(temp1 + temp2) | 0].concat(hash); hash[4] = (hash[4] + temp1) | 0; hash.pop();
      }
      for (i = 0; i < 8; i++) hash[i] = (hash[i] + oldHash[i]) | 0;
    }
    for (i = 0; i < 8; i++) for (j = 3; j + 1; j--) { const byte = (hash[i] >> (j * 8)) & 255; result += (byte < 16 ? "0" : "") + byte.toString(16); }
    return result;
  }
  async function sha256(value) {
    const text = typeof value === "string" ? value : stable(value);
    if (globalThis.crypto && globalThis.crypto.subtle) {
      const digest = await globalThis.crypto.subtle.digest("SHA-256", encoder.encode(text));
      return [...new Uint8Array(digest)].map(byte => byte.toString(16).padStart(2, "0")).join("");
    }
    const bytes = unescape(encodeURIComponent(text));
    return sha256Fallback(bytes);
  }
  const numberAt = (hex, index, min = 0, max = 1) => {
    const start = (index * 4) % Math.max(4, hex.length - 4);
    const value = parseInt(hex.slice(start, start + 4), 16) / 65535;
    return min + value * (max - min);
  };
  const score = value => Math.round(value * 1000) / 10;
  function download(filename, text, type) {
    const blob = new Blob([text], {type});
    const url = URL.createObjectURL(blob);
    const anchor = Object.assign(document.createElement("a"), {href: url, download: filename});
    document.body.append(anchor); anchor.click(); anchor.remove(); setTimeout(() => URL.revokeObjectURL(url), 1000);
  }

  function initNavigation() {
    const toggle = $(".sme-nav-toggle");
    const links = $("#sme-nav-links");
    if (!toggle || !links) return;
    toggle.addEventListener("click", () => {
      const open = !links.classList.contains("is-open");
      links.classList.toggle("is-open", open);
      toggle.setAttribute("aria-expanded", String(open));
    });
    links.addEventListener("click", event => { if (event.target.closest("a")) { links.classList.remove("is-open"); toggle.setAttribute("aria-expanded", "false"); } });
  }
  function initReveals() {
    const items = $$(".sme-reveal");
    if (!("IntersectionObserver" in window)) { items.forEach(item => item.classList.add("is-visible")); return; }
    const observer = new IntersectionObserver(entries => entries.forEach(entry => { if (entry.isIntersecting) { entry.target.classList.add("is-visible"); observer.unobserve(entry.target); } }), {threshold: .12});
    items.forEach(item => observer.observe(item));
  }

  function renderHeroMetrics() {
    const host = $("#sme-hero-metrics");
    if (!host) return;
    host.innerHTML = DATA.hero_metrics.map(metric => `<div class="sme-metric"><strong>${escapeHTML(metric.value)}</strong><span>${escapeHTML(metric.label)}</span></div>`).join("");
  }
  function renderGates() {
    const host = $("#sme-gates");
    if (!host) return;
    host.innerHTML = DATA.gates.map((gate, index) => `<article class="sme-gate" data-gate="${index}"><small><span>${escapeHTML(gate.id)}</span><b>${escapeHTML(gate.layer)}</b></small><strong>${escapeHTML(gate.name)}</strong><p>${escapeHTML(gate.description)}</p></article>`).join("");
  }
  function renderArtifactDots() {
    const host = $("#sme-artifact-river");
    if (!host) return;
    host.innerHTML = DATA.artifacts.map(item => `<div class="sme-artifact-dot" data-artifact="${escapeHTML(item.id)}" data-layer="${escapeHTML(item.layer)}" title="${escapeHTML(`${item.id} · ${item.name}`)}">${escapeHTML(item.id)}</div>`).join("");
  }
  function renderInitialEntities() {
    const meta = $("#sme-meta-candidates");
    if (meta) meta.innerHTML = DATA.meta.agents.slice(0, 9).map((agent, index) => `<div class="sme-candidate"><strong>${escapeHTML(agent.name)}</strong><span>AUTHORITY ${String(index + 1).padStart(2, "0")}</span></div>`).join("");
    const peer = $("#sme-peer-mesh");
    if (peer) peer.innerHTML = DATA.node.peers.map(item => `<div class="sme-peer" title="${escapeHTML(`${item.name} · ${item.role}`)}">${escapeHTML(item.name.slice(0, 2).toUpperCase())}</div>`).join("");
    const guild = $("#sme-guild-grid");
    if (guild) guild.innerHTML = DATA.jobs.institutions.map(item => `<div class="sme-guild"><strong>${escapeHTML(item.name)}</strong><span>${escapeHTML(item.guild)}</span></div>`).join("");
  }
  function populateForm() {
    const mission = $("#sme-mission"), preset = $("#sme-preset"), posture = $("#sme-posture"), risk = $("#sme-risk"), incidents = $("#sme-incident-options");
    if (!mission || !preset || !posture || !risk || !incidents) return;
    preset.innerHTML = DATA.presets.map(item => `<option value="${escapeHTML(item.id)}">${escapeHTML(item.name)}</option>`).join("");
    posture.innerHTML = DATA.postures.map(item => `<option value="${escapeHTML(item.id)}">${escapeHTML(item.name)}</option>`).join("");
    risk.innerHTML = DATA.risk_profiles.map(item => `<option value="${escapeHTML(item.id)}">${escapeHTML(item.name)} · ${item.validator_seats} validator seats</option>`).join("");
    incidents.innerHTML = DATA.incidents.map((item, index) => `<div class="sme-incident-option"><input type="radio" name="sme-incident" id="sme-incident-${escapeHTML(item.id)}" value="${escapeHTML(item.id)}" ${index === 0 ? "checked" : ""}><label for="sme-incident-${escapeHTML(item.id)}"><strong>${escapeHTML(item.name)}</strong><span>${escapeHTML(item.terminal)}</span></label></div>`).join("");
    mission.value = DATA.presets[0].mission;
    preset.addEventListener("change", () => { const selected = DATA.presets.find(item => item.id === preset.value); if (selected && selected.id !== "custom") mission.value = selected.mission; });
  }

  function candidateName(index) {
    const crowns = ["Aurelia", "Noetic", "Evidentiary", "Sovereign", "Helical", "Civic", "Luminous", "Recursive", "Frontier", "Concord", "Veridian", "Chronicle"];
    const forms = ["Institution", "Conclave", "Foundry", "Assembly", "Covenant", "Directorate"];
    return `${crowns[index % crowns.length]} ${forms[index % forms.length]}`;
  }
  function metaCandidates(seed, posture) {
    return Array.from({length: 12}, (_, index) => {
      const evidence = numberAt(seed, index + 1, .72, .99);
      const safety = numberAt(seed, index + 14, .72, .99);
      const capability = numberAt(seed, index + 28, .72, .99);
      const efficiency = numberAt(seed, index + 42, .62, .96);
      const novelty = numberAt(seed, index + 56, .55, .99);
      const postureBonus = posture === "evidence-first" ? evidence * .08 : posture === "safety-first" ? safety * .08 : posture === "frontier" ? novelty * .08 : 0;
      const composite = capability * .25 + evidence * .24 + safety * .22 + efficiency * .14 + novelty * .15 + postureBonus;
      return {id:`I${String(index + 1).padStart(2,"0")}`, name:candidateName(index), topology:DATA.meta.topologies[index % DATA.meta.topologies.length], evidence, safety, capability, efficiency, novelty, composite};
    }).sort((a,b) => b.composite - a.composite);
  }
  function peerRoute(seed, risk) {
    const riskBonus = {low:.03,medium:.015,high:0,critical:-.01}[risk] || 0;
    const peers = DATA.node.peers.map((peer, index) => {
      const perturb = numberAt(seed, 80 + index, -.025, .025);
      const routeScore = peer.base_reliability * .35 + peer.base_evidence * .31 + (1 - peer.base_latency / 200) * .18 + (1 - peer.base_energy) * .16 + perturb + riskBonus;
      return {...peer, routeScore};
    }).sort((a,b) => b.routeScore - a.routeScore);
    return {primary:peers.slice(0,4), shadow:peers.slice(4,7), reserve:peers.slice(7), route_id:`ROUTE-${seed.slice(0,12).toUpperCase()}`};
  }
  function paretoFrontier(items) {
    const dims = ["capability","evidence","reliability","efficiency","safety","originality"];
    return items.filter(candidate => !items.some(other => other !== candidate && dims.every(dim => other[dim] >= candidate[dim]) && dims.some(dim => other[dim] > candidate[dim])));
  }
  function jobsCoalition(seed, posture) {
    const institutions = DATA.jobs.institutions.map((item,index) => {
      const bump = numberAt(seed, 110 + index, -.018, .018);
      const composite = item.capability * .2 + item.evidence * .2 + item.reliability * .17 + item.safety * .17 + item.efficiency * .1 + item.originality * .1 + item.reputation * .06 + bump + (posture === "frontier" ? item.originality * .04 : 0);
      return {...item, composite};
    }).sort((a,b) => b.composite - a.composite);
    const frontier = paretoFrontier(institutions);
    const coalition = [];
    for (const candidate of [...frontier, ...institutions]) if (!coalition.some(item => item.id === candidate.id) && coalition.length < 5) coalition.push(candidate);
    return {institutions, frontier, coalition, coalition_id:`COUNCIL-${seed.slice(12,24).toUpperCase()}`};
  }
  async function artifactChain(context, maxArtifacts = DATA.artifacts.length) {
    const chain = [];
    let previous = "0".repeat(64);
    for (const template of DATA.artifacts.slice(0, maxArtifacts)) {
      const payload = {id:template.id, layer:template.layer, name:template.name, purpose:template.purpose, mission_commitment:context.mission_commitment, institution_id:context.institution.id, route_id:context.route.route_id, coalition_id:context.jobs.coalition_id, terminal:context.terminal};
      const commitment = await sha256({previous,payload});
      chain.push({...template, previous_commitment:previous, commitment, payload});
      previous = commitment;
    }
    return chain;
  }
  const incidentFailureGate = incident => ({"institution-divergence":3,"node-identity-drift":8,"evidence-gap":16,"budget-breach":17}[incident] ?? null);
  const artifactLimitForIncident = incident => ({"institution-divergence":8,"node-identity-drift":20,"evidence-gap":35,"budget-breach":36}[incident] ?? 36);

  async function constructState(input) {
    const seed = await sha256({mission:input.mission,posture:input.posture,risk:input.risk,incident:input.incident,release:DATA.release_id});
    const candidates = metaCandidates(seed, input.posture);
    const institution = candidates[0];
    const route = peerRoute(seed, input.risk);
    const jobs = jobsCoalition(seed, input.posture);
    const incident = DATA.incidents.find(item => item.id === input.incident) || DATA.incidents[0];
    const terminal = incident.terminal;
    const mission_commitment = await sha256({mission:input.mission,posture:input.posture,risk:input.risk});
    const institution_seal = await sha256({mission_commitment,institution,candidates:candidates.map(item => ({id:item.id,composite:item.composite}))});
    const node_receipt = `AWU-${seed.slice(24,40).toUpperCase()}`;
    const node_seal = await sha256({institution_seal,route:route.route_id,receipt:node_receipt,primary:route.primary.map(item => item.id),shadow:route.shadow.map(item => item.id)});
    const market_seal = await sha256({node_seal,coalition:jobs.coalition_id,frontier:jobs.frontier.map(item => item.id),terminal});
    const context = {mission_commitment,institution,route,jobs,terminal};
    const chain = await artifactChain(context, artifactLimitForIncident(input.incident));
    const riskProfile = DATA.risk_profiles.find(item => item.id === input.risk) || DATA.risk_profiles[1];
    const parliament = {seats:riskProfile.validator_seats, threshold:Math.ceil(riskProfile.validator_seats * .72), pass:terminal === "DISPUTE_OPEN" ? Math.max(1,riskProfile.validator_seats - 2) : Math.max(1,riskProfile.validator_seats - 1), dissent:1, reject:terminal === "DISPUTE_OPEN" ? 1 : 0, challenge_window:riskProfile.challenge};
    const docket = {
      schema:"goalos.sovereign_machine_economy.docket.v1",
      release_id:DATA.release_id,
      version:DATA.version,
      mission:{text:input.mission,posture:input.posture,risk:input.risk,incident:input.incident,commitment:mission_commitment},
      meta:{selected_institution:{id:institution.id,name:institution.name,topology:institution.topology,score:score(institution.composite)},candidate_count:candidates.length,pareto_review:"COMPLETE",constitution_seal:institution_seal},
      node:{route_id:route.route_id,primary:route.primary.map(item => item.id),shadow:route.shadow.map(item => item.id),work_unit_id:node_receipt,evidence_seal:node_seal},
      jobs:{coalition_id:jobs.coalition_id,coalition:jobs.coalition.map(item => item.id),pareto_frontier:jobs.frontier.map(item => item.id),parliament,market_seal},
      handoffs:[{id:"H01",from:"META",to:"NODE",commitment:institution_seal},{id:"H02",from:"NODE",to:"JOBS",commitment:node_seal},{id:"H03",from:"JOBS",to:"HUMAN",commitment:market_seal}],
      evidence:{artifact_count:chain.length,expected_artifact_count:36,chain_head:chain.at(-1)?.commitment || "0".repeat(64),artifacts:chain},
      authority:{terminal_state:terminal,external_authority:"NONE_GRANTED",factual_correctness:"NOT_CERTIFIED",production_activation:"NOT_ACTIVATED",user_fund_authorization:"NO",external_actions:0,network_requests:0,wallet_connections:0,live_token_movements:0,memory_promotion:"NOT_AUTHORIZED"}
    };
    docket.run_commitment = await sha256(docket);
    return {seed,input,candidates,institution,route,jobs,parliament,chain,docket,terminal,institution_seal,node_seal,market_seal,logs:[]};
  }

  function renderMeta(state) {
    $("#sme-meta-selected").textContent = state.institution.name;
    $("#sme-meta-score").textContent = `COMPOSITE ${score(state.institution.composite)} · ${state.institution.topology}`;
    $("#sme-meta-candidates").innerHTML = state.candidates.map(item => `<div class="sme-candidate ${item.id === state.institution.id ? "is-selected" : ""}"><strong>${escapeHTML(item.name)}</strong><span>${score(item.composite)} · ${escapeHTML(item.topology)}</span></div>`).join("");
  }
  function renderNode(state) {
    $("#sme-node-route").textContent = state.route.primary.map(item => item.name).join(" · ");
    $("#sme-node-receipt").textContent = state.docket.node.work_unit_id;
    const primary = new Set(state.route.primary.map(item => item.id));
    const shadow = new Set(state.route.shadow.map(item => item.id));
    $("#sme-peer-mesh").innerHTML = DATA.node.peers.map(item => `<div class="sme-peer ${primary.has(item.id) ? "primary" : shadow.has(item.id) ? "shadow" : ""}" title="${escapeHTML(`${item.name} · ${item.role}`)}">${escapeHTML(item.name.slice(0,2).toUpperCase())}</div>`).join("");
  }
  function renderJobs(state) {
    $("#sme-jobs-coalition").textContent = state.jobs.coalition.map(item => item.name).join(" · ");
    $("#sme-jobs-parliament").textContent = `${state.parliament.seats}-SEAT PARLIAMENT · ${state.parliament.dissent} DISSENT`;
    const selected = new Set(state.jobs.coalition.map(item => item.id));
    $("#sme-guild-grid").innerHTML = state.jobs.institutions.map(item => `<div class="sme-guild ${selected.has(item.id) ? "is-selected" : ""}"><strong>${escapeHTML(item.name)}</strong><span>${score(item.composite)} · ${escapeHTML(item.guild)}</span></div>`).join("");
  }
  function renderState(state) {
    $("#sme-state-label").textContent = state.terminal;
    $("#sme-state-label").style.color = state.terminal === "HUMAN_SETTLEMENT_REVIEW" ? "var(--sme-mint)" : state.terminal === "SAFE_HOLD" ? "#ff9ab7" : "var(--sme-gold-2)";
    $("#sme-state-symbol").textContent = state.terminal === "SAFE_HOLD" ? "HOLD" : state.terminal === "DISPUTE_OPEN" ? "Δ" : "αΩ";
    $("#sme-run-commitment").textContent = state.docket.run_commitment;
    $("#sme-selected-institution").textContent = state.institution.name;
    $("#sme-route-id").textContent = state.route.route_id;
    $("#sme-coalition-id").textContent = state.jobs.coalition_id;
    const copy = {HUMAN_SETTLEMENT_REVIEW:"The complete economy has prepared a review-ready proof and settlement package. Human authority remains required.",HUMAN_REVIEW_REQUIRED:"The declared budget boundary requires explicit human reconsideration before progression.",DISPUTE_OPEN:"A consequential evidence gap has preserved dissent and opened the challenge process.",SAFE_HOLD:"A constitutional integrity failure has stopped the economy while preserving the available evidence."}[state.terminal];
    $("#sme-state-copy").textContent = copy;
    $("#sme-handoff-one").textContent = state.institution_seal;
    $("#sme-handoff-two").textContent = state.node_seal;
    $("#sme-handoff-three").textContent = state.market_seal;
    $("#sme-artifact-count").textContent = `${state.chain.length} / 36`;
    $("#sme-chain-head").textContent = state.chain.at(-1)?.commitment || "UNSEALED";
    $$(".sme-artifact-dot").forEach((dot,index) => dot.classList.toggle("is-sealed", index < state.chain.length));
    renderMeta(state); renderNode(state); renderJobs(state);
  }
  async function animateGates(state) {
    const gates = $$(".sme-gate");
    gates.forEach(gate => gate.classList.remove("is-active","is-complete","is-failed"));
    const failure = incidentFailureGate(state.input.incident);
    for (let index = 0; index < gates.length; index++) {
      const gate = gates[index];
      gate.classList.add("is-active");
      $("#sme-live-gate").textContent = `${DATA.gates[index].id} · ${DATA.gates[index].name}`;
      $("#sme-live-description").textContent = DATA.gates[index].description;
      await sleep(90);
      gate.classList.remove("is-active");
      if (failure === index) { gate.classList.add("is-failed"); break; }
      gate.classList.add("is-complete");
    }
  }
  function executiveBrief(state) {
    return `# GoalOS Sovereign Machine Economy — Executive Review Brief\n\n**Run commitment:** \`${state.docket.run_commitment}\`\n**Terminal state:** \`${state.terminal}\`\n**External authority:** \`NONE_GRANTED\`\n\n## Mission\n\n${state.input.mission}\n\n## Institution\n\n- Selected: **${state.institution.name}**\n- Topology: **${state.institution.topology}**\n- Composite score: **${score(state.institution.composite)}**\n\n## Sovereign node\n\n- Route: **${state.route.route_id}**\n- Primary peers: ${state.route.primary.map(item => item.name).join(", ")}\n- Work unit: **${state.docket.node.work_unit_id}**\n\n## Work market\n\n- Council: **${state.jobs.coalition_id}**\n- Coalition: ${state.jobs.coalition.map(item => item.name).join(", ")}\n- Parliament: ${state.parliament.seats} seats; ${state.parliament.dissent} preserved dissent\n\n## Proof Chronicle\n\n- Sealed artifacts: **${state.chain.length} / 36**\n- Chain head: \`${state.docket.evidence.chain_head}\`\n\n## Authority boundary\n\nNo external action, network request, wallet connection, live value movement, production activation, user-fund authorization, or autonomous capability-memory promotion occurred.\n`;
  }

  function initExperience() {
    renderHeroMetrics(); renderGates(); renderArtifactDots(); renderInitialEntities(); populateForm();
    const form = $("#sme-economy-form");
    if (!form) return;
    let current = null;
    const run = async event => {
      event?.preventDefault();
      const button = $("#sme-run"); button.disabled = true; button.textContent = "Constituting the economy…";
      const input = {mission:$("#sme-mission").value.trim(),posture:$("#sme-posture").value,risk:$("#sme-risk").value,incident:$("input[name='sme-incident']:checked").value};
      current = await constructState(input);
      window.__SME_STATE__ = current;
      await animateGates(current);
      renderState(current);
      $("#sme-download-json").disabled = false; $("#sme-download-md").disabled = false;
      button.disabled = false; button.textContent = "Run the Sovereign Economy";
    };
    form.addEventListener("submit", run);
    $("#sme-reset").addEventListener("click", () => { form.reset(); $("#sme-mission").value = DATA.presets[0].mission; $("#sme-state-label").textContent="READY"; $("#sme-run-commitment").textContent="Awaiting mission"; $("#sme-selected-institution").textContent="Not selected"; $("#sme-route-id").textContent="Not formed"; $("#sme-coalition-id").textContent="Not formed"; $("#sme-state-copy").textContent="The constitutional economy is ready to receive a bounded mission."; $("#sme-handoff-one").textContent="awaiting-foundry-seal"; $("#sme-handoff-two").textContent="awaiting-node-seal"; $("#sme-handoff-three").textContent="awaiting-review-seal"; $("#sme-artifact-count").textContent="0 / 36"; $("#sme-chain-head").textContent="Awaiting run"; $$(".sme-gate").forEach(g => g.className="sme-gate"); $$(".sme-artifact-dot").forEach(d => d.classList.remove("is-sealed")); renderInitialEntities(); $("#sme-download-json").disabled=true; $("#sme-download-md").disabled=true; current=null; window.__SME_STATE__={running:false,terminal:"READY"}; });
    $("#sme-download-json").addEventListener("click", () => current && download(`sovereign-machine-economy-${current.docket.run_commitment.slice(0,12)}.json`,JSON.stringify(current.docket,null,2)+"\n","application/json"));
    $("#sme-download-md").addEventListener("click", () => current && download(`sovereign-machine-economy-${current.docket.run_commitment.slice(0,12)}.md`,executiveBrief(current),"text/markdown"));
    window.__SME_STATE__ = {running:false,terminal:"READY"};
  }

  function initArchitecture() {
    const stack = $("#sme-architecture-stack");
    if (stack) stack.innerHTML = [
      {rank:"SOVEREIGNTY I",title:"META‑AGENTIC Institution Foundry",text:"Creates, mutates, evaluates, and constitutionally selects specialized agent institutions.",items:["Proposal and mutation","Pareto selection","Verifier design","No external authority"]},
      {rank:"SOVEREIGNTY II",title:"AGI Alpha Sovereign Node",text:"Executes bounded work through declared primary and shadow routes and seals a proof-carrying receipt.",items:["Identity commitment","Resource envelope","Execution trace","Fail-closed guardians"]},
      {rank:"SOVEREIGNTY III",title:"AGI Jobs Work Civilization",text:"Coordinates guild competition, coalition formation, proof parliament, challenge rights, and settlement review.",items:["Rights ledger","Pareto market","Proof parliament","Settlement review only"]},
      {rank:"ULTIMATE AUTHORITY",title:"Human Constitutional Boundary",text:"Accepts, rejects, revises, authorizes, pauses, disputes, or revokes. No machine layer may impersonate this authority.",items:["Final reliance","Value movement","Capability memory","Revocation"]}
    ].map(item => `<article class="sme-stack-layer"><span>${item.rank}</span><div><h3>${item.title}</h3><p>${item.text}</p></div><ul>${item.items.map(x=>`<li>${x}</li>`).join("")}</ul></article>`).join("");
    const protocol = $("#sme-handoff-protocol");
    if (protocol) protocol.innerHTML = DATA.handoff_rules.map((text,index)=>`<article class="sme-protocol-step"><span>${String(index+1).padStart(2,"0")}</span><h3>${["Declare","Commit","Transmit","Verify","Challenge","Accept or hold"][index]}</h3><p>${escapeHTML(text)}</p></article>`).join("");
    const guardians = $("#sme-guardian-grid");
    if (guardians) guardians.innerHTML = DATA.guardians.map((item,index)=>`<article class="sme-guardian-card"><span>${index+1}</span><h3>${escapeHTML(item.name)}</h3><p>${escapeHTML(item.scope)}</p></article>`).join("");
    const lineage = $("#sme-lineage-grid");
    if (lineage) lineage.innerHTML = DATA.companions.map(item=>`<article class="sme-lineage-card"><small>${escapeHTML(item.layer)} · ${escapeHTML(item.version)}</small><h3>${escapeHTML(item.release_title)}</h3><code>${escapeHTML(item.manifest_sha256)}</code><a href="${escapeHTML(item.primary_page)}">Open flagship →</a></article>`).join("");
  }

  function initChronicle() {
    const docket = DATA.sample_docket;
    const ledger = $("#sme-ledger");
    if (!ledger) return;
    const render = () => {
      const term = ($("#sme-ledger-search")?.value || "").trim().toLowerCase();
      const active = $("#sme-ledger-filters button.active")?.dataset.layer || "ALL";
      const items = docket.evidence.artifacts.filter(item => (active === "ALL" || item.layer === active) && `${item.id} ${item.layer} ${item.name} ${item.purpose}`.toLowerCase().includes(term));
      ledger.innerHTML = items.map(item=>`<article class="sme-ledger-row"><span>${escapeHTML(item.id)}</span><span class="sme-ledger-layer">${escapeHTML(item.layer)}</span><div><strong>${escapeHTML(item.name)}</strong><small>${escapeHTML(item.purpose)}</small></div><code>${escapeHTML(item.commitment)}</code></article>`).join("");
      $("#sme-ledger-count").textContent = `${items.length} / 36 artifacts`;
    };
    $("#sme-ledger-search").addEventListener("input",render);
    $("#sme-ledger-filters").addEventListener("click",event=>{const button=event.target.closest("button");if(!button)return; $$("button",event.currentTarget).forEach(b=>b.classList.toggle("active",b===button));render();});
    render();
    $("#sme-chronicle-handoffs").innerHTML = docket.handoffs.map(item=>`<article><small>${escapeHTML(item.id)} · ${escapeHTML(item.from)} → ${escapeHTML(item.to)}</small><code>${escapeHTML(item.commitment)}</code><p>The receiving authority verifies this commitment before admitting the next layer.</p></article>`).join("");
    $("#sme-sample-json").textContent = JSON.stringify(docket,null,2);
    const copy = $("#sme-copy-sample"); if(copy) copy.addEventListener("click",async()=>{await navigator.clipboard.writeText(docket.run_commitment);copy.textContent="Copied";setTimeout(()=>copy.textContent="Copy run commitment",1200);});
  }

  function initAtlas() {
    const host=$("#sme-atlas-map"),controls=$("#sme-atlas-controls"); if(!host||!controls)return;
    const collections={META:DATA.meta.agents.map(item=>({name:item.name,sub:item.rank,detail:item.mandate})),NODE:DATA.node.peers.map(item=>({name:item.name,sub:`${item.role} · ${item.region}`,detail:item.capabilities.join(", ")})),JOBS:DATA.jobs.institutions.map(item=>({name:item.name,sub:`${item.guild} · ${item.region}`,detail:item.doctrine}))};
    const render=layer=>{const layers=layer==="ALL"?["META","NODE","JOBS"]:[layer];host.innerHTML=layers.map(name=>`<section class="sme-atlas-column" data-atlas-column="${name}"><header><strong>${name==="META"?"META‑AGENTIC Authorities":name==="NODE"?"Sovereign Peer Nodes":"Agent Work Guilds"}</strong><span>${collections[name].length} ENTITIES</span></header>${collections[name].map(item=>`<article class="sme-atlas-entity"><strong>${escapeHTML(item.name)}</strong><span>${escapeHTML(item.sub)}</span><p>${escapeHTML(truncate(item.detail,150))}</p></article>`).join("")}</section>`).join("");};
    controls.addEventListener("click",event=>{const button=event.target.closest("button");if(!button)return;$$("button",controls).forEach(b=>b.classList.toggle("active",b===button));render(button.dataset.atlasLayer);});render("ALL");
    const launches=$("#sme-launch-grid"); if(launches) launches.innerHTML=DATA.launch_surfaces.map(item=>`<a class="sme-launch-card" href="${escapeHTML(item.href)}"><small>${escapeHTML(item.layer)}</small><strong>${escapeHTML(item.title)}</strong><p>${escapeHTML(item.description)}</p></a>`).join("");
  }

  initNavigation(); initReveals();
  if (PAGE === "experience") initExperience();
  if (PAGE === "architecture") initArchitecture();
  if (PAGE === "chronicle") initChronicle();
  if (PAGE === "atlas") initAtlas();
  root.dataset.smeReady = "true";
})();
