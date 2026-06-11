#!/usr/bin/env python3
"""Generate FNS-151 output: onejav priority, Chinese, no-bracket naming."""
import os, sys
sys.path.insert(0, '/root/jav-scraper-pro')

from jav_scraper.orchestrator import scrape_merge
from jav_scraper.translator import translate_metadata, translate
from jav_scraper.nfo_generator import build_nfo
from deep_translator import GoogleTranslator

m = scrape_merge('FNS-151', max_sources=3)
if not m:
    print('Failed')
    sys.exit(1)

# Translate everything
m = translate_metadata(m)

# Force translate tags (they're English, not Japanese)
en2cn = GoogleTranslator(source='en', target='zh-CN')
if m.tags:
    translated_tags = []
    for tag in m.tags:
        try:
            t = en2cn.translate(tag)
            if t and t.strip():
                translated_tags.append(t.strip())
            else:
                translated_tags.append(tag)
        except:
            translated_tags.append(tag)
    m.tags = translated_tags

# Force translate plot
if m.plot:
    try:
        m.plot = en2cn.translate(m.plot)
    except:
        pass

# Deduplicate actors
seen = set()
unique_actors = []
for a in m.actors:
    if a.name not in seen:
        seen.add(a.name)
        unique_actors.append(a)
m.actors = unique_actors

# Build filename without brackets: FNS-151 2026-01-08
date_str = m.release or m.year or '2026'
num = m.number
base = f'{num} {date_str}'

print('Base name:', base)
print('Title CN:', m.title_cn or '(no translation)')
print('Actors:', [a.name for a in m.actors])
print('Tags:', m.tags)
print('Plot:', (m.plot or '')[:60])

outdir = '/root/jav-scraper-pro/output'
os.makedirs(outdir, exist_ok=True)

# 1. NFO
nfo_xml = build_nfo(m)
# Fix internal references
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

# Package
import tarfile
tar_path = os.path.join(outdir, 'fns151_final.tar.gz')
with tarfile.open(tar_path, 'w:gz') as tar:
    for f in [nfo_path, cover_path, fanart_path, thumb_path]:
        if os.path.exists(f):
            tar.add(f, arcname=os.path.basename(f))
print('Archive:', tar_path)
print('Done')
