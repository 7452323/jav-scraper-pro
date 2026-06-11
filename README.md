# JAV Scraper Pro

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB.svg?logo=python&logoColor=white)]()
[![License](https://img.shields.io/badge/License-MIT-green.svg)]()

**Multi-source JAV metadata scraper — 33 data sources, free multi-engine translation, batch directory scan, full NFO + covers. Does NOT download videos.**

[📖 English](#english-documentation) · [📖 中文](#中文文档)

---

## English Documentation

## Overview

**This tool is designed for users without a PC.** Typical setup: use 115 / offline download to get video files on your phone/tablet/NAS, then run this tool to scrape NFO + covers for VidHub / SenPlayer / Emby / Jellyfin.

### ❗ What this tool IS

✅ Scrapes metadata from 33 websites (title, actors, release date, runtime, studio, tags, plot, cover art)  
✅ Generates Kodi-compatible NFO files  
✅ Generates poster / fanart / thumb images from cover art  
✅ Batch scans a folder — auto-detects JAV numbers from filenames, scrapes all at once  
✅ Translates Japanese titles/plots/tags to Chinese (free, multi-engine fallback: Google → MyMemory → PONS)  
✅ Extracts video screenshots if ffmpeg is installed and video files exist  
✅ Works entirely over CLI — no GUI needed, runs on servers / NAS / VPS / cheap cloud instances  
✅ All 33 sources registered and active — but some may be blocked depending on your server's region  

### ❌ What this tool is NOT

❌ **Does NOT download or torrent any video files** — you bring your own videos  
❌ **Does NOT stream or play video** — that's VidHub/SenPlayer's job  
❌ **Does NOT have a GUI** — pure CLI  
❌ **Does NOT require a computer** — runs on any Linux server / VPS / NAS

### Typical workflow (no-PC setup)

```
1.  Find JAV torrent / magnet link on phone
2.  Offline download to 115 cloud → get video files on your storage
3.  Put video files in a folder (on NAS / cloud drive / server)
4.  Run: jav-scraper scan /path/to/videos/ --translate --merge
5.  Each video folder now has: NFO + poster.jpg + fanart.jpg + thumb.jpg
6.  Open with VidHub / SenPlayer — covers and metadata show automatically
```

### Data sources (33 total)

| # | Source | Type | Access |
|---|--------|------|--------|
| 1 | **JavBus** | javbus.com | ⚠️ Blocked outside CN/JP |
| 2 | **JavDB** | javdb.com | ❌ Cloudflare |
| 3 | **JavLibrary** | javlibrary.com | ✅ |
| 4 | **AVSOX** | avsox.how | ⚠️ Survey redirect sometimes |
| 5 | **AVSEX** | avsex.xyz | ✅ |
| 6 | **OneJAV** | onejav.com | ✅ |
| 7 | **FALENO** | faleno.jp | ✅ |
| 8 | **DMM/FANZA** | dmm.co.jp | ⚠️ Blocks non-JP IPs |
| 9 | **Jav321** | jav321.com | ✅ |
| 10 | **MGStage** | mgstage.com | ⚠️ Cookie needed |
| 11–33 | Prestige, FC2, FC2PPVDB, FC2Club, ThePornDB, JavDay, Airav, CableAV, CNMDB, Dahlia, Fantastica, FreeJavBT, GIGA, XCity, Kin8, Love6, LuluBar, MadouQu, MMTV, HDouban, HSCangku, MyWife, Official | Various | ✅ Most accessible |

If one source is blocked, the tool automatically falls through to the next. The more sources, the better the chance of getting full metadata.

### What it does

1. **Scrape** — Search a JAV number (e.g. `FNS-215`) across 33 sources
2. **Merge** — Combine the best data from all sources (priority-based fallback)
3. **Translate** — **Free multi-engine**: Google → MyMemory → PONS (auto-fallback, no API keys)
4. **Batch Scan** — Scan a folder, auto-detect all JAV numbers, scrape everything at once
5. **Process** — Generate poster/fanart/thumb images from cover art
6. **Screenshot** — Extract frames from video files via ffmpeg (video files required)
7. **Output** — Kodi/Emby NFO + images ready for your media library

### What's new in v0.2.0

- **Batch directory scanning** — `jav-scraper scan /path/to/videos/` auto-detects JAV numbers from filenames and scrapes all at once
- **DMM/FANZA source** — Official DMM.co.jp source (Japan's largest AV retailer)
- **Multi-engine translation** — Google → MyMemory → PONS automatic fallback chain. Free, no API keys
- **33 total sources** (up from 32)

### Output file naming

Files are generated in the same directory as the video:

| File | Purpose | Example |
|------|---------|---------|
| `{NUMBER}.nfo` | Kodi/Emby metadata | `FNS-215.nfo` |
| `{NUMBER}.jpg` | Original cover | `FNS-215.jpg` |
| `{NUMBER}-poster.jpg` | Vertical poster (800×1200) | `FNS-215-poster.jpg` |
| `{NUMBER}-fanart.jpg` | Horizontal background (1920×1080) | `FNS-215-fanart.jpg` |
| `{NUMBER}-thumb.jpg` | Thumbnail (480×270) | `FNS-215-thumb.jpg` |
| `{NUMBER}_screenshot_1~3.jpg` | Video screenshots | `FNS-215_screenshot_1.jpg` |

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
| `deep-translator` | ✅ Yes | Free multi-engine translation (Google → MyMemory → PONS) |
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

### 🆕 Batch directory scan (auto-detect + scrape all)

```bash
# Scan a folder, auto-detect JAV numbers, scrape everything
jav-scraper scan /path/to/videos/

# With translation and merge
jav-scraper scan /path/to/videos/ --translate --merge

# Skip video screenshots (faster)
jav-scraper scan /path/to/videos/ --no-video

# Non-recursive (one folder only)
jav-scraper scan /path/to/videos/ --no-recursive

# JSON summary output
jav-scraper scan /path/to/videos/ --json
```

The scanner:
1. Recursively finds all video files (.mp4, .mkv, .avi, .wmv, .mov, .m4v, .ts, etc.)
2. Extracts JAV numbers from filenames (supports FC2, HEYZO, 1pondo, standard formats)
3. Groups videos by number (handles multi-disc releases)
4. Scrapes metadata for each unique number
5. Writes NFO + poster/fanart/thumb in each video's directory
6. Extracts 3 screenshots from the largest video per number

**Supported filename formats:**
- Standard: `FNS-215.mp4`, `FNS_215.mkv`, `MIDV-001.avi`
- FC2: `FC2-1234567.mp4`, `FC2_123456.mkv`
- HEYZO: `HEYZO-1234.mp4`
- 1pondo: `061115_001.mp4`
- Mixed content: `[FALENO] FNS-215 美女と.mp4`

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
# Japanese → Chinese (uses multi-engine fallback)
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

---

## Supported Sources (33 total)

| # | Source | URL Pattern | Access |
|---|--------|-------------|--------|
| 1 | **JavBus** | `javbus.com/search/{ID}` | ⚠️ Cookie might be needed |
| 2 | **JavDB** | `javdb.com/search?q={ID}` | ❌ Cloudflare protected |
| 3 | **JavLibrary** | `javlibrary.com/en/?v=byid&id={ID}` | ✅ Direct |
| 4 | **AVSOX** | `avsox.how/{ID}` | ✅ Direct |
| 5 | **AVSEX** | `avsex.xyz/{ID}` | ✅ Direct |
| 6 | **OneJAV** | `onejav.com/torrent/{ID}` | ✅ Direct |
| 7 | **FALENO** | `faleno.jp/top/works/{ID}/` | ✅ Direct (FALENO only) |
| 8 | **🆕 DMM/FANZA** | `dmm.co.jp/digital/videoa/-/detail/=/cid={CID}/` | ⚠️ May block non-JP IPs |
| 9 | **Jav321** | `jav321.com` (POST search) | ✅ Direct |
| 10 | **MGStage** | `mgstage.com/product/product_detail/{ID}/` | ⚠️ Cookie `adc=1` |
| 11 | **Prestige** | `prestige-av.com` (JSON API) | ✅ Direct |
| 12 | **FC2** | `adult.contents.fc2.com/article/{ID}/` | ✅ Direct |
| 13 | **FC2PPVDB** | `fc2ppvdb.com/articles/{ID}` | ✅ Direct |
| 14 | **FC2Club** | `fc2club.top/html/FC2-{ID}.html` | ✅ Direct |
| 15 | **ThePornDB** | `api.theporndb.net/scenes?parse={ID}` | ✅ Free API |
| 16 | **JavDay** | `javday.tv` (search) | ✅ Direct |
| 17 | **Airav** | `cn.airav.wiki/video/{ID}` | ✅ Direct |
| 18 | **CableAV** | `cableav.tv` (search) | ✅ Direct |
| 19 | **CNMDB** | `cnmdb.net/s0?q={ID}` | ✅ Direct |
| 20 | **Dahlia** | `dahlia-av.jp/works/{ID}/` | ✅ Direct |
| 21 | **Fantastica** | `fantastica-vr.com` (search) | ✅ Direct |
| 22 | **FreeJavBT** | `freejavbt.com/{ID}` | ✅ Direct |
| 23 | **GIGA** | `giga-web.jp` (search) | ⚠️ Cookie needed |
| 24 | **XCity** | `xcity.jp` (search) | ✅ Direct |
| 25 | **Kin8** | `kin8tengoku.com` (search) | ✅ Direct |
| 26 | **Love6** | `love6.tv` (search) | ✅ Direct |
| 27 | **LuluBar** | `lulubar.co` (search) | ✅ Direct |
| 28 | **MadouQu** | `madouqu.com` (search) | ✅ Direct |
| 29 | **MMTV** | `7mmtv.sx` (search) | ✅ Direct |
| 30 | **HDouban** | JSON API | ✅ Direct |
| 31 | **HSCangku** | `hsck860.cc` (search) | ✅ Direct |
| 32 | **MyWife** | `mywife.jp` (search) | ✅ Direct |
| 33 | **Official** | Varies by prefix | ✅ Direct |

---

## Comparison with MDCx

| Feature | JAV Scraper Pro | MDCx |
|---------|----------------|------|
| Data sources | **33** (incl. DMM) | 40+ |
| Interface | **CLI (terminal)** | PyQt5 GUI |
| Translation | **Google + MyMemory + PONS (free, auto-fallback)** | DeepL + YouDao + OpenAI |
| Batch directory scan | **✅ NEW** | ✅ |
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
| Extra sources | ❌ | ✅ 国产/独立站等 |

### MDCx Exclusive Features (not in JAV Scraper Pro)

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
│   ├── sources/              # 33 individual source scrapers
│   │   ├── __init__.py       # Source registry
│   │   ├── onejav.py         # OneJAV
│   │   ├── javdb.py          # JavDB
│   │   ├── javbus.py         # JavBus
│   │   ├── faleno.py         # FALENO official
│   │   ├── avsox.py          # AVSOX
│   │   ├── avsex.py          # AVSEX
│   │   ├── javlibrary.py     # JavLibrary
│   │   ├── dmm.py            # 🆕 DMM/FANZA
│   │   ├── jav321.py         # Jav321
│   │   ├── ... (25 more)
│   │   └── official.py       # Generic official sites
│   ├── orchestrator.py       # Multi-source merge + fallback
│   ├── translator.py         # 🆕 Multi-engine translation (Google → MyMemory → PONS)
│   ├── scanner.py            # 🆕 Batch directory scanner
│   ├── image_processor.py    # Poster/fanart/thumb generation
│   ├── video_processor.py    # ffmpeg screenshot extraction
│   ├── nfo_generator.py      # Kodi/Emby NFO builder
│   └── cli.py                # Command-line interface (updated with scan)
├── setup.py                  # Package installation
├── requirements.txt          # Dependencies
├── .gitignore
└── README.md
```

---

## License

MIT

---

## 中文文档

## 概述

**这个工具专门为没有电脑的用户设计。** 你不需要 PC，只需要一台能跑 Linux 的服务器/VPS/云函数，就能给你的视频批量刮削 NFO 和封面，配合 VidHub / SenPlayer / Emby 使用。

### ❗ 这个工具能做什么

✅ 从 33 个网站自动抓取元数据（标题、演员、日期、时长、片商、标签、简介、封面）  
✅ 生成 Kodi/Emby/Jellyfin 兼容的 NFO 文件  
✅ 从横版封面自动裁切竖版 poster + 横版 fanart + 缩略图  
✅ **批量扫描文件夹** — 自动识别文件名中的番号，一次性全部刮完  
✅ **多引擎免费翻译** — Google → MyMemory → PONS 自动降级，全部免费无需 Key  
✅ 如果装了 ffmpeg，可从视频文件提取截图  
✅ 纯 CLI，无 GUI 需求，跑在服务器/VPS/NAS/云函数上

### ❌ 这个工具不做什么

❌ **不下载任何视频** — 视频文件你自己搞定（115离线、BT、磁力随便你）  
❌ **不播放视频** — 那是 VidHub/SenPlayer 的事  
❌ **不需要电脑** — 手机+服务器就够了

### 典型使用流程（无 PC 场景）

```
1. 手机找番号/磁力链接
2. 115 离线下载 → 得到视频文件
3. 视频文件放到服务器/NAS的某个文件夹
4. 执行：jav-scraper scan /path/to/videos/ --translate --merge
5. 每个视频目录自动生成：NFO + poster.jpg + fanart.jpg + thumb.jpg
6. VidHub / SenPlayer 打开 → 封面和元数据自动显示
```

### 数据源列表（共 33 个）

| # | 源 | 地址 | 可访问性 |
|---|------|------|---------|
| 1 | **JavBus** | javbus.com | ⚠️ 非 CN/JP 可能被拦 |
| 2 | **JavDB** | javdb.com | ❌ Cloudflare |
| 3 | **JavLibrary** | javlibrary.com | ✅ |
| 4 | **AVSOX** | avsox.how | ⚠️ 偶有跳转调查页 |
| 5 | **AVSEX** | avsex.xyz | ✅ |
| 6 | **OneJAV** | onejav.com | ✅ |
| 7 | **FALENO** | faleno.jp | ✅ |
| 8 | **DMM/FANZA** | dmm.co.jp | ⚠️ 非日本 IP 屏蔽 |
| 9 | **Jav321** | jav321.com | ✅ |
| 10 | **MGStage** | mgstage.com | ⚠️ 需 Cookie |
| 11–33 | Prestige, FC2, FC2PPVDB, FC2Club, ThePornDB 等 23 个 | 各站 | ✅ 大部分可访问 |

某个源被拦了会自动跳到下一个，源越多越容易刮到完整数据。

### 功能一览

1. **刮削** — 输入番号，自动搜索 33 个数据源（新增 DMM/FANZA）
2. **合并** — 按优先级自动 fallback，合并最佳元数据
3. **翻译** — **多引擎免费翻译链**：Google → MyMemory → PONS 自动切换，全部免费无需 API Key
4. **批量扫描** — 🆕 `jav-scraper scan` 扫文件夹，自动识别文件名中的番号，一次性全部刮完
5. **裁图** — 从横版封面生成竖版海报（poster）、横版背景（fanart）、缩略图（thumb）
6. **截图** — 从视频文件抽取 3 帧截图（需安装 ffmpeg）
7. **输出** — 完整的 NFO + 图片，直接放入视频目录即可被播放器识别

### 批量扫描（一键刮完整个文件夹）

```bash
# 扫描文件夹，自动识别番号，全部刮削
jav-scraper scan /path/to/videos/

# 带翻译和合并
jav-scraper scan /path/to/videos/ --translate --merge

# 不截图（更快）
jav-scraper scan /path/to/videos/ --no-video

# 不递归子目录
jav-scraper scan /path/to/videos/ --no-recursive
```

支持的视频格式：`.mp4` `.mkv` `.avi` `.wmv` `.mov` `.m4v` `.ts` `.webm` `.flv` 等

支持的文件名格式：
- 标准：`FNS-215.mp4`、`FNS_215.mkv`、`MIDV-001.avi`
- FC2：`FC2-1234567.mp4`
- HEYZO：`HEYZO-1234.mp4`
- 1pondo：`061115_001.mp4`
- 含前缀：`[FALENO] FNS-215 美女と.mp4`

### 多引擎翻译（自动切换，全部免费）

| 引擎 | 优先级 | 特点 |
|------|--------|------|
| ① Google Translate | 首选 | 最稳定，无限制 |
| ② Google Translate (TW) | 自动降级 | 繁体中文备线 |
| ③ MyMemory Translator | 再降级 | 日限约5000字（无需 Key） |
| ④ PONS Translator | 最后备选 | 词典翻译，保证有结果 |

如果 Google 被限流或连不上，自动切到 MyMemory，再不行切 PONS，保证翻译不断。

### 输出文件命名

文件自动输出在视频同级目录：

| 文件 | 用途 | 示例 |
|------|------|------|
| `{番号}.nfo` | Kodi/Emby 元数据 | `FNS-215.nfo` |
| `{番号}.jpg` | 原始封面 | `FNS-215.jpg` |
| `{番号}-poster.jpg` | 竖版海报 | `FNS-215-poster.jpg` |
| `{番号}-fanart.jpg` | 横版背景 | `FNS-215-fanart.jpg` |
| `{番号}-thumb.jpg` | 缩略图 | `FNS-215-thumb.jpg` |
| `{番号}_screenshot_1~3.jpg` | 视频截图（25%/50%/75%处） | `FNS-215_screenshot_1.jpg` |

### 配套 VidHub / SenPlayer 使用

VidHub 和 SenPlayer 通过文件名自动匹配封面：

```
你的视频目录/
├── FNS-215.mp4           ← 视频文件
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
| `deep-translator` | ✅ 必须 | 免费多引擎翻译（Google→MyMemory→PONS） |
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

## 更新日志

### v0.1.0 (初始版本)
- 32 个数据源
- 免费 Google 翻译
- 视频截图
- 多源合并

### v0.2.0 (当前版本) 🆕
- **批量目录扫描** — `jav-scraper scan` 自动识别番号批量刮削
- **DMM/FANZA 源** — 官方 DMM 数据源
- **多引擎翻译** — Google → MyMemory → PONS 自动降级，全部免费
- 共 33 个数据源

---

## License

MIT
