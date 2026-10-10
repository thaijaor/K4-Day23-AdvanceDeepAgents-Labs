# Survey: Reinforcement Learning for LLM Reasoning

## TL;DR
- Post-training has evolved from actor-critic algorithms like Proximal Policy Optimization (PPO) [1] to critic-free group-relative methods like GRPO [2], eliminating critic parameters while shifting memory pressure to rollout generation.
- PPO's probability ratio clipping is an empirical surrogate heuristic rather than a guaranteed trust region [1], leaving stability reliant on auxiliary code-level optimizations [3].
- Process reward models such as Math-Shepherd automate step-level verification without human annotations [4], while GRPO implicitly approximates step-level credit assignment across shared rollout prefixes [5].
- Whether reinforcement learning with verifiable rewards (RLVR) expands reasoning boundaries depends on evaluation methodology: outcome pass@k exhibits a support-constrained "invisible leash" [6][7], whereas intermediate verification (CoT-Pass@K) reveals genuine reasoning gains by filtering out lucky guesses [8].
- Frontier post-training is transitioning toward structured graph representations [9], meta-reasoning evaluation [10], multi-turn interaction [11], and branching tree search [12][13].

## Background
Reinforcement learning (RL) enhances multi-step reasoning in Large Language Models (LLMs). Early post-training adopted Proximal Policy Optimization (PPO) [1], which optimizes a clipped surrogate policy gradient objective. In actor-critic implementations, PPO uses a learned state-value baseline $V(s)$ representing expected cumulative rewards from state $s$ rather than an action-value $Q(s, a)$ function [1], enabling variance-reduced advantage estimation. However, maintaining a separate critic introduces significant memory overhead and complexity in autoregressive generation.

Although PPO is motivated by trust-region policy optimization, its ratio-clipping mechanism is an unconstrained surrogate heuristic [1] that fails to guarantee a bounded trust region on policy divergence [3]. Practical stability relies instead on auxiliary code-level optimizations, including value function clipping, learning rate annealing, and orthogonal initialization [3].

To resolve critic memory overhead, Group Relative Policy Optimization (GRPO) was introduced in DeepSeekMath [2]. GRPO discards the critic network, estimating baselines directly from normalized scores across a group of sampled completions for each prompt [2]. Concurrently, process reward models (PRMs) like Math-Shepherd [4] demonstrated that automated step-level verification provides fine-grained supervision without manual annotations. However, process rewards exhibit scoped experimental benefits rather than universal superiority over outcome reward models (ORMs), as intermediate credit assignment remains vulnerable to process reward hacking and estimation noise [5].

## Critic-Free Optimization and Post-Training Stabilization
Eliminating the critic network in GRPO reduces model-state memory by removing critic weights and optimizer states [2]. However, total training memory is divided across parameters, optimizer states, activations, KV caches, and rollout buffers [14]. Because GRPO samples multiple completions per prompt for group baselines, it expands active rollout tokens and KV cache footprints [2][14].

Importantly, PPO is not restricted to a single completion per prompt; fair cost comparisons require matching rollout budgets across algorithms [2][14]. When budgets are matched or parameters are sharded across accelerators, training bottlenecks shift from model-state storage to activation memory and KV caches [14], where multi-sample rollouts can offset critic savings [14].

Stabilizing group-relative training requires addressing three distinct failure modes:
1. **Length Bias and Loss Normalization**: Standard GRPO calculates advantages at the sequence level and applies uniform updates across tokens [2]. Normalizing loss by completion length assigns larger per-token updates to shorter solutions, inadvertently favoring brevity over detailed reasoning [14]. Token-level loss aggregation (as in DAPO [14]) and frequency weighting [5] average gradients across total tokens, preserving comprehensive deductions.
2. **Exploration and Policy Entropy**: High-variance reward landscapes can lead to entropy collapse, where policies rapidly exploit early high-reward trajectories and cease exploring alternative paths [14]. In DAPO's empirical study [14], adding standard entropy bonuses degraded accuracy by introducing excessive uncertainty, while forcing non-zero advantage sampling caused objective misalignment. Mitigating variance through tailored group baselines, as in BiasGRPO [15], provides more stable updates.
3. **KL Regularization**: Restricting policy drift from a reference model via a KL penalty scaled by $\beta$ exhibits a non-monotonic response [14]. Moderate penalties ensure optimization stability, whereas excessive penalties over-constrain the policy and impede reasoning gains [14].

