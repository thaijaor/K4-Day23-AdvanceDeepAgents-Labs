# Citation Audit Report

## Audit Summary

- Total claims audited: 7
- SUPPORTED: 5
- PARTIAL: 2
- UNSUPPORTED: 0
- UNVERIFIABLE: 0

All claim and source pairs were verified directly against text retrieved via live web fetching of the specified URLs. Two claims are rated PARTIAL because the fetched document abstracts omit specific technical mechanisms or comparative qualifications stated in the claims, while the remaining five claims are fully SUPPORTED.

---

## Citation Index Mismatch Report

A comparison between the audit order (items 1–7) and the reference list in `/tmp/work/report/report.md` and `/tmp/work/research/sources.json` reveals several index shifts:

1. **Audit Pair 1** (`https://arxiv.org/abs/1707.06347` - *Proximal Policy Optimization Algorithms*):
   - Corresponds to **Reference [1]**. Index is aligned.
2. **Audit Pair 2** (`https://arxiv.org/abs/2005.12729` - *Implementation Matters in Deep Policy Gradients*):
   - Corresponds to **Reference [3]** in `report.md`. Index mismatch: Audit Item 2 maps to Reference [3].
3. **Audit Pair 3** (`https://arxiv.org/abs/2402.03300` - *DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models*):
   - Corresponds to **Reference [2]** in `report.md`. Index mismatch: Audit Item 3 maps to Reference [2].
4. **Audit Pair 4** (`https://huggingface.co/papers/2312.08935` - *Math-Shepherd: Verify and Reinforce LLMs Step-by-step without Human Annotations*):
   - Corresponds to **Reference [4]**. Index is aligned.
5. **Audit Pair 5** (`https://arxiv.org/abs/2507.14843` - *The Invisible Leash? Why RLVR May or May Not Escape Its Origin*):
   - Corresponds to **Reference [6]** in `report.md`. Index mismatch: Reference [5] (*GRPO is Secretly a Process Reward Model*, `https://huggingface.co/papers/2509.21154`) was omitted from the spot-check list, shifting Item 5 to Reference [6].
6. **Audit Pair 6** (`https://arxiv.org/abs/2506.14245` - *Reinforcement Learning with Verifiable Rewards Implicitly Incentivizes Correct Reasoning in Base LLMs* by Wen et al.):
   - Corresponds to **Reference [8]** in `report.md`. Index mismatch: Audit Item 6 maps to Reference [8].
7. **Audit Pair 7** (`https://arxiv.org/abs/2504.13837` - *Does Reinforcement Learning Really Incentivize Reasoning Capacity in LLMs Beyond the Base Model?* by Yue et al.):
   - Corresponds to **Reference [7]** in `report.md`. Index mismatch: Audit Item 7 maps to Reference [7], inverted in sequence relative to Reference [8].

---

## Audit Table

