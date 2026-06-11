# JAV Scraper Pro

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB.svg?logo=python&logoColor=white)]()
[![License](https://img.shields.io/badge/License-MIT-green.svg)]()

**Multi-source JAV metadata scraper — 32 data sources, free Google Translate, video screenshots, full NFO.**

[📖 English](#english-documentation) · [📖 中文](#中文文档)

---

# English Documentation

## Overview

JAV Scraper Pro fetches metadata for Japanese Adult Videos (JAV) from 32 websites, merges results, translates titles/plots to Chinese (free), extracts video screenshots, and generates Kodi/Emby/Jellyfin-compatible NFO + poster/fanart/thumb images.

### What it does

1. **Scrape** — Search a JAV number (e.g. `FNS-215`) across 32 sources
2. **Merge** — Combine the best data from all sources (priority-based fallback)
3. **Translate** — Free Google Translate: Japanese → Chinese (no API key needed)
4. **Process** — Generate poster/fanart/thumb images from cover art
5. **Screenshot** — Extract frames from video files via ffmpeg
6. **Output** — Kodi/Emby NFO + images ready for your media library

### Output file naming

| File | Purpose | Example |
|------|---------|---------|
| `{NUMBER}.nfo` | Kodi/Emby metadata | `FNS-215.nfo` |
| `{NUMBER}.jpg` | Original cover | `FNS-215.jpg` |
| `{NUMBER}-poster.jpg` | Vertical poster (800×1200) | `FNS-215-poster.jpg` |
| `{NUMBER}-fanart.jpg` | Horizontal background (1920×1080) | `FNS-215-fanart.jpg` |
| `{NUMBER}-thumb.jpg` | Thumbnail (480×270) | `FNS-215-thumb.jpg` |
| `screenshot_1~3.jpg` | Video screenshots (if `--video`) | `screenshot_1.jpg` |

Place these files next to your video file (e.g. `FNS-215.mp4`) and VidHub/SenPlayer/Emby/Jellyfin will automatically pick them up.

---

## Installation

### Quick install

```bash
# Clone repo
git clone https://github.com/7452323/jav-scraper-pro.git
cd jav-scraper-pro

# Install dependencies
pip install requests pillow deep-translator

# Optional: install the package (adds `jav-scraper` command)
pip install -e .
```

### Dependencies

| Package | Required? | For |
|---------|-----------|-----|
| `requests` | ✅ Yes | HTTP fetching |
| `pillow` | ✅ Yes | Image processing (poster/fanart/thumb) |
| `deep-translator` | ✅ Yes | Free Google Translate |
| `ffmpeg` | ⚠️ Optional | Video screenshots (install via apt/brew/choco) |

### Video screenshot support

```bash
# Linux
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows
choco install ffmpeg
# or download from https://ffmpeg.org/download.html
```

---

## Usage

### Basic scrape

```bash
# Scrape a single number (fallback mode: try sources in priority order, stop at first hit)
python -m jav_scraper.cli scrape FNS-215

# Scrape and merge from ALL sources
python -m jav_scraper.cli scrape FNS-215 --merge

# Scrape + translate + merge (full pipeline)
python -m jav_scraper.cli scrape FNS-215 --merge --translate

# JSON output (for programmatic use)
python -m jav_scraper.cli scrape FNS-215 --json

# Multiple numbers
python -m jav_scraper.cli scrape FNS-215 MIDV-001 ABW-123
```

### Full pipeline with video

```bash
python -m jav_scraper.cli scrape FNS-215 --translate --video /path/to/FNS-215.mp4
```

This produces: NFO + poster.jpg + fanart.jpg + thumb.jpg + screenshot_1~3.jpg

### Generate NFO only

```bash
# Generate from scraped data
python -m jav_scraper.cli nfo FNS-215

# Custom output path
python -m jav_scraper.cli nfo FNS-215 --output /path/to/output/FNS-215.nfo

# With translation and merge
python -m jav_scraper.cli nfo FNS-215 --merge --translate
```

### List all sources

```bash
python -m jav_scraper.cli sources
```

### Translate text

```bash
# Japanese → Chinese (default)
python -m jav_scraper.cli translate "完全主観で誘惑してくる美脚ナースの卑猥な治療"

# Japanese → English
python -m jav_scraper.cli translate "完全主観で誘惑してくる美脚ナースの卑猥な治療" --target english
```

### Process images

```bash
# Generate poster (crops the right side by default)
python -m jav_scraper.cli image poster --url https://example.com/cover.jpg --output poster.jpg

# Generate fanart (with blur background)
python -m jav_scraper.cli image fanart --url https://example.com/cover.jpg --output fanart.jpg

# Generate thumbnail
python -m jav_scraper.cli image thumb --url https://example.com/cover.jpg --output thumb.jpg
```

### Video screenshots

```bash
# Single screenshot at default position (25% into video)
python -m jav_scraper.cli video video.mp4 --output screenshot.jpg

# Screenshot at custom time (seconds)
python -m jav_scraper.cli video video.mp4 --output shot.jpg --time 60

# Grid of 3 screenshots
python -m jav_scraper.cli video video.mp4 --output grid.jpg --grid
```

---

## Supported Sources (32 total)

| # | Source | URL Pattern | Access |
|---|--------|-------------|--------|
| 1 | **JavBus** | `javbus.com/search/{ID}` | ⚠️ Cookie might be needed |
| 2 | **JavDB** | `javdb.com/search?q={ID}` | ❌ Cloudflare protected |
| 3 | **JavLibrary** | `javlibrary.com/en/?v=byid&id={ID}` | ✅ Direct |
| 4 | **AVSOX** | `avsox.how/{ID}` | ✅ Direct |
| 5 | **AVSEX** | `avsex.xyz/{ID}` | ✅ Direct |
| 6 | **OneJAV** | `onejav.com/torrent/{ID}` | ✅ Direct |
| 7 | **FALENO** | `faleno.jp/top/works/{ID}/` | ✅ Direct (FALENO only) |
| 8 | **Jav321** | `jav321.com` (POST search) | ✅ Direct |
| 9 | **MGStage** | `mgstage.com/product/product_detail/{ID}/` | ⚠️ Cookie `adc=1` |
| 10 | **Prestige** | `prestige-av.com` (JSON API) | ✅ Direct |
| 11 | **FC2** | `adult.contents.fc2.com/article/{ID}/` | ✅ Direct |
| 12 | **FC2PPVDB** | `fc2ppvdb.com/articles/{ID}` | ✅ Direct |
| 13 | **FC2Club** | `fc2club.top/html/FC2-{ID}.html` | ✅ Direct |
| 14 | **ThePornDB** | `api.theporndb.net/scenes?parse={ID}` | ✅ Free API |
| 15 | **JavDay** | `javday.tv` (search) | ✅ Direct |
| 16 | **Airav** | `cn.airav.wiki/video/{ID}` | ✅ Direct |
| 17 | **CableAV** | `cableav.tv` (search) | ✅ Direct |
| 18 | **CNMDB** | `cnmdb.net/s0?q={ID}` | ✅ Direct |
| 19 | **Dahlia** | `dahlia-av.jp/works/{ID}/` | ✅ Direct |
| 20 | **Fantastica** | `fantastica-vr.com` (search) | ✅ Direct |
| 21 | **FreeJavBT** | `freejavbt.com/{ID}` | ✅ Direct |
| 22 | **GIGA** | `giga-web.jp` (search) | ⚠️ Cookie needed |
| 23 | **XCity** | `xcity.jp` (search) | ✅ Direct |
| 24 | **Kin8** | `kin8tengoku.com` (search) | ✅ Direct |
| 25 | **Love6** | `love6.tv` (search) | ✅ Direct |
| 26 | **LuluBar** | `lulubar.co` (search) | ✅ Direct |
| 27 | **MadouQu** | `madouqu.com` (search) | ✅ Direct |
| 28 | **MMTV** | `7mmtv.sx` (search) | ✅ Direct |
| 29 | **HDouban** | JSON API | ✅ Direct |
| 30 | **HSCangku** | `hsck860.cc` (search) | ✅ Direct |
| 31 | **MyWife** | `mywife.jp` (search) | ✅ Direct |
| 32 | **Official** | Varies by prefix | ✅ Direct |

---

## NFO Format

The tool generates standard Kodi/Emby/Jellyfin-compatible NFO files:

```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
<movie>
  <title>FNS-215 中文标题（已翻译）</title>
  <sorttitle>FNS-215</sorttitle>
  <originaltitle>FNS-215</originaltitle>
  <set>系列名称</set>
  <rating>8.5</rating>
  <year>2026</year>
  <mpaa>XXX</mpaa>
  <premiered>2026-06-10</premiered>
  <release>2026-06-10</release>
  <runtime>120</runtime>
  <studio>FALENO</studio>
  <maker>FALENO</maker>
  <label>FALENO</label>
  <publisher>发行商</publisher>
  <director>导演名</director>
  <plot>简介描述</plot>
  <outline>简介描述</outline>
  <genre>JAV</genre>
  <genre>Censored</genre>
  <tag>标签1</tag>
  <tag>标签2</tag>
  <actor>
    <name>女优名</name>
    <role></role>
    <thumb>女优头像URL</thumb>
  </actor>
  <artist>女优名</artist>
  <id>FNS-215</id>
  <num>FNS-215</num>
  <cover>FNS-215-poster.jpg</cover>
  <poster>FNS-215-poster.jpg</poster>
  <thumb>FNS-215-thumb.jpg</thumb>
  <fanart>FNS-215-fanart.jpg</fanart>
</movie>
```

---

## Comparison with MDCx

| Feature | JAV Scraper Pro | MDCx |
|---------|----------------|------|
| Data sources | **32** | 40+ |
| Interface | **CLI (terminal)** | PyQt5 GUI |
| Translation | **Google Translate (free, no key)** | DeepL + YouDao + OpenAI |
| Video screenshots | ✅ ffmpeg | ✅ |
| Poster/fanart/thumb | ✅ **Automatic** | ✅ |
| Multi-source merge | ✅ Priority fallback | ✅ |
| Kodi/Emby NFO | ✅ Full fields | ✅ Customizable |
| Image crop position | **Left / Center / Right** | Auto aspect-ratio |
| Actor headshots | ✅ From source | ✅ From source |
| FC2 support | ✅ FC2/FC2PPVDB/FC2Club | ✅ FC2 series |
| JSON output | ✅ Yes | ❌ |
| Docker deployment | ❌ | ✅ FastAPI + Docker |
| File renaming | ❌ (manual) | ✅ Template system |
| NFO template | ❌ (fixed) | ✅ Customizable |
| GUI batch | ❌ | ✅ |
| Extra sources | ❌ (30 more) | ✅ 国产/独立站等 |

### MDCx Exclusive Features (not in JAV Scraper Pro)

- DMM/FANZA official source
- FC2Hub additional source
- Getchu (anime/games)
- Chinese native AV (国产/麻豆/91)
- File auto-renaming & organization
- Custom NFO templates
- FastAPI server mode + Docker
- GUI batch processing

---

## Project Structure

```
jav-scraper-pro/
├── jav_scraper/
│   ├── __init__.py           # Package init, version
│   ├── metadata.py           # Data model (JavMetadata, Actor)
│   ├── http_client.py        # HTTP session with error handling
│   ├── sources/              # 32 individual source scrapers
│   │   ├── __init__.py       # Source registry
│   │   ├── onejav.py         # OneJAV
│   │   ├── javdb.py          # JavDB
│   │   ├── javbus.py         # JavBus
│   │   ├── faleno.py         # FALENO official
│   │   ├── avsox.py          # AVSOX
│   │   ├── avsex.py          # AVSEX
│   │   ├── javlibrary.py     # JavLibrary
│   │   ├── jav321.py         # Jav321
│   │   ├── mgstage.py        # MGStage
│   │   ├── prestige.py       # Prestige
│   │   ├── fc2.py            # FC2
│   │   ├── fc2ppvdb.py       # FC2PPVDB
│   │   ├── fc2club.py        # FC2Club
│   │   ├── theporndb.py      # ThePornDB
│   │   ├── javday.py         # JavDay
│   │   ├── airav.py          # Airav
│   │   ├── cableav.py        # CableAV
│   │   ├── cnmdb.py          # CNMDB
│   │   ├── dahlia.py         # Dahlia
│   │   ├── fantastica.py     # Fantastica
│   │   ├── freejavbt.py      # FreeJavBT
│   │   ├── giga.py           # GIGA
│   │   ├── xcity.py          # XCity
│   │   ├── kin8.py           # Kin8
│   │   ├── love6.py          # Love6
│   │   ├── lulubar.py        # LuluBar
│   │   ├── madouqu.py        # MadouQu
│   │   ├── mmtv.py           # MMTV
│   │   ├── hdouban.py        # HDouban
│   │   ├── hscangku.py       # HSCangku
│   │   ├── mywife.py         # MyWife
│   │   └── official.py       # Generic official sites
│   ├── orchestrator.py       # Multi-source merge + fallback
│   ├── translator.py         # Google Translate (free)
│   ├── image_processor.py    # Poster/fanart/thumb generation
│   ├── video_processor.py    # ffmpeg screenshot extraction
│   ├── nfo_generator.py      # Kodi/Emby NFO builder
│   └── cli.py                # Command-line interface
├── setup.py                  # Package installation
├── requirements.txt          # Dependencies
├── .gitignore
└── README.md
```

---

## License

MIT

---

# 中文文档

## 概述

JAV Scraper Pro 是一个多源 JAV 元数据刮削工具。输入番号（如 `FNS-215`），自动从 32 个网站抓取数据，合并最佳结果，生成 Kodi/Emby/Jellyfin 兼容的 NFO 文件和海报图片。

### 功能一览

1. **刮削** — 输入番号，自动搜索 32 个数据源
2. **合并** — 按优先级自动 fallback，合并最佳元数据
3. **翻译** — 免费谷歌翻译，日文标题/简介→中文（无需 API Key）
4. **裁图** — 从横版封面生成竖版海报（poster）、横版背景（fanart）、缩略图（thumb）
5. **截图** — 从视频文件抽取 3 帧截图（需安装 ffmpeg）
6. **输出** — 完整的 NFO + 图片，直接放入视频目录即可被播放器识别

### 配套 VidHub / SenPlayer 使用

VidHub 和 SenPlayer 不读取 NFO 文件，而是通过同目录下的文件名自动匹配封面：

```
你的视频目录/
├── FNS-215.mp4           ← 视频文件（文件名自定义）
├── FNS-215.nfo           ← 元数据（Emby/Jellyfin 用）
├── FNS-215-poster.jpg    ← 竖封面（显示在海报墙）
├── FNS-215-fanart.jpg    ← 横背景（显示在详情页）
├── FNS-215-thumb.jpg     ← 缩略图
└── FNS-215.jpg           ← 原始封面（备用）
```

---

## 安装方法

### 快速安装

```bash
# 下载代码
git clone https://github.com/7452323/jav-scraper-pro.git
cd jav-scraper-pro

# 安装依赖
pip install requests pillow deep-translator

# 可选：装为命令行工具
pip install -e .
```

### 依赖说明

| 库 | 必须？ | 用途 |
|----|--------|------|
| `requests` | ✅ 必须 | 网页请求 |
| `pillow` | ✅ 必须 | 图片处理（裁图/模糊背景） |
| `deep-translator` | ✅ 必须 | 免费谷歌翻译 |
| `ffmpeg` | ⚠️ 可选 | 视频截图（装不装都行） |

### 安装 ffmpeg（用于截图）

```bash
# Linux (Debian/Ubuntu)
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows
choco install ffmpeg
# 或从 https://ffmpeg.org/download.html 下载
```

---

## 使用说明

### 基本刮削

```bash
# 默认模式：按优先级依次尝试，第一个成功的源就返回
python -m jav_scraper.cli scrape FNS-215

# 合并模式：尝试所有源，合并最佳结果
python -m jav_scraper.cli scrape FNS-215 --merge

# 刮削+翻译+合并（完整流程）
python -m jav_scraper.cli scrape FNS-215 --merge --translate

# JSON 格式输出
python -m jav_scraper.cli scrape FNS-215 --json

# 同时刮多个
python -m jav_scraper.cli scrape FNS-215 MIDV-001 ABW-123
```

### 完整流程（含视频截图）

```bash
python -m jav_scraper.cli scrape FNS-215 --translate --video /path/to/FNS-215.mp4
```

一次输出：NFO + poster.jpg + fanart.jpg + thumb.jpg + screenshot_1~3.jpg

### 只生成 NFO

```bash
# 刮削后生成 NFO
python -m jav_scraper.cli nfo FNS-215

# 指定输出路径
python -m jav_scraper.cli nfo FNS-215 --output /path/to/FNS-215.nfo

# 合并+翻译
python -m jav_scraper.cli nfo FNS-215 --merge --translate
```

### 查看所有数据源

```bash
python -m jav_scraper.cli sources
```

输出示例：
```
Total sources: 32
  [ 1] javbus
  [ 2] javdb
  [ 3] javlibrary
  [ 4] avsox
  [ 5] avsex
  [ 6] onejav
  [ 7] faleno
  [ 8] jav321
  [ 9] mgstage
  [10] prestige
  ...
```

### 翻译文本

```bash
# 日文→中文（默认）
python -m jav_scraper.cli translate "完全主観で誘惑してくる美脚ナースの卑猥な治療"

# 日文→英文
python -m jav_scraper.cli translate "完全主観で誘惑してくる美脚ナースの卑猥な治療" --target english
```

### 图片处理

```bash
# 生成竖版海报（默认从右边裁切）
python -m jav_scraper.cli image poster --url https://example.com/cover.jpg --output poster.jpg

# 生成横版背景（高斯模糊填充）
python -m jav_scraper.cli image fanart --url https://example.com/cover.jpg --output fanart.jpg

# 生成缩略图
python -m jav_scraper.cli image thumb --url https://example.com/cover.jpg --output thumb.jpg
```

### 视频截图

```bash
# 截一帧（默认在视频 25% 位置）
python -m jav_scraper.cli video video.mp4 --output screenshot.jpg

# 指定时间点（秒）
python -m jav_scraper.cli video video.mp4 --output shot.jpg --time 60

# 三帧拼图
python -m jav_scraper.cli video video.mp4 --output grid.jpg --grid
```

---

## 32 个数据源一览

| # | 源名称 | 网址 | 访问方式 |
|---|--------|------|---------|
| 1 | **JavBus** | `javbus.com` | ⚠️ 可能需要 Cookie |
| 2 | **JavDB** | `javdb.com` | ❌ Cloudflare 保护 |
| 3 | **JavLibrary** | `javlibrary.com` | ✅ 直连 |
| 4 | **AVSOX** | `avsox.how` | ✅ 直连 |
| 5 | **AVSEX** | `avsex.xyz` | ✅ 直连 |
| 6 | **OneJAV** | `onejav.com` | ✅ 直连 |
| 7 | **FALENO** | `faleno.jp` | ✅ 仅限FALENO系列 |
| 8 | **Jav321** | `jav321.com` | ✅ 直连 |
| 9 | **MGStage** | `mgstage.com` | ⚠️ 需 Cookie |
| 10 | **Prestige** | `prestige-av.com` | ✅ 直连 |
| 11 | **FC2** | `fc2.com` | ✅ 直连 |
| 12 | **FC2PPVDB** | `fc2ppvdb.com` | ✅ 直连 |
| 13 | **FC2Club** | `fc2club.top` | ✅ 直连 |
| 14 | **ThePornDB** | `theporndb.net` | ✅ 免费 API |
| 15 | **JavDay** | `javday.tv` | ✅ 直连 |
| 16 | **Airav** | `airav.wiki` | ✅ 直连 |
| 17 | **CableAV** | `cableav.tv` | ✅ 直连 |
| 18 | **CNMDB** | `cnmdb.net` | ✅ 直连 |
| 19 | **Dahlia** | `dahlia-av.jp` | ✅ 直连 |
| 20 | **Fantastica** | `fantastica-vr.com` | ✅ 直连 |
| 21 | **FreeJavBT** | `freejavbt.com` | ✅ 直连 |
| 22 | **GIGA** | `giga-web.jp` | ⚠️ 需 Cookie |
| 23 | **XCity** | `xcity.jp` | ✅ 直连 |
| 24 | **Kin8** | `kin8tengoku.com` | ✅ 直连 |
| 25 | **Love6** | `love6.tv` | ✅ 直连 |
| 26 | **LuluBar** | `lulubar.co` | ✅ 直连 |
| 27 | **MadouQu** | `madouqu.com` | ✅ 直连 |
| 28 | **MMTV** | `7mmtv.sx` | ✅ 直连 |
| 29 | **HDouban** | API | ✅ 直连 |
| 30 | **HSCangku** | `hsck860.cc` | ✅ 直连 |
| 31 | **MyWife** | `mywife.jp` | ✅ 直连 |
| 32 | **Official** | 官方站 | ✅ 直连 |

> 直连 = 无需任何配置，开箱即用
> 需 Cookie = 可能需要登录或设置 Cookie 才能正常访问
> Cloudflare = 服务器环境被 Cloudflare 拦截，本地运行正常

---

## NFO 文件格式

Kodi/Emby/Jellyfin 标准格式：

```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
<movie>
  <title>FNS-215 中文标题（已翻译）</title>
  <sorttitle>FNS-215</sorttitle>
  <originaltitle>FNS-215</originaltitle>
  <set>系列名称</set>
  <rating>8.5</rating>
  <year>2026</year>
  <mpaa>XXX</mpaa>
  <premiered>2026-06-10</premiered>
  <release>2026-06-10</release>
  <runtime>120</runtime>
  <studio>FALENO</studio>
  <maker>FALENO</maker>
  <label>FALENO</label>
  <publisher>发行商</publisher>
  <director>导演名</director>
  <plot>简介描述</plot>
  <outline>简介描述</outline>
  <genre>JAV</genre>
  <genre>Censored</genre>
  <tag>标签1</tag>
  <tag>标签2</tag>
  <actor>
    <name>女优名</name>
    <role></role>
    <thumb>女优头像URL</thumb>
  </actor>
  <artist>女优名</artist>
  <id>FNS-215</id>
  <num>FNS-215</num>
  <cover>FNS-215-poster.jpg</cover>
  <poster>FNS-215-poster.jpg</poster>
  <thumb>FNS-215-thumb.jpg</thumb>
  <fanart>FNS-215-fanart.jpg</fanart>
</movie>
```

---

## 与 MDCx 对比

| 功能 | JAV Scraper Pro | MDCx |
|------|----------------|------|
| **数据源** | **32 个** | 40+ |
| **界面** | **命令行（终端）** | PyQt5 图形界面 |
| **翻译** | **谷歌翻译（免费，无 Key）** | DeepL + YouDao + OpenAI |
| **视频截图** | ✅ ffmpeg | ✅ |
| **海报/背景/缩略图** | ✅ **自动生成** | ✅ |
| **多源合并** | ✅ 优先级 fallback | ✅ |
| **Kodi/Emby NFO** | ✅ 全字段 | ✅ 可自定义模板 |
| **裁切位置** | **左/中/右 可选** | 自适应比例 |
| **演员头像** | ✅ 部分源 | ✅ 多数源 |
| **FC2 支持** | ✅ FC2/FC2PPVDB/FC2Club | ✅ FC2 系列 |
| **JSON 输出** | ✅ 支持 | ❌ |
| **Docker 部署** | ❌ | ✅ FastAPI + Docker |
| **文件重命名** | ❌ 需手动 | ✅ 模板系统 |
| **NFO 模板自定义** | ❌ 固定格式 | ✅ 可自定义 |
| **批量处理** | ❌ 逐个 | ✅ GUI 批量 |
| **额外源** | ❌ 还差 30+ | ✅ 国产/独立站 |

### MDCx 独有功能（本项目暂不支持）

- DMM/FANZA 官方源
- FC2Hub 额外源
- Getchu（动漫/游戏）
- 国产 AV（麻豆/91 等）
- 文件自动重命名整理
- NFO 模板自定义
- FastAPI 服务端 + Docker
- GUI 批量操作

---

## 项目结构

```
jav-scraper-pro/
├── jav_scraper/
│   ├── __init__.py           # 包初始化
│   ├── metadata.py           # 数据模型（JavMetadata, Actor）
│   ├── http_client.py        # HTTP 请求客户端
│   ├── sources/              # 32 个数据源（每个单独文件）
│   │   └── *.py              # 每个源一个爬虫
│   ├── orchestrator.py       # 多源合并 + 自动 fallback
│   ├── translator.py         # 免费谷歌翻译
│   ├── image_processor.py    # 图片处理（裁图/模糊背景）
│   ├── video_processor.py    # ffmpeg 视频截图
│   ├── nfo_generator.py      # NFO 生成器
│   └── cli.py                # 命令行入口
├── setup.py                  # 安装配置
├── requirements.txt          # 依赖列表
├── .gitignore
└── README.md                 # 本文件（中英双语）
```

---

## 许可证

MIT
