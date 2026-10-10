# Deep Research Agent — Day 23

Nguyễn Hồng Thái · `2A202602894` · GitHub: `thaijaor`

Deep Agents lead delegates parallel research to isolated subagents, combines retrieved evidence, and writes an English survey with numbered citations. Source APIs run on the host; notes, report generation and citation validation run inside an ephemeral sandbox.

## Setup (Windows PowerShell)

Requires Python 3.11+ and Docker Desktop with the Linux engine running.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Set these variables in `.env` for an OpenAI-compatible endpoint (including Gemini's compatible endpoint):

```dotenv
LAB_BASE_URL=<OpenAI-compatible endpoint>
LAB_MODEL=<tool-calling model name>
LAB_API_KEY=<your LLM key>
SANDBOX=docker
SANDBOX_IMAGE=python:3.12-slim
EXA_API_KEY=<your Exa key>
LAB_REQUESTS_PER_MINUTE=10
LAB_INPUT_TOKENS_PER_MINUTE=160000
```

The shared course variables map as follows: `OPENAI_BASE_URL` → `LAB_BASE_URL`, `OPENAI_MODEL` → `LAB_MODEL`, `OPENAI_API_KEY` → `LAB_API_KEY`. `model.py` reads the `LAB_*` variables. No Daytona key is needed with Docker. `LAB_REQUESTS_PER_MINUTE` shares pacing across lead/subagents; choose below your provider quota (0 disables pacing). `LAB_INPUT_TOKENS_PER_MINUTE` adds a shared rolling token window; the adapter also respects quota cooldowns. Exa works without a key but is quickly rate limited. `.env` is ignored by git; keys remain on the host.

Alternatively, use the provider configuration in `.env.example`, or `SANDBOX=daytona` with `DAYTONA_API_KEY`.

For Vertex AI, set `LAB_VERTEX_CREDENTIALS` to a service-account JSON path on the host, `LAB_VERTEX_PROJECT`, `LAB_VERTEX_LOCATION=global`, and `LAB_MODEL=google/<compatible Gemini model>`. Leave `LAB_API_KEY` blank. `vertex_auth.py` configures the OpenAI-compatible endpoint and supplies an OAuth callback that refreshes expired tokens automatically. Neither credentials nor access tokens are uploaded to the sandbox. See [Google's OpenAI compatibility guide](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/start/openai).

Optional `LAB_RESEARCH_MODEL` and `LAB_CHECKER_MODEL` select separate tool-calling models for the two subagent roles using the same endpoint/key. Unset them to inherit the lead model. Metadata records configured role overrides; each model's provider quota still applies.

## Run

```powershell
.\.venv\Scripts\python.exe tools.py
.\.venv\Scripts\python.exe research.py "survey about world model"
.\.venv\Scripts\python.exe run_topics.py
.\.venv\Scripts\python.exe -m unittest -v test_lab
.\.venv\Scripts\python.exe self_check.py
```

For QA corrections, run `research.py "<topic>" --feedback-file feedback.txt`; it revises an archived report when available, or starts a fresh research run otherwise. Add `--fresh` to force regeneration. Reports are never manually edited.

To revise an existing system-generated draft, add `--draft reports/<slug>.md`. This requires its `.sources.json` and `.provenance.json` discovery archive. The agent verifies claim clusters again and edits the draft inside the sandbox; original discovery labels are retained from the archive. Revision metadata records the input draft hash; call/token counts and elapsed time describe the current revision only.

Run each of the five topics in [topics.md](topics.md). Outputs in `reports/`:

- `<slug>.md`: survey (TL;DR, Background, thematic comparisons, Trends and open problems, References).
- `<slug>.sources.json`: numbered sources with discovery labels and URLs.
- `<slug>.meta.json`: topic/model, elapsed time, delegation/tool counts, lead token usage, and source families.
- `<slug>.audit.md`: citation-checker verdicts downloaded from the sandbox.
- `<slug>.provenance.json`: archived metadata from actual source discoveries, used for revisions.

Validate one report with:

```powershell
.\.venv\Scripts\python.exe check_citations.py reports/survey-about-world-model.md reports/survey-about-world-model.sources.json
```

## Implementation

`tools.py` implements arXiv, Hugging Face Daily/Search and Exa Search/Fetch with bounded retries, `Retry-After`, jitter, arXiv pacing, and secret redaction. `agents.py` defines the lead, researchers and citation checker, with model/tool limits for each. `openai_adapter.py` preserves provider tool-call metadata (including Gemini thought signatures) through the pinned LangChain adapter, using its OpenAI SDK client. `research.py` manages sandbox lifetime, uploads validation scripts, validates outputs before saving, and records actual lead message counts. `check_citations.py` verifies source IDs, URLs, body citations and one matching reference per source, excluding code and Markdown links.

`normalize_sources.py` deterministically restores labels, canonical URLs and dates from actual discoveries inside the sandbox; unresolved sources must be researched or removed by the agent. Reports and sources are downloaded unchanged. The provided finalizer and student validator run inside the sandbox before download. Lead token counts exclude subagent usage. Each run is bounded at 100 model / 200 tool calls for lead; researchers at 40 / 60 and checker at 25 / 40, with lead recursion limit 1000. When genuine source-family coverage is insufficient, the host retrieves relevant Web, HF Search or HF Daily candidates for the agent to evaluate in the sandbox. Trusted helper scripts are reuploaded before each host validation gate, preventing agent edits from bypassing checks. The final sandbox gate checks discovery provenance, requires 3-6 thematic sections, rejects bodies under 800 words, and allows at most two agent repair passes; each pass retains the same limits.

Assignment details: [GUIDE.md](GUIDE.md), [RUBRIC.md](RUBRIC.md), [REPORT_TEMPLATE.md](REPORT_TEMPLATE.md).
