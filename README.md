<div align="center">

# intelligence

**把社交平台采集的内容变成结构化信号、趋势图谱和产品决策简报**

Chinese social media intelligence pipeline and dashboard. Crawls platforms (XHS, Douyin), scores posts by keyword relevance + engagement strength, clusters results into trend directions, and renders a 5-page interactive dashboard — all with zero external dependencies.

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-Proprietary-red.svg)](LICENSE)

</div>

---

## 痛点

从小红书、抖音等平台采集到大量内容后，数据散落在不同格式的 JSONL 文件中，无法直接用于趋势判断或产品决策。手动整理耗时且不可复现，不同品类的研究逻辑又各不相同，难以沉淀为可复用的分析框架。

## Project Packs

| Pack | Category | Scoring buckets |
|------|----------|-----------------|
| `jade` | Jade jewelry trends | jade_signal, modernity, commerce, interaction_strength, commercial_intent, propagation_velocity |
| `designer_streetwear` | Streetwear / apparel trends | silhouette, graphic, layering, brand, material, commerce, interaction_strength, commercial_intent, propagation_velocity |

Scoring uses a 70/30 keyword-to-engagement weight split. Engagement buckets (`interaction_strength`, `commercial_intent`, `propagation_velocity`) are derived from parsed social engagement data (likes, saves, comments, shares).

## 解决方案

`intelligence` 是一个多品类研究引擎，位于采集工具（MediaCrawler、抖音/小红书下载器）和最终展示层之间。它将上游采集的原始内容归一化为统一 schema，通过可配置的评分引擎打分，最终输出 JSON / Markdown / HTML 三种格式的决策报告。品类研究逻辑通过 **Project Pack** 机制隔离——引擎通用，配置专属。

## 架构

```
Collected posts (.jsonl)
  → Adapters (normalize XHS/Douyin schemas)
  → Scoring (70% keyword + 30% engagement)
  → Clustering (group into trend directions)
  → Pipeline JSON outputs
  → frontend_dashboard.json → Dashboard (static HTML/CSS/JS)
```

**Pipeline** (`src/intelligence/`): adapters → scoring → analysis → workflows → reporting.
Stdlib-only Python — no pip dependencies required at runtime.

**Dashboard** (`dashboard/`): 5 static HTML pages with vanilla JS and inline SVG charts (area charts, bubble matrix, judgment donut, product-line comparison). All UI text is in Chinese.

| Page | Purpose |
|------|---------|
| 首页 (`index.html`) | Executive signal dashboard — movements, judgment, watchlist, risk alerts |
| 方向地图 (`direction-map.html`) | Sortable/filterable direction comparison table |
| 方向详情 (`direction-detail.html`) | Deep-dive on a single trend direction |
| 产品线观察 (`product-line.html`) | Market view by product line |
| 证据库 (`evidence.html`) | 3-panel evidence browser with filters and statistics |

## 快速开始

### Run the pipeline

```bash
python3 -m intelligence run-pack designer_streetwear \
  --input examples/designer_streetwear/real_pilot/streetwear_collected.jsonl \
  --output-dir output/streetwear
```

### Serve the dashboard

```bash
python3 -m http.server 8765 --directory dashboard
# Open http://localhost:8765/
```

The pipeline copies `frontend_dashboard.json` into `dashboard/data/` automatically, so the dashboard reflects the latest run.

## Pipeline output files

Each run produces 7 files:

| File | Description |
|------|-------------|
| `normalized_samples.json` | Posts in canonical form with engagement, creator, media fields |
| `scored_samples.json` | Posts with keyword + engagement bucket scores |
| `dashboard.json` | Aggregated dashboard data (backend format) |
| `frontend_dashboard.json` | Dashboard-ready JSON consumed by the HTML frontend |
| `report.json` | Compressed summary (Report model) |
| `report.md` | Markdown report |
| `report.html` | HTML report |

## Testing

### Project Pack

每个品类是一个 pack 目录，包含：

```
projects/jade/
├── config/project.yaml      # 品类配置（domain、purpose、关键词分组）
├── keywords/seed_keywords.csv # 种子关键词
├── templates/                # 报告模板（Markdown）
└── examples/                 # 可选示例
```

