# JAV Scraper Pro

Multi-source JAV (Japanese Adult Video) metadata scraper. Scrapes metadata from multiple JAV database websites, merges results, generates Kodi/Emby-compatible NFO files, processes images, and extracts video screenshots.

## Features

- **Multi-source scraping**: OneJAV, JavDB, JavBus, FALENO, AVSOX, AVSEX, JavLibrary
- **Merge & fallback**: Combine results from all sources or fall back in priority order
- **NFO generation**: Kodi/Emby/Jellyfin-compatible XML metadata files
- **Image processing**: Poster cropping, fanart generation, thumbnail creation
- **Video processing**: ffmpeg screenshot extraction and grid montages
- **Translation**: DeepSeek LLM-powered Japanese-to-Chinese/English translation
- **CLI interface**: Full command-line tool with JSON output support

## Installation

### From source

```bash
git clone https://github.com/yourusername/jav-scraper-pro.git
cd jav-scraper-pro
pip install -e .
```

### Dependencies

```
requests>=2.31.0
pillow>=10.0.0      # Optional: for image processing
openai>=1.0.0        # Optional: for DeepSeek translation
ffmpeg               # Optional: for video screenshot extraction
```

## Usage

### Scrape a JAV number

```bash
# Basic scrape (fallback mode)
jav-scraper scrape FNS-215

# Scrape with merge from all sources
jav-scraper scrape FNS-215 --merge

# JSON output
jav-scraper scrape FNS-215 --json

# Translate titles via DeepSeek
jav-scraper scrape FNS-215 --translate

# Scrape multiple numbers
jav-scraper scrape FNS-215 MIDV-001
```

### Generate NFO file

```bash
# Generate NFO for a JAV number
jav-scraper nfo FNS-215

# Custom output path
jav-scraper nfo FNS-215 --output /path/to/FNS-215.nfo

# With translation and merge
jav-scraper nfo FNS-215 --merge --translate
```

### List sources

```bash
jav-scraper sources
```

### Translate a title

```bash
jav-scraper translate "完全主観で誘惑してくる美脚ナースの卑猥な治療"
jav-scraper translate "完全主観で誘惑してくる美脚ナースの卑猥な治療" --target english
```

### Process images

```bash
# Generate poster (crops cover, defaults to right half)
jav-scraper image poster --url https://example.com/cover.jpg --output poster.jpg

# Generate fanart background (with blur)
jav-scraper image fanart --url https://example.com/cover.jpg --output fanart.jpg --blur

# Generate thumbnail
jav-scraper image thumb --url https://example.com/cover.jpg --output thumb.jpg
```

### Extract video screenshots

```bash
# Single screenshot at 30 seconds
jav-scraper video video.mp4 --output screenshot.jpg

# Screenshot at custom time
jav-scraper video video.mp4 --output shot.jpg --time 60

# Grid of screenshots
jav-scraper video video.mp4 --output grid.jpg --grid
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DEEPSEEK_API_KEY` | DeepSeek API key for translation | — |
| `OPENAI_API_KEY` | Fallback API key | — |
| `DEEPSEEK_BASE_URL` | DeepSeek API base URL | `https://api.deepseek.com` |
| `DEEPSEEK_MODEL` | DeepSeek model name | `deepseek-chat` |

## Project Structure

```
jav-scraper-pro/
├── jav_scraper/
│   ├── __init__.py           # Package init, version
│   ├── metadata.py           # JavMetadata & Actor dataclasses
│   ├── http_client.py        # HTTP session with retry
│   ├── sources/
│   │   ├── __init__.py       # Source registry
│   │   ├── onejav.py         # OneJAV scraper
│   │   ├── javdb.py          # JavDB scraper
│   │   ├── javbus.py         # JavBus scraper
│   │   ├── faleno.py         # FALENO official scraper
│   │   ├── avsox.py          # AVSOX scraper
│   │   ├── avsex.py          # AVSEX scraper
│   │   └── javlibrary.py     # JavLibrary scraper
│   ├── orchestrator.py       # Multi-source merge + fallback
│   ├── translator.py         # DeepSeek LLM translation
│   ├── image_processor.py    # Poster/fanart/thumb generation
│   ├── video_processor.py    # ffmpeg screenshots
│   ├── nfo_generator.py      # Kodi/Emby NFO builder
│   └── cli.py                # Command-line interface
├── setup.py                  # Package setup
├── requirements.txt          # Dependencies
├── .gitignore
└── README.md
```

## Comparison with MDCx

| 特性 | JAV Scraper Pro | MDCx |
|------|----------------|------|
| **数据源** | 7个（OneJAV/JavDB/JavBus/Faleno/AVSOX/AVSEX/JavLibrary） | 40+（含FC2/国产/独立站/Getchu等） |
| **语言** | Python CLI | Python + PyQt5 GUI |
| **翻译** | DeepSeek LLM | DeepL + YouDao + OpenAI LLM |
| **视频截图** | ✅ ffmpeg | ✅ |
| **批量处理** | CLI 循环 | GUI 批量选择 |
| **Docker 部署** | ❌ | ✅ FastAPI + Docker |
| **NFO 格式** | Kodi/Emby 兼容 XML | Kodi/Emby 兼容 XML（可自定义模板） |
| **图片裁切** | left/center/right | 自适应比例裁切 |
| **文件重命名** | ❌（需手动） | ✅ 模板命名系统 |
| **演员头像** | ✅ 部分源支持 | ✅ 多数源支持 |
| **多源合并** | ✅ 优先级fallback | ✅ 自动 |

**MDCx 能做但我们还没做的：**
- FC2 / 国产 / 独立工作室等 30+ 额外数据源
- 文件自动重命名与整理
- NFO 模板自定义
- Docker 部署 / FastAPI 接口
- GUI 批量操作

### 数据源对照

| 源 | JAV Scraper Pro | MDCx |
|----|----------------|------|
| OneJAV | ✅ | ❌ |
| JavDB | ✅ | ✅ |
| JavBus | ✅ | ✅ |
| FALENO | ✅ | ✅ |
| AVSOX | ✅ | ✅ |
| AVSEX | ✅ | ✅ |
| JavLibrary | ✅ | ✅ |
| DMM/FANZA | ❌ | ✅ |
| MGStage | ❌ | ✅ |
| Prestige | ❌ | ✅ |
| FC2/FC2Club/FC2Hub/FC2PPVDB | ❌ | ✅ |
| ThePornDB | ❌ | ✅ |
| 国产（麻豆/91等） | ❌ | ✅ |
| CableAV/CNMDB/iQqtv等 | ❌ | ✅ |

## License

MIT
