<div align="center">

# intelligence

**把社交平台采集的内容变成结构化信号、趋势图谱和产品决策简报**

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-Proprietary-red.svg)](LICENSE)

</div>

---

## 痛点

从小红书、抖音等平台采集到大量内容后，数据散落在不同格式的 JSONL 文件中，无法直接用于趋势判断或产品决策。手动整理耗时且不可复现，不同品类的研究逻辑又各不相同，难以沉淀为可复用的分析框架。

## Project Packs

| Pack | Category | Scoring buckets |
|------|----------|-----------------|
| `jade` | Jade jewelry trends | jade_signal, modernity, commerce |
| `designer_streetwear` | Streetwear / apparel trends | silhouette, graphic, layering, brand, material, commerce |

## 解决方案

`intelligence` 是一个多品类研究引擎，位于采集工具（MediaCrawler、抖音/小红书下载器）和最终展示层之间。它将上游采集的原始内容归一化为统一 schema，通过可配置的评分引擎打分，最终输出 JSON / Markdown / HTML 三种格式的决策报告。品类研究逻辑通过 **Project Pack** 机制隔离——引擎通用，配置专属。

## 架构

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  采集工具        │     │  intelligence    │     │  输出层          │
│  MediaCrawler    │────▶│                 │────▶│  JSON / MD / HTML│
│  抖音 Downloader │     │  Adapters       │     │  决策报告         │
│  小红书 Downloader│     │  → Schema       │     └─────────────────┘
└─────────────────┘     │  → Scoring      │
                        │  → Reporting    │
                        └────────┬────────┘
                                 │
                        ┌────────▼────────┐
                        │  Project Packs   │
                        │  jade / ...      │
                        │  config + 关键词  │
                        │  + 模板 + 示例    │
                        └─────────────────┘
```

## 快速开始

```bash
# 1. 克隆仓库
git clone https://github.com/zinan92/intelligence.git
cd intelligence

# 2. 安装（开发模式，零外部依赖）
pip install -e .

# 3. 运行 jade pack demo（使用内置 fixture 数据）
intelligence run-pack jade --output-dir /tmp/jade-demo

# 4. 查看输出
ls /tmp/jade-demo/
# → normalized_samples.json  scored_samples.json  report.json  report.md  report.html
```

## 功能一览

| 功能 | 说明 | 状态 |
|------|------|------|
| 多源适配器 | MediaCrawler / 抖音 / 小红书 JSONL → 统一 schema | ✅ 已完成 |
| Canonical Schema | 不可变数据类，provenance + content 分离 | ✅ 已完成 |
| 评分引擎 | 加权桶评分 + 置信度/分类规则，品类无关 | ✅ 已完成 |
| 多格式报告 | JSON / Markdown / HTML 三种渲染器 | ✅ 已完成 |
| Project Pack | 按品类组织 config、关键词、模板、示例 | ✅ 已完成 |
| Pack 发现机制 | 自动扫描并校验 pack 目录结构 | ✅ 已完成 |
| 审核状态 | ReviewState / ValidationState 独立于评分 | ✅ 已完成 |
| Workflow 编排 | ingest → normalize → score → validate → report | 🔧 占位中 |

## 核心概念

### Canonical Schema

所有采集数据归一化为 `CanonicalSample`，由两部分组成：

- **`CanonicalProvenance`** — 来源元数据（平台、ID、URL、时间戳、原始字段）
- **`CanonicalContent`** — 内容本体（标题、正文、摘要、标签）

所有 dataclass 均为 `frozen=True`，确保不可变。

### Scoring Engine

品类无关的加权评分引擎：

```python
ScoringConfig(
    bucket_weights={"jade_signal": 0.5, "modernity": 0.25, "commerce": 0.25},
    confidence_rules=(ConfidenceRule(0.8, "high"), ConfidenceRule(0.5, "medium")),
    classification_rules=(ClassificationRule(0.8, "confirmed"), ClassificationRule(0.6, "emerging")),
)
```

输出 `ScoringResult`：加权分数 + 置信度标签 + 分类标签。

## Dashboard prototype — 翡翠信号图谱

A high-fidelity Chinese dashboard prototype lives in `dashboard/`. This is the business-owner-facing signal product surface, separate from the compact evaluation reports.

```bash
# View the dashboard
python3 -m http.server 8765 --directory dashboard
# Open http://localhost:8765/ in your browser
```

**Pages:**
- **首页** — Executive signal dashboard with 7 modules (movement board, judgment summary, watchlist, risk alerts, evidence feed, product line snapshot, 14-day change)
- **方向地图** — Sortable/filterable direction comparison table
- **方向详情** — Deep-dive on a specific trend direction with product-line decision cards
- **产品线观察** — Market view by product line (which directions help/hurt each line)
- **证据库** — 3-panel evidence exploration with filters

The prototype uses local mock data (`dashboard/data/jade_dashboard.json`) with jade as the first content case. See `dashboard/README.md` for details.

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

## 技术栈

| 层级 | 技术 | 用途 |
|------|------|------|
| 语言 | Python 3.10+ | 核心运行时 |
| 数据模型 | dataclasses (frozen) | 不可变 schema |
| 序列化 | 标准库 json | JSONL 读取 / JSON 输出 |
| 模板 | string.Template | HTML 报告渲染 |
| 构建 | 自定义 build backend | 零外部依赖打包 |
| 测试 | pytest | 730 行测试覆盖 |

**零外部依赖** — 仅使用 Python 标准库。

## 项目结构

```
intelligence/
├── src/intelligence/
│   ├── adapters/             # 采集工具输出适配器
│   │   ├── _common.py        #   共享 JSONL 读取 + sample 构建
│   │   ├── mediacrawler.py   #   MediaCrawler 适配
│   │   ├── douyin_downloader.py  # 抖音适配
│   │   └── xhs_downloader.py    # 小红书适配
│   ├── schema/               # 数据模型
│   │   ├── canonical.py      #   CanonicalSample / Provenance / Content
│   │   └── review.py         #   ReviewState / ValidationState
│   ├── scoring/              # 评分引擎
│   │   └── engine.py         #   ScoringEngine + Config + Result
│   ├── reporting/            # 报告生成
│   │   ├── model.py          #   Report / ReportBlock 数据模型
│   │   ├── json_report.py    #   JSON 渲染
│   │   ├── markdown_report.py #  Markdown 渲染
│   │   └── html_report.py    #   HTML 渲染
│   ├── projects/             # Project Pack 目录
│   │   └── jade/             #   第一个品类 pack
│   ├── workflows/            # 工作流编排（占位中）
│   └── cli.py                # CLI 入口
├── tests/                    # pytest 测试
├── docs/                     # 架构文档 + 案例研究
├── examples/                 # 使用示例
└── pyproject.toml
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
