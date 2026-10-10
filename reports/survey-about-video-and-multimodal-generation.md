# Advances in Video and Multimodal Generative Modeling: A Historical and Architectural Survey

## TL;DR
* Text-to-video synthesis transitioned from early hybrid architectures decoupling static background layout from dynamic filters [1] and frozen spatial transformers with temporal attention [2] to continuous-time latent and cascaded pixel diffusion architectures [3][4].
* Joint audio-video systems address cascaded desynchronization using unified diffusion transformers with hierarchical spatiotemporal priors [5] and asymmetric cross-modal interactions [6], demonstrating improved synchronization within reported benchmark evaluations [7].
* Streaming inference is achieved by adapting bidirectional diffusion models into causal autoregressive architectures, where key-value caching avoids recomputing past key and value projections while continuing to evaluate causal attention over cached states [8].
* Distilling causal students from bidirectional teachers with privileged future context accelerates sampling without universal lossless guarantees, exhibiting characteristic trade-offs in output diversity [8].
* Video evaluation is moving from feature-distribution distances subject to study-scoped content bias [9][10] toward multidimensional diagnostic benchmarks [11], zero-shot multimodal judges [12][13], and goal-directed procedural world models [14].

## Background
Generative modeling of visual media has progressed substantially over the past decade. Early text-to-video baselines struggled to map text prompts directly to high-dimensional video tensors, yielding low-resolution clips with restricted duration [1]. To manage spatiotemporal complexity, initial approaches explored hybrid networks that decoupled static background appearance from motion trajectories [1]. With large-scale pretraining, researchers adapted frozen text-to-image representations within autoregressive sequence models to inherit broad open-domain visual knowledge [2].

Diffusion models subsequently supplanted discrete autoregression, bifurcating into cascaded pixel-space pipelines that iteratively upscale frame resolution and framerate [4], and latent diffusion models (LDMs) that denoise within compressed latent spaces [3][15]. The field has broadened toward unified video generation and understanding agents [16], joint audio-video diffusion transformers [17][5], and goal-directed procedural world models performing closed-loop action-effect simulation [14].

## Foundational Paradigms: From Hybrid VAE/GANs to Autoregressive Transformers
Early text-to-video synthesis decoupled static spatial layout from temporal motion transitions. A foundational baseline combined a Variational Autoencoder (VAE) and Generative Adversarial Network (GAN) [1]. A conditional VAE synthesized background layouts and color distributions, while a text-to-filter mechanism mapped prompts into dynamic convolutional filters convolved with background features for a GAN generator [1]. Although computationally efficient, this hybrid design suffered from adversarial instability, limited mode coverage, and poor generalization across open-domain text prompts [1].

To expand domain coverage, CogVideo demonstrated the power of adapting pretrained text-to-image transformers for video synthesis [2]. CogVideo inherited representations from a pretrained image model and interleaved trainable temporal attention channels within transformer blocks to capture motion while preserving static visual representations [2]. Generation proceeded hierarchically, producing low-frame-rate keyframes before recursively interpolating intermediate frames [2]. While successfully transferring image priors, discrete autoregressive modeling faced high inference latency and memory costs from quadratic self-attention over long frame sequences [2].

## Diffusion Frontiers: Cascaded Pixel-Space vs. Compressed Latent-Space Architectures
Continuous-time diffusion models avoided discrete token bottlenecks, bifurcating into cascaded pixel-space and compressed latent-space systems. In pixel space, Imagen Video cascaded diffusion models guided by a frozen text encoder to upscale base video clips through interleaved spatial and temporal super-resolution stages [4]. Training utilized v-prediction parameterization and progressive distillation, yet operating directly on RGB pixels incurred extreme compute and memory costs [4].

Conversely, Latent Video Diffusion Models (Video LDMs) run diffusion within a compressed latent space [3]. Video LDM adapts pretrained image diffusion backbones by freezing spatial layers and inserting trainable temporal attention and 3D convolutions [3]. To eliminate temporal flickering, the autoencoder decoder is fine-tuned with 3D convolutions and a temporal discriminator while keeping the encoder fixed, followed by temporally aligned latent upsampling [3]. This modularity enables zero-shot temporal transfer across fine-tuned image checkpoints [3], underpinning open frameworks like VideoCrafter1 [15] and unified architectures like Uni-ViGU [16].

