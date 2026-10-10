# Citation Audit Report

This document records the results of a citation audit evaluating seven claim/source pairs against text retrieved directly from original sources via web fetch.

## Audit Summary

- **Total Claims Audited:** 7
- **SUPPORTED:** 2
- **PARTIAL:** 4
- **UNSUPPORTED:** 1
- **UNVERIFIABLE:** 0

## Findings Table

| Claim | URL | Verdict | Evidence | Excerpt |
| :--- | :--- | :--- | :--- | :--- |
| ReAct couples reasoning, execution, and observation in an in-context loop, allowing agents to update plans dynamically and handle operational exceptions during execution, though it relies on local context and greedy decisions rather than explicit tree search. | https://arxiv.org/abs/2210.03629 | PARTIAL | The source confirms that ReAct interleaves reasoning traces and actions to update plans and handle execution exceptions, but it does not evaluate greedy decision making against explicit tree search. | update action plans as well as handle exceptions |
| In Toolformer's original formulation, candidate API calls were generated independently across text during dataset construction, so the fine-tuning data contained no demonstrations of chained tool use where one API's output feeds into another; this restriction reflects the independent candidate generation method rather than an inherent barrier to parametric tool use. | https://arxiv.org/abs/2302.04761 | UNSUPPORTED | The retrieved abstract outlines Toolformer's self-supervised tool integration abilities but provides no evidence regarding independent candidate API generation or the absence of chained tool use demonstrations. | decide which APIs to call, when to call them |
| SPIRAL embeds a multi-agent cognitive architecture in an MCTS loop, using Planner (proposes actions), Simulator (models state transitions to ground exploration), and Critic (computes dense reflective rewards) roles to guide deliberation across branching paths, with trade-offs in search latency/compute costs and dependence on simulator fidelity. | https://huggingface.co/papers/2512.23167 | PARTIAL | The retrieved text validates the integration of Planner, Simulator, and Critic roles within an MCTS loop, but it omits discussion of search latency trade-offs or simulator fidelity dependence. | embeds a cognitive architecture of three specialized LLM agents |
| Tool-R0 eliminates human demonstrations via zero-data self-play reinforcement learning, co-evolving a task Generator synthesizing tasks based on Solver uncertainty and a task Solver learning tool execution via outcome-based rewards, with scoped challenges in exploration stability. | https://huggingface.co/papers/2602.21320 | PARTIAL | The source corroborates that Tool-R0 employs zero-data self-play reinforcement learning to co-evolve a Generator and Solver, but it does not discuss exploration stability challenges. | co-evolves a Generator and a Solver with complementary rewards |
| The Building Block Economy is an opinionated, developer-centric design perspective describing a shift where agents compose standardized remote services (such as Model Context Protocol servers) instead of writing custom application logic, introducing failure modes including service version drift, abstraction leakage, and operational overhead from network latency. | https://codex.danielvaughan.com/2026/07/19/building-block-economy-agent-native-tools-composable-services-codex-cli-developer-role-shift/ | SUPPORTED | The article describes the building block economy as an agent-driven composition of remote services like Model Context Protocol servers and explicitly identifies service version drift, abstraction leakage, and latency overhead as key failure modes. | building block economy has failure modes that differ |
| Agent skill sharing on GitHub forms an unmanaged supply chain lacking formal registries, versioning, or provenance tracking, where upstream patches rarely propagate downstream, copied skills frequently acquire privileged execution capabilities, and statistical source-choice models (such as conditional logit estimation) prioritize high-risk repositories for audit over star counts. | https://huggingface.co/papers/2610.11169 | PARTIAL | The source confirms that GitHub skill sharing constitutes an unversioned supply chain lacking registries and provenance where fixes rarely propagate, but it omits conditional logit estimation and skills acquiring privileged execution. | software supply chain without a registry, versions or provenance |
| Agent security spans information flow, delegated authority, and state, with threat surfaces encompassing prompt injection, tool-mediated control hijacking, persistent memory poisoning, and multi-agent vulnerability propagation, while defensive layers (privilege hierarchies, runtime guards, sandboxes) remain weakly compositional. | https://arxiv.org/abs/2606.10749 | SUPPORTED | The source establishes that agent security models information flow, delegated authority, and persistent state, identifies the specified threat surfaces, and concludes that current defensive layers remain weakly compositional. | current defenses provide useful building blocks but remain weakly compositional |

## Index Mismatch Report

Matching the supplied spot-check claim numbers against the canonical metadata in `sources.json` and the citations in `report.md` reveals shifts in numbering caused by intermediate entries in the repository source registry:

