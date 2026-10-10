# Advancing Autonomy: A Survey of LLM Agents and Tool Use

## TL;DR
* Foundational frameworks like ReAct [1] and Toolformer [2] established agentic reasoning by interleaving verbal thoughts with actions and introducing self-supervised tool use.
* Advanced planning architectures, including SPIRAL's grounded tree search [3] and Tool-R0's zero-data self-play reinforcement learning [4], enable structured deliberation and autonomous tool discovery.
* Composable tooling spans execution abstractions like meta-tools [5] and programmatic tool calling [6] to conceptual paradigms like the Building Block Economy [7].
* Trustworthy agent deployment requires transitioning to process-aware evaluation [8] [9] and mitigating unmanaged skill supply chains [10] and systemic attack surfaces [11].

## Background
The transition of large language models (LLMs) from static text generators into active autonomous agents represents a fundamental paradigm shift. Early models operated as single-turn predictors bound to static parameters and vulnerable to factual hallucination during multi-step reasoning. Scaffolding models with dynamic reasoning traces and external interfaces resolved these boundaries.

Central to this progression is **ReAct** [1], which introduced synergistic interleaving of reasoning traces ("thoughts") with task actions. Augmenting the action space with natural language thoughts enables agents to track plans, maintain working memory, and process observations to handle runtime exceptions. Complementing prompt interleaving, **Toolformer** [2] demonstrated that language models acquire tool use through self-supervised pre-training. Rather than relying on human demonstrations, Toolformer trains models to decide which APIs to call, when to invoke them, and how to integrate returned results into token predictions via a perplexity-based filtering loss that retains API calls reducing prediction loss on subsequent tokens. Dynamic interleaved reasoning and model-level API integration established the bedrock for modern autonomous agents.

## The Architecture of Agentic Reasoning
Agentic reasoning has evolved from prompting heuristics into structured control loops, contrasting foundational prompt-based and fine-tuning methods with symbolic search and reinforcement learning.

At the foundational level, ReAct [1] establishes an in-context loop coupling reasoning, execution, and observation. This feedback loop allows agents to update plans dynamically and handle operational exceptions during execution. By grounding reasoning in external observations, ReAct mitigates error propagation across interactive workflows.

Toolformer [2] integrates tools at the parameter level via self-supervised perplexity filtering, teaching models to invoke external tools without task-specific fine-tuning datasets. Nevertheless, Toolformer's original implementation focused on discrete, independent API calls rather than chained multi-tool execution where one tool's output directly feeds into another. This limitation reflects the independent candidate generation method rather than an inherent barrier to parametric tool use.

To advance beyond linear prompting and independent tool calls, modern architectures introduce formal search and reinforcement learning. **SPIRAL** [3] embeds a multi-agent cognitive architecture in a Monte Carlo Tree Search (MCTS) loop, using Planner, Simulator, and Critic roles to guide deliberation across branching paths. Concurrently, **Tool-R0** [4] eliminates human demonstrations via zero-data self-play reinforcement learning, co-evolving a task Generator and task Solver with complementary rewards.

## Evolution of Planning and Tool Learning
Modern agentic architectures emphasize structured planning and autonomous skill acquisition over static prompting. Planning has shifted from linear execution to grounded tree search, while tool learning has progressed from imitation to self-evolving reinforcement learning.

In search-based planning, **SPIRAL** [3] employs MCTS with symbolic reasoning. A Planner proposes actions, a Simulator models state transitions to ground exploration, and a Critic computes dense reflective rewards. However, tree search planning generally introduces operational trade-offs: multi-agent search requires multiple model invocations per decision step for expansion, simulation, and evaluation, which increases latency and compute costs. Furthermore, search validity depends heavily on simulation fidelity, as inaccurate state transitions risk propagating flawed values through the decision tree.

In parallel, autonomous tool learning has advanced through self-play reinforcement learning. **Tool-R0** [4] trains tool-using agents from scratch without human demonstrations. By co-evolving a Generator proposing challenging tasks and a Solver learning tool invocations with real-world calls, the framework creates an adaptive self-play curriculum. As with autonomous reinforcement learning systems generally, maintaining balanced curriculum difficulty and exploration stability is essential to support robust policy convergence.

## The Shift to Composable Tooling
As agents encounter diverse digital interfaces, system designers must manage tool schema complexity. Proliferation of atomic tools expands context windows, introduces selection ambiguity, and degrades reliability. To mitigate these issues, recent research emphasizes "tool minimalism"—consolidating toolsets into concise, non-overlapping schemas to reduce model distractions and enhance decision clarity [12].

Beyond prompt curation, execution-level abstractions optimize multi-step workflows. Frameworks like **HyperTool** [6] address execution granularity mismatches where granular tool calls clutter context windows. By exposing a unified programmatic interface, HyperTool enables models to write code blocks that invoke multiple tools, manage intermediate variables, and transfer state locally, returning only final outputs. Similarly, **Agent Workflow Optimization (AWO)** [5] analyzes historical logs to detect recurring sequential tool calls, coalescing them into deterministic "meta-tools" that reduce redundant LLM invocations and improve workflow stability.

In parallel, developer communities discuss the "Building Block Economy" [7]. Rather than representing an empirical efficiency model, this is an opinionated design perspective describing a shift where agents compose standardized remote services (such as Model Context Protocol servers) instead of writing custom application logic. Human engineers shift from writing imperative code to architectural curation. However, this perspective introduces failure modes: service version drift from asynchronous updates, abstraction leakage when debugging stateful interactions, and operational overhead from compounding network latency across remote microservices [7].