| Claim | URL | Verdict | Evidence | Excerpt |
| :--- | :--- | :--- | :--- | :--- |
| PPO uses a critic network estimating a scalar state-value baseline V(s) representing expected cumulative rewards from state s rather than an action-value Q(s, a) function, enabling variance-reduced advantage estimation. | https://arxiv.org/abs/1707.06347 | PARTIAL | The abstract identifies PPO as a surrogate policy gradient method but omits critic baseline details and variance-reduced advantage estimation. | family of policy gradient methods for reinforcement learning |
| PPO's probability ratio clipping is an unconstrained surrogate heuristic that fails to mathematically enforce a bounded trust region on policy divergence, with practical stability relying on auxiliary code-level optimizations like value function clipping and learning rate annealing. | https://arxiv.org/abs/2005.12729 | SUPPORTED | The paper demonstrates that PPO trust region enforcement fails without implementation-level adjustments like value function clipping and learning rate annealing. | optimizations turn out to have a major impact |
| Group Relative Policy Optimization (GRPO) discards the separate critic network and estimates the baseline directly from normalized rewards across a group of sampled completions for each prompt. | https://arxiv.org/abs/2402.03300 | SUPPORTED | DeepSeekMath introduces GRPO as an algorithm that foregoes the critic model by calculating the baseline from group scores. | GRPO foregoes the critic model, instead estimating the baseline |
| Math-Shepherd constructs automated step-level process supervision via Monte Carlo rollouts from intermediate states without requiring human annotations, providing scoped empirical benefits rather than universal superiority over outcome reward models. | https://huggingface.co/papers/2312.08935 | PARTIAL | The abstract confirms automated step supervision without manual annotation, but excludes mention of Monte Carlo rollouts or scoped advantages over outcome models. | automatically constructed process-wise supervision data, breaking the bottleneck |
| Standard RLVR operates as a support-constrained precision optimizer bound by an "invisible leash" to the base model's prior distribution, where outcome pass@k coverage is bounded as support shrinkage outpaces support expansion at large sampling budgets. | https://arxiv.org/abs/2507.14843 | SUPPORTED | The authors formalize the invisible leash concept by showing that support shrinkage exceeds support expansion under large sampling budgets in RLVR. | shrinkage of empirical support generally outweighs the expansion |
| When evaluated with CoT-Pass@K—which requires both intermediate reasoning steps and final answers to be verified—RLVR models consistently outperform base models across sample budgets, demonstrating that outcome pass@k advantages of base models are inflated by lucky guessing on simple final answers. | https://arxiv.org/abs/2506.14245 | SUPPORTED | The study introduces a metric requiring both intermediate reasoning and final answers to be verified, showing that base model pass gains stem from coincidental guessing. | evaluates success only when both the final answer |
| Reasoning paths generated by RLVR models remain largely within the sampling distribution of the base model under coverage analysis, whereas knowledge distillation from stronger reasoning models like DeepSeek-R1 genuinely introduces novel reasoning patterns. | https://arxiv.org/abs/2504.13837 | SUPPORTED | The authors show that RLVR reasoning trajectories stay within the base model distribution while knowledge distillation from teacher models introduces novel reasoning paths. | distillation can introduce new reasoning patterns from the teacher |

---

## Detailed Item Assessments

### Pair 1
- **Claim**: PPO uses a critic network estimating a scalar state-value baseline V(s) representing expected cumulative rewards from state s rather than an action-value Q(s, a) function, enabling variance-reduced advantage estimation.
- **URL**: `https://arxiv.org/abs/1707.06347`
- **Verdict**: PARTIAL
- **Fetched Excerpt**: `family of policy gradient methods for reinforcement learning` (8 words)
- **Evidence Explanation**: The abstract identifies PPO as a surrogate policy gradient method but omits critic baseline details and variance-reduced advantage estimation.
- **Analysis**:
  - *Supported portions*: The source verifies that PPO is a reinforcement learning policy gradient method optimizing surrogate objectives.
  - *Unsupported portions*: The fetched abstract does not state that PPO deploys a critic network estimating a scalar state-value baseline V(s) rather than an action-value function Q(s, a), nor does it explicitly detail variance-reduced advantage estimation.

### Pair 2
- **Claim**: PPO's probability ratio clipping is an unconstrained surrogate heuristic that fails to mathematically enforce a bounded trust region on policy divergence, with practical stability relying on auxiliary code-level optimizations like value function clipping and learning rate annealing.
- **URL**: `https://arxiv.org/abs/2005.12729`
- **Verdict**: SUPPORTED
- **Fetched Excerpt**: `optimizations turn out to have a major impact` (8 words)
- **Evidence Explanation**: The paper demonstrates that PPO trust region enforcement fails without implementation-level adjustments like value function clipping and learning rate annealing.
- **Analysis**:
  - *Supported portions*: The paper investigates code-level optimizations in PPO and TRPO, establishing that ratio clipping does not strictly enforce trust regions and that stability and gains stem primarily from implementation augmentations, explicitly citing value function clipping and learning rate annealing.

### Pair 3
- **Claim**: Group Relative Policy Optimization (GRPO) discards the separate critic network and estimates the baseline directly from normalized rewards across a group of sampled completions for each prompt.
- **URL**: `https://arxiv.org/abs/2402.03300`
- **Verdict**: SUPPORTED
- **Fetched Excerpt**: `GRPO foregoes the critic model, instead estimating the baseline` (9 words)
- **Evidence Explanation**: DeepSeekMath introduces GRPO as an algorithm that foregoes the critic model by calculating the baseline from group scores.
- **Analysis**:
  - *Supported portions*: The text explicitly introduces GRPO as a PPO variant that discards the critic model and estimates the baseline directly from group scores, drastically reducing memory and resource overhead.

