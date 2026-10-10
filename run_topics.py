"""Generate missing preset surveys sequentially and run the provided submission check."""
import json
import re
import subprocess
import sys
from pathlib import Path

from check_citations import check
from research import ROOT, slugify


def complete(topic):
    stem = ROOT / 'reports' / slugify(topic)
    try:
        meta = json.loads(stem.with_suffix('.meta.json').read_text(encoding='utf-8'))
        sources = json.loads(stem.with_suffix('.sources.json').read_text(encoding='utf-8'))
        report = stem.with_suffix('.md').read_text(encoding='utf-8')
        return meta['topic'] == topic and meta['subagent_calls'] >= 3 and len(meta['source_families']) >= 3 and stem.with_suffix('.audit.md').exists() and not check(report,sources)
    except (OSError, ValueError, KeyError):
        return False


def main():
    topics = re.findall(r'^\d+\. (.+)$', (ROOT / 'topics.md').read_text(encoding='utf-8'), re.M)
    for topic in topics:
        if complete(topic):
            print('Already valid: '+topic, flush=True)
            continue
        print('Running: '+topic, flush=True)
        result = subprocess.run([sys.executable, '-u', str(ROOT/'research.py'), topic], cwd=ROOT)
        if result.returncode:
            return result.returncode
    return subprocess.run([sys.executable, str(ROOT/'self_check.py')],cwd=ROOT).returncode


if __name__ == '__main__':
    sys.exit(main())