| Spot-Check # | Canonical Title | URL | Repo Source ID | Report Citation | Index Status / Discrepancy |
| :---: | :--- | :--- | :---: | :---: | :--- |
| 1 | ReAct: Synergizing Reasoning and Acting in Language Models | https://arxiv.org/abs/2210.03629 | [1] | [1] | Aligned: Spot-check index matches repository index [1]. |
| 2 | Toolformer: Language Models Can Teach Themselves to Use Tools | https://arxiv.org/abs/2302.04761 | [2] | [2] | Aligned: Spot-check index matches repository index [2]. |
| 3 | SPIRAL: Symbolic LLM Planning via Grounded and Reflective Search | https://huggingface.co/papers/2512.23167 | [3] | [3] | Aligned: Spot-check index matches repository index [3]. |
| 4 | Tool-R0: Self-Evolving LLM Agents for Tool-Learning from Zero Data | https://huggingface.co/papers/2602.21320 | [4] | [4] | Aligned: Spot-check index matches repository index [4]. |
| 5 | The Building Block Economy: How Agent-Native Tools Are Reshaping What It Means to Build Software | https://codex.danielvaughan.com/2026/07/19/building-block-economy-agent-native-tools-composable-services-codex-cli-developer-role-shift/ | [7] | [7] | Shifted (+2): Spot-check #5 corresponds to source [7] in `sources.json` and `report.md`, offset by entries [5] (Meta-tools) and [6] (HyperTool). |
| 6 | Skill Constellations: Tracing the Supply Chain of Agent Skills on GitHub | https://huggingface.co/papers/2610.11169 | [10] | [10] | Shifted (+4): Spot-check #6 corresponds to source [10] in `sources.json` and `report.md`, offset by entries [8] (Evaluation review) and [9] (AEMA). |
| 7 | Toward Secure LLM Agents: Threat Surfaces, Attacks, Defenses, and Evaluation | https://arxiv.org/abs/2606.10749 | [11] | [11] | Shifted (+4): Spot-check #7 corresponds to source [11] in `sources.json` and `report.md`, offset by intermediate entries [8] and [9]. |

## Detailed Claim Analyses

### 1. ReAct
- **URL:** https://arxiv.org/abs/2210.03629
- **Verdict:** PARTIAL
- **Supported Elements:** Interleaving natural language reasoning traces and domain actions to dynamically maintain and update action plans, handle operational exceptions, and incorporate environmental observations into reasoning.
- **Unverified Elements / Discrepancies:** The retrieved text does not evaluate or mention greedy decision making versus explicit tree search methods.
- **Verbatim Excerpt:** `update action plans as well as handle exceptions` (8 words)

### 2. Toolformer
- **URL:** https://arxiv.org/abs/2302.04761
- **Verdict:** UNSUPPORTED
- **Supported Elements:** General concept of self-supervised tool usage via APIs (e.g., calculator, question answering, search engines).
- **Unverified Elements / Discrepancies:** The retrieved abstract does not contain evidence regarding candidate API calls being generated independently across text during dataset construction, the absence of chained tool use demonstrations in the fine-tuning data, or why this restriction occurred.
- **Verbatim Excerpt:** `decide which APIs to call, when to call them` (9 words)

### 3. SPIRAL
- **URL:** https://huggingface.co/papers/2512.23167
- **Verdict:** PARTIAL
- **Supported Elements:** Embedding a tri-agent cognitive architecture (Planner, Simulator, Critic) into a Monte Carlo Tree Search loop, where the Planner proposes steps, the Simulator models realistic outcomes, and the Critic supplies reflective dense reward signals.
- **Unverified Elements / Discrepancies:** The retrieved abstract does not discuss search latency trade-offs, compute costs, or dependence on simulator fidelity (in fact, it highlights superior token efficiency).
- **Verbatim Excerpt:** `embeds a cognitive architecture of three specialized LLM agents` (9 words)

### 4. Tool-R0
- **URL:** https://huggingface.co/papers/2602.21320
- **Verdict:** PARTIAL
- **Supported Elements:** Training general-purpose tool-using agents from scratch without initial datasets or human demonstrations via self-play reinforcement learning, co-evolving a Generator and a Solver with complementary rewards.
- **Unverified Elements / Discrepancies:** The retrieved abstract does not mention synthesizing tasks based on Solver uncertainty, outcome-based rewards, or scoped challenges in exploration stability.
- **Verbatim Excerpt:** `co-evolves a Generator and a Solver with complementary rewards` (9 words)

### 5. Building Block Economy
- **URL:** https://codex.danielvaughan.com/2026/07/19/building-block-economy-agent-native-tools-composable-services-codex-cli-developer-role-shift/
- **Verdict:** SUPPORTED
- **Supported Elements:** Characterization of the building block economy where agents select and compose standardized remote services (specifically citing Model Context Protocol servers) rather than generating implementation code from scratch, along with explicit identification of failure modes including service version drift, abstraction leakage, and operational overhead from compounding latency.
- **Unverified Elements / Discrepancies:** None.
- **Verbatim Excerpt:** `building block economy has failure modes that differ` (8 words)

### 6. Skill Constellations
- **URL:** https://huggingface.co/papers/2610.11169
- **Verdict:** PARTIAL
- **Supported Elements:** Agent skills on GitHub forming an unmanaged software supply chain lacking registries, versions, and provenance; security fixes at the source rarely propagating downstream; and an audit ranking model outperforming star counts.
- **Unverified Elements / Discrepancies:** The retrieved abstract does not state that copied skills frequently acquire privileged execution capabilities (only that skills run with user permissions), nor does it explicitly name conditional logit estimation as the underlying model.
- **Verbatim Excerpt:** `software supply chain without a registry, versions or provenance` (9 words)

### 7. Toward Secure LLM Agents
- **URL:** https://arxiv.org/abs/2606.10749
- **Verdict:** SUPPORTED
- **Supported Elements:** Modeling agent security across information flow, delegated authority, and persistent state; identifying prompt injection, tool-mediated control-flow hijacking, persistent state corruption, and multi-agent propagation as primary threats; and concluding that current defensive layers remain weakly compositional.
- **Unverified Elements / Discrepancies:** None regarding substantive claims. The parenthetical defense examples illustrate defensive layers from the broader literature review.
- **Verbatim Excerpt:** `current defenses provide useful building blocks but remain weakly compositional` (10 words)
