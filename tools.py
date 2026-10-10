"""Host-side source tools with retries and secret redaction."""
import json
import os
import random
import re
import threading
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from urllib.parse import quote

import httpx
from dotenv import load_dotenv
from langchain_core.tools import tool

load_dotenv()
ARXIV_URL = "https://export.arxiv.org/api/query"
HF_DAILY_URL = "https://huggingface.co/api/daily_papers"
HF_SEARCH_URL = "https://huggingface.co/api/papers/search"
EXA_URL = "https://mcp.exa.ai/mcp"
_arxiv_lock = threading.Lock()
_last_arxiv = 0.0
_provenance = {}
_provenance_lock = threading.Lock()


class RetryableError(Exception):
    def __init__(self, message, retry_after=None):
        super().__init__(message)
        self.retry_after = retry_after


def with_retry(fn, *, attempts=5, base=1.0, cap=30.0):
    """Retry transient failures with capped backoff and jitter; never sleep after the last attempt."""
    if attempts < 1:
        raise ValueError("attempts must be positive")
    for attempt in range(attempts):
        try:
            return fn()
        except RetryableError as exc:
            if attempt == attempts - 1:
                raise
            delay = exc.retry_after
            if delay is None:
                delay = base * 2**attempt + random.uniform(0, base)
            time.sleep(min(cap, max(0, delay)))


def _retry_after(value):
    if not value:
        return None
    try:
        return max(0, float(value))
    except ValueError:
        try:
            return max(0, (parsedate_to_datetime(value) - datetime.now(timezone.utc)).total_seconds())
        except (ValueError, TypeError, OverflowError):
            return None


def _request(method, url, **kwargs):
    try:
        r = httpx.request(method, url, timeout=kwargs.pop("timeout", 45), follow_redirects=True, **kwargs)
    except httpx.TransportError as exc:
        raise RetryableError(type(exc).__name__) from exc
    if r.status_code in {429, 500, 502, 503, 504}:
        raise RetryableError(f"HTTP {r.status_code}", _retry_after(r.headers.get("Retry-After")))
    r.raise_for_status()
    return r


def safe_error(exc):
    message = f"{type(exc).__name__}: {exc}"
    for name, value in os.environ.items():
        if value and any(word in name for word in ("KEY", "TOKEN", "SECRET", "PASSWORD")):
            message = message.replace(value, "[REDACTED]").replace(quote(value, safe=""), "[REDACTED]")
    return "ERROR: " + message


def _clean(value):
    return " ".join(str(value or "").split())


def source_provenance():
    with _provenance_lock:
        return [{k:r[k] for k in ('source','id','url','title','published') if k in r}
                for r in _provenance.values()]


def _remember(family, records):
    with _provenance_lock:
        for record in records:
            if record.get('url'):
                key = (family, record['url'])
                _provenance[key] = {**_provenance.get(key, {}), **record, 'source':family}


def restore_provenance(records):
    """Reuse the system's archived discovery metadata during report revision."""
    if not isinstance(records, list) or not records:
        raise ValueError('revision requires a non-empty discovery archive')
    for record in records:
        if not isinstance(record, dict) or record.get('source') not in {'arxiv','hf-search','hf-daily','web'} or not re.match(r'^https?://\S+$', record.get('url','')):
            raise ValueError('invalid discovery archive record')
    for record in records:
        _remember(record['source'], [{k:record[k] for k in ('id','url','title','published') if k in record}])


def _records(records, family=None):
    if family:
        _remember(family, records)
    return json.dumps(records, ensure_ascii=False) if records else "NO RESULTS"


@tool
def arxiv_search(query: str, max_results: int = 10) -> str:
    """Search arXiv by a few keywords, newest first. JSON: id, url, published, title, summary."""
    global _last_arxiv
    try:
        terms = [t for t in re.findall(r"[^\W_]+(?:-[^\W_]+)*", query) if t.upper() not in {"AND", "OR", "NOT", "ALL", "TI", "AU", "ABS"}]
        if not terms:
            return "NO RESULTS"

        def fetch():
            global _last_arxiv
            with _arxiv_lock:
                time.sleep(max(0, 3 - (time.monotonic() - _last_arxiv)))
                _last_arxiv = time.monotonic()
                return _request("GET", ARXIV_URL, timeout=20, params={"search_query": " AND ".join("all:" + t for t in terms),
                    "sortBy": "submittedDate", "sortOrder": "descending", "start": 0, "max_results": min(30, max(1, max_results))})
        r = with_retry(fetch, attempts=7, base=2, cap=60)
        records = []
        for entry in ET.fromstring(r.text).findall("{http://www.w3.org/2005/Atom}entry"):
            def field(name):
                return _clean(entry.findtext("{http://www.w3.org/2005/Atom}" + name))
            paper_id = re.sub(r"v\d+$", "", field("id").split("/abs/")[-1])
            if "api/errors" in paper_id:
                raise ValueError(field("summary"))
            records.append({"id": paper_id, "url": "https://arxiv.org/abs/" + paper_id,
                "published": field("published")[:10], "title": field("title"), "summary": field("summary")[:600]})
        return _records(records, "arxiv")
    except Exception as exc:
        return safe_error(exc)


