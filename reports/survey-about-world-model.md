# Survey: World Models in Reinforcement Learning

## TL;DR
* Model-based reinforcement learning has evolved from online planning in latent dynamics like PlaNet [1] to policy learning in imagined rollouts like Dreamer [2][3][4].
* Visual reconstruction grounds latent states, with ablations showing severe degradation across benchmarks when reconstruction gradients are disabled [3][4].
* Pixel diffusion models like DIAMOND preserve fine visual details by avoiding discrete bottlenecks, but incur high rollout computational cost [5][6].
* In matched Atari experiments, rollout drift scales with uncontrolled scene motion entropy rather than model family alone [7].
* Joint-Embedding Predictive Architectures bypass pixel decoding, empirically addressing the train-plan gap without formal causal recovery guarantees [8][9].

## Background
World models serve as internal simulators that allow reinforcement learning agents to plan and learn behaviors without continuous real-world interaction. The Deep Planning Network (PlaNet) [1] introduced the Recurrent State-Space Model (RSSM), integrating a deterministic recurrent path for temporal context with a stochastic state path for transition uncertainty. PlaNet performs online planning by applying the Cross-Entropy Method (CEM) over latent trajectories at decision time, without training a policy or value network [1].

Subsequent research shifted from online planning to policy learning inside imagined rollouts. Dreamer [2] unified RSSM transitions with actor-critic learning. By rolling out imagined futures within learned dynamics, Dreamer trains parametric action and value networks by backpropagating analytic gradients directly through differentiable transition dynamics [2], eliminating online search latency. Latent dynamics also extend to physical embodiments: DayDreamer [10] demonstrates that latent world models can learn control behaviors directly on physical robots without simulators, executing asynchronous world model learning alongside continuous physical interaction [10].

## Foundations of Latent Dynamics and Behavior Learning
DreamerV1 [2] formulated latent dynamics with continuous Gaussian distributions, regularizing posteriors toward transition priors via a Kullback-Leibler (KL) divergence penalty alongside observation reconstruction and reward prediction.

DreamerV2 [3] advanced this foundation by replacing continuous Gaussians with discrete categorical latents optimized via straight-through gradient estimators, capturing distinct modal regimes and non-smooth transitions [3]. To stabilize latent transitions, DreamerV2 introduced KL balancing, regularizing the transition predictor toward learned representations [3]. However, KL balancing acts as an empirical training regularizer rather than providing a mathematical guarantee against posterior collapse [3]. DreamerV2 ablations further showed that observation reconstruction is essential, confirming that latent grounding depends heavily on pixel supervision [3].

DreamerV3 [4] extended this approach into a domain-agnostic generalist across diverse benchmarks. Rather than altering core losses per environment, DreamerV3 maintains robust learning using normalization, balancing, and transformations with fixed settings in evaluated domains [4]. Under this unified configuration, DreamerV3 achieves monotonic performance gains as model capacity scales, while preserving observation reconstruction as its primary representation signal [4].

## Pixel-Space Generative Diffusion vs. Compressed Latent Dynamics
A prominent alternative to latent-space RSSMs is generative modeling directly in observation space. DIAMOND (DIffusion As a Model Of eNvironment Dreams) [5][6] implements an autoregressive, pixel-space conditional diffusion world model. By operating directly in raw pixel space, DIAMOND bypasses representational bottlenecks in discrete tokenizers or compact latents, preserving fine-grained visual details—such as small moving projectiles and interface indicators—that compressed latent models frequently blur or discard [5][6].

To maintain stability over multi-step rollouts, DIAMOND adopts an elucidated diffusion formulation to mitigate compounding drift and out-of-distribution noise during sequential simulation [5][6]. This continuous formulation allows stable multi-step imagination rollouts with very few denoising steps per environment transition [5][6].

The key trade-off centers on rollout efficiency. Pixel diffusion requires iterative reverse-diffusion passes through image-resolution networks for every transition, incurring substantial computational training cost and lower generation speeds [5][6]. Conversely, latent models like Dreamer evaluate transitions through compact vector operations in low-dimensional space, enabling high-throughput imagination rollouts for efficient policy optimization [4].

## Rollout Drift Dynamics and Error Modes in Matched Atari Environments
Compounding temporal error during multi-step imagination presents a fundamental challenge. The `dream-drift` benchmark [7] evaluated these dynamics through a matched empirical comparison across pixel diffusion (DIAMOND), discrete token transformers (IRIS), and recurrent latent dynamics (DreamerV3) under identical initial states and deterministic action sequences.

Strictly within this repository's matched Atari experiment, compounding rollout drift was found to scale primarily with scene motion complexity outside agent control rather than architectural paradigm alone [7]. In environments with static backgrounds and predictable dynamics, all evaluated models maintained stable multi-step rollouts, whereas the presence of multiple independently moving elements accelerated trajectory divergence across all model families [7].

The matched experiment also demonstrated that architectures incur distinct representation taxes: discrete tokenizers suffer from an upfront reconstruction error floor prior to dynamic rollout prediction, and recurrent latent decoders maintain a baseline reconstruction floor, whereas pixel diffusion operates directly in visual space without upfront tokenization penalties [7].

