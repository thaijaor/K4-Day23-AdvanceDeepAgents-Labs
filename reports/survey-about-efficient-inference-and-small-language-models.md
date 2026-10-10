# Survey: Efficient Inference and Small Language Models

## TL;DR
- Small Language Models (SLMs) achieve competitive performance via curated educational and synthetic pretraining data, allowing compact models to rival larger baselines on evaluated benchmarks [1].
- Low-bit quantization and structured pruning reduce memory footprints, though maintaining accuracy requires specialized training like data-free distillation, while speedups depend on task alignment and kernel support [2] [3] [4].
- Context compaction can be modeled under rate-distortion theory, proving theoretical lower bounds on task fidelity when compression budgets fall below task information entropy rather than universal operational collapse [5].
- Edge serving efficiency is governed by interactions among accelerator dataflows, memory hierarchy bandwidth, precision, and batching, where quantization alleviates memory traffic bottlenecks rather than universally suffering diminishing returns [6] [7] [8].

## Background
Deploying Large Language Models (LLMs) on resource-constrained platforms exposes severe bottlenecks. Serving tens or hundreds of billions of parameters demands memory capacity and bandwidth exceeding edge thermal and power envelopes. These constraints motivate Small Language Models (SLMs)—decoder-only transformers spanning 100M to 5B parameters—and efficient serving techniques [9].

While conventional scaling laws linked reasoning capability directly to parameter scale, curated educational text and synthetic reasoning corpora enable compact models to rival larger baselines on structured analytical tasks [1]. Local deployment, however, introduces multifaceted trade-offs across accuracy, latency, memory footprint, energy consumption, and environmental sustainability [8]. Effective inference requires distinguishing static weight compression from dynamic context compaction and hardware serving, examined below across key architectural themes.

## Parameter Quantization and Quantization-Aware Optimization
Quantization compresses representations by mapping continuous floating-point weights and activations to discrete, lower-precision formats. Post-Training Quantization (PTQ) compresses pretrained weights without retraining, but degrades substantially in low-bit regimes. In contrast, Quantization-Aware Training (QAT) simulates quantization noise during training, enabling dynamic adaptation to discrete constraints.

Autoregressive models present high-magnitude activation outliers. The LLM-QAT framework addresses this using data-free distillation [2]. Rather than requiring original corpora, LLM-QAT uses generative self-play, distilling a student model on synthetic generations produced by the teacher via top-1 argmax and stochastic token sampling [2].

LLM-QAT evaluates compressed LLaMA models down to 4-bit weights and KV caches (such as W4A8KV4) [2]. Preserving outlier distributions is critical for generative stability; symmetric MinMax quantization and per-token KV quantization retain outlier dynamics, whereas clipping causes catastrophic perplexity degradation [2]. Crucially, LLM-QAT demonstrates quantizing weights and KV caches down to 4 bits and activations down to 6-bit precision, but does not establish sub-4-bit weight or KV compression [2].

Joint compression extends efficiency further. QPruner integrates structured pruning with layer-wise mixed-precision quantization [3]. It evaluates layer importance via mutual information between intermediate layer representations and predictions, using Bayesian optimization to determine non-uniform bit allocations under memory constraints, followed by parameter-efficient recovery [3]. Low-bit quantization reduces memory traffic by shrinking byte volume, directly mitigating memory bus saturation during generation.

## Structural Pruning Across Granularities
While quantization lowers numeric precision, model pruning removes redundant parameters entirely. Unstructured pruning eliminates individual weights, yielding high theoretical sparsity; however, irregular sparse matrices fail to deliver latency speedups on dense matrix hardware without specialized execution kernels.

Structured pruning removes contiguous parameter blocks—such as attention heads, intermediate channels, or complete layers—preserving regular tensor geometries. The CoFi (Coarse- and Fine-grained Pruning) framework unifies structured pruning across granularities [4]. CoFi applies multi-granularity masks to simultaneously prune entire layers, attention heads, and hidden dimensions, combined with layerwise distillation from an unpruned teacher model [4].

Importantly, CoFi's empirical findings represent task-specific structured pruning and distillation evaluations conducted on GLUE and SQuAD benchmarks, rather than demonstrating generic, task-agnostic LLM speedups [4]. Translating structured sparsity into measured latency gains remains highly contingent on dedicated kernel support for non-standard pruned matrix shapes, batch sizes, and target task specialization [4]. Consequently, structured pruning requires careful co-design between model architectural choices and underlying execution hardware.

## Context Compaction and Information-Theoretic Bounds
Orthogonal to parameter compression, autoregressive decoding suffers from linear growth of the key-value (KV) cache. In long contexts, KV cache footprints frequently surpass model weights, exhausting device memory.

The rate-distortion view of memory compaction formalizes KV cache eviction, prompt compression, and recurrent state architectures under a unified theoretical framework [5]. Memory compaction is defined as minimizing mutual information between context history and compressed state representations under a memory budget, while maximizing downstream query response accuracy [5].

This theoretical framework proves a layer-agnostic mathematical lower bound demonstrating that when the compressed memory rate drops below a task's conditioned information requirement, errors become theoretically inevitable across all architectures [5]. Crucially, these formulations model information-theoretic lower bounds under specific mathematical conditions rather than establishing universal operational performance cliffs across arbitrary deployments.

