<div align="center">

# intelligence

**把社交平台采集的内容变成结构化信号、趋势图谱和产品决策简报**

Chinese social media trend intelligence engine — normalizes XHS/Douyin exports into canonical schema, scores by keyword relevance + engagement strength, clusters into trend directions, and renders multi-format reports with an interactive dashboard.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-3776AB.svg?logo=python&logoColor=white)](https://python.org)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-138_passing-brightgreen.svg)]()
[![Dependencies](https://img.shields.io/badge/dependencies-0_(stdlib_only)-blue.svg)]()

</div>

---

## 痛点

从小红书、抖音等平台采集到大量内容后，数据散落在不同格式的 JSONL 文件中，无法直接用于趋势判断或产品决策：

- **格式混乱** — 每个平台的导出格式不同（MediaCrawler、抖音下载器、小红书下载器），字段命名和层级结构各异
- **无法量化** — 哪些帖子是真正的趋势信号？互动量高但关键词不相关的内容是噪音还是机会？
- **不可复现** — 手动整理一次就够累了，换个品类又要从头来过
- **缺少全景** — 单条帖子看不出方向，需要聚类才能发现趋势走向

## 解决方案

`intelligence` 是一个多品类趋势研究引擎，位于上游采集工具（MediaCrawler、抖音/小红书下载器）和最终决策之间。它将原始内容归一化为统一 schema，通过可配置的评分引擎打分，聚类成趋势方向，最终输出 JSON / Markdown / HTML 三种格式的决策报告和一个 5 页交互式看板。

品类研究逻辑通过 **Project Pack** 机制隔离 — 引擎通用，配置专属。

## 架构

```
                         intelligence 数据流
  ┌─────────────────────────────────────────────────────────────┐
  │                                                             │
  │   数据源 (.jsonl)                                           │
  │   ├── MediaCrawler 导出                                     │
  │   ├── 抖音下载器导出                                         │
  │   └── 小红书下载器导出                                       │
  │         │                                                   │
  │         ▼                                                   │
  │   ┌──────────┐    ┌──────────────┐    ┌──────────────┐     │
  │   │ Adapters  │───▶│ Scoring      │───▶│ Clustering   │     │
  │   │ 归一化    │    │ 70%关键词    │    │ 趋势方向聚类 │     │
  │   │          │    │ 30%互动量    │    │              │     │
  │   └──────────┘    └──────────────┘    └──────┬───────┘     │
  │                                              │              │
  │                    ┌─────────────────────────┤              │
  │                    ▼                         ▼              │
  │             ┌────────────┐          ┌──────────────┐       │
  │             │ Reports    │          │ Dashboard    │       │
  │             │ JSON/MD/   │          │ 5页交互式    │       │
  │             │ HTML       │          │ 静态看板     │       │
  │             └────────────┘          └──────────────┘       │
  │                                                             │
  └─────────────────────────────────────────────────────────────┘
```

## 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/zinan92/intelligence.git
cd intelligence
```

### 2. 安装（可选，直接运行也可以）

```bash
pip install -e .
```

> 零外部依赖 — 仅使用 Python 标准库，无需 `pip install` 任何第三方包。

### 3. 运行 Pipeline

```bash
# 使用内置示例数据
python3 -m intelligence run-pack jade --output-dir output/jade

# 或指定自己的采集文件
python3 -m intelligence run-pack designer_streetwear \
  --input examples/designer_streetwear/real_pilot/streetwear_collected.jsonl \
  --output-dir output/streetwear
```

### 4. 启动看板

```bash
python3 -m http.server 8765 --directory dashboard
# 浏览器打开 http://localhost:8765/
```

Pipeline 运行后会自动将 `frontend_dashboard.json` 复制到 `dashboard/data/`，看板即时反映最新数据。

## 功能一览

| 功能 | 说明 |
|------|------|
| 多源归一化 | MediaCrawler / 抖音 / 小红书三种导出格式统一为 `CanonicalSample` |
| 加权评分引擎 | 70% 关键词匹配 + 30% 互动量（点赞、收藏、评论、分享） |
| 趋势方向聚类 | 将高分信号自动聚类为趋势方向（Direction） |
| 多格式报告 | 同时输出 JSON / Markdown / HTML 三种报告 |
| 交互式看板 | 5 页静态 HTML 看板，中文界面，内联 SVG 图表 |
| Project Pack | 品类配置隔离，种子关键词 + YAML 配置即可定义新品类 |
| 零依赖 | 仅使用 Python 标准库，frozen dataclass 保证数据不可变 |

## CLI 命令

### `run-pack` — 运行品类研究 Pipeline

```bash
python3 -m intelligence run-pack <pack> --output-dir <dir> [--input <file.jsonl>]
```

| 参数 | 必填 | 说明 |
|------|------|------|
| `pack` | 是 | Pack 名称：`jade` 或 `designer_streetwear` |
| `--output-dir` | 是 | 输出目录路径 |
| `--input` | 否 | JSONL 输入文件路径，省略则使用内置 fixture |

每次运行产出 7 个文件：

| 文件 | 说明 |
|------|------|
| `normalized_samples.json` | 归一化后的帖子（含互动、作者、媒体字段） |
| `scored_samples.json` | 带分桶评分的帖子 |
| `dashboard.json` | 聚合看板数据（后端格式） |
| `frontend_dashboard.json` | 前端看板消费的 JSON |
| `report.json` | 压缩摘要（Report 模型） |
| `report.md` | Markdown 报告 |
| `report.html` | HTML 报告 |

### `validate-pack` — 校验品类配置

```bash
python3 -m intelligence validate-pack <pack>
```

校验 Pack 目录结构、配置文件、种子关键词是否完整且合规。

### `--version` — 查看版本

```bash
python3 -m intelligence --version
```

## 看板页面

| 页面 | 文件 | 用途 |
|------|------|------|
| 首页 | `index.html` | 信号总览 — 趋势运动、判断摘要、观察清单、风险提示 |
| 方向地图 | `direction-map.html` | 可排序/筛选的方向对比表 |
| 方向详情 | `direction-detail.html` | 单个趋势方向的深度分析 |
| 产品线观察 | `product-line.html` | 按产品线维度的市场视图 |
| 证据库 | `evidence.html` | 三栏证据浏览器，含筛选和统计 |

## 技术栈

| 层级 | 技术 | 用途 |
|------|------|------|
| 语言 | Python 3.10+ | 核心运行时 |
| 数据模型 | `dataclasses` (frozen, slots) | 不可变 canonical schema |
| 序列化 | 标准库 `json` | JSONL 读取 / JSON 输出 |
| 模板 | `string.Template` | HTML 报告渲染 |
| 构建 | 自定义 PEP 517 build backend | 零外部依赖打包 |
| 前端 | 原生 HTML / CSS / JS | 5 页静态看板，内联 SVG 图表 |
| 测试 | pytest | 138 tests |

**零外部运行时依赖** — 仅使用 Python 标准库。测试时需要 `pytest`。

## 项目结构

```
intelligence/
├── src/intelligence/
│   ├── adapters/              # XHS / Douyin / MediaCrawler 归一化器
│   │   ├── mediacrawler.py
│   │   ├── xhs_downloader.py
│   │   └── douyin_downloader.py
│   ├── scoring/               # 加权评分引擎
│   │   ├── engine.py          # ScoringEngine + ScoringConfig
│   │   └── engagement_buckets.py
│   ├── analysis/              # 聚类 + 前端数据构建
│   │   ├── direction_clustering.py
│   │   └── frontend_builder.py
│   ├── workflows/             # Pipeline 编排
│   │   ├── pack_runner.py     # 通用 run-pack 流程
│   │   ├── jade_pack.py       # 翡翠 PackSpec
│   │   └── streetwear_pack.py # 潮牌 PackSpec
│   ├── reporting/             # 报告生成（JSON / MD / HTML）
│   ├── schema/                # Canonical 数据模型
│   │   └── canonical.py       # CanonicalSample 及子结构
│   ├── projects/              # Pack 定义
│   │   ├── jade/              # 翡翠趋势 pack
│   │   └── designer_streetwear/ # 潮牌街头 pack
│   ├── cli.py                 # CLI 入口
│   └── __main__.py
├── dashboard/                 # 5 页静态 HTML 看板（中文）
│   ├── index.html
│   ├── direction-map.html
│   ├── direction-detail.html
│   ├── product-line.html
│   ├── evidence.html
│   ├── data/                  # frontend_dashboard.json（自动生成）
│   ├── css/
│   └── js/
├── tests/                     # 138 unit + integration tests
├── examples/                  # 示例输入和预生成输出
│   ├── jade/
│   └── designer_streetwear/
├── docs/
├── pyproject.toml
└── build_backend.py           # 自定义 PEP 517 构建后端
```

## 配置

### Project Pack YAML

每个品类是一个 Pack 目录，通过 `discover_project_pack("jade")` 自动发现和校验：

```
projects/jade/
├── config/project.yaml        # 品类配置
├── keywords/seed_keywords.csv # 种子关键词
└── templates/                 # 报告模板（Markdown）
```

**project.yaml** 示例：

```yaml
name: jade
domain: xiaohongshu
purpose: jade_trend_research
contract:
  config: config/project.yaml
  keywords: keywords/seed_keywords.csv
  templates: templates/
  examples: optional
keyword_groups:
  - jade_basics
  - modern_jade_design
  - material_combination
  - style_and_scene
  - price_and_gifting
  - adjacent_categories
```

### 种子关键词 CSV

`seed_keywords.csv` 定义每个分组的关键词，评分引擎根据命中情况计算关键词得分。

### 评分权重

评分使用 70/30 关键词-互动量权重分配。互动量分桶（`interaction_strength`、`commercial_intent`、`propagation_velocity`）从社交互动数据（点赞、收藏、评论、分享）推导。

### 添加新 Pack

详见 [docs/adding-a-pack.md](docs/adding-a-pack.md)。

## Project Packs

| Pack | 品类 | 评分分桶 |
|------|------|----------|
| `jade` | 翡翠珠宝趋势 | jade_signal, modernity, commerce, interaction_strength, commercial_intent, propagation_velocity |
| `designer_streetwear` | 潮牌街头趋势 | silhouette, graphic, layering, brand, material, commerce, interaction_strength, commercial_intent, propagation_velocity |

## 测试

```bash
python3 -m pytest tests/ -x -q    # 138 tests, all passing
```

## For AI Agents

本节面向需要将此项目作为工具或依赖集成的 AI Agent。

### 结构化元数据

```yaml
name: intelligence
type: cli-tool
version: 0.1.0
description: >
  Multi-category trend research engine that normalizes Chinese social media
  content (XHS/Douyin) into scored signals, trend directions, and decision
  reports. Zero runtime dependencies.
source: https://github.com/zinan92/intelligence
language: python
python_requires: ">=3.10"
dependencies: []
install_command: pip install -e .
health_check: python3 -m intelligence --version

cli:
  entrypoint: python3 -m intelligence
  commands:
    run-pack:
      description: Run a category research pipeline
      args:
        pack:
          type: string
          required: true
          choices: [jade, designer_streetwear]
        --input:
          type: path
          required: false
          description: JSONL input file (falls back to built-in fixture)
        --output-dir:
          type: path
          required: true
          description: Directory for generated outputs
    validate-pack:
      description: Validate a project pack's assets
      args:
        pack:
          type: string
          required: true

input_format: JSONL (one JSON object per line, MediaCrawler/XHS/Douyin export)
output_files:
  - normalized_samples.json
  - scored_samples.json
  - dashboard.json
  - frontend_dashboard.json
  - report.json
  - report.md
  - report.html

capabilities:
  - Normalize social media content from MediaCrawler, Douyin, XHS into canonical schema
  - Score samples using configurable weighted bucket engine (70% keyword + 30% engagement)
  - Cluster scored signals into trend directions
  - Generate decision reports in JSON, Markdown, and HTML
  - Build interactive 5-page dashboard data
  - Discover and validate project packs for category-specific research
```

### Agent 调用示例（CLI）

```bash
# Step 1: 运行 pipeline
python3 -m intelligence run-pack jade --output-dir /tmp/intel-output

# Step 2: 读取关键输出
cat /tmp/intel-output/report.json      # 结构化报告
cat /tmp/intel-output/scored_samples.json  # 评分后样本
```

### Agent 调用示例（Python）

```python
import subprocess
import json
from pathlib import Path

def run_intelligence(pack: str = "jade") -> dict:
    """运行研究引擎并解析输出。"""
    output_dir = Path("/tmp/intelligence-output")
    output_dir.mkdir(exist_ok=True)

    result = subprocess.run(
        ["python3", "-m", "intelligence", "run-pack", pack,
         "--output-dir", str(output_dir)],
        capture_output=True, text=True
    )
    assert result.returncode == 0, f"Pipeline failed: {result.stderr}"

    scored = json.loads((output_dir / "scored_samples.json").read_text())
    report = json.loads((output_dir / "report.json").read_text())

    return {"scored_samples": scored, "report": report}
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

## License

MIT
