#!/usr/bin/env python3
"""Generate FNS-151 output with date naming."""
import os
import sys
sys.path.insert(0, '/root/jav-scraper-pro')

from jav_scraper.orchestrator import scrape_with_fallback
from jav_scraper.nfo_generator import build_nfo

m = scrape_with_fallback('FNS-151')
if not m:
    print('Failed to scrape FNS-151')
    sys.exit(1)

date_str = m.release or m.year or '2026'
num = m.number  # FNS-151
base = f'{num} ({date_str})'

print('Base name:', base)

outdir = '/root/jav-scraper-pro/output'
os.makedirs(outdir, exist_ok=True)

# 1. Generate NFO
nfo_xml = build_nfo(m)

# Fix internal references to use date-based naming
nfo_xml = nfo_xml.replace(f'{num}-poster.jpg', f'{base}-poster.jpg')
nfo_xml = nfo_xml.replace(f'{num}-fanart.jpg', f'{base}-fanart.jpg')
nfo_xml = nfo_xml.replace(f'{num}-thumb.jpg', f'{base}-thumb.jpg')

nfo_path = os.path.join(outdir, f'{base}.nfo')
with open(nfo_path, 'w', encoding='utf-8') as f:
    f.write(nfo_xml)
print('NFO:', nfo_path)

# 2. Download cover
cover_path = os.path.join(outdir, f'{base}-poster.jpg')
if m.cover_url:
    import requests
    r = requests.get(m.cover_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=30)
    if r.status_code == 200:
        with open(cover_path, 'wb') as f:
            f.write(r.content)
        print('Cover:', cover_path, f'({len(r.content)} bytes)')

# 3. Fanart
from jav_scraper.image_processor import generate_fanart, generate_thumb
fanart_path = os.path.join(outdir, f'{base}-fanart.jpg')
if generate_fanart(m.cover_url, fanart_path, blur=True):
    print('Fanart:', fanart_path)

# 4. Thumb
thumb_path = os.path.join(outdir, f'{base}-thumb.jpg')
if generate_thumb(m.cover_url, thumb_path):
    print('Thumb:', thumb_path)

print('Done')
