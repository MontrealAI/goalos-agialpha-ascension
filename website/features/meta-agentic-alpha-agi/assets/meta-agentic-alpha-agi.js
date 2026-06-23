(() => {
  'use strict';

  const DATA_URL = 'data/meta-agentic-alpha-agi.json';
  const SVG_NS = 'http://www.w3.org/2000/svg';
  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => Array.from(root.querySelectorAll(selector));
  const el = (tag, className = '', text) => {
    const item = document.createElement(tag);
    if (className) item.className = className;
    if (text !== undefined) item.textContent = text;
    return item;
  };
  const svg = (tag, attributes = {}) => {
    const item = document.createElementNS(SVG_NS, tag);
    Object.entries(attributes).forEach(([key, value]) => item.setAttribute(key, String(value)));
    return item;
  };
  const append = (parent, ...children) => {
    children.flat().filter(Boolean).forEach((child) => parent.appendChild(child));
    return parent;
  };
  const clamp = (value, minimum, maximum) => Math.max(minimum, Math.min(maximum, value));
  const pad = (value, width = 2) => String(value).padStart(width, '0');
  const safeName = (value) => String(value).normalize('NFKD').replace(/[^a-z0-9_-]+/gi, '-').replace(/^-+|-+$/g, '').toLowerCase();
  const round = (value, precision = 1) => Number(value.toFixed(precision));
  const isoSeconds = (date = new Date()) => date.toISOString().replace(/\.\d{3}Z$/, 'Z');
  const sleep = (milliseconds) => new Promise((resolve) => window.setTimeout(resolve, milliseconds));

  const hash32 = (value) => {
    let hash = 2166136261;
    for (let index = 0; index < value.length; index += 1) {
      hash ^= value.charCodeAt(index);
      hash = Math.imul(hash, 16777619);
    }
    return hash >>> 0;
  };

  const randomAt = (seed, salt) => {
    let value = (seed ^ Math.imul(salt + 1, 0x9e3779b1)) >>> 0;
    value ^= value << 13;
    value ^= value >>> 17;
    value ^= value << 5;
    return (value >>> 0) / 4294967295;
  };

  const pick = (values, seed, salt, offset = 0) => values[(Math.floor(randomAt(seed, salt) * values.length) + offset) % values.length];
  const textAt = (selector, value) => {
    const target = $(selector);
    if (target) target.textContent = value;
  };
  const setDisabled = (selector, value) => {
    const target = $(selector);
    if (target instanceof HTMLButtonElement) target.disabled = value;
  };

  let release = null;
  let currentDocket = null;
  let currentCandidates = [];
  let currentSelection = null;
  let activeRunToken = 0;
  let clockFrame = 0;
  let runStartedAt = 0;

  const candidateNames = [
    ['Atlas Monolith', 'Axiom Council', 'Helix Lattice', 'Orion Studio', 'Sovereign Mesh', 'Agora Engine'],
    ['Lumen Federation', 'Vanguard Council', 'Proofweave Lattice', 'Recursive Atelier', 'Sentinel Mesh', 'Deliberative Exchange'],
    ['Veritas Federation', 'Aegis Tribunal', 'Evidence Cathedral', 'Recursive Observatory', 'Covenant Mesh', 'Proof Market'],
    ['Ascension Federation', 'Sovereign Deliberative Council', 'Chronicle Proof Lattice', 'Meta-Recursive Foundry', 'GoalOS Constitutional Mesh', 'Aletheia Decision Market']
  ];

  const archetypeBias = {
    evidence: [10, 2, 7, 8, 1, 5],
    utility: [3, 10, 7, 4, 9, 1],
    safety: [8, 2, 10, 6, 5, 1],
    efficiency: [1, 10, 4, 8, 3, 7],
    novelty: [2, 4, 1, 7, 10, 9]
  };

  const showLoadFailure = (error) => {
    const message = `Local GoalOS release data could not be loaded: ${error instanceof Error ? error.message : String(error)}`;
    textAt('#maa-runtime-state', 'CONFIGURATION ERROR');
    textAt('#maa-runtime-caption', message);
    const fallback = $('#maa-architecture-stages') || $('#maa-definition');
    if (fallback) fallback.textContent = message;
    document.documentElement.dataset.maaReady = 'error';
  };

  const renderHeroMetrics = () => {
    const root = $('#maa-hero-metrics');
    if (!root) return;
    root.replaceChildren(...release.hero_metrics.map((metric) => {
      const card = el('article', 'maa-hero-metric');
      return append(card, el('strong', '', metric.value), el('span', '', metric.label));
    }));
  };

  const renderThesis = () => {
    const root = $('#maa-thesis-grid');
    if (!root) return;
    root.replaceChildren(...release.thesis.map((item) => {
      const card = el('article', 'maa-thesis-card maa-reveal');
      return append(card, el('span', '', item.number), el('h3', '', item.title), el('p', '', item.copy));
    }));
    textAt('#maa-definition', release.definition);
  };

  const renderBoundary = () => {
    const root = $('#maa-boundary-list');
    if (!root) return;
    root.replaceChildren(...release.claim_boundary.map((statement, index) => {
      const item = el('div', 'maa-boundary-item');
      return append(item, el('span', '', pad(index + 1)), el('p', '', statement));
    }));
  };

  const renderPresets = () => {
    const root = $('#maa-presets');
    if (!root) return;
    const buttons = release.presets.map((preset, index) => {
      const button = el('button', `maa-preset${index === 0 ? ' is-selected' : ''}`, preset.label);
      button.type = 'button';
      button.dataset.preset = preset.id;
      button.setAttribute('aria-pressed', String(index === 0));
      button.addEventListener('click', () => {
        const mission = $('#maa-mission');
        const decision = $('#maa-decision');
        const horizon = $('#maa-horizon');
        if (mission) mission.value = preset.mission;
        if (decision) decision.value = preset.decision;
        if (horizon) {
          const option = Array.from(horizon.options).find((item) => item.textContent.trim() === preset.horizon);
          if (option) horizon.value = option.value;
        }
        $$('.maa-preset', root).forEach((item) => {
          const selected = item === button;
          item.classList.toggle('is-selected', selected);
          item.setAttribute('aria-pressed', String(selected));
        });
        updateCharacterCount();
      });
      return button;
    });
    root.replaceChildren(...buttons);
  };

  const renderPostures = () => {
    const root = $('#maa-postures');
    if (!root) return;
    root.replaceChildren(...release.risk_postures.map((posture) => {
      const shell = el('div', 'maa-posture');
      const input = el('input');
      const label = el('label');
      input.type = 'radio';
      input.name = 'posture';
      input.id = `maa-posture-${safeName(posture.id)}`;
      input.value = posture.id;
      input.checked = posture.id === 'ascension';
      label.htmlFor = input.id;
      append(label, el('strong', '', posture.label), el('small', '', posture.description));
      return append(shell, input, label);
    }));
  };

  const renderStages = () => {
    const root = $('#maa-stage-list');
    if (!root) return;
    root.replaceChildren(...release.mission_flow.map((stage) => {
      const card = el('article', 'maa-stage');
      card.dataset.stageId = stage.id;
      const details = el('div');
      append(details, el('strong', '', stage.verb), el('small', '', stage.agent));
      return append(card, el('span', 'maa-stage-index', pad(stage.order)), details, el('span', 'maa-stage-state', 'QUEUED'));
    }));
  };

  const renderArtifacts = (readyCount = 0) => {
    const root = $('#maa-artifact-list');
    if (!root) return;
    root.replaceChildren(...release.artifacts.map((artifact, index) => {
      const item = el('div', `maa-artifact${index < readyCount ? ' is-ready' : ''}`);
      return append(item, el('i'), el('span', '', artifact), el('b', '', index < readyCount ? 'SEALED' : 'PENDING'));
    }));
    textAt('#maa-artifact-count', `${readyCount} / ${release.artifacts.length}`);
  };

  const renderAgents = () => {
    const root = $('#maa-agent-grid');
    if (!root) return;
    root.replaceChildren(...release.agents.map((agent) => {
      const card = el('article', 'maa-agent-card maa-reveal');
      card.dataset.symbol = agent.symbol;
      card.dataset.agentId = agent.id;
      return append(card,
        el('div', 'maa-agent-symbol', agent.symbol),
        el('span', '', agent.rank),
        el('h3', '', agent.name),
        el('p', '', agent.mandate),
        el('div', 'maa-agent-boundary', agent.boundary)
      );
    }));
  };

  const renderArchitecture = () => {
    const translation = $('#maa-translation-map');
    if (translation) {
      const header = el('div', 'maa-map-row maa-map-head');
      append(header, append(el('div'), el('b', '', 'Original signal')), append(el('div'), el('b', '', 'GoalOS reimplementation')), append(el('div'), el('b', '', 'Institutional consequence')));
      const rows = release.architecture_translation.map((item) => {
        const row = el('article', 'maa-map-row');
        append(row,
          append(el('div'), el('b', '', item.legacy)),
          append(el('div'), el('b', '', item.goalos)),
          append(el('div'), el('p', '', item.consequence))
        );
        return row;
      });
      translation.replaceChildren(header, ...rows);
    }

    const states = $('#maa-architecture-stages');
    if (states) {
      states.replaceChildren(...release.mission_flow.map((stage) => {
        const card = el('article', 'maa-state-card maa-reveal');
        card.dataset.stageId = stage.id;
        const facts = el('dl');
        append(facts,
          el('dt', '', 'GoalOS state'), el('dd', '', stage.goalos_state),
          el('dt', '', 'Owner'), el('dd', '', stage.agent),
          el('dt', '', 'Proof artifact'), el('dd', '', stage.artifact),
          el('dt', '', 'Gate'), el('dd', '', stage.proof_gate)
        );
        return append(card, el('span', '', `${pad(stage.order)} · ${stage.verb}`), el('h3', '', stage.title), el('p', '', stage.output), facts);
      }));
    }

    const agents = $('#maa-architecture-agents');
    if (agents) {
      agents.replaceChildren(...release.agents.map((agent) => {
        const card = el('article', 'maa-architecture-agent maa-reveal');
        return append(card, el('span', '', agent.symbol), el('h3', '', agent.name), el('p', '', agent.mandate), el('small', '', `PROHIBITION · ${agent.boundary}`));
      }));
    }

    const governance = $('#maa-governance-grid');
    if (governance) {
      governance.replaceChildren(...release.governance_principles.map((principle) => {
        const card = el('article', 'maa-governance-card maa-reveal');
        return append(card, el('span', '', principle.id), el('h3', '', principle.title), el('p', '', principle.copy));
      }));
    }
  };

  const updateCharacterCount = () => {
    const input = $('#maa-mission');
    const output = $('#maa-character-count');
    if (input && output) output.value = `${input.value.length} / ${input.maxLength}`;
  };

  const selectedPosture = () => {
    const id = $('input[name="posture"]:checked')?.value || 'ascension';
    return release.risk_postures.find((item) => item.id === id) || release.risk_postures[0];
  };

  const populationFromBudget = () => {
    const value = $('#maa-budget')?.value || 'full';
    const perGeneration = value === 'focused' ? 3 : value === 'deep' ? 9 : release.candidate_engine.population_per_generation;
    return { id: value, perGeneration, total: perGeneration * release.candidate_engine.generations };
  };

  const candidateSummary = (candidate) => `${candidate.topology} using ${candidate.reasoning.toLowerCase()}, ${candidate.verifier.toLowerCase()}, and ${candidate.governance.toLowerCase()} under a ${candidate.execution.toLowerCase()} boundary.`;

  const scoreCandidate = (generation, archetype, seed, serial) => {
    const generationBases = {
      evidence: 50 + generation * 7,
      utility: 52 + generation * 5,
      safety: 48 + generation * 7,
      efficiency: 74 - generation * 4,
      novelty: 48 + generation * 6
    };
    const scores = {};
    release.objectives.forEach((objective, objectiveIndex) => {
      const noise = Math.round((randomAt(seed, serial * 31 + objectiveIndex * 11) - 0.5) * 7);
      const bias = archetypeBias[objective.id][archetype % archetypeBias[objective.id].length];
      scores[objective.id] = clamp(generationBases[objective.id] + bias + noise, 42, 98);
    });
    return scores;
  };

  const createCandidatePopulation = ({ seed, posture, perGeneration }) => {
    const engine = release.candidate_engine;
    const candidates = [];
    const parentPoolByGeneration = [];
    for (let generation = 0; generation < engine.generations; generation += 1) {
      const generationCandidates = [];
      for (let index = 0; index < perGeneration; index += 1) {
        const serial = generation * perGeneration + index;
        const archetype = index % 6;
        const parentPool = parentPoolByGeneration[generation - 1] || [];
        const parent = generation === 0 ? null : parentPool[(index + Math.floor(randomAt(seed, serial * 7 + 3) * Math.max(parentPool.length, 1))) % parentPool.length];
        const componentOffset = generation + index;
        const mutations = generation === 0
          ? ['seed constitution']
          : Array.from(new Set([
            pick(engine.mutation_operators, seed, serial * 13 + 1, generation),
            pick(engine.mutation_operators, seed, serial * 13 + 2, index),
            generation > 1 ? pick(engine.mutation_operators, seed, serial * 13 + 3, generation + index) : null
          ].filter(Boolean)));
        const scores = scoreCandidate(generation, archetype, seed, serial);
        const weightedScore = release.objectives.reduce((total, objective) => total + scores[objective.id] * posture.weights[objective.id], 0);
        const candidate = {
          id: `MPSI-G${generation + 1}-C${pad(index + 1)}`,
          code: `MΨ-${pad(serial + 1)}`,
          name: candidateNames[generation][archetype] || `Institution ${pad(serial + 1)}`,
          generation,
          parent_id: parent?.id || null,
          topology: pick(engine.topologies, seed, serial * 17 + 1, componentOffset),
          reasoning: pick(engine.reasoning_modes, seed, serial * 17 + 2, archetype),
          verifier: pick(engine.verifier_models, seed, serial * 17 + 3, generation),
          governance: pick(engine.governance_models, seed, serial * 17 + 4, index),
          memory: pick(engine.memory_models, seed, serial * 17 + 5, generation + archetype),
          execution: pick(engine.execution_models, seed, serial * 17 + 6, generation),
          mutations,
          scores,
          weighted_score: round(weightedScore),
          is_frontier: false,
          is_selected: false
        };
        candidate.summary = candidateSummary(candidate);
        candidates.push(candidate);
        generationCandidates.push(candidate);
      }
      parentPoolByGeneration.push(generationCandidates);
    }
    return candidates;
  };

  const dominates = (left, right) => {
    const scoreKeys = release.objectives.map((objective) => objective.id);
    return scoreKeys.every((key) => left.scores[key] >= right.scores[key]) && scoreKeys.some((key) => left.scores[key] > right.scores[key]);
  };

  const markParetoFrontier = (candidates) => {
    const frontier = candidates.filter((candidate) => !candidates.some((rival) => rival.id !== candidate.id && dominates(rival, candidate)));
    frontier.forEach((candidate) => { candidate.is_frontier = true; });
    return frontier;
  };

  const selectCandidate = (candidates) => {
    const frontier = markParetoFrontier(candidates);
    const selected = [...frontier].sort((left, right) =>
      right.weighted_score - left.weighted_score ||
      right.scores.evidence - left.scores.evidence ||
      right.scores.safety - left.scores.safety ||
      left.id.localeCompare(right.id)
    )[0];
    selected.is_selected = true;
    return { frontier, selected };
  };

  const renderScoreboard = (candidate = null) => {
    const root = $('#maa-scoreboard');
    if (!root) return;
    root.replaceChildren(...release.objectives.map((objective) => {
      const score = candidate ? candidate.scores[objective.id] : null;
      const card = el('article', 'maa-score');
      card.dataset.objective = objective.id;
      card.style.setProperty('--score', `${score || 0}%`);
      const value = el('strong');
      if (score === null) value.textContent = '—';
      else append(value, document.createTextNode(String(score)), el('b', '', '/100'));
      return append(card, el('span', '', objective.label), value, el('small', '', score === null ? 'Awaiting candidate' : objective.description));
    }));
  };

  const inspectCandidate = (candidate, options = {}) => {
    if (!candidate) return;
    textAt('#maa-inspector-code', candidate.code);
    textAt('#inspector-title', candidate.name);
    textAt('#maa-inspector-summary', candidate.summary);
    textAt('#maa-inspector-badge', candidate.is_selected ? 'SELECTED' : candidate.is_frontier ? 'PARETO FRONTIER' : 'CANDIDATE');
    textAt('#maa-weighted-score', candidate.weighted_score.toFixed(1));
    textAt('#maa-selection-note', candidate.is_selected
      ? 'Highest posture-weighted score among non-dominated candidates. Human authorization remains withheld.'
      : candidate.is_frontier
        ? 'Non-dominated under the five declared simulated objectives.'
        : 'Dominated by at least one rival under the declared simulated objectives.');
    textAt('#maa-constitution-count', '6 LAYERS');
    textAt('#maa-generation-label', `GENERATION ${candidate.generation + 1}`);
    textAt('#maa-mutation-line', `${candidate.parent_id ? `Parent ${candidate.parent_id}. ` : 'Seed lineage. '}${candidate.mutations.join(' · ')}.`);
    const constitution = $('#maa-constitution-list');
    if (constitution) {
      const entries = [
        ['Topology', candidate.topology],
        ['Reasoning', candidate.reasoning],
        ['Verification', candidate.verifier],
        ['Governance', candidate.governance],
        ['Memory', candidate.memory],
        ['Execution', candidate.execution]
      ];
      constitution.replaceChildren(...entries.flatMap(([key, value]) => [el('dt', '', key), el('dd', '', value)]));
    }
    renderScoreboard(candidate);
    $$('.maa-candidate-card').forEach((card) => card.classList.toggle('is-inspected', card.dataset.candidateId === candidate.id));
    $$('.maa-lineage-node,.maa-plot-point').forEach((point) => point.classList.toggle('is-inspected', point.dataset.candidateId === candidate.id));
    if (!options.silent) {
      const inspector = $('.maa-inspector');
      if (inspector && window.innerWidth < 1020) inspector.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  const makeInteractiveSvgGroup = (className, candidate, label) => {
    const group = svg('g', { class: className, tabindex: '0', role: 'button', 'aria-label': label });
    group.dataset.candidateId = candidate.id;
    const activate = () => inspectCandidate(candidate, { silent: true });
    group.addEventListener('click', activate);
    group.addEventListener('keydown', (event) => {
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        activate();
      }
    });
    return group;
  };

  const renderLineageGraph = (candidates = []) => {
    const root = $('#maa-lineage-svg');
    if (!root) return;
    if (!candidates.length) {
      const empty = svg('g', { class: 'maa-lineage-empty' });
      append(empty, svg('circle', { cx: 460, cy: 260, r: 92 }), svg('text', { x: 460, y: 250 }), svg('text', { x: 460, y: 286 }));
      empty.children[1].textContent = 'MΨ';
      empty.children[2].textContent = 'MISSION AWAITING COMMITMENT';
      root.replaceChildren(empty);
      return;
    }

    const generations = release.candidate_engine.generations;
    const width = 920;
    const height = 520;
    const marginX = 88;
    const marginY = 52;
    const generationGroups = Array.from({ length: generations }, (_, generation) => candidates.filter((candidate) => candidate.generation === generation));
    const positions = new Map();
    generationGroups.forEach((group, generation) => {
      group.forEach((candidate, index) => {
        const x = marginX + generation * ((width - marginX * 2) / (generations - 1));
        const y = group.length === 1 ? height / 2 : marginY + index * ((height - marginY * 2) / (group.length - 1));
        positions.set(candidate.id, { x, y });
      });
    });

    const defs = svg('defs');
    const gradient = svg('linearGradient', { id: 'maa-lineage-gradient', x1: 0, y1: 0, x2: 1, y2: 1 });
    append(gradient, svg('stop', { offset: 0, 'stop-color': '#70f0ce' }), svg('stop', { offset: 1, 'stop-color': '#ffe08b' }));
    defs.appendChild(gradient);
    const layers = svg('g');
    const headers = svg('g');
    generationGroups.forEach((group, generation) => {
      const x = marginX + generation * ((width - marginX * 2) / (generations - 1));
      const label = svg('text', { x, y: 24, 'text-anchor': 'middle', fill: '#66738a', 'font-size': 10, 'font-weight': 900 });
      label.textContent = `GEN ${generation + 1} · ${group.length}`;
      headers.appendChild(label);
    });

    candidates.filter((candidate) => candidate.parent_id).forEach((candidate) => {
      const source = positions.get(candidate.parent_id);
      const target = positions.get(candidate.id);
      if (!source || !target) return;
      const midpoint = (source.x + target.x) / 2;
      const path = svg('path', {
        d: `M${source.x},${source.y} C${midpoint},${source.y} ${midpoint},${target.y} ${target.x},${target.y}`,
        class: `maa-lineage-edge${candidate.is_selected ? ' is-selected' : ''}`
      });
      layers.appendChild(path);
    });

    candidates.forEach((candidate) => {
      const position = positions.get(candidate.id);
      const classes = ['maa-lineage-node'];
      if (candidate.is_frontier) classes.push('is-frontier');
      if (candidate.is_selected) classes.push('is-selected');
      const group = makeInteractiveSvgGroup(classes.join(' '), candidate, `Inspect ${candidate.name}, score ${candidate.weighted_score}`);
      group.setAttribute('transform', `translate(${position.x} ${position.y})`);
      append(group, svg('circle', { r: candidate.is_selected ? 14 : 11 }), svg('text', { y: -18 }), svg('text', { y: 3, class: 'maa-node-score' }));
      group.children[1].textContent = candidate.code.replace('MΨ-', '');
      group.children[2].textContent = candidate.weighted_score.toFixed(0);
      layers.appendChild(group);
    });
    root.replaceChildren(defs, headers, layers);
  };

  const renderParetoPlot = (candidates = []) => {
    const root = $('#maa-pareto-svg');
    if (!root) return;
    if (!candidates.length) {
      const empty = svg('g', { class: 'maa-plot-empty' });
      append(empty, svg('path', { d: 'M66 30V330H488' }), svg('text', { x: 277, y: 187 }));
      empty.children[1].textContent = 'FRONTIER FORMS HERE';
      root.replaceChildren(empty);
      return;
    }
    const left = 58;
    const right = 492;
    const top = 25;
    const bottom = 334;
    const scaleX = (value) => left + ((value - 40) / 60) * (right - left);
    const scaleY = (value) => bottom - ((value - 40) / 60) * (bottom - top);
    const grid = svg('g');
    [40, 60, 80, 100].forEach((value) => {
      append(grid,
        svg('line', { x1: scaleX(value), y1: top, x2: scaleX(value), y2: bottom, class: 'maa-plot-grid' }),
        svg('line', { x1: left, y1: scaleY(value), x2: right, y2: scaleY(value), class: 'maa-plot-grid' })
      );
      const xLabel = svg('text', { x: scaleX(value), y: 352, 'text-anchor': 'middle', class: 'maa-plot-label' });
      xLabel.textContent = String(value);
      const yLabel = svg('text', { x: 46, y: scaleY(value) + 3, 'text-anchor': 'end', class: 'maa-plot-label' });
      yLabel.textContent = String(value);
      append(grid, xLabel, yLabel);
    });
    append(grid, svg('line', { x1: left, y1: top, x2: left, y2: bottom, class: 'maa-plot-axis' }), svg('line', { x1: left, y1: bottom, x2: right, y2: bottom, class: 'maa-plot-axis' }));

    const frontier = candidates.filter((candidate) => candidate.is_frontier).sort((a, b) => a.scores.utility - b.scores.utility);
    const frontierPath = svg('path', {
      class: 'maa-plot-frontier',
      d: frontier.map((candidate, index) => `${index ? 'L' : 'M'}${scaleX(candidate.scores.utility)},${scaleY(candidate.scores.evidence)}`).join(' ')
    });
    const points = svg('g');
    candidates.forEach((candidate) => {
      const classes = ['maa-plot-point'];
      if (candidate.is_frontier) classes.push('is-frontier');
      if (candidate.is_selected) classes.push('is-selected');
      const group = makeInteractiveSvgGroup(classes.join(' '), candidate, `Inspect ${candidate.name}: utility ${candidate.scores.utility}, evidence ${candidate.scores.evidence}`);
      group.setAttribute('transform', `translate(${scaleX(candidate.scores.utility)} ${scaleY(candidate.scores.evidence)})`);
      const radius = 3.6 + ((candidate.scores.safety - 40) / 60) * 4.4;
      append(group, svg('circle', { r: round(radius, 2) }), svg('text', { x: 8, y: -8 }));
      group.children[1].textContent = candidate.code;
      points.appendChild(group);
    });
    root.replaceChildren(grid, frontierPath, points);
  };

  const renderCandidateStrip = (candidates = []) => {
    const root = $('#maa-candidate-list');
    if (!root) return;
    if (!candidates.length) {
      root.replaceChildren(el('div', 'maa-candidate-placeholder', 'Candidate institutions will appear across four generations.'));
      return;
    }
    root.replaceChildren(...candidates.map((candidate) => {
      const classes = ['maa-candidate-card'];
      if (candidate.is_frontier) classes.push('is-frontier');
      if (candidate.is_selected) classes.push('is-selected');
      const button = el('button', classes.join(' '));
      button.type = 'button';
      button.dataset.candidateId = candidate.id;
      const meta = el('span');
      append(meta, document.createTextNode(`GEN ${candidate.generation + 1}`), el('b', '', candidate.is_selected ? 'SELECTED' : candidate.is_frontier ? 'FRONTIER' : candidate.code));
      append(button, meta, el('h4', '', candidate.name), el('p', '', candidate.topology), el('strong', '', candidate.weighted_score.toFixed(1)));
      button.addEventListener('click', () => inspectCandidate(candidate));
      return button;
    }));
  };

  const renderPopulation = (candidates) => {
    renderLineageGraph(candidates);
    renderParetoPlot(candidates);
    renderCandidateStrip(candidates);
    const frontier = candidates.filter((candidate) => candidate.is_frontier);
    textAt('#maa-frontier-count', `${frontier.length} NON-DOMINATED`);
    textAt('#maa-lineage-status', `${candidates.length} institutions · ${frontier.length} frontier`);
    textAt('#maa-candidate-count', String(candidates.length));
  };

  const setRuntimeState = (state, caption) => {
    const app = $('#maa-app');
    if (app) app.dataset.runState = state;
    textAt('#maa-runtime-state', state.replaceAll('_', ' '));
    if (caption) textAt('#maa-runtime-caption', caption);
    textAt('#maa-core-state', state === 'HUMAN_REVIEW_READY' ? 'REVIEW READY' : state.replaceAll('_', ' '));
  };

  const formatClock = (milliseconds) => {
    const tenths = Math.max(0, Math.floor(milliseconds / 100));
    return `${pad(Math.floor(tenths / 600))}:${pad(Math.floor((tenths % 600) / 10))}.${tenths % 10}`;
  };

  const startClock = (token) => {
    cancelAnimationFrame(clockFrame);
    runStartedAt = performance.now();
    const tick = () => {
      if (token !== activeRunToken) return;
      textAt('#maa-runtime-clock', formatClock(performance.now() - runStartedAt));
      clockFrame = requestAnimationFrame(tick);
    };
    clockFrame = requestAnimationFrame(tick);
  };

  const stopClock = () => {
    cancelAnimationFrame(clockFrame);
    clockFrame = 0;
  };

  const elapsed = () => formatClock(performance.now() - runStartedAt);

  const addLog = (actor, message, tone = '') => {
    const root = $('#maa-console');
    if (!root) return;
    const line = el('p', tone ? `is-${tone}` : '');
    append(line, el('time', '', elapsed()), el('b', '', actor), el('span', '', message));
    root.appendChild(line);
    root.scrollTop = root.scrollHeight;
  };

  const resetRuntime = () => {
    activeRunToken += 1;
    stopClock();
    currentDocket = null;
    currentCandidates = [];
    currentSelection = null;
    $$('.maa-stage').forEach((stage) => {
      stage.classList.remove('is-active', 'is-complete');
      const state = $('.maa-stage-state', stage);
      if (state) state.textContent = 'QUEUED';
    });
    textAt('#maa-run-id', 'RUN · NOT STARTED');
    textAt('#maa-runtime-clock', '00:00.0');
    textAt('#maa-lineage-status', 'Awaiting mission');
    textAt('#maa-frontier-count', '0 NON-DOMINATED');
    textAt('#maa-decision-state', 'NOT GENERATED');
    textAt('#maa-decision-summary', 'Launch a mission to create a reproducible, human-review-ready decision package.');
    textAt('#maa-gate-count', `0 / ${release.mission_flow.length}`);
    textAt('#maa-candidate-count', '0');
    textAt('#maa-action-count', '0');
    textAt('#maa-inspector-code', 'MΨ‑00');
    textAt('#inspector-title', 'No institution selected');
    textAt('#maa-inspector-summary', 'Run the foundry, then inspect any candidate, rejected lineage, or frontier institution.');
    textAt('#maa-inspector-badge', 'UNGENERATED');
    textAt('#maa-weighted-score', '—');
    textAt('#maa-selection-note', 'Selection rationale will appear here.');
    textAt('#maa-constitution-count', '0 LAYERS');
    textAt('#maa-generation-label', 'GENERATION —');
    textAt('#maa-mutation-line', 'No mutation history yet.');
    $('#maa-constitution-list')?.replaceChildren();
    $('#maa-console')?.replaceChildren(append(el('p'), el('time', '', '00:00.0'), el('b', '', 'SYSTEM'), el('span', '', 'Institution Foundry ready. No mission data has left this browser.')));
    renderArtifacts(0);
    renderScoreboard();
    renderLineageGraph();
    renderParetoPlot();
    renderCandidateStrip();
    setRuntimeState('READY', 'Commit a mission to generate the institution population.');
    setDisabled('#maa-download', true);
    setDisabled('#maa-download-md', true);
    setDisabled('#maa-copy', true);
    setDisabled('#maa-launch', false);
    const preview = $('#maa-json-preview');
    if (preview) preview.textContent = JSON.stringify({ status: 'READY', done: false, next_action: 'Compose and launch a mission' }, null, 2);
  };

  const actionGraph = (selected) => [
    { order: 1, action: 'Commission authenticated evidence retrieval against the EvidencePlan.', owner: 'Evidence Cartographer', authorization: 'HUMAN_REQUIRED', reversible: true },
    { order: 2, action: 'Run domain-specific evaluators and independent reproductions.', owner: 'Verifier Mesh', authorization: 'HUMAN_REQUIRED', reversible: true },
    { order: 3, action: `Pilot ${selected.name} inside a sandbox with declared stop rules.`, owner: 'Execution Conductor', authorization: 'HUMAN_REQUIRED', reversible: true },
    { order: 4, action: 'Review outcomes, risks, permissions, and revocation conditions before any external use.', owner: 'Sovereign Guardian', authorization: 'HUMAN_REQUIRED', reversible: true }
  ];

  const buildDocket = ({ mission, decision, horizon, posture, budget, runId, seed, candidates, frontier, selected }) => {
    const generatedAt = isoSeconds();
    const candidateRecords = candidates.map((candidate) => ({
      id: candidate.id,
      code: candidate.code,
      name: candidate.name,
      generation: candidate.generation + 1,
      parent_id: candidate.parent_id,
      constitution: {
        topology: candidate.topology,
        reasoning: candidate.reasoning,
        verifier: candidate.verifier,
        governance: candidate.governance,
        memory: candidate.memory,
        execution: candidate.execution
      },
      mutations: candidate.mutations,
      scores: candidate.scores,
      posture_weighted_score: candidate.weighted_score,
      pareto_frontier: candidate.is_frontier,
      selected: candidate.is_selected
    }));
    const artifacts = release.artifacts.map((name, index) => ({ index: index + 1, name, state: 'SEALED_FOR_REVIEW', external_proof_attached: false }));
    const stages = release.mission_flow.map((stage) => ({
      order: stage.order,
      verb: stage.verb,
      goalos_state: stage.goalos_state,
      owner: stage.agent,
      artifact: stage.artifact,
      structural_gate: 'PASS',
      factual_certification: 'NOT_PERFORMED'
    }));
    return {
      schema: 'goalos.meta_agentic_alpha_agi.evidence_docket.v2',
      release: { id: release.release_id, title: release.release_title, version: release.version },
      run: {
        id: runId,
        deterministic_seed: seed,
        generated_at: generatedAt,
        runtime: 'LOCAL_BROWSER_ONLY',
        transmitted: false,
        persisted: false
      },
      mission_contract: {
        objective: mission,
        decision_to_support: decision,
        horizon,
        operating_posture: posture.id,
        candidate_budget: budget.id,
        candidate_population: candidates.length,
        reviewer_attestation: 'COMPLETED_BY_USER',
        authority: 'ANALYSIS_AND_PROPOSAL_ONLY'
      },
      evolution_engine: {
        generations: release.candidate_engine.generations,
        population_per_generation: budget.perGeneration,
        selection_law: release.candidate_engine.selection,
        objective_weights: posture.weights,
        candidates: candidateRecords,
        pareto_frontier_ids: frontier.map((candidate) => candidate.id),
        selected_candidate_id: selected.id,
        selection_reason: 'Highest posture-weighted score among non-dominated candidates after structural claim-boundary checks.'
      },
      selected_institution: {
        id: selected.id,
        code: selected.code,
        name: selected.name,
        summary: selected.summary,
        constitution: candidateRecords.find((candidate) => candidate.id === selected.id).constitution,
        mutations: selected.mutations,
        scores: selected.scores,
        posture_weighted_score: selected.weighted_score,
        authority: 'NONE_GRANTED'
      },
      goalos_state_machine: stages,
      evidence_manifest: artifacts,
      open_requirements: [
        'Retrieve and authenticate mission-specific external evidence.',
        'Evaluate factual claims with qualified domain reviewers.',
        'Run real task benchmarks and adversarial tests in a controlled environment.',
        'Perform security, privacy, legal, and operational review as applicable.',
        'Issue a separate minimum-right authorization before any external action.'
      ],
      action_graph: actionGraph(selected),
      claim_boundary: release.claim_boundary,
      authorization: {
        state: 'HUMAN_REVIEW_REQUIRED',
        publication: 'WITHHELD',
        credentials: 'WITHHELD',
        production_activation: 'WITHHELD',
        wallet_or_funds: 'WITHHELD',
        external_actions: 0,
        settlement: 'NONE'
      },
      decision_state: {
        status: 'HUMAN_REVIEW_READY',
        done: true,
        structural_checks: 'PASS',
        factual_correctness: 'NOT_CERTIFIED',
        real_world_superiority: 'NOT_CLAIMED',
        next_action: 'Qualified human review and evidence acquisition'
      }
    };
  };

  const docketBrief = (docket) => {
    const selected = docket.selected_institution;
    return [
      `# ${release.release_title}`,
      '',
      `**Run:** ${docket.run.id}`,
      `**Decision state:** ${docket.decision_state.status}`,
      '',
      '## Mission contract',
      `**Objective:** ${docket.mission_contract.objective}`,
      `**Decision supported:** ${docket.mission_contract.decision_to_support}`,
      `**Horizon:** ${docket.mission_contract.horizon}`,
      `**Posture:** ${docket.mission_contract.operating_posture}`,
      '',
      '## Selected institution',
      `**${selected.code} — ${selected.name}**`,
      selected.summary,
      `Posture-weighted simulated score: ${selected.posture_weighted_score}`,
      `Pareto frontier: ${docket.evolution_engine.pareto_frontier_ids.length} of ${docket.mission_contract.candidate_population} candidates`,
      '',
      '### Constitution',
      ...Object.entries(selected.constitution).map(([key, value]) => `- **${key}:** ${value}`),
      '',
      '## Authorization boundary',
      '- External actions: 0',
      '- Publication: withheld',
      '- Production activation: withheld',
      '- Wallet or funds: withheld',
      '- Qualified human review: required',
      '',
      '## Claim boundary',
      ...docket.claim_boundary.map((statement) => `- ${statement}`),
      '',
      `Generated locally at ${docket.run.generated_at}. No mission content was transmitted or persisted by this experience.`
    ].join('\n');
  };

  const triggerDownload = (content, type, filename) => {
    const blob = new Blob([content], { type });
    const url = URL.createObjectURL(blob);
    const anchor = el('a');
    anchor.href = url;
    anchor.download = filename;
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
    window.setTimeout(() => URL.revokeObjectURL(url), 0);
  };

  const downloadDocket = () => {
    if (!currentDocket) return;
    triggerDownload(`${JSON.stringify(currentDocket, null, 2)}\n`, 'application/json', `${currentDocket.run.id.toLowerCase()}-evidence-docket.json`);
  };

  const downloadBrief = () => {
    if (!currentDocket) return;
    triggerDownload(`${docketBrief(currentDocket)}\n`, 'text/markdown', `${currentDocket.run.id.toLowerCase()}-executive-brief.md`);
  };

  const copyBrief = async () => {
    if (!currentDocket) return;
    const text = docketBrief(currentDocket);
    try {
      await navigator.clipboard.writeText(text);
    } catch {
      const area = el('textarea');
      area.value = text;
      area.setAttribute('readonly', '');
      area.style.position = 'fixed';
      area.style.opacity = '0';
      document.body.appendChild(area);
      area.select();
      document.execCommand('copy');
      area.remove();
    }
    const button = $('#maa-copy');
    if (button) {
      const original = button.textContent;
      button.textContent = 'Summary copied';
      window.setTimeout(() => { button.textContent = original; }, 1600);
    }
  };

  const completeStage = (stageIndex) => {
    const stages = $$('.maa-stage');
    stages.forEach((stage, index) => {
      const state = $('.maa-stage-state', stage);
      stage.classList.toggle('is-active', index === stageIndex);
      if (index < stageIndex) {
        stage.classList.add('is-complete');
        if (state) state.textContent = 'PASS';
      } else if (index === stageIndex && state) state.textContent = 'ACTIVE';
    });
  };

  const runMission = async (event) => {
    event.preventDefault();
    const mission = $('#maa-mission')?.value.trim() || '';
    const decision = $('#maa-decision')?.value.trim() || '';
    const horizon = $('#maa-horizon')?.selectedOptions[0]?.textContent.trim() || '36 months';
    const reviewer = $('#maa-reviewer');
    if (mission.length < 24 || decision.length < 12 || !(reviewer instanceof HTMLInputElement) || !reviewer.checked) {
      setRuntimeState('INPUT_REQUIRED', 'Add a clear objective, a decision to support, and the human-review attestation.');
      if (mission.length < 24) $('#maa-mission')?.focus();
      else if (decision.length < 12) $('#maa-decision')?.focus();
      else reviewer?.focus();
      return;
    }

    resetRuntime();
    const token = activeRunToken + 1;
    activeRunToken = token;
    const posture = selectedPosture();
    const budget = populationFromBudget();
    const seedMaterial = [release.release_id, release.version, mission, decision, horizon, posture.id, budget.id].join('|');
    const seed = hash32(seedMaterial);
    const runId = `MΨ-${seed.toString(16).toUpperCase().padStart(8, '0')}`;
    const candidates = createCandidatePopulation({ seed, posture, perGeneration: budget.perGeneration });
    const { frontier, selected } = selectCandidate(candidates);
    currentCandidates = candidates;
    currentSelection = selected;

    textAt('#maa-run-id', `RUN · ${runId}`);
    textAt('#maa-candidate-count', String(candidates.length));
    setDisabled('#maa-launch', true);
    startClock(token);
    setRuntimeState('MISSION_COMMITTED', 'Mission contract committed locally. Beginning proof-gated institutional evolution.');
    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const pace = reducedMotion ? 35 : 310;
    const artifactsPerStage = [2, 4, 6, 8, 10, 12, 15, 16];
    const logs = [
      ['NAVIGATOR', 'Mission boundary, decision, horizon, stop rules, and human authority committed.'],
      ['CARTOGRAPHER', 'Evidence requirements, contradictions, source families, and unknowns separated from narrative.'],
      ['META-ARCHITECT', `${candidates.length} candidate institutions generated from deterministic constitutions and mutation operators.`],
      ['SYNTHESIST', `${frontier.length} non-dominated candidates exposed across evidence, utility, safety, efficiency, and novelty.`],
      ['STRATEGIST', `${selected.code} ${selected.name} selected from the frontier under the ${posture.label} posture.`],
      ['CONDUCTOR', 'Proposal-only action graph composed with prerequisites, monitoring, reversal, and zero external execution.'],
      ['VERIFIER MESH', 'Structural gates passed; factual correctness, production safety, and real-world superiority remain uncertified.'],
      ['GUARDIAN', 'All external rights withheld. Evidence Docket sealed for qualified human review.']
    ];

    for (let stageIndex = 0; stageIndex < release.mission_flow.length; stageIndex += 1) {
      if (token !== activeRunToken) return;
      const stage = release.mission_flow[stageIndex];
      completeStage(stageIndex);
      setRuntimeState(stage.goalos_state, stage.title);
      addLog(logs[stageIndex][0], logs[stageIndex][1], stageIndex === 7 ? 'success' : '');
      renderArtifacts(artifactsPerStage[stageIndex]);
      textAt('#maa-gate-count', `${stageIndex} / ${release.mission_flow.length}`);

      if (stageIndex === 2) {
        const firstGeneration = candidates.filter((candidate) => candidate.generation === 0);
        renderPopulation(firstGeneration);
        inspectCandidate(firstGeneration[0], { silent: true });
      }
      if (stageIndex === 3) {
        renderPopulation(candidates);
        inspectCandidate(selected, { silent: true });
      }
      if (stageIndex === 4) {
        textAt('#maa-selection-note', `Selected from ${frontier.length} Pareto candidates using the declared ${posture.label} weights.`);
      }
      await sleep(pace);
    }

    if (token !== activeRunToken) return;
    const stages = $$('.maa-stage');
    stages.forEach((stage) => {
      stage.classList.remove('is-active');
      stage.classList.add('is-complete');
      const state = $('.maa-stage-state', stage);
      if (state) state.textContent = 'PASS';
    });
    currentDocket = buildDocket({ mission, decision, horizon, posture, budget, runId, seed, candidates, frontier, selected });
    currentSelection = selected;
    renderPopulation(candidates);
    inspectCandidate(selected, { silent: true });
    renderArtifacts(release.artifacts.length);
    textAt('#maa-gate-count', `${release.mission_flow.length} / ${release.mission_flow.length}`);
    textAt('#maa-action-count', '0');
    textAt('#maa-decision-state', 'HUMAN REVIEW REQUIRED');
    textAt('#maa-decision-summary', `${selected.name} is the posture-weighted selection from ${frontier.length} non-dominated institutions. The local structural package is complete; factual, security, domain, and authorization review remain open.`);
    setRuntimeState('HUMAN_REVIEW_READY', 'Evidence Docket sealed. No external action has been authorized or performed.');
    const preview = $('#maa-json-preview');
    if (preview) preview.textContent = JSON.stringify(currentDocket, null, 2);
    setDisabled('#maa-download', false);
    setDisabled('#maa-download-md', false);
    setDisabled('#maa-copy', false);
    setDisabled('#maa-launch', false);
    stopClock();
    document.documentElement.dataset.maaRunComplete = 'true';
  };

  const setupNavigation = () => {
    const toggle = $('.maa-nav-toggle');
    const nav = $('#maa-nav');
    if (!toggle || !nav) return;
    toggle.addEventListener('click', () => {
      const open = toggle.getAttribute('aria-expanded') !== 'true';
      toggle.setAttribute('aria-expanded', String(open));
      nav.classList.toggle('is-open', open);
    });
    $$('a', nav).forEach((link) => link.addEventListener('click', () => {
      toggle.setAttribute('aria-expanded', 'false');
      nav.classList.remove('is-open');
    }));
  };

  const setupReveal = () => {
    const items = $$('.maa-reveal');
    if (!items.length) return;
    if (!('IntersectionObserver' in window) || window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      items.forEach((item) => item.classList.add('is-visible'));
      return;
    }
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.08, rootMargin: '0px 0px -5% 0px' });
    items.forEach((item) => observer.observe(item));
  };

  const setupField = () => {
    const canvas = $('#maa-field');
    if (!(canvas instanceof HTMLCanvasElement)) return;
    const context = canvas.getContext('2d');
    if (!context) return;
    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    let width = 0;
    let height = 0;
    let points = [];
    const resize = () => {
      const ratio = Math.min(window.devicePixelRatio || 1, 2);
      width = window.innerWidth;
      height = window.innerHeight;
      canvas.width = Math.round(width * ratio);
      canvas.height = Math.round(height * ratio);
      canvas.style.width = `${width}px`;
      canvas.style.height = `${height}px`;
      context.setTransform(ratio, 0, 0, ratio, 0, 0);
      const count = clamp(Math.round((width * height) / 24000), 30, 84);
      points = Array.from({ length: count }, (_, index) => ({
        x: randomAt(0x5f3759df, index * 5) * width,
        y: randomAt(0x9e3779b9, index * 5 + 1) * height,
        radius: 0.45 + randomAt(0x85ebca6b, index * 5 + 2) * 1.2,
        vx: (randomAt(0xc2b2ae35, index * 5 + 3) - 0.5) * 0.11,
        vy: (randomAt(0x27d4eb2f, index * 5 + 4) - 0.5) * 0.11
      }));
    };
    const draw = () => {
      context.clearRect(0, 0, width, height);
      points.forEach((point, index) => {
        if (!reducedMotion) {
          point.x = (point.x + point.vx + width) % width;
          point.y = (point.y + point.vy + height) % height;
        }
        context.beginPath();
        context.arc(point.x, point.y, point.radius, 0, Math.PI * 2);
        context.fillStyle = index % 3 === 0 ? 'rgba(255,224,139,.46)' : index % 3 === 1 ? 'rgba(112,240,206,.38)' : 'rgba(117,168,255,.34)';
        context.fill();
      });
      if (!reducedMotion) requestAnimationFrame(draw);
    };
    resize();
    draw();
    window.addEventListener('resize', resize, { passive: true });
  };

  const setupExperience = () => {
    if (!$('#maa-app')) return;
    renderPresets();
    renderPostures();
    renderStages();
    renderAgents();
    renderScoreboard();
    renderArtifacts();
    updateCharacterCount();
    resetRuntime();
    $('#maa-mission')?.addEventListener('input', updateCharacterCount);
    $('#maa-mission-form')?.addEventListener('submit', runMission);
    $('#maa-reset')?.addEventListener('click', resetRuntime);
    $('#maa-download')?.addEventListener('click', downloadDocket);
    $('#maa-download-md')?.addEventListener('click', downloadBrief);
    $('#maa-copy')?.addEventListener('click', copyBrief);
  };

  const init = async () => {
    try {
      if (window.GOALOS_META_AGENTIC_DATA && typeof window.GOALOS_META_AGENTIC_DATA === 'object') {
        release = window.GOALOS_META_AGENTIC_DATA;
      } else {
        const response = await fetch(DATA_URL, { cache: 'no-store' });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        release = await response.json();
      }
      renderHeroMetrics();
      renderThesis();
      renderBoundary();
      renderArchitecture();
      setupNavigation();
      setupExperience();
      setupReveal();
      setupField();
      document.documentElement.dataset.maaReady = 'true';
    } catch (error) {
      showLoadFailure(error);
      console.error(error);
    }
  };

  document.addEventListener('DOMContentLoaded', init, { once: true });
})();
