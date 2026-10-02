# /// script
# requires-python = ">=3.11"
# dependencies = ["requests", "pyyaml"]
# ///
"""Cross-post a guide page to dev.to with a canonical link back to the guide site.

    DEV_API_KEY=... uv run _tools/devto_publish.py bulk-google-trends.md            # unpublished draft
    DEV_API_KEY=... uv run _tools/devto_publish.py bulk-google-trends.md --publish  # live
    DEV_API_KEY=... uv run _tools/devto_publish.py --next --publish                 # next not-yet-posted page
                                                                                    # (by nav_order; used weekly by CI)

Relative links are made absolute, the canonical URL points at the guide (so search engines credit
the guide, not dev.to), and _tools/devto_posted.json remembers what was posted so reruns update the
same article instead of duplicating it.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from urllib.parse import urljoin

import requests
import yaml

SITE = 'https://aivaras-mastermind.github.io/google-trends-guide/'
STATE = Path(__file__).with_name('devto_posted.json')
TAGS = {  # dev.to allows at most 4 tags, lowercase alphanumeric
    'index.md': ['googletrends', 'seo', 'datascience', 'marketing'],
    'pytrends-alternative.md': ['python', 'googletrends', 'datascience', 'webscraping'],
    'google-trends-search-volume.md': ['seo', 'googletrends', 'marketing', 'python'],
    'bulk-google-trends.md': ['seo', 'googletrends', 'python', 'marketing'],
}
FOOTER = ('\n\n---\n\n*Originally published at [{host}]({url}). '
          'Written with AI assistance.*\n')


def convert(path: Path) -> dict:
    fm_text, body = re.match(r'^---\n(.*?)\n---\n(.*)$', path.read_text(encoding='utf-8'), re.S).groups()
    fm = yaml.safe_load(fm_text)
    url = urljoin(SITE, fm.get('permalink', '/').lstrip('/'))
    # make relative markdown links absolute: ](../x/) -> ](https://.../x/)
    body = re.sub(r'\]\((?!https?://|#|mailto:)([^)]+)\)', lambda m: f']({urljoin(url, m.group(1))})', body)
    body = body.replace('*Updated October 2026 for the new Google Trends Explore.*\n\n', '')
    return {'title': fm['title'], 'description': fm['description'][:250], 'canonical_url': url,
            'tags': TAGS.get(path.name, ['googletrends', 'seo']),
            'body_markdown': body.strip() + FOOTER.format(host='Google Trends Guides', url=url)}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('page', type=Path, nargs='?')
    ap.add_argument('--next', action='store_true', help='pick the first page (by nav_order) not posted yet')
    ap.add_argument('--publish', action='store_true', help='publish live (default: unpublished draft)')
    ap.add_argument('--dry-run', action='store_true', help='print the converted article, send nothing')
    args = ap.parse_args()
    state = json.loads(STATE.read_text()) if STATE.exists() else {}
    if args.next:
        root = Path(__file__).resolve().parent.parent
        pages = []
        for f in root.glob('*.md'):
            m = re.match(r'^---\n(.*?)\n---\n', f.read_text(encoding='utf-8'), re.S)
            fm = yaml.safe_load(m.group(1)) if m else {}
            if fm.get('nav_title') and f.name not in state:
                pages.append((fm.get('nav_order', 99), f))
        if not pages:
            print('Nothing left to cross-post.')
            return
        args.page = min(pages)[1]
    if not args.page:
        ap.error('give a page or --next')

    article = {**convert(args.page), 'published': args.publish}
    if args.dry_run:
        print(json.dumps({k: v for k, v in article.items() if k != 'body_markdown'}, indent=1))
        print(article['body_markdown'])
        return
    key = os.environ['DEV_API_KEY']
    prev = state.get(args.page.name)
    hdr = {'api-key': key, 'Accept': 'application/vnd.forem.api-v1+json'}
    if prev:
        r = requests.put(f'https://dev.to/api/articles/{prev["id"]}', headers=hdr, json={'article': article}, timeout=60)
    else:
        r = requests.post('https://dev.to/api/articles', headers=hdr, json={'article': article}, timeout=60)
    r.raise_for_status()
    d = r.json()
    state[args.page.name] = {'id': d['id'], 'url': d['url'], 'published': d.get('published')}
    STATE.write_text(json.dumps(state, indent=1))
    print(('Published' if article['published'] else 'Draft saved'), d['url'])


if __name__ == '__main__':
    sys.exit(main())