## Multimodal Joint Audio-Video Generation and Asymmetric Synchronization
Multimodal generative modeling has expanded toward synthesizing synchronized audio and video streams. Independent cascaded pipelines generate audio conditioned on pre-rendered video, often suffering from temporal desynchronization and acoustic mismatch [7]. AV-DiT addressed this by inserting temporal and audio adapters into a pretrained image Diffusion Transformer backbone to model visual frames and audio spectrograms jointly [17].

Recent architectures introduce explicit spatiotemporal synchronization priors. JavisDiT employs a dual-branch diffusion transformer governed by a Hierarchical Spatial-Temporal Synchronized Prior (HiST-Sypo) estimator, deriving global semantic priors and fine-grained spatiotemporal priors to align acoustic events with visual regions [5]. UniAVGen coordinates cross-modal attention via asymmetric interaction while restricting facial audio-visual attention to improve speech coherence [6]. In reported benchmark evaluations, unified joint architectures show improved audio-visual alignment over cascaded baselines [5][7], though gains remain scoped to evaluated datasets and acoustic settings [7].

## Inference Efficiency: Causal Streaming, Caching, and Distillation
Interactive applications require low-latency streaming, which bidirectional diffusion models fail to support due to future attention dependencies. CausVid adapts bidirectional models into causal autoregressive video diffusion transformers that synthesize frames sequentially [8]. During inference, key-value (KV) caching avoids recomputing past key and value projections across previous frames; crucially, this caching strategy does not bypass the causal attention operation itself, which must still be evaluated over cached states [8].

To accelerate sampling, CausVid applies distribution matching distillation (DMD) to temporal sequences [8]. An asymmetric distillation objective supervises the causal student via a bidirectional teacher endowed with privileged future context to curb error accumulation [8]. However, this distillation offers no universal lossless guarantees: it incurs typical trade-offs in output diversity and faces degradation when extended over long autoregressive sequences [8].

## The Evolution of Video Evaluation: Diagnostic Suites Beyond Content Bias
Evaluating video generative models historically relied on Fréchet Video Distance (FVD), fitting multivariate Gaussians to features from a Kinetics-400 pretrained I3D backbone [9]. However, FVD has demonstrated critical shortcomings:
* **Feature Distribution Metric:** FVD captures aggregate feature distributions but fails to verify text prompt alignment or audio-visual synchronization [10][11].
* **Content Bias:** Investigations show FVD is disproportionately sensitive to per-frame appearance over motion realism: in study settings, large temporal corruptions barely impacted scores, whereas motionless frames could artificially improve them due to static background biases in Kinetics-400 I3D representations [10].
* **Sample Sensitivity:** FVD requires large sample sets for covariance convergence and is sensitive to cropping and compression [10][18].

To address these gaps, JEDi extracts Video-JEPA features to compute Maximum Mean Discrepancy without Gaussian assumptions [18]. Concurrently, VBench decomposes video quality into disentangled spatiotemporal and prompt adherence dimensions evaluated by specialized models [11]. Multimodal large language models (MLLMs) are also deployed as zero-shot judges: Video-Bench calibrates scoring via chain-of-query dialogue [12], while UVE-Bench reveals that MLLMs excel at semantic alignment but struggle with temporal dynamics and geometry [13]. For audiovisual models, T2AV-Compass [19] and VABench [7] expose an audio realism bottleneck where models struggle to synthesize physically grounded, realistic acoustic textures matching visual fidelity [19][7].

