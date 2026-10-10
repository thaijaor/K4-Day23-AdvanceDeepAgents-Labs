"""Normalize source metadata from actual tool discoveries, inside the sandbox."""
import json
import re
import sys
from difflib import SequenceMatcher

SOURCES = '/tmp/work/research/sources.json'
PROVENANCE = '/tmp/work/research/provenance.json'


def reliable_title(value):
    return isinstance(value,str) and 0 < len(value.strip()) <= 300 and value.strip().casefold() not in {'n/a','na','untitled','unknown','no title'}


def paper_id(record):
    match = re.search(r'/(?:abs|html|papers)/(\d{4}\.\d{4,5})(?:v\d+)?', record.get('url',''))
    if match:
        return match[1]
    value = str(record.get('id',''))
    return re.sub(r'v\d+$','',value) if re.fullmatch(r'\d{4}\.\d{4,5}(?:v\d+)?',value) else None


def normalize(sources, provenance):
    repaired, problems = [], []
    for source in sources:
        identity = paper_id(source)
        candidates = [r for r in provenance if r.get('url') == source.get('url')]
        if not candidates and identity:
            candidates = [r for r in provenance if paper_id(r) == identity]
        if not candidates:
            problems.append(f"source [{source.get('n')}] needs a real discovery or removal of unsupported claims: {source.get('url')}")
            repaired.append(source)
            continue
        record = next((r for r in candidates if r['source'] == source.get('source')), candidates[0])
        entry = dict(source, source=record['source'], url=record['url'],
                     date=record.get('published') or '')
        if record.get('id'):
            entry['id'] = record['id']
        elif identity:
            entry['id'] = identity
        if reliable_title(record.get('title')):
            old_title = source.get('title') or ''
            clean_title = lambda value: ' '.join(re.findall(r'\w+', value.lower()))
            subtitle_extension = record['title'].casefold().startswith(old_title.casefold().rstrip()+':')
            if reliable_title(old_title) and not subtitle_extension and SequenceMatcher(None, clean_title(old_title), clean_title(record['title'])).ratio() < .65:
                problems.append(f"source [{source.get('n')}] title mismatch: supplied {old_title!r}, retrieved {record['title']!r}. Metadata is now corrected; verify and repair EVERY body claim citing this source against its actual retrieved content, or remove unsupported claims. Do not merely rename the reference.")
            entry['title'] = record['title']
        elif not reliable_title(source.get('title')):
            problems.append(f"source [{source.get('n')}] has no reliable bibliographic title. Exa may extract a figure caption as title; retrieve the real title with arxiv_search or hf_search_papers. Do not use N/A or paste a figure caption into References.")
        repaired.append(entry)
    return repaired, problems


def main():
    try:
        with open(SOURCES,encoding='utf-8') as f:
            sources=json.load(f)
        with open(PROVENANCE,encoding='utf-8') as f:
            provenance=json.load(f)
        repaired, problems=normalize(sources,provenance)
        with open(SOURCES,'w',encoding='utf-8') as f:
            json.dump(repaired,f,ensure_ascii=False,indent=2)
    except (OSError,ValueError,TypeError,KeyError) as exc:
        print(f'cannot normalize sources: {exc}')
        return 1
    report_path = '/tmp/work/report/report.md'
    try:
        with open(report_path,encoding='utf-8') as f:
            report=f.read()
        for heading in ('TL;DR','Background','Trends and open problems'):
            report=re.sub(r'(?im)^##[ \t]+(?:\d+[.)][ \t]+)?(?:\*\*)?'+re.escape(heading)+r'(?:\*\*)?[ \t]*$', '## '+heading, report)
        with open(report_path,'w',encoding='utf-8') as f:
            f.write(report)
    except OSError:
        pass
    print('\n'.join(problems) if problems else f'NORMALIZED: {len(repaired)} sources grounded in tool discoveries')
    return int(bool(problems))


if __name__=='__main__':
    sys.exit(main())
