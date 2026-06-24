(() => {
  'use strict';
  const doc = document;
  const dataNode = doc.getElementById('aan-release-data');
  if (!dataNode) return;
  let release;
  try { release = JSON.parse(dataNode.textContent || '{}'); }
  catch (error) { console.error('AGI Alpha Node release contract could not be parsed.', error); return; }

  const byId = (id) => doc.getElementById(id);
  const el = (tag, className = '', text) => { const node = doc.createElement(tag); if (className) node.className = className; if (text !== undefined) node.textContent = String(text); return node; };
  const svg = (tag, attrs = {}) => { const node = doc.createElementNS('http://www.w3.org/2000/svg', tag); Object.entries(attrs).forEach(([k, v]) => node.setAttribute(k, String(v))); return node; };
  const clear = (node) => node && node.replaceChildren();
  const clamp = (v, min, max) => Math.min(max, Math.max(min, v));
  const round = (v, digits = 2) => Number(Number(v).toFixed(digits));
  const pad = (v) => String(v).padStart(2, '0');
  const safe = (v, fallback = '') => String(v ?? fallback).trim();
  const sleep = (ms) => new Promise((resolve) => window.setTimeout(resolve, ms));
  const deepClone = (value) => JSON.parse(JSON.stringify(value));

  function stableStringify(value) {
    if (value === null || typeof value !== 'object') return JSON.stringify(value);
    if (Array.isArray(value)) return `[${value.map(stableStringify).join(',')}]`;
    return `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${stableStringify(value[key])}`).join(',')}}`;
  }
  function hashString(value) {
    let hash = 2166136261;
    const text = String(value);
    for (let i = 0; i < text.length; i += 1) { hash ^= text.charCodeAt(i); hash = Math.imul(hash, 16777619); }
    return hash >>> 0;
  }
  function mulberry32(seed) {
    let state = seed >>> 0;
    return () => { state += 0x6D2B79F5; let t = state; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
  }
  function fallbackHash(value) {
    const text = String(value); let out = ''; let seed = hashString(text);
    for (let i = 0; out.length < 64; i += 1) { seed = hashString(`${seed}:${i}:${text}`); out += seed.toString(16).padStart(8, '0'); }
    return out.slice(0, 64);
  }
  async function sha256(value) {
    const text = String(value);
    if (window.crypto && window.crypto.subtle && window.TextEncoder) {
      const bytes = new TextEncoder().encode(text);
      const digest = await window.crypto.subtle.digest('SHA-256', bytes);
      return Array.from(new Uint8Array(digest), (b) => b.toString(16).padStart(2, '0')).join('');
    }
    return fallbackHash(text);
  }
  function deterministicTimestamp(seed, step = 0) {
    const base = Date.UTC(2026, 5, 23, 12, 0, 0);
    return new Date(base + ((seed % 10000000) + step * 1379) * 10).toISOString();
  }
  function append(parent, tag, className, text) { const node = el(tag, className, text); parent.appendChild(node); return node; }
  function option(value, label) { const node = el('option', '', label); node.value = value; return node; }
  function formatPct(value) { return `${Math.round(value * 100)}%`; }
  function shortHash(value, size = 12) { return value ? `${String(value).slice(0, size)}…` : '—'; }

  function setupNavigation() {
    const toggle = byId('aan-nav-toggle'); const nav = byId('aan-nav');
    if (!toggle || !nav) return;
    toggle.addEventListener('click', () => { const open = nav.classList.toggle('is-open'); toggle.setAttribute('aria-expanded', String(open)); });
    nav.querySelectorAll('a').forEach((link) => link.addEventListener('click', () => { nav.classList.remove('is-open'); toggle.setAttribute('aria-expanded', 'false'); }));
  }
  function renderHeroMetrics() {
    const target = byId('aan-hero-metrics'); if (!target) return;
    clear(target); release.hero_metrics.forEach((metric) => { const block = el('div'); append(block, 'b', '', metric.value); append(block, 'span', '', metric.label); target.appendChild(block); });
  }
  function setupDialogs() {
    const tour = byId('aan-tour-dialog'); const tourOpen = byId('aan-tour-open'); const help = byId('aan-help-dialog');
    if (tour && tourOpen) tourOpen.addEventListener('click', () => tour.showModal ? tour.showModal() : tour.setAttribute('open', ''));
    doc.querySelectorAll('.aan-dialog-close').forEach((button) => button.addEventListener('click', () => button.closest('dialog')?.close()));
    doc.addEventListener('keydown', (event) => {
      const target = event.target;
      const typing = target && ['INPUT', 'TEXTAREA', 'SELECT'].includes(target.tagName);
      if (typing) return;
      if (event.key === '?' && help) { event.preventDefault(); help.showModal ? help.showModal() : help.setAttribute('open', ''); }
    });
  }

  const runtime = {
    token: 0, running: false, held: false, phase: -1, config: null, seed: 0, rng: null,
    candidates: [], route: null, receipt: null, evaluation: null, consensus: null, guardians: null,
    chain: [], docket: null, brief: '', terminal: 'READY', logs: [], view: 'executive'
  };
  window.__AAN_STATE__ = runtime;

  function requiredCapabilities(workClass) {
    return {
      reason: ['reasoning', 'research', 'synthesis'], build: ['engineering', 'orchestration'], verify: ['verification', 'security', 'benchmark', 'evidence'],
      orchestrate: ['orchestration', 'synthesis', 'reasoning'], critical: ['security', 'verification', 'orchestration', 'evidence']
    }[workClass] || ['reasoning'];
  }
  function capabilityScore(peer, workClass) {
    const required = requiredCapabilities(workClass);
    const hits = peer.capabilities.filter((capability) => required.includes(capability)).length;
    return clamp(0.55 + hits * 0.2 + (peer.role.toLowerCase().includes(workClass) ? 0.08 : 0), 0.45, 0.99);
  }
  function selectedIncidentIds(config) { return new Set(config.incidents || []); }

  function createCandidates(config, rng) {
    const incidents = selectedIncidentIds(config);
    const posture = release.postures.find((item) => item.id === config.posture) || release.postures[0];
    const candidates = release.peers.map((peer, index) => {
      const jitter = () => (rng() - 0.5);
      const capability = capabilityScore(peer, config.work_class);
      const latency = Math.round(peer.base_latency * (0.94 + rng() * 0.14));
      const reliability = clamp(peer.base_reliability + jitter() * 0.012, 0.82, 0.999);
      const energy = clamp(peer.base_energy + jitter() * 0.08, 0.35, 0.99);
      const evidence = clamp(peer.base_evidence + jitter() * 0.045, 0.55, 0.999);
      const latencyScore = clamp(1 - Math.max(0, latency - 30) / Math.max(50, config.latency_ceiling * 1.4), 0.05, 1);
      const energyScore = clamp(1 - Math.abs(energy - config.energy_target) * 1.8, 0.05, 1);
      const diversity = clamp(0.72 + ((index * 17 + config.seed) % 23) / 100, 0.6, 0.98);
      const quality = clamp(capability * 0.58 + evidence * 0.26 + reliability * 0.16, 0, 1);
      let score = quality * posture.weights.quality + reliability * posture.weights.reliability + energyScore * posture.weights.energy + latencyScore * posture.weights.latency + evidence * posture.weights.evidence + diversity * posture.weights.diversity;
      let status = 'candidate'; let reason = 'Meets baseline constitutional constraints.';
      if (latency > config.latency_ceiling * 1.18) { score -= 0.12; reason = 'Latency exceeds preferred ceiling.'; }
      if (incidents.has('peer-eclipse') && ['orion', 'helix', 'vesper'].includes(peer.id)) { score -= 0.1; reason = 'Correlation risk detected during eclipse rehearsal.'; }
      if (incidents.has('identity-drift') && peer.id === 'aegis') { status = 'quarantined'; score = 0; reason = 'Identity commitment mismatch; guardian quarantine.'; }
      return { ...peer, capability, latency, reliability, energy, evidence, diversity, quality, energy_score: energyScore, latency_score: latencyScore, score: clamp(score, 0, 1), status, reason };
    });
    return candidates.sort((a, b) => b.score - a.score || a.id.localeCompare(b.id));
  }
  function chooseDistinct(candidates, count, used = new Set()) {
    const selected = []; const regions = new Set();
    for (const candidate of candidates) {
      if (candidate.status === 'quarantined' || used.has(candidate.id)) continue;
      const regionFamily = candidate.region.split(' ')[0];
      if (selected.length < count && (!regions.has(regionFamily) || selected.length >= Math.ceil(count / 2))) { selected.push(candidate); regions.add(regionFamily); used.add(candidate.id); }
      if (selected.length === count) break;
    }
    for (const candidate of candidates) { if (selected.length === count) break; if (candidate.status !== 'quarantined' && !used.has(candidate.id)) { selected.push(candidate); used.add(candidate.id); } }
    return selected;
  }
  function createRoute(config, candidates, rng) {
    const used = new Set();
    const primary = chooseDistinct(candidates, 4, used);
    const shadow = chooseDistinct(candidates, 3, used);
    const incidents = selectedIncidentIds(config);
    const quarantined = candidates.filter((item) => item.status === 'quarantined');
    const allRegions = new Set([...primary, ...shadow].map((item) => item.region.split(' ')[0])).size;
    const diversity = clamp(allRegions / 7, 0, 1);
    const mean = (items, key) => items.reduce((sum, item) => sum + item[key], 0) / Math.max(1, items.length);
    const primaryLatency = mean(primary, 'latency');
    const primaryReliability = mean(primary, 'reliability');
    const primaryEvidence = mean(primary, 'evidence');
    const routeCommitmentSeed = stableStringify({ node: config.node_name, mission: config.mission, primary: primary.map((p) => p.id), shadow: shadow.map((p) => p.id), incidents: [...incidents].sort() });
    return {
      primary, shadow, quarantined, diversity, mean_latency: round(primaryLatency, 1), reliability: round(primaryReliability, 4), evidence: round(primaryEvidence, 4),
      route_id: `route-${fallbackHash(routeCommitmentSeed).slice(0, 14)}`,
      shadow_ready: shadow.length >= 3,
      mitigation: incidents.has('peer-eclipse') ? 'Correlated peers demoted; shadow route diversity elevated.' : incidents.has('identity-drift') ? 'Identity-drift peer quarantined before route commitment.' : 'No incident-specific route mitigation required.',
      packets: Math.round(120 + rng() * 80)
    };
  }
  function createReceipt(config, route, rng) {
    const incidents = selectedIncidentIds(config);
    const resourcePressure = incidents.has('resource-surge') ? 1.28 : 0.78 + rng() * 0.18;
    const concurrency = incidents.has('resource-surge') ? 2 : 4 + Math.floor(rng() * 3);
    const duration = Math.round(route.mean_latency * (7.8 + rng() * 2.7));
    const normalizedWork = round((0.92 + rng() * 0.46) * (config.work_class === 'critical' ? 1.2 : 1), 3);
    const energy = round(clamp(config.energy_target * (0.86 + rng() * 0.16) * resourcePressure, 0.25, 1.4), 3);
    const memory = Math.round(410 + rng() * 470 * resourcePressure);
    const streams = Math.round(12 + rng() * 14 * resourcePressure);
    const resourceCompliant = !incidents.has('resource-surge') || config.risk !== 'critical';
    return {
      work_unit_id: `awu-${fallbackHash(`${config.seed}:${config.mission}`).slice(0, 16)}`, normalized_work_units: normalizedWork, duration_ms: duration,
      energy_score: energy, memory_mb: memory, streams, concurrency, packets: route.packets, route_id: route.route_id,
      resource_pressure: round(resourcePressure, 2), resource_compliant: resourceCompliant,
      mode: 'deterministic-browser-local-simulation', external_compute: false, timestamp: deterministicTimestamp(config.seed, 6)
    };
  }
  function createEvaluation(config, route, receipt, rng) {
    const incidents = selectedIncidentIds(config);
    const candidateQuality = route.primary.reduce((sum, p) => sum + p.quality, 0) / route.primary.length;
    const quality = clamp(candidateQuality * (0.94 + rng() * 0.055), 0, 1);
    const reliability = clamp(route.reliability - (incidents.has('peer-eclipse') ? 0.035 : 0), 0, 1);
    const evidence = clamp(route.evidence - (incidents.has('validator-divergence') ? 0.025 : 0), 0, 1);
    const diversity = clamp(route.diversity - (incidents.has('peer-eclipse') ? 0.08 : 0), 0, 1);
    const energy = clamp(1 - Math.max(0, receipt.energy_score - config.energy_target) * 1.8, 0, 1);
    const latency = clamp(1 - Math.max(0, route.mean_latency - config.latency_ceiling) / config.latency_ceiling, 0, 1);
    const uncertainty = clamp(0.08 + rng() * 0.08 + config.incidents.length * 0.035 + (config.risk === 'critical' ? 0.03 : 0), 0.05, 0.45);
    const posture = release.postures.find((item) => item.id === config.posture) || release.postures[0];
    const readiness = quality * posture.weights.quality + reliability * posture.weights.reliability + energy * posture.weights.energy + latency * posture.weights.latency + evidence * posture.weights.evidence + diversity * posture.weights.diversity;
    return { quality: round(quality, 3), reliability: round(reliability, 3), evidence: round(evidence, 3), diversity: round(diversity, 3), energy: round(energy, 3), latency: round(latency, 3), uncertainty: round(uncertainty, 3), readiness: round(readiness * (1 - uncertainty * 0.24), 3) };
  }
  function createConsensus(config, evaluation, rng) {
    const incidents = selectedIncidentIds(config);
    const risk = release.risk_profiles.find((item) => item.id === config.risk) || release.risk_profiles[1];
    const axisValues = [evaluation.evidence, evaluation.quality, Math.min(evaluation.energy, evaluation.latency), evaluation.diversity, 1 - evaluation.uncertainty, evaluation.reliability, 1 - evaluation.uncertainty * 0.9];
    const votes = release.validators.map((validator, index) => {
      let score = clamp(axisValues[index] + (rng() - 0.5) * 0.08, 0, 1);
      let vote = score >= 0.72 ? 'PASS' : score >= 0.58 ? 'DISSENT' : 'REJECT';
      let rationale = score >= 0.72 ? 'Gate evidence satisfies the simulated review threshold.' : score >= 0.58 ? 'Material caution remains and must be preserved for human review.' : 'The gate is not sufficiently supported for advancement.';
      if (incidents.has('validator-divergence') && [1, 4].includes(index)) { vote = 'DISSENT'; score = Math.min(score, 0.67); rationale = 'Divergence rehearsal produced a non-conforming interpretation.'; }
      if (incidents.has('resource-surge') && index === 2) { vote = config.risk === 'critical' ? 'REJECT' : 'DISSENT'; score = config.risk === 'critical' ? 0.49 : 0.63; rationale = 'Resource pressure exceeded the preferred admission envelope.'; }
      if (incidents.has('peer-eclipse') && index === 3) { vote = 'DISSENT'; score = Math.min(score, 0.66); rationale = 'Route resilience is acceptable only with the committed shadow path.'; }
      if (incidents.has('identity-drift') && index === 5) { vote = 'REJECT'; score = 0.21; rationale = 'Identity commitment mismatch requires a guardian safe hold.'; }
      return { ...validator, vote, score: round(score, 3), rationale };
    });
    const pass = votes.filter((item) => item.vote === 'PASS').length;
    const dissent = votes.filter((item) => item.vote === 'DISSENT').length;
    const reject = votes.filter((item) => item.vote === 'REJECT').length;
    return { votes, pass, dissent, reject, threshold: risk.quorum, quorum_met: pass >= risk.quorum && reject === 0, summary: `${pass} pass · ${dissent} dissent · ${reject} reject` };
  }
  function createGuardians(config, evaluation, consensus) {
    const incidents = selectedIncidentIds(config);
    return release.guardians.map((guardian, index) => {
      let disposition = 'APPROVE'; let rationale = 'Constitutional boundary is intact for human review.';
      if (index === 0 && incidents.has('identity-drift')) { disposition = 'VETO'; rationale = 'Identity commitment drift remains unresolved.'; }
      else if (index === 1 && incidents.has('resource-surge')) { disposition = config.risk === 'critical' ? 'VETO' : 'CAUTION'; rationale = 'Resource surge requires constrained scope and explicit review.'; }
      else if (index === 2 && evaluation.evidence < (release.risk_profiles.find((r) => r.id === config.risk)?.evidence_floor || 0.76)) { disposition = 'CAUTION'; rationale = 'Evidence coverage is below the risk-adjusted floor.'; }
      else if (index === 3) { disposition = 'APPROVE'; rationale = 'No wallet, execution, settlement, production, or legal authority is present.'; }
      else if (index === 4 && config.incidents.length) { disposition = consensus.quorum_met ? 'CAUTION' : 'VETO'; rationale = consensus.quorum_met ? 'Recovery path is documented; residual risk remains.' : 'Recovery path did not restore the required quorum.'; }
      return { ...guardian, disposition, rationale };
    });
  }
  function determineTerminal(config, receipt, consensus, guardians) {
    const vetoes = guardians.filter((item) => item.disposition === 'VETO');
    if (!receipt.resource_compliant || !consensus.quorum_met || vetoes.length) {
      const reasons = [];
      if (!receipt.resource_compliant) reasons.push('resource envelope not admitted');
      if (!consensus.quorum_met) reasons.push('validator quorum not met');
      if (vetoes.length) reasons.push(`${vetoes.length} guardian veto${vetoes.length === 1 ? '' : 'es'}`);
      return { state: 'SAFE_HOLD', title: 'The node refused to advance.', copy: `Fail-closed disposition: ${reasons.join(', ')}. Evidence is preserved for diagnosis; no external authority exists.` };
    }
    return { state: 'HUMAN_REVIEW_REQUIRED', title: 'The proof package is ready for a human decision.', copy: 'The route, receipt, evaluation, validator quorum, dissent, guardian review, and chained evidence are complete. Factual correctness and external action remain unapproved.' };
  }

  async function createArtifactChain(config, route, receipt, evaluation, consensus, guardians, terminal) {
    const payloads = [
      { node_name: config.node_name, declared_operator: 'public-review-simulator', jurisdiction: 'human-declared', reviewer: 'human-required', origin: release.origin.repository },
      { mission: config.mission, work_class: config.work_class, risk: config.risk, success: 'review-ready evidence package', stop: terminal.state },
      { posture: config.posture, weights: release.postures.find((p) => p.id === config.posture).weights, prohibitions: ['network','wallet','transaction','settlement','production'] },
      { latency_ceiling_ms: config.latency_ceiling, energy_target: config.energy_target, resource_compliant: receipt.resource_compliant, concurrency: receipt.concurrency, memory_mb: receipt.memory_mb },
      { candidates: runtime.candidates.map((p) => ({ id: p.id, score: round(p.score, 3), status: p.status, reason: p.reason })) },
      { route_id: route.route_id, primary: route.primary.map((p) => p.id), shadow: route.shadow.map((p) => p.id), diversity: route.diversity, mitigation: route.mitigation },
      { incidents: config.incidents, quarantined: route.quarantined.map((p) => p.id), residual_risk: config.incidents.length ? 'human-review-required' : 'baseline' },
      receipt,
      { latency_ms: route.mean_latency, reliability: route.reliability, evidence: route.evidence, packets: route.packets, external_network: false },
      evaluation,
      consensus,
      { seats: guardians, vetoes: guardians.filter((g) => g.disposition === 'VETO').map((g) => g.id) },
      { state: terminal.state, permissions: { external_action: false, production: false, funds: false, factual_certification: false }, human_review_required: true },
      { pipeline: release.pipeline.map((stage) => stage.state), seed: config.seed, algorithm: window.crypto?.subtle ? 'SHA-256' : 'deterministic-fallback' },
      { schema: 'goalos.agi_alpha_node_v0.node_evidence_docket.v2', release_id: release.release_id, terminal_state: terminal.state },
      { title: 'Executive Review Brief', recommendation: terminal.title, unresolved: consensus.votes.filter((v) => v.vote !== 'PASS').map((v) => v.name) }
    ];
    let previous = '0'.repeat(64); const chain = [];
    for (let index = 0; index < release.artifacts.length; index += 1) {
      const meta = release.artifacts[index]; const payload = payloads[index];
      const artifactHash = await sha256(stableStringify(payload));
      const commitment = await sha256(`${previous}:${artifactHash}:${meta.name}`);
      chain.push({ index: index + 1, id: meta.id, name: meta.name, plane: meta.plane, purpose: meta.purpose, payload, previous_commitment: previous, artifact_hash: artifactHash, commitment });
      previous = commitment;
    }
    return chain;
  }
  function createDocket(config, route, receipt, evaluation, consensus, guardians, terminal, chain) {
    return {
      schema: 'goalos.agi_alpha_node_v0.node_evidence_docket.v2', release: { id: release.release_id, title: release.release_title, version: release.version },
      generated_at: deterministicTimestamp(config.seed, 16), deterministic_seed: config.seed, cryptographic_chain: window.crypto?.subtle ? 'SHA-256' : 'deterministic-fallback',
      node: { identity: config.node_name, origin: release.origin, mode: 'browser-local-digital-twin' }, mission: config,
      peer_route: { route_id: route.route_id, primary: route.primary.map((p) => ({ id: p.id, name: p.name, region: p.region, score: round(p.score, 3) })), shadow: route.shadow.map((p) => ({ id: p.id, name: p.name, region: p.region, score: round(p.score, 3) })), quarantined: route.quarantined.map((p) => p.id), mitigation: route.mitigation },
      alpha_work_unit_receipt: receipt, evaluation, validator_consensus: consensus, guardian_review: guardians, terminal_disposition: terminal,
      proof_chronicle: { artifacts: chain, chain_head: chain.at(-1)?.commitment || null },
      claim_boundary: release.claim_boundary, authority: { factual_correctness: 'NOT_CERTIFIED', production_activation: 'NOT_ACTIVATED', funds_authorization: 'NO', external_actions: 0, final_state: terminal.state }
    };
  }
  function createBrief(docket) {
    const nonPass = docket.validator_consensus.votes.filter((item) => item.vote !== 'PASS');
    const vetoes = docket.guardian_review.filter((item) => item.disposition === 'VETO');
    return `# GoalOS AGIALPHA Ascension AGI Alpha Node v0 — Executive Review Brief\n\n## Terminal disposition\n\n**${docket.terminal_disposition.state}** — ${docket.terminal_disposition.title}\n\n${docket.terminal_disposition.copy}\n\n## Mission\n\n${docket.mission.mission}\n\n- Node: ${docket.node.identity}\n- Work class: ${docket.mission.work_class}\n- Risk profile: ${docket.mission.risk}\n- Operating constitution: ${docket.mission.posture}\n- Primary route: ${docket.peer_route.primary.map((p) => p.name).join(' → ')}\n- Shadow route: ${docket.peer_route.shadow.map((p) => p.name).join(' → ')}\n- Review readiness: ${formatPct(docket.evaluation.readiness)} (simulated; not factual confidence)\n- Validator result: ${docket.validator_consensus.summary}; threshold ${docket.validator_consensus.threshold}/7\n- Guardian vetoes: ${vetoes.length ? vetoes.map((g) => g.name).join(', ') : 'none'}\n- Chain head: ${docket.proof_chronicle.chain_head}\n\n## Dissent and unresolved review surfaces\n\n${nonPass.length ? nonPass.map((v) => `- **${v.name} — ${v.vote}:** ${v.rationale}`).join('\n') : '- No simulated validator dissent.'}\n\n## Human decision required\n\nReview the identity, mission contract, route diversity, resource envelope, evidence coverage, validator dissent, guardian dispositions, and residual uncertainty. This package grants no external authority.\n\n## Explicit boundary\n\n- Factual correctness: NOT CERTIFIED\n- Production activation: NOT ACTIVATED\n- Funds authorization: NO\n- External actions: 0\n- Final state: ${docket.terminal_disposition.state}\n`;
  }

  const ui = {};
  function collectUI() {
    Object.assign(ui, {
      form: byId('aan-node-form'), preset: byId('aan-preset'), nodeName: byId('aan-node-name'), mission: byId('aan-mission'), workClass: byId('aan-work-class'),
      risk: byId('aan-risk'), posture: byId('aan-posture'), postureDescription: byId('aan-posture-description'), energy: byId('aan-energy'), latency: byId('aan-latency'),
      energyOutput: byId('aan-energy-output'), latencyOutput: byId('aan-latency-output'), run: byId('aan-run'), hold: byId('aan-hold'), reset: byId('aan-reset')
    });
  }
  function renderThesis() {
    const target = byId('aan-thesis-grid'); if (!target) return; clear(target);
    release.thesis.forEach((item) => { const card = el('article'); append(card, 'span', 'number', item.number); append(card, 'h3', '', item.title); append(card, 'p', '', item.copy); target.appendChild(card); });
  }
  function renderControls() {
    release.presets.forEach((item) => ui.preset.appendChild(option(item.id, item.label)));
    release.work_unit_classes.forEach((item) => ui.workClass.appendChild(option(item.id, `${item.symbol} · ${item.label}`)));
    release.risk_profiles.forEach((item) => ui.risk.appendChild(option(item.id, `${item.label} · quorum ${item.quorum}/7`)));
    release.postures.forEach((item) => ui.posture.appendChild(option(item.id, item.label)));
    ui.preset.value = release.presets[0].id; ui.posture.value = 'sovereign'; applyPreset(); syncPosture(); syncRanges();
    const incidents = byId('aan-incident-grid'); clear(incidents);
    release.incidents.forEach((item) => { const wrap = el('div', 'aan-incident-option'); const input = el('input'); input.type = 'checkbox'; input.id = `aan-incident-${item.id}`; input.value = item.id; input.name = 'incident'; const label = el('label'); label.htmlFor = input.id; append(label, 'i', '', item.symbol); const text = el('span'); append(text, 'b', '', item.label); append(text, 'small', '', item.description); label.appendChild(text); wrap.append(input, label); incidents.appendChild(wrap); });
  }
  function applyPreset() {
    const preset = release.presets.find((item) => item.id === ui.preset.value) || release.presets[0];
    ui.mission.value = preset.mission; ui.workClass.value = preset.work_class; ui.risk.value = preset.risk;
  }
  function syncPosture() { const posture = release.postures.find((item) => item.id === ui.posture.value); ui.postureDescription.textContent = posture?.description || ''; }
  function syncRanges() { ui.energyOutput.value = (Number(ui.energy.value) / 100).toFixed(2); ui.energyOutput.textContent = (Number(ui.energy.value) / 100).toFixed(2); ui.latencyOutput.value = `${ui.latency.value} ms`; ui.latencyOutput.textContent = `${ui.latency.value} ms`; }
  function collectConfig() {
    const incidents = [...doc.querySelectorAll('input[name="incident"]:checked')].map((input) => input.value).sort();
    const mission = safe(ui.mission.value);
    const config = { node_name: safe(ui.nodeName.value, '1.alpha.node.agi.eth'), mission, work_class: ui.workClass.value, risk: ui.risk.value, posture: ui.posture.value, energy_target: Number(ui.energy.value) / 100, latency_ceiling: Number(ui.latency.value), incidents };
    config.seed = hashString(stableStringify(config)); return config;
  }
  function renderStageRail() {
    const target = byId('aan-stage-rail'); clear(target);
    release.pipeline.forEach((stage, index) => { const item = el('div', 'aan-stage'); item.dataset.stage = String(index); item.title = stage.title; append(item, 'span', '', pad(stage.order)); append(item, 'b', '', stage.id.toUpperCase()); target.appendChild(item); });
  }
  function setStage(index, held = false) {
    runtime.phase = index;
    doc.querySelectorAll('.aan-stage').forEach((item, i) => { item.classList.toggle('is-complete', i < index); item.classList.toggle('is-active', i === index && !held); item.classList.toggle('is-hold', held && i === index); });
    const stage = release.pipeline[index]; if (stage) { byId('aan-state-label').textContent = stage.state; byId('aan-runtime-badge').textContent = held ? 'SAFE HOLD' : `GATE ${pad(index + 1)} / 10`; }
  }
  function log(message, type = '') {
    const list = byId('aan-terminal-log'); if (!runtime.logs.length) clear(list);
    const item = el('li', type, message); list.appendChild(item); runtime.logs.push({ message, type }); list.scrollTop = list.scrollHeight; byId('aan-terminal-count').textContent = `${runtime.logs.length} EVENT${runtime.logs.length === 1 ? '' : 'S'}`;
  }
  function resetLog() { runtime.logs = []; const list = byId('aan-terminal-log'); clear(list); list.appendChild(el('li', 'muted', 'Awaiting a bounded mission.')); byId('aan-terminal-count').textContent = '0 EVENTS'; }
  function renderInitialArtifacts() {
    const target = byId('aan-artifact-chain'); if (!target) return; clear(target);
    release.artifacts.forEach((item, index) => { const card = el('article', 'aan-artifact-card'); card.dataset.artifact = String(index); append(card, 'span', '', `${pad(index + 1)} · ${item.plane.toUpperCase()}`); append(card, 'h3', '', item.name); append(card, 'p', 'aan-executive-only', item.purpose); append(card, 'code', 'aan-technical-only', 'UNSEALED'); target.appendChild(card); });
  }
  function renderArtifactProgress(chain = [], count = 0) {
    doc.querySelectorAll('.aan-artifact-card').forEach((card, index) => { const record = chain[index]; const sealed = index < count && record; card.classList.toggle('is-sealed', Boolean(sealed)); const code = card.querySelector('code'); if (code) code.textContent = sealed ? shortHash(record.commitment, 16) : 'UNSEALED'; });
    byId('aan-artifact-count').textContent = `${Math.min(count, 16)} / 16`;
    if (count >= 16 && chain.length) { byId('aan-chain-status').textContent = 'SEALED'; byId('aan-chain-code').textContent = chain.at(-1).commitment; byId('aan-chain-head').textContent = shortHash(chain.at(-1).commitment); }
  }
  function renderCouncil(consensus = null, guardians = null) {
    const validatorGrid = byId('aan-validator-grid'); const guardianGrid = byId('aan-guardian-grid'); clear(validatorGrid); clear(guardianGrid);
    (consensus?.votes || release.validators).forEach((item) => { const card = el('article', `aan-validator${item.vote ? ` is-${item.vote === 'PASS' ? 'pass' : item.vote === 'DISSENT' ? 'dissent' : 'reject'}` : ''}`); append(card, 'i', '', item.symbol); append(card, 'b', '', item.name); append(card, 'small', '', item.rationale || item.focus); append(card, 'em', '', item.vote || 'AWAITING'); validatorGrid.appendChild(card); });
    (guardians || release.guardians).forEach((item) => { const cls = item.disposition ? ` is-${item.disposition === 'APPROVE' ? 'approve' : item.disposition === 'CAUTION' ? 'caution' : 'veto'}` : ''; const card = el('article', `aan-guardian${cls}`); append(card, 'i', '', item.symbol); append(card, 'b', '', item.name); append(card, 'small', '', item.rationale || item.focus); append(card, 'em', '', item.disposition || 'AWAITING'); guardianGrid.appendChild(card); });
    byId('aan-quorum-label').textContent = consensus ? `QUORUM ${consensus.pass} / ${consensus.threshold}` : 'QUORUM —';
    byId('aan-guardian-label').textContent = guardians ? `${guardians.filter((g) => g.disposition === 'VETO').length} VETO` : 'AWAITING';
  }
  function renderFlightMetrics(route = null, receipt = null, evaluation = null) {
    const target = byId('aan-flight-metrics'); clear(target);
    const values = route && receipt && evaluation ? [
      [route.mean_latency ? `${route.mean_latency} ms` : '—', 'mean latency'], [formatPct(evaluation.quality), 'quality'], [formatPct(evaluation.evidence), 'evidence'], [formatPct(evaluation.diversity), 'route diversity'], [receipt.energy_score.toFixed(2), 'energy'], [formatPct(evaluation.uncertainty), 'uncertainty']
    ] : [['—','mean latency'],['—','quality'],['—','evidence'],['—','route diversity'],['—','energy'],['—','uncertainty']];
    values.forEach(([value, label]) => { const card = el('div'); append(card, 'b', '', value); append(card, 'span', '', label); target.appendChild(card); });
  }
  function renderMesh(candidates = [], route = null) {
    const target = byId('aan-mesh'); if (!target) return; clear(target);
    const defs = svg('defs'); const grad = svg('linearGradient', { id: 'aan-mesh-grad', x1: '0', y1: '0', x2: '1', y2: '1' }); grad.append(svg('stop', { offset: '0', 'stop-color': '#ffe56d' }), svg('stop', { offset: '.5', 'stop-color': '#66f6c8' }), svg('stop', { offset: '1', 'stop-color': '#43c9ff' })); defs.appendChild(grad); target.appendChild(defs);
    const center = { x: 450, y: 270 }; const radiusX = 350; const radiusY = 190;
    const source = candidates.length ? candidates : release.peers.map((peer) => ({ ...peer, score: 0, status: 'candidate' }));
    const positions = new Map(); source.forEach((peer, index) => { const angle = -Math.PI / 2 + (Math.PI * 2 * index) / source.length; positions.set(peer.id, { x: center.x + Math.cos(angle) * radiusX, y: center.y + Math.sin(angle) * radiusY }); });
    const rings = svg('g', { class: 'aan-mesh-rings' }); rings.append(svg('ellipse', { cx: center.x, cy: center.y, rx: 350, ry: 190 }), svg('ellipse', { cx: center.x, cy: center.y, rx: 255, ry: 135 }), svg('line', { x1: 80, y1: center.y, x2: 820, y2: center.y })); target.appendChild(rings);
    source.forEach((peer) => { const pos = positions.get(peer.id); const status = route?.primary.some((p) => p.id === peer.id) ? 'primary' : route?.shadow.some((p) => p.id === peer.id) ? 'shadow' : peer.status === 'quarantined' ? 'quarantine' : 'candidate'; const line = svg('line', { x1: center.x, y1: center.y, x2: pos.x, y2: pos.y, class: `aan-mesh-edge ${status}` }); target.appendChild(line); if (status === 'primary' || status === 'shadow') { const packet = svg('circle', { r: status === 'primary' ? 4 : 3, class: `aan-mesh-packet ${status}` }); const animation = svg('animateMotion', { dur: status === 'primary' ? '2.5s' : '3.4s', repeatCount: 'indefinite', path: `M${center.x},${center.y} L${pos.x},${pos.y}` }); packet.appendChild(animation); target.appendChild(packet); } });
    const core = svg('g', { class: 'aan-mesh-core' }); core.append(svg('circle', { cx: center.x, cy: center.y, r: 64 }), svg('circle', { cx: center.x, cy: center.y, r: 42, class: 'inner' })); const alpha = svg('text', { x: center.x, y: center.y + 13 }); alpha.textContent = 'α'; core.appendChild(alpha); const coreName = svg('text', { x: center.x, y: center.y + 91, class: 'name' }); coreName.textContent = '1.alpha.node.agi.eth'; core.appendChild(coreName); target.appendChild(core);
    source.forEach((peer) => { const pos = positions.get(peer.id); const status = route?.primary.some((p) => p.id === peer.id) ? 'primary' : route?.shadow.some((p) => p.id === peer.id) ? 'shadow' : peer.status === 'quarantined' ? 'quarantine' : 'candidate'; const group = svg('g', { class: `aan-peer-node ${status}`, transform: `translate(${pos.x} ${pos.y})` }); group.append(svg('circle', { r: status === 'primary' ? 28 : 23 })); const symbol = svg('text', { y: 4 }); symbol.textContent = peer.name.slice(0, 2).toUpperCase(); group.appendChild(symbol); const name = svg('text', { y: status === 'primary' ? 46 : 41, class: 'name' }); name.textContent = peer.name; group.appendChild(name); const score = svg('text', { y: status === 'primary' ? 60 : 55, class: 'score' }); score.textContent = candidates.length ? `${Math.round(peer.score * 100)}` : '—'; group.appendChild(score); target.appendChild(group); });
  }
  function renderDecision(terminal = null) {
    const card = byId('aan-decision-card'); card.classList.remove('is-review', 'is-hold');
    if (!terminal) { byId('aan-decision-title').textContent = 'No cycle has run.'; byId('aan-decision-copy').textContent = 'The node has not produced an evidence chain, validator result, guardian review, or decision package.'; return; }
    card.classList.add(terminal.state === 'SAFE_HOLD' ? 'is-hold' : 'is-review'); byId('aan-decision-title').textContent = terminal.title;
    byId('aan-decision-copy').textContent = runtime.view === 'technical' ? `${terminal.copy} Terminal state: ${terminal.state}. Chain: ${runtime.chain.at(-1)?.commitment || 'unsealed'}.` : terminal.copy;
  }
  function setTrust(value = null, terminal = null) {
    const ring = byId('aan-trust-ring'); const label = byId('aan-trust-value'); const circumference = 2 * Math.PI * 100;
    if (value === null) { ring.style.strokeDashoffset = String(circumference); label.textContent = '—'; return; }
    ring.style.strokeDasharray = String(circumference); ring.style.strokeDashoffset = String(circumference * (1 - clamp(value, 0, 1))); ring.style.stroke = terminal?.state === 'SAFE_HOLD' ? 'var(--aan-rose)' : 'var(--aan-mint)'; label.textContent = `${Math.round(value * 100)}`;
  }
  function enableExports(enabled) { ['aan-download-json','aan-download-md','aan-copy-summary'].forEach((id) => { const button = byId(id); if (button) button.disabled = !enabled; }); }
  function setStatus(state, chain = null, route = null) { byId('aan-state-label').textContent = state; byId('aan-chain-head').textContent = chain ? shortHash(chain) : '—'; byId('aan-route-label').textContent = route ? route.route_id.toUpperCase() : 'UNCOMMITTED'; byId('aan-hero-mode').textContent = state === 'SAFE_HOLD' ? 'SAFE HOLD' : state === 'HUMAN_REVIEW_REQUIRED' ? 'REVIEW READY' : runtime.running ? 'PROOF FLIGHT' : 'REVIEW MODE'; }

  async function runFlight(event) {
    event?.preventDefault(); if (runtime.running) return;
    const config = collectConfig(); if (!config.mission) { ui.mission.focus(); byId('aan-export-status').textContent = 'Enter a bounded mission before launch.'; return; }
    const token = ++runtime.token; Object.assign(runtime, { running: true, held: false, phase: -1, config, seed: config.seed, rng: mulberry32(config.seed), candidates: [], route: null, receipt: null, evaluation: null, consensus: null, guardians: null, chain: [], docket: null, brief: '', terminal: 'RUNNING' });
    enableExports(false); resetLog(); renderInitialArtifacts(); renderCouncil(); renderFlightMetrics(); setTrust(null); renderDecision(); setStatus('COMPILING'); ui.run.disabled = true; ui.run.textContent = 'Proof flight running…'; byId('aan-runtime-badge').textContent = 'COMPILING'; byId('aan-chain-status').textContent = 'BUILDING'; byId('aan-chain-code').textContent = '—'; byId('aan-artifact-count').textContent = '0 / 16';
    const stageDelay = window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 20 : 220;
    try {
      const rng = runtime.rng;
      runtime.candidates = createCandidates(config, rng); runtime.route = createRoute(config, runtime.candidates, rng); runtime.receipt = createReceipt(config, runtime.route, rng); runtime.evaluation = createEvaluation(config, runtime.route, runtime.receipt, rng); runtime.consensus = createConsensus(config, runtime.evaluation, rng); runtime.guardians = createGuardians(config, runtime.evaluation, runtime.consensus); const terminal = determineTerminal(config, runtime.receipt, runtime.consensus, runtime.guardians);
      runtime.chain = await createArtifactChain(config, runtime.route, runtime.receipt, runtime.evaluation, runtime.consensus, runtime.guardians, terminal);
      const artifactsByStage = [1,2,3,4,7,9,10,11,12,16];
      const stageActions = [
        () => log(`Identity sealed for ${config.node_name}.`, 'ok'),
        () => log(`Work unit contracted: ${config.work_class} / ${config.risk}.`, 'ok'),
        () => log(`Constitution compiled: ${config.posture}; external authority = none.`, 'ok'),
        () => { log(`Resource envelope ${runtime.receipt.resource_compliant ? 'admitted' : 'exceeded'}: ${runtime.receipt.memory_mb} MB · ${runtime.receipt.streams} streams.`, runtime.receipt.resource_compliant ? 'ok' : 'deny'); },
        () => { renderMesh(runtime.candidates, runtime.route); byId('aan-route-label').textContent = runtime.route.route_id.toUpperCase(); log(`Primary route committed: ${runtime.route.primary.map((p) => p.name).join(' → ')}.`, 'ok'); log(`Shadow route committed: ${runtime.route.shadow.map((p) => p.name).join(' → ')}.`, 'ok'); if (config.incidents.length) log(`Incident disposition: ${runtime.route.mitigation}`, 'warn'); },
        () => { renderFlightMetrics(runtime.route, runtime.receipt, runtime.evaluation); log(`α-Work Unit receipt ready: ${runtime.receipt.work_unit_id}.`, 'ok'); },
        () => { setTrust(runtime.evaluation.readiness, terminal); log(`Evaluation ready: ${formatPct(runtime.evaluation.readiness)} review readiness; ${formatPct(runtime.evaluation.uncertainty)} residual uncertainty.`, 'ok'); },
        () => { renderCouncil(runtime.consensus); log(`Validator mesh: ${runtime.consensus.summary}; threshold ${runtime.consensus.threshold}/7.`, runtime.consensus.quorum_met ? 'ok' : 'deny'); runtime.consensus.votes.filter((v) => v.vote !== 'PASS').forEach((v) => log(`${v.name}: ${v.vote} — ${v.rationale}`, v.vote === 'REJECT' ? 'deny' : 'warn')); },
        () => { renderCouncil(runtime.consensus, runtime.guardians); const vetoes = runtime.guardians.filter((g) => g.disposition === 'VETO'); log(`Guardian council packaged: ${vetoes.length} veto${vetoes.length === 1 ? '' : 'es'}.`, vetoes.length ? 'deny' : 'ok'); },
        () => { runtime.terminal = terminal.state; renderDecision(terminal); log(`${terminal.state}: ${terminal.title}`, terminal.state === 'SAFE_HOLD' ? 'deny' : 'warn'); log('Factual correctness remains NOT CERTIFIED. External actions remain 0.', 'warn'); }
      ];
      for (let index = 0; index < release.pipeline.length; index += 1) {
        if (token !== runtime.token) return; setStage(index); stageActions[index](); renderArtifactProgress(runtime.chain, artifactsByStage[index]); await sleep(stageDelay);
      }
      runtime.docket = createDocket(config, runtime.route, runtime.receipt, runtime.evaluation, runtime.consensus, runtime.guardians, terminal, runtime.chain); runtime.brief = createBrief(runtime.docket);
      setStatus(terminal.state, runtime.chain.at(-1).commitment, runtime.route); byId('aan-chain-status').textContent = 'SEALED'; byId('aan-chain-code').textContent = runtime.chain.at(-1).commitment; byId('aan-artifact-count').textContent = '16 / 16'; enableExports(true); byId('aan-export-status').textContent = terminal.state === 'SAFE_HOLD' ? 'Evidence preserved. The node failed closed.' : 'Evidence Docket sealed. Human review is now required.';
    } catch (error) { console.error(error); runtime.terminal = 'SAFE_HOLD'; setStatus('SAFE_HOLD'); log(`Runtime exception preserved: ${error.message}`, 'deny'); byId('aan-export-status').textContent = 'The local simulation entered SAFE_HOLD.'; }
    finally { runtime.running = false; ui.run.disabled = false; ui.run.innerHTML = 'Launch proof flight <span>⚡</span>'; byId('aan-runtime-badge').textContent = runtime.terminal === 'SAFE_HOLD' ? 'SAFE HOLD' : 'REVIEW READY'; }
  }
  function safeHold() {
    runtime.token += 1; runtime.running = false; runtime.held = true; runtime.terminal = 'SAFE_HOLD'; ui.run.disabled = false; ui.run.innerHTML = 'Launch proof flight <span>⚡</span>'; setStage(Math.max(runtime.phase, 0), true); setStatus('SAFE_HOLD', runtime.chain.at(-1)?.commitment, runtime.route); byId('aan-runtime-badge').textContent = 'SAFE HOLD'; log('Manual safe hold engaged. No external action was available or taken.', 'deny'); renderDecision({ state: 'SAFE_HOLD', title: 'The operator placed the node on safe hold.', copy: 'The current local trace is frozen. Restart or reset to begin a new bounded cycle.' }); byId('aan-export-status').textContent = 'Manual safe hold engaged.';
  }
  function resetExperience() {
    runtime.token += 1; Object.assign(runtime, { running: false, held: false, phase: -1, config: null, candidates: [], route: null, receipt: null, evaluation: null, consensus: null, guardians: null, chain: [], docket: null, brief: '', terminal: 'READY' });
    ui.run.disabled = false; ui.run.innerHTML = 'Launch proof flight <span>⚡</span>'; doc.querySelectorAll('input[name="incident"]').forEach((item) => { item.checked = false; }); renderStageRail(); renderMesh(); renderInitialArtifacts(); renderCouncil(); renderFlightMetrics(); resetLog(); setTrust(null); renderDecision(); setStatus('READY'); byId('aan-runtime-badge').textContent = 'READY'; byId('aan-chain-status').textContent = 'UNSEALED'; byId('aan-chain-code').textContent = '—'; byId('aan-artifact-count').textContent = '0 / 16'; byId('aan-export-status').textContent = ''; enableExports(false);
  }
  function download(filename, content, type) { const blob = new Blob([content], { type }); const url = URL.createObjectURL(blob); const anchor = el('a'); anchor.href = url; anchor.download = filename; doc.body.appendChild(anchor); anchor.click(); anchor.remove(); URL.revokeObjectURL(url); }
  function exportJson() { if (!runtime.docket) return; download(`goalos-agi-alpha-node-v0-${runtime.docket.deterministic_seed}-evidence-docket.json`, `${JSON.stringify(runtime.docket, null, 2)}\n`, 'application/json'); byId('aan-export-status').textContent = 'Evidence Docket downloaded.'; }
  function exportMarkdown() { if (!runtime.brief) return; download(`goalos-agi-alpha-node-v0-${runtime.seed}-review-brief.md`, runtime.brief, 'text/markdown'); byId('aan-export-status').textContent = 'Executive review brief downloaded.'; }
  async function copySummary() { if (!runtime.brief) return; try { await navigator.clipboard.writeText(runtime.brief); byId('aan-export-status').textContent = 'Executive summary copied.'; } catch { byId('aan-export-status').textContent = 'Clipboard unavailable; download the review brief instead.'; } }
  function setView(view) {
    runtime.view = view; doc.body.dataset.view = view; doc.querySelectorAll('.aan-view-switch button').forEach((button) => button.classList.toggle('is-active', button.dataset.view === view));
    if (runtime.docket) renderDecision(runtime.docket.terminal_disposition);
  }
  function setupExperience() {
    collectUI(); renderThesis(); renderControls(); renderStageRail(); renderMesh(); renderInitialArtifacts(); renderCouncil(); renderFlightMetrics(); resetLog(); setView('executive');
    ui.preset.addEventListener('change', applyPreset); ui.posture.addEventListener('change', syncPosture); [ui.energy, ui.latency].forEach((input) => input.addEventListener('input', syncRanges)); ui.form.addEventListener('submit', runFlight); ui.hold.addEventListener('click', safeHold); ui.reset.addEventListener('click', resetExperience);
    byId('aan-download-json').addEventListener('click', exportJson); byId('aan-download-md').addEventListener('click', exportMarkdown); byId('aan-copy-summary').addEventListener('click', copySummary);
    doc.querySelectorAll('.aan-view-switch button').forEach((button) => button.addEventListener('click', () => setView(button.dataset.view)));
    doc.addEventListener('keydown', (event) => { const target = event.target; if (target && ['INPUT','TEXTAREA','SELECT'].includes(target.tagName)) return; const key = event.key.toLowerCase(); if (key === 'g') { event.preventDefault(); ui.form.requestSubmit(); } else if (key === 'h') { event.preventDefault(); safeHold(); } else if (key === 'r') { event.preventDefault(); resetExperience(); } else if (key === 'e') { event.preventDefault(); setView(runtime.view === 'executive' ? 'technical' : 'executive'); } });
  }

  async function renderArchitecture() {
    const stack = byId('aan-stack-diagram'); if (!stack) return;
    release.node_roles.forEach((role, index) => { const card = el('article', 'aan-stack-plane'); card.dataset.symbol = role.symbol; append(card, 'span', '', `${pad(index + 1)} · ${role.symbol}`); append(card, 'h3', '', role.name); append(card, 'p', '', role.mandate); stack.appendChild(card); });
    const pipeline = byId('aan-arch-pipeline'); release.pipeline.forEach((stage) => { const item = el('li'); append(item, 'span', '', pad(stage.order)); const label = el('div'); append(label, 'b', '', stage.state); append(label, 'h3', '', stage.title); item.appendChild(label); append(item, 'p', '', stage.plain); append(item, 'small', '', `${stage.agent} · ${stage.artifact}`); pipeline.appendChild(item); });
    const translation = byId('aan-translation-grid'); release.architecture_translation.forEach((item, index) => { const card = el('article', 'aan-translation-card'); const legacy = el('div'); append(legacy, 'span', '', `ORIGINAL ${pad(index + 1)}`); append(legacy, 'b', '', item.legacy); const arrow = el('i', '', '→'); const goalos = el('div'); append(goalos, 'span', '', 'GOALOS ASCENSION'); append(goalos, 'b', '', item.goalos); append(goalos, 'p', '', item.consequence); card.append(legacy, arrow, goalos); translation.appendChild(card); });
    const lineageBody = byId('aan-lineage-table'); release.lineage_fingerprints.forEach((item) => { const row = el('tr'); append(row, 'td', '', item.title); append(row, 'td', '', item.path); append(row, 'td', '', `${item.sha256.slice(0, 14)}… · ${item.lines} lines`); append(row, 'td', '', item.consequence); lineageBody.appendChild(row); });
    const lineageRoot = await sha256(release.lineage_fingerprints.map((item) => item.sha256).join(':')); byId('aan-lineage-root').textContent = `root ${lineageRoot}`; byId('aan-lineage-count').textContent = String(release.lineage_fingerprints.length);
    const threats = byId('aan-threat-grid'); release.threats.forEach((item) => { const card = el('article', 'aan-threat-card'); append(card, 'span', '', item.id.toUpperCase()); append(card, 'h3', '', item.name); append(card, 'p', '', item.control); append(card, 'b', '', item.disposition); threats.appendChild(card); });
    const principles = byId('aan-principle-grid'); release.governance_principles.forEach((item, index) => { const card = el('article', 'aan-principle-card'); append(card, 'span', '', pad(index + 1)); append(card, 'h3', '', item.title); append(card, 'p', '', item.copy); principles.appendChild(card); });
    const mainnet = byId('aan-mainnet-grid'); const record = release.mainnet_record || { contracts: '48', verification: '48/48', phase_b_grants: '14/14', production_activation: 'NOT_ACTIVATED', user_fund_authorization: 'NO', source_identity: 'PENDING' };
    [
      ['GOALOS CONTRACTS', record.contracts ?? 48, 'Repository registry'], ['SOURCE VERIFICATION', record.verification ?? '48/48', 'Recorded operator evidence'], ['PHASE-B GRANTS', record.phase_b_grants ?? '14/14', 'Recorded release state'], ['PRODUCTION', record.production_activation ?? 'NOT_ACTIVATED', 'Explicit boundary'], ['USER FUNDS', record.user_fund_authorization ?? 'NO', 'No authorization'], ['SOURCE IDENTITY', record.source_identity ?? 'PENDING', 'Reproducibility boundary']
    ].forEach(([label, value, note]) => { const card = el('article', 'aan-mainnet-card'); append(card, 'span', '', label); append(card, 'b', '', value); append(card, 'small', '', note); mainnet.appendChild(card); });
    const boundaries = byId('aan-boundary-list'); release.claim_boundary.forEach((item) => boundaries.appendChild(el('li', '', item)));
  }

  function renderLedger() {
    const catalog = byId('aan-ledger-catalog'); if (!catalog) return;
    release.artifacts.forEach((item, index) => { const card = el('article', 'aan-ledger-item'); append(card, 'span', '', `${pad(index + 1)} · ${item.plane.toUpperCase()}`); append(card, 'h3', '', item.name); append(card, 'p', '', item.purpose); append(card, 'code', '', `sha256(prev || ${item.id})`); catalog.appendChild(card); });
    const sample = release.sample_docket || {};
    const summary = byId('aan-sample-summary'); const fields = [
      ['FINAL STATE', sample.authority?.final_state || 'HUMAN_REVIEW_REQUIRED'], ['PRIMARY ROUTE', sample.peer_route?.primary?.map((p) => p.name || p).join(' → ') || 'Orion → Mnemosyne → Aegis → Quanta'], ['QUORUM', sample.validator_consensus ? `${sample.validator_consensus.pass}/${sample.validator_consensus.threshold}` : '6/6'], ['READINESS', sample.evaluation ? formatPct(sample.evaluation.readiness) : '88%'], ['CHAIN HEAD', shortHash(sample.proof_chronicle?.chain_head || 'sample-chain-head', 14)]
    ];
    fields.forEach(([label, value]) => { const card = el('div'); append(card, 'span', '', label); append(card, 'b', '', value); summary.appendChild(card); });
    const chain = byId('aan-sample-chain'); (sample.proof_chronicle?.artifacts || release.artifacts.map((item, index) => ({ index: index + 1, name: item.name, commitment: fallbackHash(`${item.id}:${index}`) }))).forEach((item) => { const card = el('div'); append(card, 'span', '', pad(item.index)); append(card, 'b', '', item.name); append(card, 'code', '', shortHash(item.commitment, 14)); chain.appendChild(card); });
    byId('aan-sample-json').textContent = JSON.stringify(sample, null, 2);
    const copy = byId('aan-sample-copy'); if (copy) copy.addEventListener('click', async () => { const text = `AGI Alpha Node v0 sample — ${fields.map(([k,v]) => `${k}: ${v}`).join(' · ')}`; try { await navigator.clipboard.writeText(text); byId('aan-sample-status').textContent = 'Sample summary copied.'; } catch { byId('aan-sample-status').textContent = 'Clipboard unavailable.'; } });
  }

  async function boot() {
    setupNavigation(); setupDialogs(); renderHeroMetrics();
    if (byId('aan-node-form')) setupExperience();
    if (byId('aan-stack-diagram')) await renderArchitecture();
    if (byId('aan-ledger-catalog')) renderLedger();
    doc.documentElement.dataset.aanReady = 'true';
  }
  boot().catch((error) => { doc.documentElement.dataset.aanReady = 'error'; console.error('AGI Alpha Node boot entered SAFE_HOLD.', error); });
})();
