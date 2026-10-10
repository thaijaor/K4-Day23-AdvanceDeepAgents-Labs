# Citation Audit Report

This report documents the verification audit for 6 refined claim/URL pairs cited in the research report. Each source URL was fetched directly and independently verified against the specific claim assertions using `web_fetch`.

## Citation Index Mapping and Mismatch Analysis

The numbering of the claims in the audit request differs from the numeric citation indices used in the report bibliography (`/tmp/work/report/report.md`) and `/tmp/work/research/sources.json`. The matching by URL, title, and citation index is detailed below:

- **Claim 1** corresponds to Report Citation **[2]** (`n=2` in `sources.json`):
  - **Title**: LLM-QAT: Data-Free Quantization Aware Training for Large Language Models
  - **URL**: `https://huggingface.co/papers/2305.17888`
  - **Index Mismatch**: Claim 1 maps to Citation [2].

- **Claim 2** corresponds to Report Citation **[4]** (`n=4` in `sources.json`):
  - **Title**: Structured Pruning Learns Compact and Accurate Models
  - **URL**: `https://huggingface.co/papers/2204.00408`
  - **Index Mismatch**: Claim 2 maps to Citation [4].

- **Claim 3** corresponds to Report Citation **[5]** (`n=5` in `sources.json`):
  - **Title**: What to Keep, What to Forget: A Rate–Distortion View of Memory Compaction in LLMs and Agents
  - **URL**: `https://arxiv.org/abs/2607.08032`
  - **Index Mismatch**: Claim 3 maps to Citation [5].

- **Claim 4** corresponds to Report Citation **[6]** (`n=6` in `sources.json`):
  - **Title**: SLM-Arch: Trade-off Analysis and Optimized Hardware Design for Small Language Models | ACM Transactions on Design Automation of Electronic Systems
  - **URL**: `https://dl.acm.org/doi/10.1145/3830468`
  - **Index Mismatch**: Claim 4 maps to Citation [6].

- **Claim 5** corresponds to Report Citation **[1]** (`n=1` in `sources.json`):
  - **Title**: Phi-3 Technical Report: A Highly Capable Language Model Locally on Your Phone
  - **URL**: `https://arxiv.org/abs/2404.14219`
  - **Index Mismatch**: Claim 5 maps to Citation [1].

- **Claim 6** corresponds to Report Citation **[9]** (`n=9` in `sources.json`):
  - **Title**: Small Language Models: Survey, Measurements, and Insights
  - **URL**: `https://arxiv.org/abs/2409.15790`
  - **Index Mismatch**: Claim 6 maps to Citation [9].

---

## Audit Verification Table

| Claim | URL | Verdict | Evidence | Excerpt |
| :--- | :--- | :--- | :--- | :--- |
| LLM-QAT evaluates compressed LLaMA variants down to 4-bit weights and KV caches (such as W4A8KV4) using data-free generative self-play distillation, demonstrates quantizing weights and KV caches down to 4 bits and activations down to 6-bit precision, but does not establish sub-4-bit weight or KV compression. | https://huggingface.co/papers/2305.17888 | SUPPORTED | The publication validates quantizing LLaMA weights and key-value caches down to four bits via data-free distillation and reaching six-bit activations, without evaluating sub-four-bit compression regimes. | weights and KV cache quantized down to 4-bits |
| CoFi's empirical findings represent task-specific structured pruning and distillation evaluations conducted on GLUE and SQuAD benchmarks, rather than demonstrating generic, task-agnostic LLM speedups. | https://huggingface.co/papers/2204.00408 | SUPPORTED | The source demonstrates that CoFi applies task-specific structured pruning and layerwise distillation specifically benchmarked on GLUE and SQuAD datasets rather than presenting task-agnostic model acceleration. | task-specific structured pruning method called CoFi |
| The rate-distortion view of memory compaction derives a layer-agnostic mathematical lower bound on task error when memory falls below task information requirements, modeling theoretical lower bounds under specific mathematical conditions rather than establishing universal operational performance cliffs across arbitrary deployments. | https://arxiv.org/abs/2607.08032 | SUPPORTED | The work introduces a rate-distortion framework and proves a layer-agnostic mathematical lower bound establishing inevitable task error when memory drops below task information requirements under formal mathematical conditions. | derive a layer-agnostic lower bound |
| SLM-Arch analyzes accelerator design for small language models, showing that processing element (PE) array sizing couples to dataflows (~240x240 for IS/OS vs >=300x300 for WS) and requires at least 30 GB/s DRAM bandwidth under relaxed area constraints to avoid processing stalls. | https://dl.acm.org/doi/10.1145/3830468 | SUPPORTED | The study establishes that optimal processing element arrays measure approximately 240 by 240 for input-stationary and output-stationary dataflows versus at least 300 by 300 for weight-stationary designs, requiring at least thirty gigabytes per second of DRAM bandwidth under relaxed area limits to sustain utilization. | at least 30 GB/s of bandwidth is needed |
| The Phi-3 model family demonstrates that training compact models (such as Phi-3 Mini at 3.8B parameters) on heavily filtered educational web data and synthetic reasoning exercises allows compact models to rival larger architectures on targeted academic and logic benchmarks. | https://arxiv.org/abs/2404.14219 | SUPPORTED | The technical report confirms that the 3.8 billion parameter Phi-3 Mini model was trained on heavily filtered web and synthetic data to rival much larger models across academic benchmarks and reasoning evaluations. | heavily filtered publicly available web data and synthetic data |
| A comprehensive survey reviewing dozens of open decoder-only SLMs (100M-5B parameters) analyzes architectures, datasets, and training algorithms, profiling on-device latency and memory footprints, with no medical prompt consistency or atomic instruction gap statistics established. | https://arxiv.org/abs/2409.15790 | SUPPORTED | The survey investigates 70 open decoder-only models ranging from 100M to 5B parameters across architectures, datasets, and training algorithms while profiling latency and memory usage, without establishing medical prompt consistency or atomic instruction gap metrics. | benchmark their inference latency and memory footprints |

---

## Verdict Summary

- **SUPPORTED**: 6
- **PARTIAL**: 0
- **UNSUPPORTED**: 0
- **UNVERIFIABLE**: 0
- **Total Claims Audited**: 6