## Process Supervision versus Implicit Outcome-Based Credit Assignment
Outcome Reward Models (ORMs) provide sparse feedback based strictly on final answers, risking positive reinforcement for erroneous deductions that reach correct solutions by chance [2][4]. Process Reward Models (PRMs) mitigate this by evaluating each intermediate step [4].

Addressing the cost of human supervision, Math-Shepherd constructs automated step-level process supervision without manual annotations [4]. While effective for step-level guidance, process supervision exhibits scoped experimental benefits rather than universal dominance over outcome reward models, facing risks of process-level reward hacking and evaluation noise [5].

Moreover, group-relative policy optimization inherently provides implicit process supervision [5]. When multiple rollouts are sampled from the same prompt, completions share overlapping prefix trajectories before branching [5]. Because identical prefix tokens across divergent completions receive differential outcome rewards, standard GRPO mathematically approximates a Monte Carlo process reward model [5]. However, this implicit mechanism suffers from prefix frequency imbalance: frequently traversed early steps accumulate disproportionate gradient updates [5]. Normalizing prefix frequency, as implemented in $\lambda$-GRPO, resolves this gradient distortion and accelerates training convergence [5].

## The Reasoning Boundary: Support Constraints versus Intermediate Verification
A central question in post-training is whether Reinforcement Learning with Verifiable Rewards (RLVR) expands an LLM's intrinsic reasoning boundary or merely sharpens sampling within its pre-existing support.

Studies evaluating outcome-based pass@k suggest that RLVR acts as a support-constrained precision optimizer bound by an "invisible leash" [6][7]. The invisible leash hypothesis asserts that online RLVR cannot discover reasoning paths with negligible initial probability in the base model's distribution [6]. RLVR improves greedy accuracy ($pass@1$) by concentrating probability mass on known successful trajectories, but contracts broader exploration coverage [6][7]. Yue et al. [7] demonstrate that under large trial budgets $k$, the base model matches or exceeds the RLVR-trained model in outcome coverage, as support shrinkage outpaces support expansion [6][7]. Generated reasoning chains remain largely within the base model's prior distribution, whereas true capability expansion requires distillation from stronger teachers like DeepSeek-R1 [16][7].

In contrast, Wen et al. [8] show that base model pass@k advantages stem from lucky guessing on integer-answer benchmarks. When evaluated with CoT-Pass@K—which requires both intermediate reasoning steps and final answers to be verified—the RLVR-trained model consistently outperforms the base model across all values of $k$ [8]. This confirms that RLVR actively reinforces logically valid reasoning structures while suppressing invalid chains [8].

## Interactive Environments, Meta-Reasoning, and Structured Search
Post-training research is expanding beyond single-turn outcome verification toward structured, multi-turn, and search-guided reasoning.

To prevent models from exploiting superficial formatting tricks, the Graph Reasoning Paradigm (GRP) introduces symbolic, topology-aware reinforcement learning [9]. GRP structures text into cognitive graph representations, rewarding valid topological flow and mitigating gibberish reward hacking [9].

Simultaneously, interactive benchmarks expose the limitations of single-turn training. MTR-Bench evaluates models across Information Probing, Dynamic Adaptation, State Operation, and Strategic Gaming [11], showing that single-turn competence does not ensure robust multi-turn interaction or adaptive error correction [11].

Furthermore, logical competence requires meta-reasoning. The MR-GSM8K benchmark evaluates models on detecting, explaining, and correcting reasoning errors [10]. Frontier models exhibit deficiencies here, indicating that standard RLVR over-optimizes forward generation at the expense of deductive critique [10].

To promote exploratory breadth during training, recent frameworks incorporate tree search. Difficulty-Adaptive Tree-Structured Policy Optimization (DATPO) organizes rollouts into tree structures with sibling-diversity rewards to explore alternative valid deductions [12]. Similarly, Branching Policy Optimization (BPO) samples trajectories from intermediate sandbox states, enabling language agents to master complex decision branches [13].