The framework exposes two structural failure modes in context compaction [5]. First, query-agnostic eviction strategies that discard KV tokens before the query is revealed pay an inherent capacity penalty proportional to query entropy [5]. Second, when context compaction is applied repeatedly and irreversibly across multi-step execution traces (such as recursive summarization in autonomous agents), downstream reconstruction errors compound super-linearly [5]. Thus, context compression is governed by strict trade-offs between memory retention budgets and recall fidelity.

## Hardware Serving Architectures and Edge Performance Constraints
Deploying SLMs onto edge hardware requires managing compute and memory subsystems. In on-device settings, inference often operates at batch size 1, where latency is governed by memory bandwidth as weights and KV states transfer to compute units [7].

However, memory boundedness is not an absolute constant of edge execution. It varies dynamically based on hardware memory hierarchies, precision, on-chip cache residency, batch size, and network topology. On resource-constrained edge platforms, low-bit parameter quantization reduces the total byte volume transferred during decoding steps, alleviating memory bus saturation and providing practical latency benefits rather than universally suffering diminishing returns [7].

To resolve microarchitectural bottlenecks, analytical frameworks like SLM-Arch investigate dedicated accelerator designs for small models [6]. SLM-Arch demonstrates that processing element (PE) array sizing must couple to dataflows [6]. Input-Stationary and Output-Stationary dataflows achieve optimal utilization with balanced ~240x240 PE arrays, while Weight-Stationary dataflows require larger arrays (>=300x300) with lower memory bandwidth demands [6]. Under relaxed area constraints, sustaining full compute utilization requires at least 30 GB/s DRAM bandwidth to prevent processing stalls [6].

Physical edge characterization across embedded compute modules and single-board platforms confirms that bottlenecks shift dynamically between storage transfers, DRAM bandwidth saturation, and on-chip SRAM capacity depending on device tier and parameter scale [7].

## Curated Pretraining and Evaluated Model Capacities
Strategic data curation represents a primary driver of SLM efficiency. The Phi-3 family demonstrates that training compact models (such as Phi-3 Mini at 3.8B parameters) on heavily filtered educational web text and synthetic reasoning exercises allows compact models to rival larger architectures on targeted academic and logic benchmarks [1].

Nevertheless, deploying compact architectures involves inherent capacity trade-offs compared to massive models. Balancing parameter scale and data curation highlights the role of architectural specialization and external retrieval augmentation rather than unconstrained parametric memorization.

Surveys across open decoder-only SLMs show that pretraining curricula, architectural choices (grouped-query attention, rotary embeddings), and fine-tuning dictate operational efficiency, memory footprints, and throughput [9]. Validating performance requires rigorous isolation from benchmark artifacts and prompt templates [9].

## Trends and open problems
Evaluation methodologies are shifting from isolated academic accuracy toward holistic multi-metric audits. Frameworks such as SLM-Bench evaluate models across task correctness, serving latency, operational energy consumption, and carbon emissions [8]. These audits establish that parameter volume alone does not determine energy efficiency; architectural overhead, parallelization, and pretraining data quality exert dominant influences [8].

Furthermore, empirical mapping of the SLM efficiency landscape reveals sharp non-linearities: marginal accuracy improvements frequently incur disproportionate latency and energy costs [10]. Real-world deployments must therefore balance parameter budgets and precision formats against operational task constraints rather than maximizing raw benchmark metrics [10].

Standardizing benchmarking across heterogeneous edge runtimes (such as llama.cpp, vLLM, and mobile inference engines) remains an unresolved challenge, as runtime execution disparities often eclipse architectural distinctions [7]. Finally, data contamination and alignment sensitivity at small parameter scales highlight the ongoing need for co-designed neural architectures and robust instruction-tuning protocols [9].

## References
[1] [2404.14219] Phi-3 Technical Report: A Highly Capable Language Model Locally on Your Phone. web. https://arxiv.org/abs/2404.14219 (2024-04-22)
[2] LLM-QAT: Data-Free Quantization Aware Training for Large Language Models. hf-search. https://huggingface.co/papers/2305.17888 (2023-05-29)
[3] QPruner: Probabilistic Decision Quantization for Structured Pruning in Large Language Models. hf-search. https://huggingface.co/papers/2412.11629 (2024-12-16)
[4] Structured Pruning Learns Compact and Accurate Models. hf-search. https://huggingface.co/papers/2204.00408 (2022-04-01)
[5] What to Keep, What to Forget: A Rate--Distortion View of Memory Compaction in LLMs and Agents. arxiv. https://arxiv.org/abs/2607.08032 (2026-07-09)
[6] SLM-Arch: Trade-off Analysis and Optimized Hardware Design for Small Language Models | ACM Transactions on Design Automation of Electronic Systems. web. https://dl.acm.org/doi/10.1145/3830468 (2025-12-08)
[7] GRP-134 Characterizing and Understanding the Performance of Small Language Models on Edge Devices. web. https://digitalcommons.kennesaw.edu/cgi/viewcontent.cgi?article=1600&context=cday (n.d.)
[8] SLM-Bench: A Comprehensive Benchmark of Small Language Models on Environmental Impacts. web. https://aclanthology.org/anthology-files/anthology-files/pdf/findings/2025.findings-emnlp.1165.pdf (n.d.)
[9] Small Language Models:Survey, Measurements, and Insights. web. https://arxiv.org/abs/2409.15790 (2025-02-26)
[10] Mapping the Efficiency Landscape of Small Language Models. web. https://www.ijcai.org/proceedings/2026/0627.pdf (n.d.)