Despite architectural differences, all evaluated families exhibited shared qualitative error modes in the matched setup [7]:
1. Confident hallucination: Models show higher agreement among their own stochastic dream rollouts than with ground-truth reality, making rollout variance an uninformative measure of epistemic uncertainty [7].
2. Entity fading: Independent entities not governed by agent actions frequently lose permanence and fade over extended imagination horizons [7].
3. Confident healing: When exposed to out-of-distribution states such as expert-modified environments, models systematically erase novel alterations and regenerate familiar training configurations [7].
4. Sampling limits: Increasing iterative sampling steps during diffusion rollouts yields diminishing returns, inflating runtime without extending the reliable dream horizon [7].

## Joint-Embedding Predictive Architectures for Planning and Action Coupling
To eliminate the computational cost and representational distractions of pixel decoding, Joint-Embedding Predictive Architectures (JEPAs) learn dynamics by predicting representations directly in target embedding spaces [8][9].

Standard JEPAs historically encountered the train-plan gap: one-step predictive objectives do not naturally produce an aligned metric for evaluating multi-step candidate trajectories in Model Predictive Control (MPC) [8]. Temporal-Distance JEPA (TD-JEPA) [8] empirically addresses this train-plan gap by mining an asymmetric directed temporal progress cost alongside a multi-step rollout consistency objective from offline trajectories. TD-JEPA demonstrates task-dependent deployment roles: in topological reachability domains, the learned temporal distance directly serves as the planning cost, whereas in contact-rich manipulation tasks, temporal pre-training shapes latent geometry so that planning with standard Euclidean distance succeeds [8]. Importantly, TD-JEPA operates as an empirical predictive sequence approximator and does not guarantee the train-plan gap is resolved or identify formal causal states [8].

Bridging predictive dynamics and policy execution, JEPA-WAM [9] introduces a joint-embedding world action model for continuous manipulation. JEPA-WAM couples latent transition prediction and continuous action generation through a single shared predictor backbone during training, using patch-level cosine targets from frozen visual representations and conditional flow matching for action generation [9]. At deployment, JEPA-WAM removes the auxiliary transition prediction branch entirely, retaining only the action expert [9]. By sharing representation capacity during training and eliminating auxiliary transition prediction and pixel decoding at test time, JEPA-WAM enables efficient closed-loop control [9].

## Trends and open problems
The synthesis of latent RSSMs, pixel-space diffusion models, and Joint-Embedding Predictive Architectures reveals foundational directions and open problems:

1. Generative Rendering vs. Latent Throughput: Pixel diffusion models [5][6] preserve fine visual details, but iterative generation contrasts with the high-throughput rollouts of latent dynamics [4]. Developing generative models capable of real-time simulation without visual degradation remains an open problem.
2. Task-Relevant Representation vs. Reconstruction Burden: Reconstruction forces world models to commit capacity to visually salient yet control-irrelevant elements [3][4]. While non-reconstructive JEPAs avoid pixel decoding, they require task-dependent metric selection [8], underscoring the need for objectives that automatically isolate task-critical state factors.
3. Causal Grounding and Distribution Shifts: Modern world models act as statistical sequence predictors rather than true causal mechanisms [8]. Under distribution shifts, models default to confident healing or entity fading [7]. Establishing formal causal identifiability in high-dimensional dynamics remains an unsolved theoretical challenge.
4. Uncertainty Calibration in Latent Rollouts: Rollout dreams consistently exhibit confident hallucination, where internal consistency masks divergence from reality [7]. Formulating calibrated uncertainty estimators distinguishing environment stochasticity from model inadequacy is essential for safe exploration.
5. Embodied Deployment and Physical Transfer: While latent world models enable physical robot learning [10], deploying non-reconstructive, action-coupled world models [9] directly on complex physical hardware under strict latency budgets remains an active frontier.

## References
[1] Learning Latent Dynamics for Planning from Pixels. arxiv. https://arxiv.org/abs/1811.04551 (2018-11-12)
[2] Dream to Control: Learning Behaviors by Latent Imagination. web. https://arxiv.org/abs/1912.01603 (n.d.)
[3] Mastering Atari with Discrete World Models. arxiv. https://arxiv.org/abs/2010.02193 (2020-10-05)
[4] Mastering Diverse Domains through World Models. arxiv. https://arxiv.org/abs/2301.04104 (2023-01-10)
[5] Diffusion for World Modeling:Visual Details Matter in Atari. web. https://arxiv.org/abs/2405.12399 (n.d.)
[6] DIAMOND. web. https://diamond-wm.github.io/ (n.d.)
[7] iwillsolvehardestproblem/dream-drift. web. https://github.com/iwillsolvehardestproblem/dream-drift (n.d.)
[8] Temporal-Distance JEPA: Plan-Aware Representation Learning for Latent World Model Predictive Control. hf-search. https://huggingface.co/papers/2607.25337 (2026-07-28)
[9] JEPA-WAM: Learning Vision-Language-Action Policies with Joint-Embedding World Modeling. hf-search. https://huggingface.co/papers/2608.09381 (2026-08-10)
[10] DayDreamer: World Models for Physical Robot Learning. arxiv. https://arxiv.org/abs/2206.14176 (2022-06-28)