## Trends and open problems
Reinforcement learning for LLM reasoning is advancing rapidly toward critic-free optimization, process verification, and interactive problem solving. Key open challenges include:
1. **Generalization Beyond Closed Verifiable Domains**: Current RLVR relies heavily on automated ground-truth verifiers in mathematics and coding [2][16]. Adapting post-training to open-ended and commonsense domains remains constrained by high reward variance and lack of robust verifiers [13].
2. **Exploration and Policy Entropy Maintenance**: Preventing entropy collapse over extended training without injecting harmful token randomness requires principled group baseline formulations [14], diversity incentives [12], and variance mitigation [15].
3. **Rigorous Evaluation Metrics**: The divergence between outcome pass@k and intermediate-verified CoT-Pass@K underlines the risk of lucky guesses [8]. Future evaluation must incorporate intermediate verification [8], meta-reasoning critique [10], and multi-turn environments [11].
4. **Rollout Throughput and KV Cache Scaling**: While removing critics eliminates value model memory [2], online rollout sampling and KV cache demands remain the primary throughput bottleneck [14]. Scaling post-training necessitates tight integration with high-throughput serving engines and cache compression techniques [14].

## References
[1] [1707.06347] Proximal Policy Optimization Algorithms. web. https://arxiv.org/abs/1707.06347 (2017-07-20)
[2] DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models. arxiv. https://arxiv.org/abs/2402.03300 (2024-02-05)
[3] Implementation Matters in Deep PolicyGradients: A Case Study on PPO and TRPO. web. https://arxiv.org/abs/2005.12729 (n.d.)
[4] Math-Shepherd: Verify and Reinforce LLMs Step-by-step without Human Annotations. web. https://huggingface.co/papers/2312.08935 (n.d.)
[5] GRPO is Secretly a Process Reward Model. hf-search. https://huggingface.co/papers/2509.21154 (2025-09-25)
[6] The Invisible Leash? Why RLVR May or May Not Escape Its Origin. web. https://arxiv.org/abs/2507.14843 (n.d.)
[7] Does Reinforcement Learning Really Incentivize .... web. https://arxiv.org/abs/2504.13837 (n.d.)
[8] Reinforcement Learning with Verifiable Rewards Implicitly Incentivizes Correct Reasoning in Base LLMs. web. https://arxiv.org/abs/2506.14245 (n.d.)
[9] Graph Reasoning Paradigm: Structured and Symbolic Reasoning with Topology-Aware Reinforcement Learning for Large Language Models - ACL Anthology. web. https://aclanthology.org/2026.acl-long.1660/ (n.d.)
[10] MR-GSM8K: A Meta-Reasoning Revolution in Large Language Model Evaluation. web. https://arxiv.org/html/2312.17080v2 (n.d.)
[11] MTR-Bench: A Comprehensive Benchmark for Multi-Turn Reasoning Evaluation - ACL Anthology. web. https://aclanthology.org/2026.acl-long.984/ (n.d.)
[12] [2609.08650] Difficulty-Adaptive Tree-Structured Policy Optimization for Expanding Reasoning Coverage in RLVR. web. https://arxiv.org/abs/2609.08650 (2026-09-08)
[13] Branching Policy Optimization: Sandbox-Native Language Agent Reinforcement Learning. arxiv. https://arxiv.org/abs/2607.14171 (2026-07-15)
[14] Comparative Analysis and Parametric Tuning of PPO, GRPO, and DAPO for LLM Reasoning Enhancement. web. https://arxiv.org/abs/2512.07611 (n.d.)
[15] BiasGRPO: Stabilizing Bias Mitigation in High-Variance Reward Landscapes via Group-Relative Policy Optimization. arxiv. https://arxiv.org/abs/2606.04807 (2026-06-03)
[16] DeepSeek-R1: Incentivizing Reasoning Capability in LLMs .... web. https://arxiv.org/abs/2501.12948 (2025-01-22)
