# Citation Audit Report

This report evaluates six claim-source pairs against web evidence retrieved directly from their respective URLs.

## Audit Table

| Claim | URL | Verdict | Evidence | Excerpt |
|---|---|---|---|---|
| During inference, key-value (KV) caching avoids recomputing past key and value projections across previous frames; crucially, this caching strategy does not bypass the causal attention operation itself, which must still be evaluated over cached states. | https://arxiv.org/abs/2412.07772 | PARTIAL | The retrieved text confirms that key-value caching enables efficient autoregressive inference, but it does not discuss avoiding key and value recomputations or evaluating causal attention over cached states. | efficient autoregressive inference through key-value (KV) caching |
| An asymmetric distillation objective supervises the causal student via a bidirectional teacher endowed with privileged future context, mitigating error accumulation. However, this distillation offers no universal lossless guarantees: it incurs typical trade-offs in output diversity and faces degradation when extended over long autoregressive sequences. | https://arxiv.org/abs/2412.07772 | PARTIAL | While the fetched text confirms that asymmetric distillation with a bidirectional teacher mitigates error accumulation, it does not mention trade-offs in output diversity, lack of lossless guarantees, or sequence degradation. | supervises a causal student model with a bidirectional teacher |
| In reported benchmark evaluations, unified joint architectures show improved audio-visual alignment over cascaded baselines, though gains remain scoped to evaluated datasets and acoustic settings. | https://huggingface.co/papers/2503.23377 | PARTIAL | The retrieved source confirms that the joint model outperforms existing methods in synchronization, but it does not state that gains remain scoped to specific datasets or acoustic settings. | ensuring both high-quality generation and precise synchronization |
| FVD captures aggregate feature distributions but fails to verify text prompt alignment or audio-visual synchronization, and investigations show FVD is disproportionately sensitive to per-frame appearance over motion realism: in study settings, large temporal corruptions barely impacted scores, whereas motionless frames could artificially improve them due to static background biases in Kinetics-400 I3D representations. | https://arxiv.org/abs/2404.12391 | PARTIAL | The retrieved text demonstrates that FVD favors individual frame appearance over temporal realism and shows that motionless videos can lower scores, but it never mentions text prompt alignment or audio-visual synchronization. | FVD increases only slightly with large temporal corruption |
| Moving from passive clip synthesis to goal-directed procedural simulation—as demonstrated by WorldGuide—requires closed-loop planning and visual execution, where compounding roll-out errors and high-dimensional memory maintenance remain critical open problems. | https://huggingface.co/papers/2610.12459 | PARTIAL | The source demonstrates closed-loop planning and execution in visual world space with hierarchical memory, but it does not frame compounding roll-out errors and memory maintenance as unresolved critical open problems. | procedural video generation as closed-loop task execution |
| CogVideo froze the spatial parameters of a pretrained image model and interleaved trainable temporal attention channels ('attention-plus') within each transformer block to capture motion while preserving static visual representations, generating sparse keyframes before recursively interpolating intermediate frames. | https://arxiv.org/abs/2205.15868 | PARTIAL | The retrieved text confirms that CogVideo inherits from a pretrained text-to-image model and generates keyframes before recursively interpolating intermediate frames, but it lacks the details regarding frozen spatial parameters and attention-plus channels. | generates key frames according to the text |

## Verdict Summary

- Total Audited Claims: 6
- SUPPORTED: 0
- PARTIAL: 6
- UNSUPPORTED: 0
- UNVERIFIABLE: 0

## Citation Index Mismatch Analysis

In the report and project bibliography (`sources.json` and `report.md`), the source URLs are indexed differently from the audit claim numbering:

1. **Claim 1 & Claim 2 (`https://arxiv.org/abs/2412.07772`)**:
   - Matches Report Citation **[8]** ("From Slow Bidirectional to Fast Autoregressive Video Diffusion Models").
   - Audit claim indices 1 and 2 both map to reference index [8].

2. **Claim 3 (`https://huggingface.co/papers/2503.23377`)**:
   - Matches Report Citation **[5]** ("JavisDiT: Joint Audio-Video Diffusion Transformer with Hierarchical Spatio-Temporal Prior Synchronization").
   - Audit claim index 3 maps to reference index [5]. In the report text, this statement also synthesized findings cited under [7] ("VABench: A Comprehensive Benchmark for Audio-Video Generation"), explaining why dataset-scoping limitations were absent from the JavisDiT paper page itself.

3. **Claim 4 (`https://arxiv.org/abs/2404.12391`)**:
   - Matches Report Citation **[10]** ("On the Content Bias in Fréchet Video Distance").
   - Audit claim index 4 maps to reference index [10]. In the report text, the preamble regarding text prompt alignment and audio-visual synchronization drew upon citations [9] and [11] rather than [10] alone.

4. **Claim 5 (`https://huggingface.co/papers/2610.12459`)**:
   - Matches Report Citation **[14]** ("WorldGuide: Goal-Directed Video World Model for Procedural Task Execution").
   - Audit claim index 5 maps to reference index [14]. In the report text, this citation was combined with open challenges synthesis from the survey's discussion section.

5. **Claim 6 (`https://arxiv.org/abs/2205.15868`)**:
   - Matches Report Citation **[2]** ("CogVideo: Large-scale Pretraining for Text-to-Video Generation via Transformers").
   - Audit claim index 6 maps to reference index [2].