## Evaluation, Trust, and Security
Deploying autonomous agents in production introduces critical evaluation, reliability, and security bottlenecks. Traditional benchmark practices and unmanaged tool ecosystems often obscure operational failure modes.

A comprehensive review of agentic evaluation highlights a pronounced divergence between benchmark success and deployment viability [8]. Standard benchmarks predominantly evaluate binary task completion under static conditions, omitting cost efficiency, trajectory conciseness, and runtime safety. Consequently, high task success can mask unmaintainable code or redundant tool executions. To bridge this gap, modern methodologies emphasize multidimensional frameworks incorporating cost-normalized success, trajectory quality, and safety-constrained completion [8].

To enhance scoring consistency, the **AEMA** framework [9] implements a verifiable multi-agent evaluation architecture under human oversight. AEMA coordinates specialized agent roles—including a Planning Agent debating evaluation steps, a Prompt-Refinement Agent retrieving domain-specific functions via hybrid search, Evaluation Agents, and a Final Report Agent. Prioritizing transparent deliberation and auditability mitigates scoring drift common to single LLM judges [9].

Simultaneously, the supply chain integrity of agent ecosystems presents operational risks. An investigation into agent skill sharing on GitHub—where skills combine executable scripts and documentation run with user permissions—reveals an unmanaged supply chain lacking formal registries, versioning, or provenance tracking [10]. Upstream patches rarely propagate to downstream copies, leaving forks vulnerable to known security issues. To improve security, statistical source-choice auditing models can prioritize high-risk repositories for security audits far more effectively than popularity indicators like star counts [10].

At the systems level, agent security spans three dimensions: information flow, delegated authority, and state [11]. Beyond prompt injection, threat surfaces encompass tool-mediated control hijacking, persistent memory poisoning, and multi-agent vulnerability propagation. Existing defensive layers—including privilege hierarchies, runtime guards, and sandboxes—provide essential protections but remain weakly compositional, requiring careful engineering to avoid compounding latency and execution costs [11].

## Trends and open problems
Addressing open challenges in autonomous agent systems requires concerted advances across several research frontiers:
* **Standardizing Composable Security Stacks:** Current defensive primitives, including instruction hierarchies, input classifiers, and isolated sandboxes, remain weakly compositional [11]. Developing unified architectures that guarantee safety invariants across stateful tool executions without incurring prohibitive latency remains an essential priority.
* **Process-Aware and Cost-Normalized Evaluation:** Moving beyond binary task completion requires standardizing multidimensional evaluation protocols [8]. Incorporating cost normalization, trajectory conciseness, and verifiable multi-agent auditability [9] is critical for determining production readiness.
* **Securing the Agent Skill Supply Chain:** Unmanaged skill copying without provenance or automated fix propagation creates widespread vulnerabilities [10]. Establishing trusted registries, cryptographic provenance, and automated patch notification mechanisms is vital for secure tool sharing.
* **Mitigating Stateful and Multi-Agent Vulnerabilities:** As agents incorporate persistent memory and communicate across distributed topologies, threats such as memory poisoning and cascading failures become prominent [11]. Benchmarking and mitigating state corruption across extended interactions represents an urgent frontier.
* **Balancing Search Deliberation and Execution Efficiency:** While symbolic search architectures like SPIRAL [3] offer structured recovery, their computational latency is substantial. Reconciling expressive tree search with lightweight execution abstractions like meta-tools [5] and programmatic tool composition [6] is crucial for cost-effective deployment.

## References
[1] ReAct: Synergizing Reasoning and Acting in Language Models. web. https://arxiv.org/abs/2210.03629 (2023-03-10)
[2] [2302.04761] Toolformer: Language Models Can Teach Themselves to Use Tools. web. https://arxiv.org/abs/2302.04761 (2023-02-09)
[3] SPIRAL: Symbolic LLM Planning via Grounded and Reflective Search. hf-search. https://huggingface.co/papers/2512.23167 (2025-12-29)
[4] Tool-R0: Self-Evolving LLM Agents for Tool-Learning from Zero Data. hf-search. https://huggingface.co/papers/2602.21320 (2026-02-24)
[5] Optimizing Agentic Workflows using Meta-tools. web. https://arxiv.org/html/2601.22037v2 (2026-02-02)
[6] HyperTool: Beyond Step-Wise Tool Calls for Tool-Augmented Agents. web. https://arxiv.org/abs/2606.13663 (2026-06-11)
[7] The Building Block Economy: How Agent-Native Tools Are Reshaping What It Means to Build Software | Codex Knowledge Base. web. https://codex.danielvaughan.com/2026/07/19/building-block-economy-agent-native-tools-composable-services-codex-cli-developer-role-shift/ (2026-07-19)
[8] From benchmarks to deployment: a comprehensive review of agentic AI evaluation | springerprofessional.de. web. https://www.springerprofessional.de/from-benchmarks-to-deployment-a-comprehensive-review-of-agentic-/52333694 (2026-04-24)
[9] AEMA: Verifiable Evaluation Framework for Trustworthy and Controlled Agentic LLM Systems. web. https://arxiv.org/abs/2601.11903 (n.d.)
[10] Skill Constellations: Tracing the Supply Chain of Agent Skills on GitHub. hf-daily. https://huggingface.co/papers/2610.11169 (2026-10-08)
[11] [2606.10749] Toward Secure LLM Agents: Threat Surfaces, Attacks, Defenses, and Evaluation. web. https://arxiv.org/abs/2606.10749 (2026-06-09)
[12] Tool Minimalism and High-Level Prompting. web. https://agentpatterns.ai/tool-engineering/tool-minimalism/ (n.d.)