## Trends and open problems
Advancing video and multimodal generative modeling toward interactive visual simulators highlights several persistent open challenges:
1. **Physical Causality and Commonsense:** Generative models synthesize detailed visual textures but frequently violate physical laws regarding gravity, collision boundaries, and fluid interaction [11][12].
2. **Computational Scaling and Streaming:** While causal autoregressive architectures mitigate future frame dependencies, generating continuous long-horizon high-definition videos with bounded memory and latency remains a formidable scaling challenge [8].
3. **Cross-Modal Synchronization and Acoustic Fidelity:** Maintaining fine-grained temporal synchrony and synthesizing physically grounded audio textures during complex occlusions and dynamic scenes presents an unresolved audio realism bottleneck [19][7].
4. **Holistic Multimodal Evaluation:** Current diagnostic suites lack unified, computationally efficient metrics capable of evaluating visual fidelity, cross-modal synchronization, and physical causal reasoning simultaneously without relying on resource-intensive model ensembles [13][7].
5. **Interactive Procedural World Models:** Moving from passive clip synthesis to goal-directed procedural simulation—as demonstrated by WorldGuide [14] and unified generation-understanding architectures [16]—requires closed-loop planning and visual execution, where compounding roll-out errors and high-dimensional memory maintenance remain critical open problems [14].

## References
[1] Video Generation From Text. hf-search. https://huggingface.co/papers/1710.00421 (2017-10-01)
[2] CogVideo: Large-scale Pretraining for Text-to-Video Generation via Transformers. arxiv. https://arxiv.org/abs/2205.15868 (2022-05-29)
[3] Align your Latents: High-Resolution Video Synthesis with Latent Diffusion Models. hf-search. https://huggingface.co/papers/2304.08818 (2023-04-18)
[4] Imagen Video: High Definition Video Generation with Diffusion Models. hf-search. https://huggingface.co/papers/2210.02303 (2022-10-05)
[5] JavisDiT: Joint Audio-Video Diffusion Transformer with Hierarchical Spatio-Temporal Prior Synchronization. hf-search. https://huggingface.co/papers/2503.23377 (2025-03-30)
[6] UniAVGen: Unified Audio and Video Generation with Asymmetric Cross-Modal Interactions. hf-search. https://huggingface.co/papers/2511.03334 (2025-11-05)
[7] VABench: A Comprehensive Benchmark for Audio-Video Generation. hf-search. https://huggingface.co/papers/2512.09299 (2025-12-10)
[8] From Slow Bidirectional to Fast Autoregressive Video Diffusion Models. web. https://arxiv.org/abs/2412.07772 (2025-09-23)
[9] Towards Accurate Generative Models of Video: A New Metric & Challenges. web. https://arxiv.org/abs/1812.01717 (2019-03-27)
[10] On the Content Bias in Fréchet Video Distance. web. https://arxiv.org/abs/2404.12391 (n.d.)
[11] VBench: Comprehensive Benchmark Suite for Video Generative Models. web. https://openaccess.thecvf.com/content/CVPR2024/papers/Huang_VBench_Comprehensive_Benchmark_Suite_for_Video_Generative_Models_CVPR_2024_paper.pdf (n.d.)
[12] Video-Bench: Human-Aligned Video Generation Benchmark. web. https://openaccess.thecvf.com/content/CVPR2025/html/Han_Video-Bench_Human-Aligned_Video_Generation_Benchmark_CVPR_2025_paper.html (n.d.)
[13] UVE: Are MLLMs Unified Evaluators for AI-Generated Videos?. web. https://proceedings.neurips.cc/paper_files/paper/2025/file/1874f129f231fad431dd40119e3bd6af-Paper-Datasets_and_Benchmarks_Track.pdf (n.d.)
[14] WorldGuide: Goal-Directed Video World Model for Procedural Task Execution. hf-daily. https://huggingface.co/papers/2610.12459 (2026-10-08)
[15] VideoCrafter1: Open Diffusion Models for High-Quality Video Generation. hf-search. https://huggingface.co/papers/2310.19512 (2023-10-30)
[16] Uni-ViGU: Towards Unified Video Generation and Understanding via A Diffusion-Based Video Generator. hf-search. https://huggingface.co/papers/2604.08121 (2026-04-09)
[17] AV-DiT: Efficient Audio-Visual Diffusion Transformer for Joint Audio and Video Generation. hf-search. https://huggingface.co/papers/2406.07686 (2024-06-11)
[18] Beyond FVD: Enhanced Evaluation Metrics for Video Generation Quality. web. https://arxiv.org/html/2410.05203 (n.d.)
[19] T2AV-Compass: Towards Unified Evaluation for Text-to- .... web. https://arxiv.org/abs/2512.21094 (n.d.)