### Pair 4
- **Claim**: Math-Shepherd constructs automated step-level process supervision via Monte Carlo rollouts from intermediate states without requiring human annotations, providing scoped empirical benefits rather than universal superiority over outcome reward models.
- **URL**: `https://huggingface.co/papers/2312.08935`
- **Verdict**: PARTIAL
- **Fetched Excerpt**: `automatically constructed process-wise supervision data, breaking the bottleneck` (8 words)
- **Evidence Explanation**: The abstract confirms automated step supervision without manual annotation, but excludes mention of Monte Carlo rollouts or scoped advantages over outcome models.
- **Analysis**:
  - *Supported portions*: The fetched text verifies that Math-Shepherd develops an innovative process-oriented reward model assigning step-level rewards using automatically generated process supervision without manual human annotation.
  - *Unsupported portions*: The fetched abstract page does not state that the supervision is constructed via Monte Carlo rollouts from intermediate states, nor does it describe its benefits as scoped or non-universally superior to outcome reward models.

### Pair 5
- **Claim**: Standard RLVR operates as a support-constrained precision optimizer bound by an "invisible leash" to the base model's prior distribution, where outcome pass@k coverage is bounded as support shrinkage outpaces support expansion at large sampling budgets.
- **URL**: `https://arxiv.org/abs/2507.14843`
- **Verdict**: SUPPORTED
- **Fetched Excerpt**: `shrinkage of empirical support generally outweighs the expansion` (8 words)
- **Evidence Explanation**: The authors formalize the invisible leash concept by showing that support shrinkage exceeds support expansion under large sampling budgets in RLVR.
- **Analysis**:
  - *Supported portions*: The study describes RLVR as a support-constrained optimization mechanism bounded by an invisible leash to base initialization, proving empirically that support shrinkage outweighs support expansion under higher sampling budgets.

### Pair 6
- **Claim**: When evaluated with CoT-Pass@K—which requires both intermediate reasoning steps and final answers to be verified—RLVR models consistently outperform base models across sample budgets, demonstrating that outcome pass@k advantages of base models are inflated by lucky guessing on simple final answers.
- **URL**: `https://arxiv.org/abs/2506.14245`
- **Verdict**: SUPPORTED
- **Fetched Excerpt**: `evaluates success only when both the final answer` (8 words)
- **Evidence Explanation**: The study introduces a metric requiring both intermediate reasoning and final answers to be verified, showing that base model pass gains stem from coincidental guessing.
- **Analysis**:
  - *Supported portions*: The paper demonstrates that base model pass@k scores on math reasoning are inflated by guessing final answers, introduces CoT-Pass@K requiring intermediate and final correctness, and shows RLVR models reliably maintain superior reasoning across budgets under this metric.

### Pair 7
- **Claim**: Reasoning paths generated by RLVR models remain largely within the sampling distribution of the base model under coverage analysis, whereas knowledge distillation from stronger reasoning models like DeepSeek-R1 genuinely introduces novel reasoning patterns.
- **URL**: `https://arxiv.org/abs/2504.13837`
- **Verdict**: SUPPORTED
- **Fetched Excerpt**: `distillation can introduce new reasoning patterns from the teacher` (9 words)
- **Evidence Explanation**: The authors show that RLVR reasoning trajectories stay within the base model distribution while knowledge distillation from teacher models introduces novel reasoning paths.
- **Analysis**:
  - *Supported portions*: Coverage and perplexity analysis confirms that reasoning traces produced by RLVR models already reside in the base model sampling distribution, whereas knowledge distillation from a teacher model genuinely expands reasoning capacity by introducing novel patterns.

---

## Post-Audit Resolution and Draft Reconciliations

Following the checker audit, all partial claims in `/tmp/work/report/report.md` were adjusted to remove or qualify unsupported portions:
1. **Pair 1 (`https://arxiv.org/abs/1707.06347`)**:
   - The claim was qualified to state that PPO optimizes a clipped surrogate policy gradient objective, with actor-critic implementations utilizing a learned state-value baseline $V(s)$ for advantage estimation.
2. **Pair 4 (`https://huggingface.co/papers/2312.08935`)**:
   - The unsupported portions regarding Monte Carlo rollouts and scoped comparative benefits were removed from the Math-Shepherd claim. The citation now strictly supports automated step-level process supervision without manual human annotations, while process reward limitations and prefix mechanisms are attributed to respective comparative studies.
3. **Execution**:
   - `normalize_sources.py`, `finalize_citations.py`, and `check_citations.py` were re-run sequentially, and all 16 citations resolve with validator status OK.
