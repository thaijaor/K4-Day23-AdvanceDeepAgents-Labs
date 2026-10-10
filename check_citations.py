"""Standard-library citation validator, executed inside the sandbox."""
import json
import re
import sys
from collections import Counter

REPORT = "/tmp/work/report/report.md"
SOURCES = "/tmp/work/research/sources.json"


def _without_code(text):
    text = re.sub(r"(?ms)^(`{3,}|~{3,})[^\n]*\n.*?^\1[^\n]*$", "", text)
    return re.sub(r"(`+).*?\1", "", text, flags=re.S)


def check(report_text, sources, provenance=None):
    """Return problems for malformed sources, unresolved citations and references."""
    if not isinstance(sources, list) or not sources:
        return ["no sources: expected a non-empty JSON list"]
    problems, by_n, urls = [], {}, set()
    for entry in sources:
        if not isinstance(entry, dict):
            problems.append("source must be an object")
            continue
        n, url = entry.get("n"), entry.get("url")
        family = entry.get("source")
        if family is not None:
            expected = ('https://arxiv.org/abs/' if family == 'arxiv' else
                        'https://huggingface.co/papers/' if family in {'hf-daily','hf-search'} else None)
            if family not in {'arxiv','hf-daily','hf-search','web'}:
                problems.append(f"source [{n}] has unknown family")
            elif expected and url != expected + str(entry.get('id', '')):
                problems.append(f"source [{n}] family/URL mismatch: {family} must use {expected}<id> without version")
        if type(n) is not int or n < 1:
            problems.append("source n must be a positive integer")
        elif n in by_n:
            problems.append(f"duplicate source number [{n}]")
        else:
            by_n[n] = entry
        if not isinstance(url, str) or not re.match(r"^https?://\S+$", url):
            problems.append(f"source [{n}] has invalid URL")
        elif url in urls:
            problems.append(f"duplicate URL for [{n}]")
        else:
            urls.add(url)
    text = _without_code(report_text)
    headings = list(re.finditer(r"(?m)^##[ \t]+References[ \t]*$", text))
    if len(headings) != 1:
        problems.append("report must contain exactly one ## References heading")
    body = text[:headings[0].start()] if headings else text
    references = text[headings[0].end():] if headings else ""
    cited = set()
    if re.search(r'\[@https?://', body):
        problems.append('uncompiled URL citations: run normalize_sources.py before finalization')
    for match in re.finditer(r"\[(\d+(?:\s*[,–-]\s*\d+)*)\](?!\s*\()", body):
        for part in re.split(r"\s*,\s*", match[1]):
            span = re.fullmatch(r"(\d+)\s*[–-]\s*(\d+)", part)
            if span:
                first, last = map(int, span.groups())
                if not 0 <= last - first <= 200:
                    problems.append("invalid citation range")
                else:
                    cited.update(range(first, last + 1))
            else:
                cited.add(int(part))
    problems.extend(f"[{n}] cited but missing from sources.json" for n in sorted(cited - by_n.keys()))
    problems.extend(f"source [{n}] never cited" for n in sorted(by_n.keys() - cited))
    counts = Counter()
    for line in references.splitlines():
        if not line.strip():
            continue
        match = re.match(r"^\[(\d+)\]\s+", line)
        if not match:
            problems.append("reference line must start with [n]")
            continue
        n = int(match[1])
        counts[n] += 1
        if n not in by_n:
            problems.append(f"reference [{n}] missing from sources.json")
        found = re.findall(r"https?://[^\s<>\[\]]+", line)
        found = [url.rstrip(".,;)") for url in found]
        if len(found) != 1:
            problems.append(f"reference [{n}] must contain exactly one URL")
        elif n in by_n and found[0] != by_n[n].get("url"):
            problems.append(f"reference [{n}] URL does not match sources.json")
    for n in by_n:
        if counts[n] != 1:
            problems.append(f"source [{n}] needs exactly one reference line (found {counts[n]})")
    if provenance is not None:
        discovered = {(r['source'],r['url']):r for r in provenance}
        families = {s.get('source') for s in sources if isinstance(s,dict)}
        if len(families & {'arxiv','hf-daily','hf-search','web'}) < 3:
            problems.append('need at least three genuinely discovered source families. Delegate researcher specifically to hf_daily_papers with relevant historical dates or arxiv_search, and cite relevant returned evidence; do not relabel a source unless that tool really returned it.')
        for entry in sources:
            if not isinstance(entry,dict):
                continue
            key = (entry.get('source'),entry.get('url'))
            if key not in discovered:
                alternatives = [r for r in provenance if r['url'] == entry.get('url') or
                                (r.get('id') and r['id'] == entry.get('id'))]
                problems.append(f"source [{entry.get('n')}] not returned by its claimed tool; actual candidates: " +
                                json.dumps([{k:r.get(k) for k in ('source','id','url','published')} for r in alternatives]) +
                                '; do NOT guess metadata. Delegate researcher to retrieve this exact paper via hf_search_papers or web_fetch; alternatively remove the source AND its unsupported claims. After any new retrieval, return control to host to refresh provenance, rather than loop on this snapshot.')
            elif discovered[key].get('published') and entry.get('date') != discovered[key]['published']:
                problems.append(f"source [{entry.get('n')}] ({entry.get('url')}) date must match retrieved published date " + discovered[key]['published'] + "; use the URL, not a previous citation index; run normalize_sources.py when available")
        for heading in ('## TL;DR','## Background','## Trends and open problems'):
            if heading not in report_text.split('## References')[0].splitlines():
                problems.append('missing exact required heading: '+heading)
        section_names = re.findall(r'(?m)^##[ \t]+(.+?)\s*$', body)
        themes = [name for name in section_names if name not in {'TL;DR','Background','Trends and open problems'}]
        if not 3 <= len(themes) <= 6:
            problems.append('required survey structure: write 3-6 substantive thematic comparison sections, excluding TL;DR, Background and Trends and open problems')
        word_count = len(body.split())
        if word_count < 800:
            problems.append(f'survey body is too short: currently {word_count} words, at least {800-word_count} more needed for the 800-word minimum. Develop the 1200-1800 word survey requested by the lead prompt, comparing retrieved evidence, concrete mechanisms and limitations. Use execute to count words before returning. Do not pad or invent claims.')
        if word_count > 1800:
            problems.append(f'survey body exceeds the requested length: {word_count} words, maximum 1800. Condense comparisons, remove repetitive passages and unrequested numerical examples, and preserve cited mechanisms and limitations. Recount words before returning.')
    return problems


def main(argv):
    try:
        with open(argv[1] if len(argv) > 1 else REPORT, encoding="utf-8") as f:
            report = f.read()
        with open(argv[2] if len(argv) > 2 else SOURCES, encoding="utf-8") as f:
            sources = json.load(f)
    except (OSError, ValueError) as exc:
        print(f"cannot read inputs: {exc}")
        return 1
    provenance_path = argv[3] if len(argv) > 3 else None
    try:
        if provenance_path is None:
            provenance = None
        else:
            with open(provenance_path, encoding='utf-8') as f:
                provenance = json.load(f)
    except FileNotFoundError:
        provenance = None
    problems = check(report, sources, provenance)
    print("\n".join(problems) if problems else f"OK: {len(sources)} sources, all citations resolve")
    return int(bool(problems))


if __name__ == "__main__":
    sys.exit(main(sys.argv))