Pack 通过 `discover_project_pack("jade")` 自动发现和校验。

## Testing

```bash
python3 -m pytest tests/ -x -q    # 138 tests, all passing
```

## 技术栈

| 层级 | 技术 | 用途 |
|------|------|------|
| 语言 | Python 3.10+ | 核心运行时 |
| 数据模型 | dataclasses (frozen) | 不可变 schema |
| 序列化 | 标准库 json | JSONL 读取 / JSON 输出 |
| 模板 | string.Template | HTML 报告渲染 |
| 构建 | 自定义 build backend | 零外部依赖打包 |
| 测试 | pytest | 138 tests |

**零外部依赖** — 仅使用 Python 标准库。

## Key directories

```
src/intelligence/
  adapters/       # XHS/Douyin normalizers
  scoring/        # Keyword + engagement scoring
  analysis/       # Clustering, trend direction extraction
  workflows/      # Pipeline orchestration
  reporting/      # Report and dashboard generation
  projects/       # Pack definitions (jade, designer_streetwear)
  schema/         # Shared data models
dashboard/
  data/           # frontend_dashboard.json (auto-generated)
  css/ js/        # Shared styles and scripts
tests/            # 138 unit + integration tests
examples/         # Sample inputs and pre-generated outputs
```

## For AI Agents

本节面向需要将此项目作为工具或依赖集成的 AI Agent。

### 结构化元数据

```yaml
name: intelligence
description: Multi-category research engine that normalizes social content into scored signals and decision reports
version: 0.1.0
cli_command: intelligence
cli_args:
  - name: command
    type: string
    required: true
    description: "子命令 (run-pack)"
  - name: pack
    type: string
    required: true
    description: "Project pack 名称 (jade)"
cli_flags:
  - name: --output-dir
    type: string
    required: true
    description: "输出目录路径"
install_command: pip install -e .
health_check: intelligence --version
dependencies: []
capabilities:
  - "normalize social media content from MediaCrawler, Douyin, and XHS into canonical schema"
  - "score normalized samples using configurable weighted bucket engine"
  - "generate decision reports in JSON, Markdown, and HTML formats"
  - "discover and validate project packs for category-specific research"
input_format: JSONL (one JSON object per line)
output_format: JSON, Markdown, HTML reports
```

### Agent 调用示例

```python
import subprocess
import json
from pathlib import Path

async def research_pipeline(pack: str = "jade"):
    """运行研究引擎并解析输出"""
    output_dir = Path("/tmp/intelligence-output")

    # Step 1: 运行 pack
    result = subprocess.run(
        ["intelligence", "run-pack", pack, "--output-dir", str(output_dir)],
        capture_output=True, text=True
    )
    assert result.returncode == 0, f"Failed: {result.stderr}"

    # Step 2: 读取评分结果
    scored = json.loads((output_dir / "scored_samples.json").read_text())
    top_signals = [s for s in scored if s["confidence"] in ("high", "medium")]

    # Step 3: 读取报告
    report = json.loads((output_dir / "report.json").read_text())
    return {"top_signals": top_signals, "report": report}
```

### Python API 调用

```python
from intelligence.adapters.mediacrawler import load_samples
from intelligence.scoring.engine import ScoringEngine, ScoringConfig

# 加载 + 归一化
samples = load_samples("path/to/export.jsonl")

# 评分
engine = ScoringEngine(ScoringConfig(
    bucket_weights={"signal_a": 0.6, "signal_b": 0.4},
    confidence_rules=(...),
    classification_rules=(...),
))
results = [engine.score(compute_buckets(s)) for s in samples]
```

## 相关项目

| 项目 | 说明 | 链接 |
|------|------|------|
| MediaCrawler | 小红书/抖音等平台的采集引擎（上游数据源） | — |
| quant-data-pipeline | 量化数据管道（同生态系统） | [GitHub](https://github.com/zinan92/quant-data-pipeline) |
| qualitative-data-pipeline | 定性数据管道（同生态系统） | [GitHub](https://github.com/zinan92/qualitative-data-pipeline) |

## Adding a new pack

See [docs/adding-a-pack.md](docs/adding-a-pack.md) for the full pack authoring contract.

## License

Proprietary