def _hf_records(items, prefer_ai=False):
    if not isinstance(items, list):
        raise ValueError("expected a list of papers")
    records = []
    for item in items:
        paper = item.get("paper") or {}
        if not paper.get("id"):
            continue
        summary = (paper.get("ai_summary") or item.get("ai_summary")) if prefer_ai else None
        records.append({"id": paper["id"], "url": "https://huggingface.co/papers/" + paper["id"],
            "published": _clean(paper.get("publishedAt") or item.get("publishedAt"))[:10],
            "title": _clean(paper.get("title") or item.get("title")),
            "summary": _clean(summary or paper.get("summary") or item.get("summary"))[:600],
            "upvotes": paper.get("upvotes") or item.get("upvotes") or 0,
            "github": paper.get("githubRepo") or item.get("githubRepo") or "",
            "stars": paper.get("githubStars") or item.get("githubStars") or 0})
    return records


@tool
def hf_daily_papers(limit: int = 30, date: str = "", keyword: str = "") -> str:
    """Trending Hugging Face papers sorted by upvotes. Optional date YYYY-MM-DD and title/summary keyword filter; no topic search."""
    try:
        params = {"limit": min(100, max(1, limit))}
        if date:
            params["date"] = date
        records = _hf_records(with_retry(lambda: _request("GET", HF_DAILY_URL, params=params)).json())
        if keyword:
            records = [r for r in records if keyword.casefold() in (r["title"] + " " + r["summary"]).casefold()]
        return _records(sorted(records, key=lambda r: r["upvotes"], reverse=True), "hf-daily")
    except Exception as exc:
        return safe_error(exc)


@tool
def hf_search_papers(query: str, limit: int = 10) -> str:
    """Search Hugging Face papers by topic. JSON: id, url, published, title, summary, upvotes, github, stars."""
    try:
        if not query.strip():
            return "NO RESULTS"
        r = with_retry(lambda: _request("GET", HF_SEARCH_URL, params={"q": query, "limit": min(50, max(1, limit))}))
        return _records(_hf_records(r.json(), prefer_ai=True), "hf-search")
    except Exception as exc:
        return safe_error(exc)


def _mcp(name, arguments):
    def fetch():
        key = os.getenv("EXA_API_KEY", "")
        r = _request("POST", EXA_URL, params={"exaApiKey": key} if key else {},
            headers={"Accept": "application/json, text/event-stream"},
            json={"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": name, "arguments": arguments}})
        payloads = [json.loads(line[5:].strip()) for line in r.text.splitlines() if line.startswith("data:")]
        if not payloads:
            payloads = [r.json()]
        payload = next((p for p in payloads if p.get("id") == 1), {})
        if "error" in payload:
            raise ValueError(json.dumps(payload["error"]))
        if "result" not in payload:
            raise ValueError("MCP response has no result")
        result = payload["result"]
        text = "\n".join(c.get("text", "") for c in result.get("content", []) if c.get("type") == "text")
        meta = result.get("_meta", {})
        def limited(value):
            if isinstance(value, dict):
                return any((re.search(r"rate.?limit", str(k), re.I) and v is True) or limited(v) for k, v in value.items())
            if isinstance(value, list):
                return any(limited(v) for v in value)
            return isinstance(value, str) and bool(re.search(r"rate.?limit|too many requests|quota exceeded", value, re.I))
        if limited(meta) or re.search(r"rate limit (?:exceeded|reached)|rate.limited|too many requests|quota exceeded", text, re.I):
            raise RetryableError("Exa rate limited", retry_after=20)
        if result.get("isError"):
            raise ValueError(text or "MCP tool error")
        records = []
        for match in re.finditer(r'(?m)^(?:Title: |# )([^\n]+)\nURL:\s*(https?://\S+)(?:\nPublished:\s*([^\n]+))?', text):
            title, url, date = match.groups()
            record = {'url':url}
            if len(_clean(title)) <= 300 and _clean(title).casefold() not in {'n/a','na','untitled','unknown','no title'}:
                record['title'] = _clean(title)
            if date and re.match(r'\d{4}-\d{2}-\d{2}',date):
                record['published']=date[:10]
            records.append(record)
        urls = re.findall(r"(?m)^URL:\s*(https?://\S+)", text)
        if name == 'web_fetch_exa' and text.strip():
            urls.extend(arguments['urls'])
        known = {r['url'] for r in records}
        records.extend({'url':url} for url in urls if url not in known)
        _remember('web', records)
        return text.strip() or "NO RESULTS"
    return with_retry(fetch, attempts=7, base=2, cap=60)


@tool
def web_search(query: str, objective: str = "", num_results: int = 5) -> str:
    """Search Exa for authoritative pages. Returns retrieved text with URLs; supply a query and desired evidence."""
    try:
        if not query.strip():
            return "NO RESULTS"
        return _mcp("web_search_exa", {"query": query, "objective": objective or f"Find authoritative sources about {query}",
            "numResults": min(10, max(1, num_results))})
    except Exception as exc:
        return safe_error(exc)


@tool
def web_fetch(url: str) -> str:
    """Fetch one http(s) page with Exa, up to 12000 characters. Use to verify claims against original sources."""
    try:
        if not re.match(r"^https?://", url):
            raise ValueError("URL must start with http(s)")
        return _mcp("web_fetch_exa", {"urls": [url], "maxCharacters": 12000})[:12000]
    except Exception as exc:
        return safe_error(exc)


SOURCE_TOOLS = [arxiv_search, hf_daily_papers, hf_search_papers, web_search, web_fetch]

if __name__ == "__main__":
    for fn, args in [(arxiv_search, {"query": "world model", "max_results": 3}),
        (hf_daily_papers, {"limit": 20}), (hf_search_papers, {"query": "world model", "limit": 3}),
        (web_search, {"query": "survey paper on world models", "num_results": 2}),
        (web_fetch, {"url": "https://arxiv.org/abs/1803.10122"})]:
        print(f"== {fn.name}\n{fn.invoke(args)[:400]}\n")
