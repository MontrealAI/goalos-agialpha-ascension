(() => {
  'use strict';

  const doc = document;
  const dataNode = doc.getElementById('aan-release-data');
  if (!dataNode) return;

  let release;
  try {
    release = JSON.parse(dataNode.textContent || '{}');
  } catch (error) {
    console.error('AGI Alpha Node release contract could not be parsed.', error);
    return;
  }

  const byId = (id) => doc.getElementById(id);
  const el = (tag, className, text) => {
    const node = doc.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  };
  const svgEl = (tag, attrs = {}) => {
    const node = doc.createElementNS('http://www.w3.org/2000/svg', tag);
    Object.entries(attrs).forEach(([key, value]) => node.setAttribute(key, String(value)));
    return node;
  };
  const clamp = (value, min, max) => Math.min(max, Math.max(min, value));
  const round = (value, digits = 2) => Number(value.toFixed(digits));
  const pad = (value) => String(value).padStart(2, '0');
  const safeText = (value, fallback = '') => String(value ?? fallback).trim();

  function hashString(value) {
    let hash = 2166136261;
    const text = String(value);
    for (let index = 0; index < text.length; index += 1) {
      hash ^= text.charCodeAt(index);
      hash = Math.imul(hash, 16777619);
    }
    return hash >>> 0;
  }

  function hashHex(value, length = 16) {
    const text = String(value);
    const parts = [];
    let seed = hashString(text);
    for (let index = 0; parts.join('').length < length; index += 1) {
      seed = hashString(`${seed}:${text}:${index}`);
      parts.push(seed.toString(16).padStart(8, '0'));
    }
    return parts.join('').slice(0, length);
  }

  function mulberry32(seed) {
    let state = seed >>> 0;
    return () => {
      state += 0x6D2B79F5;
      let value = state;
      value = Math.imul(value ^ (value >>> 15), value | 1);
      value ^= value + Math.imul(value ^ (value >>> 7), value | 61);
      return ((value ^ (value >>> 14)) >>> 0) / 4294967296;
    };
  }

  function deterministicTimestamp(seed) {
    const base = Date.UTC(2026, 5, 23, 0, 0, 0);
    const offset = seed % (23 * 60 * 60 * 1000);
    return new Date(base + offset).toISOString();
  }

  function clear(node) {
    if (node) node.replaceChildren();
  }

  function appendText(parent, tag, className, text) {
    const node = el(tag, className, text);
    parent.appendChild(node);
    return node;
  }

  function option(value, label) {
    const node = el('option', '', label);
    node.value = value;
    return node;
  }

  function setupNavigation() {
    const toggle = byId('aan-nav-toggle');
    const nav = byId('aan-nav');
    if (!toggle || !nav) return;
    toggle.addEventListener('click', () => {
      const open = nav.classList.toggle('is-open');
      toggle.setAttribute('aria-expanded', String(open));
    });
    nav.querySelectorAll('a').forEach((link) => link.addEventListener('click', () => {
      nav.classList.remove('is-open');
      toggle.setAttribute('aria-expanded', 'false');
    }));
  }

  function renderArchitecture() {
    const translationGrid = byId('aan-translation-grid');
    const pipeline = byId('aan-arch-pipeline');
    const boundaryList = byId('aan-boundary-list');
    if (!translationGrid || !pipeline || !boundaryList) return false;

    clear(translationGrid);
    release.architecture_translation.forEach((item, index) => {
      const card = el('article', 'aan-translation-card');
      const legacy = el('div');
      appendText(legacy, 'span', '', `ORIGINAL ${pad(index + 1)}`);
      appendText(legacy, 'b', '', item.legacy);
      const arrow = el('i', '', '→');
      arrow.setAttribute('aria-hidden', 'true');
      const goalos = el('div');
      appendText(goalos, 'span', '', 'GOALOS ASCENSION');
      appendText(goalos, 'b', '', item.goalos);
      appendText(goalos, 'p', '', item.consequence);
      card.append(legacy, arrow, goalos);
      translationGrid.appendChild(card);
    });

    clear(pipeline);
    release.pipeline.forEach((stage) => {
      const item = el('li');
      appendText(item, 'span', '', pad(stage.order));
      appendText(item, 'b', '', stage.state);
      appendText(item, 'h3', '', stage.title);
      appendText(item, 'p', '', stage.gate);
      appendText(item, 'small', '', stage.artifact);
      pipeline.appendChild(item);
    });

    clear(boundaryList);
    release.claim_boundary.forEach((boundary, index) => {
      const item = el('li');
      appendText(item, 'span', '', `B${pad(index + 1)}`);
      appendText(item, 'p', '', boundary);
      boundaryList.appendChild(item);
    });
    return true;
  }

  const runtime = {
    runToken: 0,
    safeHold: false,
    phaseIndex: -1,
    seed: 0,
    deterministic_seed: '',
    config: null,
    peerRoute: null,
    receipt: null,
    evaluation: null,
    consensus: null,
    docket: null,
    brief: '',
    logs: [],
    started: false
  };

  const ids = {
    form: byId('aan-node-form'),
    preset: byId('aan-preset'),
    nodeName: byId('aan-node-name'),
    mission: byId('aan-mission'),
    workClass: byId('aan-work-class'),
    posture: byId('aan-posture'),
    quorum: byId('aan-quorum'),
    energy: byId('aan-energy'),
    latency: byId('aan-latency'),
    quorumOutput: byId('aan-quorum-output'),
    energyOutput: byId('aan-energy-output'),
    latencyOutput: byId('aan-latency-output'),
    run: byId('aan-run'),
    pause: byId('aan-pause'),
    reset: byId('aan-reset')
  };

  function renderHero() {
    const metrics = byId('aan-hero-metrics');
    const thesis = byId('aan-thesis-grid');
    if (metrics) {
      clear(metrics);
      release.hero_metrics.forEach((metric) => {
        const block = el('div');
        appendText(block, 'b', '', metric.value);
        appendText(block, 'span', '', metric.label);
        metrics.appendChild(block);
      });
    }
    if (thesis) {
      clear(thesis);
      release.thesis.forEach((item) => {
        const card = el('article');
        appendText(card, 'span', 'number', item.number);
        appendText(card, 'h3', '', item.title);
        appendText(card, 'p', '', item.copy);
        thesis.appendChild(card);
      });
    }
  }

  function renderControls() {
    release.presets.forEach((item) => ids.preset.appendChild(option(item.id, item.label)));
    release.work_unit_classes.forEach((item) => ids.workClass.appendChild(option(item.id, `${item.symbol} · ${item.label}`)));
    release.postures.forEach((item) => ids.posture.appendChild(option(item.id, item.label)));
    ids.preset.value = release.presets[0].id;
    ids.posture.value = 'ascension';
    applyPreset(ids.preset.value);
    syncRangeOutputs();
  }

  function applyPreset(presetId) {
    const preset = release.presets.find((item) => item.id === presetId) || release.presets[0];
    ids.mission.value = preset.mission;
    ids.workClass.value = preset.work_class;
  }

  function syncRangeOutputs() {
    ids.quorumOutput.value = `${ids.quorum.value} / 7`;
    ids.quorumOutput.textContent = `${ids.quorum.value} / 7`;
    ids.energyOutput.value = `${(Number(ids.energy.value) / 100).toFixed(2)} score`;
    ids.energyOutput.textContent = `${(Number(ids.energy.value) / 100).toFixed(2)} score`;
    ids.latencyOutput.value = `${ids.latency.value} ms`;
    ids.latencyOutput.textContent = `${ids.latency.value} ms`;
  }

  function renderStageRail() {
    const rail = byId('aan-stage-rail');
    clear(rail);
    release.pipeline.forEach((stage, index) => {
      const node = el('div', 'aan-stage');
      node.dataset.stage = String(index);
      appendText(node, 'span', '', pad(stage.order));
      appendText(node, 'b', '', stage.state.replaceAll('_', ' '));
      rail.appendChild(node);
    });
  }

  function setStage(index) {
    runtime.phaseIndex = index;
    doc.querySelectorAll('.aan-stage').forEach((node, nodeIndex) => {
      node.classList.toggle('is-complete', nodeIndex < index || (index === release.pipeline.length && nodeIndex < index));
      node.classList.toggle('is-active', nodeIndex === index);
    });
  }

  function renderInitialPeers() {
    runtime.peerRoute = {
      peers: release.peers.map((peer) => ({ ...peer, latency: peer.base_latency, energy: peer.base_energy, reliability: peer.base_reliability, status: 'standby', reason: 'Awaiting a contracted work unit.' })),
      admitted: [],
      rejected: [],
      standby: release.peers.map((peer) => peer.id)
    };
    renderPeerRoute(runtime.peerRoute, true);
  }

  function createPeerRoute(config, rng) {
    const peers = release.peers.map((peer) => {
      const capabilityFit = peer.capabilities.includes(config.workClass.capability);
      const latency = Math.max(26, Math.round(peer.base_latency + (rng() - 0.5) * 18));
      const energy = round(clamp(peer.base_energy + (rng() - 0.5) * 0.12, 0.42, 0.92), 2);
      const reliability = round(clamp(peer.base_reliability + (rng() - 0.5) * 0.018, 0.91, 0.997), 3);
      const latencyFit = latency <= config.latency;
      const energyFit = energy >= config.energyTarget;
      const roleBoost = peer.role === 'Verifier' || peer.role === 'Guardian' ? 0.05 : 0;
      const score = (capabilityFit ? 0.35 : 0) + clamp(1 - latency / 180, 0, 1) * 0.2 + energy * 0.2 + reliability * 0.2 + roleBoost;
      return { ...peer, latency, energy, reliability, capabilityFit, latencyFit, energyFit, score: round(score, 4), status: 'rejected', reason: '' };
    });

    const ranked = [...peers].sort((a, b) => b.score - a.score || a.id.localeCompare(b.id));
    const requiredRoles = new Set(['Orchestrator', 'Verifier']);
    const selected = new Set();

    requiredRoles.forEach((role) => {
      const match = ranked.find((peer) => peer.role === role && peer.capabilityFit && peer.latency <= config.latency + 18);
      if (match) selected.add(match.id);
    });
    ranked.forEach((peer) => {
      if (selected.size < 4 && peer.capabilityFit && peer.latencyFit && (peer.energyFit || peer.energy >= config.energyTarget - 0.1)) selected.add(peer.id);
    });
    ranked.forEach((peer) => {
      if (selected.size < 3 && peer.capabilityFit) selected.add(peer.id);
    });
    if (!Array.from(selected).some((id) => peers.find((peer) => peer.id === id)?.role === 'Verifier')) {
      const verifier = ranked.find((peer) => peer.role === 'Verifier');
      if (verifier) selected.add(verifier.id);
    }

    peers.forEach((peer) => {
      if (selected.has(peer.id)) {
        peer.status = 'accepted';
        peer.reason = `Admitted: ${peer.capabilityFit ? 'capability fit' : 'fallback fit'}, ${peer.latency} ms, energy ${peer.energy.toFixed(2)}.`;
      } else if (peer.capabilityFit && (peer.latency <= config.latency + 20 || peer.energy >= config.energyTarget - 0.08)) {
        peer.status = 'standby';
        peer.reason = 'Held as a reversible fallback; not needed by the minimum route.';
      } else {
        peer.status = 'rejected';
        const reasons = [];
        if (!peer.capabilityFit) reasons.push(`missing ${config.workClass.capability} capability`);
        if (!peer.latencyFit) reasons.push(`latency exceeds ${config.latency} ms`);
        if (!peer.energyFit) reasons.push(`energy score below ${config.energyTarget.toFixed(2)}`);
        peer.reason = `Rejected: ${reasons.join('; ') || 'lower policy-adjusted route score'}.`;
      }
    });

    const admitted = peers.filter((peer) => peer.status === 'accepted');
    const standby = peers.filter((peer) => peer.status === 'standby');
    const rejected = peers.filter((peer) => peer.status === 'rejected');
    const averageLatency = admitted.reduce((sum, peer) => sum + peer.latency, 0) / admitted.length;
    const averageEnergy = admitted.reduce((sum, peer) => sum + peer.energy, 0) / admitted.length;
    const averageReliability = admitted.reduce((sum, peer) => sum + peer.reliability, 0) / admitted.length;

    return {
      route_id: `route_${hashHex(`${config.commitment}:peers`, 12)}`,
      deterministic_seed: config.deterministic_seed,
      peers,
      admitted: admitted.map((peer) => peer.id),
      standby: standby.map((peer) => peer.id),
      rejected: rejected.map((peer) => peer.id),
      route_metrics: {
        average_latency_ms: round(averageLatency, 1),
        average_energy_score: round(averageEnergy, 3),
        average_reliability: round(averageReliability, 4),
        admitted_count: admitted.length,
        standby_count: standby.length,
        rejected_count: rejected.length
      },
      external_connections: 0,
      mode: 'deterministic_browser_simulation'
    };
  }

  function renderPeerRoute(route, initial = false) {
    const table = byId('aan-peer-table');
    const mesh = byId('aan-mesh-svg');
    clear(table);
    clear(mesh);

    route.peers.forEach((peer) => {
      const row = el('tr');
      const name = el('td', '', peer.name);
      name.title = peer.reason;
      row.append(name, el('td', '', peer.role), el('td', '', `${peer.latency} ms`), el('td', '', peer.energy.toFixed(2)));
      const statusCell = el('td');
      statusCell.appendChild(el('span', `aan-peer-status ${peer.status}`, peer.status.toUpperCase()));
      row.appendChild(statusCell);
      table.appendChild(row);
    });

    const defs = svgEl('defs');
    const gradient = svgEl('radialGradient', { id: 'aan-mesh-core-gradient', cx: '50%', cy: '40%', r: '65%' });
    gradient.append(svgEl('stop', { offset: '0', 'stop-color': '#fff9c6' }), svgEl('stop', { offset: '.45', 'stop-color': '#ffd95d' }), svgEl('stop', { offset: '1', 'stop-color': '#7c47ff' }));
    defs.appendChild(gradient);
    mesh.appendChild(defs);
    const positions = [[390, 62], [610, 130], [700, 315], [585, 480], [390, 510], [190, 480], [78, 315], [170, 128]];
    route.peers.forEach((peer, index) => {
      const [x, y] = positions[index];
      mesh.appendChild(svgEl('line', { x1: 390, y1: 285, x2: x, y2: y, class: `aan-mesh-line ${peer.status}` }));
    });
    const core = svgEl('g', { class: 'aan-mesh-core', transform: 'translate(390 285)' });
    core.append(svgEl('circle', { r: 62 }), svgEl('text', { y: 8 }));
    core.querySelector('text').textContent = 'α';
    const sub = svgEl('text', { class: 'sub', y: 31 });
    sub.textContent = 'NODE NΩ-01';
    core.appendChild(sub);
    mesh.appendChild(core);
    route.peers.forEach((peer, index) => {
      const [x, y] = positions[index];
      const group = svgEl('g', { class: `aan-mesh-node ${peer.status}`, transform: `translate(${x} ${y})` });
      group.appendChild(svgEl('circle', { r: 42 }));
      const name = svgEl('text', { y: 1 });
      name.textContent = peer.name.toUpperCase();
      const role = svgEl('text', { class: 'role', y: 19 });
      role.textContent = peer.role.toUpperCase();
      group.append(name, role);
      mesh.appendChild(group);
    });

    const status = byId('aan-mesh-status');
    const summary = byId('aan-route-summary');
    if (initial) {
      status.textContent = 'awaiting route';
      clear(summary);
      appendText(summary, 'b', '', 'No route committed.');
      appendText(summary, 'span', '', 'Run a governed cycle to generate the Resource Envelope and Peer Route.');
    } else {
      status.textContent = `${route.admitted.length} admitted · ${route.standby.length} standby · ${route.rejected.length} rejected`;
      clear(summary);
      appendText(summary, 'b', '', `${route.admitted.length} peers admitted under route ${route.route_id}.`);
      appendText(summary, 'span', '', `Mean latency ${route.route_metrics.average_latency_ms} ms · energy ${route.route_metrics.average_energy_score.toFixed(3)} · reliability ${(route.route_metrics.average_reliability * 100).toFixed(2)}%. Every non-selected peer retains an inspectable rationale.`);
    }
  }

  function calculateAlphaWorkUnit(config, route, rng) {
    const gpuSeconds = round(11 + rng() * 14 + route.admitted.length * 1.4, 2);
    const throughputNorm = round(0.86 + rng() * 0.27, 3);
    const sloPass = route.route_metrics.average_latency_ms <= config.latency ? 1 : 0.88;
    const routeQuality = clamp(0.66 + route.route_metrics.average_reliability * 0.18 + route.route_metrics.average_energy_score * 0.12 + rng() * 0.06, 0.78, 0.98);
    const quality = round(routeQuality, 3);
    const value = round(gpuSeconds * throughputNorm * config.workClass.model_tier * sloPass * quality, 3);
    const executionMs = Math.round(1680 + rng() * 2600 + route.admitted.length * 170);
    const energyKwh = round(gpuSeconds * (1.08 - route.route_metrics.average_energy_score) * 0.011, 4);
    return {
      receipt_id: `awu_${hashHex(`${config.commitment}:receipt`, 14)}`,
      work_unit_class: config.workClass.id,
      work_unit_symbol: config.workClass.symbol,
      gpu_seconds: gpuSeconds,
      throughput_normalized: throughputNorm,
      model_tier: config.workClass.model_tier,
      slo_pass_multiplier: sloPass,
      quality_multiplier: quality,
      alpha_work_units: value,
      execution_time_ms: executionMs,
      estimated_energy_kwh: energyKwh,
      external_compute_calls: 0,
      mode: 'deterministic_sandbox_receipt'
    };
  }

  function createEvaluation(config, route, receipt, rng) {
    const evidence = round(clamp(0.86 + rng() * 0.1, 0, 0.98), 3);
    const quality = round(clamp(receipt.quality_multiplier + (rng() - 0.5) * 0.04, 0.76, 0.98), 3);
    const reliability = round(route.route_metrics.average_reliability, 3);
    const energy = round(route.route_metrics.average_energy_score, 3);
    const latency = round(clamp(1 - route.route_metrics.average_latency_ms / 210, 0.5, 0.96), 3);
    const weights = config.posture.weights;
    const composite = round(quality * weights.quality + reliability * weights.reliability + energy * weights.energy + latency * weights.latency + evidence * weights.evidence, 3);
    return {
      evaluation_id: `eval_${hashHex(`${config.commitment}:quality`, 12)}`,
      posture: config.posture.id,
      dimensions: { quality, reliability, energy, latency, evidence },
      weights,
      composite,
      slo_pass: receipt.slo_pass_multiplier === 1,
      uncertainty: round(0.08 + rng() * 0.07, 3),
      contradiction: {
        title: 'Capability evidence remains simulated.',
        severity: 'material review reservation',
        statement: 'The cycle demonstrates structural completeness and deterministic traceability, but it does not establish live peer performance, factual correctness, production security, legal fitness, or economic value.'
      },
      factual_correctness: 'NOT_CERTIFIED'
    };
  }

  function createValidatorConsensus(config, evaluation, rng) {
    const threshold = config.quorum;
    const dissentIndex = release.validators.findIndex((validator) => validator.id === 'v6');
    let supportNeeded = Math.max(0, threshold - 1);
    const votes = release.validators.map((validator, index) => {
      if (index === dissentIndex) {
        return {
          validator_id: validator.id,
          name: validator.name,
          symbol: validator.symbol,
          status: 'dissent',
          supports_quorum: true,
          score: round(clamp(evaluation.composite - 0.07, 0.68, 0.93), 3),
          rationale: 'Supports structural review readiness while preserving a material reservation: simulated evidence cannot certify live capability or factual correctness.'
        };
      }
      if (supportNeeded > 0) {
        supportNeeded -= 1;
        return {
          validator_id: validator.id,
          name: validator.name,
          symbol: validator.symbol,
          status: 'pass',
          supports_quorum: true,
          score: round(clamp(evaluation.composite + (rng() - 0.5) * 0.08, 0.72, 0.98), 3),
          rationale: `${validator.focus} is structurally represented with explicit limitations and review boundaries.`
        };
      }
      return {
        validator_id: validator.id,
        name: validator.name,
        symbol: validator.symbol,
        status: 'fail',
        supports_quorum: false,
        score: round(clamp(evaluation.composite - 0.13 - rng() * 0.05, 0.55, 0.83), 3),
        rationale: `Seat withholds support pending independent live evidence for ${validator.focus}.`
      };
    });
    const supportCount = votes.filter((vote) => vote.supports_quorum).length;
    return {
      consensus_id: `consensus_${hashHex(`${config.commitment}:validators`, 12)}`,
      threshold,
      seats: votes.length,
      support_count: supportCount,
      quorum_recorded: supportCount >= threshold,
      dissent_preserved: votes.some((vote) => vote.status === 'dissent'),
      votes,
      authority_conferred: false,
      factual_correctness: 'NOT_CERTIFIED'
    };
  }

  function buildNodeEvidenceDocket(config, route, receipt, evaluation, consensus) {
    const artifactHashes = release.artifacts.map((name, index) => ({
      name,
      sha256_simulated: hashHex(`${config.commitment}:${name}:${index}`, 64),
      status: 'SEALED_IN_LOCAL_SIMULATION'
    }));
    return {
      schema: 'goalos.agi_alpha_node_v0.node_evidence_docket.v1',
      release: release.release_title,
      release_version: release.version,
      run_id: config.runId,
      deterministic_seed: config.deterministic_seed,
      generated_at_simulated: config.timestamp,
      mode: 'browser_local_deterministic_simulation',
      node_identity: {
        declared_name: config.nodeName,
        identity_status: 'DECLARED_NOT_RESOLVED',
        ens_resolution_performed: false,
        operator_authority_proven: false
      },
      work_unit_contract: {
        mission: config.mission,
        decision: config.preset.decision,
        class: config.workClass,
        posture: config.posture.id,
        success_criteria: [
          'All eight GoalOS node states are represented.',
          'Every peer receives a visible admission rationale.',
          'Work, energy, quality, contradiction, validator, and authorization artifacts are sealed.',
          'All external permissions remain absent.'
        ],
        stop_rules: ['safe hold requested', 'mission scope becomes ambiguous', 'quorum not recorded', 'external authority would be required']
      },
      resource_envelope: {
        validator_quorum: config.quorum,
        energy_target: config.energyTarget,
        latency_ceiling_ms: config.latency,
        maximum_admitted_peers: 5,
        external_credentials: 0
      },
      peer_route: route,
      work_unit_receipt: receipt,
      quality_evaluation: evaluation,
      validator_consensus: consensus,
      guardian_council: {
        threshold: 4,
        review_signatures_simulated: 4,
        treasury_guardian_signed: false,
        external_authority_granted: false,
        transaction_broadcast: false
      },
      authorization_state: {
        state: 'HUMAN_REVIEW_REQUIRED',
        authority: 'NONE_GRANTED',
        factual_correctness: 'NOT_CERTIFIED',
        production_activation: 'NOT_ACTIVATED',
        funds_authorization: 'NO',
        settlement: 'NONE',
        external_actions: 0
      },
      claim_boundary: release.claim_boundary,
      security: release.security,
      artifact_chain: artifactHashes,
      chronicle: {
        terminal_events: [...runtime.logs],
        persistence: 'NONE_AFTER_BROWSER_SESSION',
        network_transmission: 'NONE'
      }
    };
  }

  function createReviewBrief(docket) {
    const route = docket.peer_route.route_metrics;
    const receipt = docket.work_unit_receipt;
    const consensus = docket.validator_consensus;
    return [
      '# GoalOS AGIALPHA Ascension AGI Alpha Node v0 — Executive Review Brief',
      '',
      `**Run:** ${docket.run_id}`,
      `**Deterministic seed:** ${docket.deterministic_seed}`,
      `**Final state:** ${docket.authorization_state.state}`,
      '',
      '## Mission',
      docket.work_unit_contract.mission,
      '',
      '## Simulated node result',
      `- ${route.admitted_count} peers admitted; ${route.standby_count} standby; ${route.rejected_count} rejected.`,
      `- Mean route latency: ${route.average_latency_ms} ms.`,
      `- Mean energy score: ${route.average_energy_score}.`,
      `- Normalized Alpha Work Units: ${receipt.alpha_work_units}.`,
      `- Validator support: ${consensus.support_count}/${consensus.seats}; threshold ${consensus.threshold}.`,
      `- Dissent preserved: ${consensus.dissent_preserved ? 'yes' : 'no'}.`,
      '',
      '## Authority boundary',
      '- Factual correctness: NOT CERTIFIED.',
      '- Production activation: NOT ACTIVATED.',
      '- Funds authorization: NO.',
      '- External actions: 0.',
      '- Authority: NONE GRANTED.',
      '',
      'This package is a deterministic browser-local design and review artifact. It is not evidence of a live node, AGI, production performance, security certification, ENS ownership, treasury authorization, or economic settlement.'
    ].join('\n');
  }

  function renderValidators(consensus = null) {
    const grid = byId('aan-validator-grid');
    clear(grid);
    release.validators.forEach((validator) => {
      const vote = consensus?.votes.find((item) => item.validator_id === validator.id);
      const card = el('article', `aan-validator-card${vote ? ` ${vote.status}` : ''}`);
      appendText(card, 'span', 'symbol', validator.symbol);
      appendText(card, 'h3', '', validator.name);
      appendText(card, 'p', '', vote ? vote.rationale : validator.focus);
      const voteNode = el('div', 'vote');
      voteNode.appendChild(el('i'));
      let label = 'AWAITING';
      if (vote?.status === 'pass') label = `SUPPORT · ${Math.round(vote.score * 100)}`;
      if (vote?.status === 'dissent') label = `DISSENT / SUPPORT · ${Math.round(vote.score * 100)}`;
      if (vote?.status === 'fail') label = `HOLD · ${Math.round(vote.score * 100)}`;
      voteNode.appendChild(doc.createTextNode(label));
      card.appendChild(voteNode);
      grid.appendChild(card);
    });
    const ring = byId('aan-quorum-ring');
    const label = byId('aan-quorum-label');
    if (consensus) {
      ring.textContent = `${consensus.support_count}/7`;
      label.textContent = consensus.quorum_recorded ? `QUORUM ${consensus.threshold} RECORDED` : 'QUORUM NOT MET';
    } else {
      ring.textContent = '0/7';
      label.textContent = 'AWAITING VOTES';
    }
  }

  function renderGuardians(signedCount = 0) {
    const row = byId('aan-guardian-row');
    clear(row);
    release.guardians.forEach((guardian, index) => {
      const node = el('span', `aan-guardian${index < signedCount ? ' signed' : ''}`, guardian.symbol);
      node.title = `${guardian.name}${index < signedCount ? ' — simulated review signature' : ' — unsigned'}`;
      row.appendChild(node);
    });
  }

  function renderArtifacts(sealedCount = 0) {
    const list = byId('aan-artifact-list');
    clear(list);
    release.artifacts.forEach((artifact, index) => {
      list.appendChild(el('li', index < sealedCount ? 'sealed' : '', artifact));
    });
    byId('aan-artifact-count').textContent = `${sealedCount} / ${release.artifacts.length} sealed`;
  }

  function setReceipt(receipt = null) {
    byId('aan-receipt-hash').textContent = receipt ? receipt.receipt_id : 'not generated';
    byId('aan-receipt-class').textContent = receipt ? `${receipt.work_unit_symbol} · ${receipt.work_unit_class.toUpperCase()}` : '—';
    byId('aan-receipt-wu').textContent = receipt ? receipt.alpha_work_units.toFixed(3) : '—';
    byId('aan-receipt-time').textContent = receipt ? `${receipt.execution_time_ms.toLocaleString()} ms` : '—';
    byId('aan-receipt-energy').textContent = receipt ? `${receipt.estimated_energy_kwh.toFixed(4)} kWh` : '—';
    byId('aan-receipt-slo').textContent = receipt ? (receipt.slo_pass_multiplier === 1 ? 'YES' : 'CONDITIONAL') : '—';
  }

  function setLiveMetrics(receipt = null, evaluation = null, consensus = null, route = null) {
    byId('aan-metric-wu').textContent = receipt ? receipt.alpha_work_units.toFixed(3) : '—';
    byId('aan-metric-quality').textContent = evaluation ? `${Math.round(evaluation.dimensions.quality * 100)}%` : '—';
    byId('aan-metric-energy').textContent = route ? route.route_metrics.average_energy_score.toFixed(3) : '—';
    byId('aan-metric-quorum').textContent = consensus ? `${consensus.support_count}/7` : '—';
  }

  function setPulse(values = []) {
    const line = byId('aan-pulse-line');
    const area = byId('aan-pulse-area');
    const points = byId('aan-pulse-points');
    clear(points);
    if (!values.length) {
      line.setAttribute('d', 'M30 190L650 190');
      area.setAttribute('d', 'M30 190L650 190L650 190L30 190Z');
      return;
    }
    const width = 620;
    const coords = values.map((value, index) => {
      const x = 30 + (values.length === 1 ? 0 : index * width / (values.length - 1));
      const y = 195 - clamp(value, 0, 1) * 150;
      return [round(x, 1), round(y, 1)];
    });
    const path = coords.map(([x, y], index) => `${index ? 'L' : 'M'}${x} ${y}`).join('');
    line.setAttribute('d', path);
    area.setAttribute('d', `${path}L${coords[coords.length - 1][0]} 195L${coords[0][0]} 195Z`);
    coords.forEach(([x, y]) => points.appendChild(svgEl('circle', { class: 'aan-pulse-point', cx: x, cy: y, r: 5 })));
  }

  function logEvent(message, type = '') {
    const index = runtime.logs.length;
    const elapsed = `${pad(Math.floor(index / 60))}:${pad(index % 60)}`;
    runtime.logs.push({ sequence: index + 1, elapsed, message, type: type || 'info' });
    const terminal = byId('aan-terminal');
    const item = el('li', type ? `is-${type}` : '');
    item.append(el('time', '', elapsed), el('span', '', message));
    terminal.appendChild(item);
    terminal.scrollTop = terminal.scrollHeight;
  }

  function clearTerminal() {
    runtime.logs = [];
    const terminal = byId('aan-terminal');
    clear(terminal);
  }

  function setRuntimeState(state, copy, mode = 'active') {
    const banner = byId('aan-state-banner');
    const stateNode = banner.querySelector('b');
    const copyNode = banner.querySelector('p');
    stateNode.textContent = state;
    copyNode.textContent = copy;
    banner.classList.toggle('is-complete', state === 'HUMAN_REVIEW_REQUIRED');
    byId('aan-runtime-mode').textContent = mode === 'hold' ? 'SAFE HOLD / DEFAULT DENY' : state === 'HUMAN_REVIEW_REQUIRED' ? 'EVIDENCE DOCKET COMPLETE' : `CYCLE / ${state.replaceAll('_', ' ')}`;
    const dot = byId('aan-runtime-dot');
    dot.classList.toggle('is-hold', mode === 'hold');
  }

  function collectConfig() {
    const preset = release.presets.find((item) => item.id === ids.preset.value) || release.presets[0];
    const workClass = release.work_unit_classes.find((item) => item.id === ids.workClass.value) || release.work_unit_classes[0];
    const posture = release.postures.find((item) => item.id === ids.posture.value) || release.postures[0];
    const nodeName = safeText(ids.nodeName.value, '1.alpha.node.agi.eth').slice(0, 72);
    const mission = safeText(ids.mission.value, preset.mission).slice(0, 640);
    const quorum = Number(ids.quorum.value);
    const energyTarget = Number(ids.energy.value) / 100;
    const latency = Number(ids.latency.value);
    const seedMaterial = [release.release_id, nodeName, mission, preset.id, workClass.id, posture.id, quorum, energyTarget, latency].join('|');
    const seed = hashString(seedMaterial);
    const deterministic_seed = `0x${hashHex(seedMaterial, 16)}`;
    const runId = `node_${hashHex(`${seedMaterial}:run`, 14)}`;
    return {
      preset,
      workClass,
      posture,
      nodeName,
      mission,
      quorum,
      energyTarget,
      latency,
      seed,
      deterministic_seed,
      commitment: `sha256:${hashHex(seedMaterial, 64)}`,
      runId,
      timestamp: deterministicTimestamp(seed)
    };
  }

  const sleep = (ms) => new Promise((resolve) => window.setTimeout(resolve, ms));

  async function runCycle(event) {
    event.preventDefault();
    if (runtime.safeHold) return;
    const config = collectConfig();
    if (config.mission.length < 20) {
      ids.mission.focus();
      setRuntimeState('MISSION_REQUIRES_DETAIL', 'Describe a consequential work unit in at least 20 characters.', 'hold');
      return;
    }

    const token = ++runtime.runToken;
    runtime.started = true;
    runtime.config = config;
    runtime.seed = config.seed;
    runtime.deterministic_seed = config.deterministic_seed;
    runtime.peerRoute = null;
    runtime.receipt = null;
    runtime.evaluation = null;
    runtime.consensus = null;
    runtime.docket = null;
    runtime.brief = '';
    ids.run.disabled = true;
    ids.pause.disabled = false;
    byId('aan-run-id').textContent = `${config.runId} / ${config.deterministic_seed}`;
    byId('aan-authority').textContent = 'NONE GRANTED';
    byId('aan-hero-status').textContent = 'PROOF CYCLE';
    clearTerminal();
    renderValidators();
    renderGuardians(0);
    renderArtifacts(0);
    setReceipt();
    setLiveMetrics();
    setPulse([]);
    byId('aan-download-json').disabled = true;
    byId('aan-download-md').disabled = true;
    byId('aan-copy-summary').disabled = true;
    byId('aan-final-state').textContent = 'IN PROGRESS';
    byId('aan-final-copy').textContent = 'The node is assembling a structural evidence package.';
    byId('aan-review-headline').textContent = 'A governed cycle is in progress.';
    byId('aan-review-summary').textContent = 'Evidence remains incomplete and all external authority is withheld.';
    byId('aan-export-status').textContent = '';
    doc.querySelector('.aan-auth-card')?.classList.remove('is-ready');
    const rng = mulberry32(config.seed);
    const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const delay = reduced ? 20 : 190;
    const pulse = [];
    const artifactCounts = [1, 2, 3, 4, 7, 9, 11, 14];

    const stages = [
      () => {
        logEvent(`Identity commitment ${config.commitment.slice(0, 24)}… bound to declared node ${config.nodeName}.`, 'good');
        pulse.push(0.36 + rng() * 0.08);
      },
      () => {
        logEvent(`Work unit contracted as ${config.workClass.symbol} / ${config.workClass.label}; scope expansion prohibited.`, 'good');
        pulse.push(0.44 + rng() * 0.08);
      },
      () => {
        logEvent(`Resource envelope admitted: latency ≤ ${config.latency} ms, energy ≥ ${config.energyTarget.toFixed(2)}, quorum ${config.quorum}/7.`, 'good');
        pulse.push(0.53 + rng() * 0.08);
      },
      () => {
        runtime.peerRoute = createPeerRoute(config, rng);
        renderPeerRoute(runtime.peerRoute);
        logEvent(`${runtime.peerRoute.admitted.length} peers admitted; ${runtime.peerRoute.rejected.length} rejected with rationale; external connections 0.`, 'good');
        pulse.push(0.62 + rng() * 0.08);
      },
      () => {
        runtime.receipt = calculateAlphaWorkUnit(config, runtime.peerRoute, rng);
        setReceipt(runtime.receipt);
        setLiveMetrics(runtime.receipt, null, null, runtime.peerRoute);
        logEvent(`Sandbox receipt ${runtime.receipt.receipt_id} produced ${runtime.receipt.alpha_work_units.toFixed(3)} α-WU; live compute calls 0.`, 'good');
        pulse.push(0.72 + rng() * 0.07);
      },
      () => {
        runtime.evaluation = createEvaluation(config, runtime.peerRoute, runtime.receipt, rng);
        setLiveMetrics(runtime.receipt, runtime.evaluation, null, runtime.peerRoute);
        byId('aan-contradiction-title').textContent = runtime.evaluation.contradiction.title;
        byId('aan-contradiction-copy').textContent = runtime.evaluation.contradiction.statement;
        logEvent(`Quality evaluation ${Math.round(runtime.evaluation.composite * 100)} / 100 recorded; factual correctness NOT CERTIFIED.`, 'warn');
        pulse.push(0.79 + rng() * 0.06);
      },
      () => {
        runtime.consensus = createValidatorConsensus(config, runtime.evaluation, rng);
        renderValidators(runtime.consensus);
        setLiveMetrics(runtime.receipt, runtime.evaluation, runtime.consensus, runtime.peerRoute);
        renderGuardians(4);
        byId('aan-guardian-copy').textContent = 'Four simulated review signatures are recorded. The Treasury Guardian remains unsigned; no transaction, settlement, or external permission can be produced by this experience.';
        logEvent(`Validator support ${runtime.consensus.support_count}/7 meets threshold ${runtime.consensus.threshold}; dissent preserved; authority conferred false.`, 'warn');
        pulse.push(0.86 + rng() * 0.05);
      },
      () => {
        runtime.docket = buildNodeEvidenceDocket(config, runtime.peerRoute, runtime.receipt, runtime.evaluation, runtime.consensus);
        runtime.brief = createReviewBrief(runtime.docket);
        byId('aan-final-state').textContent = 'HUMAN_REVIEW_REQUIRED';
        byId('aan-final-copy').textContent = 'Fourteen artifacts are sealed. Production, funds, settlement, and external actions remain explicitly absent.';
        byId('aan-review-headline').textContent = 'The proof package is complete. Authority remains withheld.';
        byId('aan-review-summary').textContent = `${runtime.peerRoute.admitted.length} peers were admitted, ${runtime.receipt.alpha_work_units.toFixed(3)} normalized α-WU were simulated, and ${runtime.consensus.support_count}/7 validator seats supported review readiness with dissent preserved. This is not factual or production certification.`;
        byId('aan-download-json').disabled = false;
        byId('aan-download-md').disabled = false;
        byId('aan-copy-summary').disabled = false;
        doc.querySelector('.aan-auth-card')?.classList.add('is-ready');
        logEvent('Evidence Docket complete. HUMAN_REVIEW_REQUIRED. External actions 0. Authority NONE GRANTED.', 'hold');
        pulse.push(0.91 + rng() * 0.04);
      }
    ];

    for (let index = 0; index < stages.length; index += 1) {
      if (token !== runtime.runToken || runtime.safeHold) return;
      setStage(index);
      const stage = release.pipeline[index];
      byId('aan-terminal-state').textContent = `${pad(index + 1)} / ${pad(stages.length)} · ${stage.agent}`;
      setRuntimeState(stage.state, stage.output);
      stages[index]();
      renderArtifacts(artifactCounts[index]);
      setPulse(pulse);
      await sleep(delay);
    }

    if (token !== runtime.runToken || runtime.safeHold) return;
    setStage(release.pipeline.length);
    setRuntimeState('HUMAN_REVIEW_REQUIRED', 'Evidence is ready for qualified human judgment. All external permissions remain absent.');
    byId('aan-terminal-state').textContent = 'complete / review hold';
    byId('aan-hero-status').textContent = 'REVIEW PACKAGE';
    ids.run.disabled = false;
    window.__AAN_QA__ = {
      getState: () => ({ ...runtime, docket: runtime.docket }),
      getDocket: () => runtime.docket,
      deterministic_seed: config.deterministic_seed,
      external_actions: 0,
      authority: 'NONE_GRANTED',
      factual_correctness: 'NOT_CERTIFIED'
    };
  }

  function toggleSafeHold() {
    runtime.safeHold = !runtime.safeHold;
    runtime.runToken += 1;
    ids.pause.textContent = runtime.safeHold ? 'Release safe hold' : 'Place on safe hold';
    ids.run.disabled = runtime.safeHold;
    if (runtime.safeHold) {
      setStage(-1);
      setRuntimeState('SAFE_HOLD', 'The local cycle is paused. No authority, network, compute, wallet, transaction, or settlement action exists.', 'hold');
      byId('aan-terminal-state').textContent = 'safe hold';
      logEvent('Safe hold engaged. Default deny remains in force.', 'hold');
    } else {
      setRuntimeState('READY_FOR_MISSION', 'Safe hold released. A new bounded local cycle may be composed.');
      byId('aan-terminal-state').textContent = 'idle';
      logEvent('Safe hold released. No previous cycle resumed automatically.', 'warn');
    }
  }

  function resetRuntime() {
    runtime.runToken += 1;
    runtime.safeHold = false;
    runtime.phaseIndex = -1;
    runtime.config = null;
    runtime.peerRoute = null;
    runtime.receipt = null;
    runtime.evaluation = null;
    runtime.consensus = null;
    runtime.docket = null;
    runtime.brief = '';
    ids.pause.textContent = 'Place on safe hold';
    ids.run.disabled = false;
    byId('aan-run-id').textContent = 'Awaiting mission';
    byId('aan-authority').textContent = 'NONE GRANTED';
    byId('aan-hero-status').textContent = 'REVIEW MODE';
    setStage(-1);
    clearTerminal();
    logEvent('Node cycle is ready. Compose a bounded work unit.');
    renderInitialPeers();
    renderValidators();
    renderGuardians(0);
    renderArtifacts(0);
    setReceipt();
    setLiveMetrics();
    setPulse([]);
    setRuntimeState('READY_FOR_MISSION', 'All external authority is withheld.');
    byId('aan-terminal-state').textContent = 'idle';
    byId('aan-contradiction-title').textContent = 'No evaluation yet.';
    byId('aan-contradiction-copy').textContent = 'The Contradiction Validator will preserve the strongest dissent after a cycle runs.';
    byId('aan-guardian-copy').textContent = 'Guardian seats remain unsigned until a review package exists. Even a complete simulated threshold cannot broadcast a transaction.';
    byId('aan-final-state').textContent = 'NOT GENERATED';
    byId('aan-final-copy').textContent = 'Run a governed cycle to assemble the docket.';
    byId('aan-review-headline').textContent = 'The node is ready to receive a bounded mission.';
    byId('aan-review-summary').textContent = 'No work-unit claim, resource route, validator result, or authorization state has been generated.';
    byId('aan-download-json').disabled = true;
    byId('aan-download-md').disabled = true;
    byId('aan-copy-summary').disabled = true;
    byId('aan-export-status').textContent = '';
    doc.querySelector('.aan-auth-card')?.classList.remove('is-ready');
    window.__AAN_QA__ = {
      getState: () => ({ ...runtime }),
      getDocket: () => runtime.docket,
      deterministic_seed: '',
      external_actions: 0,
      authority: 'NONE_GRANTED',
      factual_correctness: 'NOT_CERTIFIED'
    };
  }

  function downloadFile(filename, content, type) {
    const blob = new Blob([content], { type });
    const url = URL.createObjectURL(blob);
    const anchor = el('a');
    anchor.href = url;
    anchor.download = filename;
    anchor.hidden = true;
    doc.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
    window.setTimeout(() => URL.revokeObjectURL(url), 0);
  }

  function exportJson() {
    if (!runtime.docket) return;
    downloadFile(`${runtime.config.runId}-NodeEvidenceDocket.json`, `${JSON.stringify(runtime.docket, null, 2)}\n`, 'application/json');
    byId('aan-export-status').textContent = 'Evidence Docket downloaded locally. Nothing was transmitted.';
  }

  function exportMarkdown() {
    if (!runtime.brief) return;
    downloadFile(`${runtime.config.runId}-ExecutiveReviewBrief.md`, `${runtime.brief}\n`, 'text/markdown');
    byId('aan-export-status').textContent = 'Executive review brief downloaded locally.';
  }

  async function copySummary() {
    if (!runtime.brief) return;
    const summary = runtime.brief;
    try {
      await navigator.clipboard.writeText(summary);
      byId('aan-export-status').textContent = 'Review summary copied to the clipboard.';
    } catch (_) {
      const area = el('textarea');
      area.value = summary;
      area.setAttribute('readonly', '');
      area.style.position = 'fixed';
      area.style.opacity = '0';
      doc.body.appendChild(area);
      area.select();
      doc.execCommand('copy');
      area.remove();
      byId('aan-export-status').textContent = 'Review summary copied to the clipboard.';
    }
  }

  function setupExperience() {
    if (!ids.form) return false;
    renderHero();
    renderControls();
    renderStageRail();
    resetRuntime();
    ids.preset.addEventListener('change', () => applyPreset(ids.preset.value));
    [ids.quorum, ids.energy, ids.latency].forEach((input) => input.addEventListener('input', syncRangeOutputs));
    ids.form.addEventListener('submit', runCycle);
    ids.pause.addEventListener('click', toggleSafeHold);
    ids.reset.addEventListener('click', resetRuntime);
    byId('aan-download-json').addEventListener('click', exportJson);
    byId('aan-download-md').addEventListener('click', exportMarkdown);
    byId('aan-copy-summary').addEventListener('click', copySummary);
    return true;
  }

  setupNavigation();
  if (!renderArchitecture()) setupExperience();
  doc.documentElement.dataset.aanReady = 'true';
})();
