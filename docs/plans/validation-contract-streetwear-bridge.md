# Validation Contract: Streetwear Intelligence → Dashboard Bridge

**Mission:** Bridge the designer_streetwear intelligence pipeline to the Jade Signal Atlas frontend dashboard using 293 real XHS streetwear posts.

**Date:** 2026-03-27
**Data source:** `examples/designer_streetwear/real_pilot/streetwear_collected.jsonl` (293 posts)
**Pipeline:** `designer_streetwear` pack → new direction clustering layer → `frontend_dashboard.json`
**Frontend:** `dashboard/` (static HTML/CSS/JS, 5 pages, pure SVG/CSS charts)

---

## Area 1: Direction Clustering (Pipeline)

### VAL-BRIDGE-001 — Post-to-Direction Grouping Produces 6–10 Directions

**Title:** Direction clustering yields between 6 and 10 trend directions from 293 posts.

**Behavioral Description:** When the streetwear pack runs the direction clustering step against all 293 scored posts, the output contains a `trend_directions` array with 6 ≤ N ≤ 10 entries. Each entry represents a coherent trend direction derived from keyword/tag clustering on real post data.

**Evidence Requirements:**
- Run pipeline end-to-end with `streetwear_collected.jsonl` (293 posts).
- Assert `len(output["trend_directions"])` is in range `[6, 10]`.
- Visually inspect direction names for coherence (no duplicates, no empty names).

---

### VAL-BRIDGE-002 — Direction Schema Completeness

**Title:** Each direction has all required fields: display name, aggregate score, confidence, judgment state, top tags, member post count.

**Behavioral Description:** Every entry in `trend_directions` includes at minimum: `id` (string), `name` (non-empty string), `heat` (numeric, 0–100), `confidence_level` (one of: 高/中/低), `judgment_state` (one of: 值得跟/观察中/短热噪音/需要补证据), top tags (list, ≥1 item), and `member_post_count` (integer ≥ 1).

**Evidence Requirements:**
- JSON schema validation on each direction entry in output.
- Assert every required field is present and non-null.
- Assert `judgment_state` is one of the four allowed values.
- Assert `confidence_level` is one of the three allowed values.
- Assert `name` is a non-empty string.
- Assert `heat` is numeric and in `[0, 100]`.
- Assert `member_post_count` ≥ 1 for every direction.

---

### VAL-BRIDGE-003 — Multi-Keyword Posts Are Not Lost

**Title:** Posts matching keywords from multiple directions are assigned, not dropped.

**Behavioral Description:** If a post's text/tags match keyword sets for multiple directions (e.g., a post about "oversized graphic tee" matches both silhouette and graphic directions), the post appears as a member of at least one direction. No scored post is orphaned—i.e., the total sum of `member_post_count` across directions is ≥ 293, and every post ID appears in at least one direction's membership.

**Evidence Requirements:**
- Collect all post IDs from `scored_samples`.
- Collect all post IDs referenced by all directions' member lists.
- Assert the union of direction member lists covers 100% of scored posts.
- Assert `sum(d["member_post_count"] for d in trend_directions) >= 293`.

---

### VAL-BRIDGE-004 — Directions Ranked by Aggregate Score

**Title:** Directions in the output are sorted descending by aggregate heat score.

**Behavioral Description:** The `trend_directions` array is ordered such that `trend_directions[i]["heat"] >= trend_directions[i+1]["heat"]` for all consecutive pairs. The highest-signal direction appears first.

**Evidence Requirements:**
- Parse `trend_directions` array from output JSON.
- Assert strict non-increasing order of `heat` values.
- Run on 293-post dataset and verify ordering holds.

---

## Area 2: Dashboard JSON Generation (Pipeline)

### VAL-BRIDGE-010 — Frontend-Compatible JSON Generated

**Title:** Pipeline produces a `frontend_dashboard.json` file matching the `jade_dashboard.json` schema.

**Behavioral Description:** After running the full pipeline, a file named `frontend_dashboard.json` is written to the output directory. Its top-level structure matches the schema of `dashboard/data/jade_dashboard.json`: keys include `product_name`, `timestamp`, `executive_summary`, `today_judgments`, `trend_directions`, `product_lines`, `evidence_entries`, `fourteen_day_changes`.

**Evidence Requirements:**
- Assert file `frontend_dashboard.json` exists in output directory.
- Assert all required top-level keys are present: `product_name`, `timestamp`, `executive_summary`, `today_judgments`, `trend_directions`, `product_lines`, `evidence_entries`, `fourteen_day_changes`.
- Validate against the existing `jade_dashboard.json` schema by comparing key structures (not values).

---

### VAL-BRIDGE-011 — trend_directions Array Has All Required Fields

**Title:** Each trend direction in the JSON has all dashboard-required fields.

**Behavioral Description:** Every entry in `trend_directions` contains at minimum: `id`, `name`, `description`, `heat_magnitude`, `time_window`, `confidence_level`, `classification`, `judgment_state`, `audience_fit`, `price_band_fit`, `opportunity` (0–100), `risk` (0–100), `heat` (0–100), `movement_history` (array of 14 numbers), `product_line_breakdown` (object), `risks` (array), `evidence_summary`, `proof_snapshot`, `one_line_recommendation`, `content_cues`, `why_it_matters`, `freshness`.

**Evidence Requirements:**
- For each direction in the output, assert all fields listed above are present and non-null.
- Assert `movement_history` is an array of exactly 14 numeric values.
- Assert `opportunity` and `risk` are integers in `[0, 100]`.
- Assert `product_line_breakdown` is an object with ≥ 1 product line key.
- Assert `risks` is an array (may be empty, but present).

---

### VAL-BRIDGE-012 — product_lines Array With Strengthening/Weakening

**Title:** JSON includes a `product_lines` array with direction linkages.

**Behavioral Description:** The output JSON contains a `product_lines` array. Each product line entry has: `name`, `status`, `opportunity_level`, `risk_level`, `strengthening_directions` (array of direction IDs/names that boost this product line), `weakening_directions` (array of direction IDs/names that reduce this product line's outlook).

**Evidence Requirements:**
- Assert `product_lines` is an array with ≥ 1 entry.
- For each product line, assert `name`, `status`, `opportunity_level`, `risk_level` are present.
- Assert `strengthening_directions` and `weakening_directions` are arrays (may be empty).
- Assert all direction IDs referenced in `strengthening_directions` / `weakening_directions` correspond to actual entries in `trend_directions`.

---

### VAL-BRIDGE-013 — Evidence Entries Linked to Directions

**Title:** JSON includes `evidence_entries` array with direction linkage.

**Behavioral Description:** The output JSON contains an `evidence_entries` array. Each evidence entry has: `id`, `type` (笔记/图片/评论/视频), `title`, `direction_id` (referencing a valid direction in `trend_directions`), `freshness`, `relevance_weight`.

**Evidence Requirements:**
- Assert `evidence_entries` is an array with ≥ 1 entry.
- For each entry, assert `id`, `type`, `title`, `direction_id` are present.
- Assert every `direction_id` in evidence entries maps to a valid `id` in `trend_directions`.
- Assert at least 50% of directions have ≥ 1 linked evidence entry.

---

### VAL-BRIDGE-014 — Judgment Summary and 14-Day Changes Present

**Title:** JSON includes `today_judgments`, `fourteen_day_changes`, and `executive_summary`.

**Behavioral Description:** The output JSON contains:
- `today_judgments`: an object with keys for each judgment state (值得跟, 观察中, 短热噪音, 需要补证据) and integer count values that sum to the total number of directions.
- `fourteen_day_changes`: an object with `warming` (array), `cooling` (array), `new_appearances` (array).
- `executive_summary`: an object with `one_line`, `key_opportunity`, `key_risk` (all non-empty strings).

**Evidence Requirements:**
- Assert `today_judgments` keys match the four judgment states exactly.
- Assert `sum(today_judgments.values()) == len(trend_directions)`.
- Assert `fourteen_day_changes` has `warming`, `cooling`, `new_appearances` arrays.
- Assert `executive_summary` has `one_line`, `key_opportunity`, `key_risk` as non-empty strings.

---

### VAL-BRIDGE-015 — Existing 6 Output Files Still Generated

**Title:** All 6 original output files are still produced alongside the new frontend JSON.

**Behavioral Description:** Running the streetwear pack still produces: `normalized_samples.json`, `scored_samples.json`, `report.json`, `report.md`, `report.html`, `dashboard.json`. The new `frontend_dashboard.json` is an additional 7th file, not a replacement.

**Evidence Requirements:**
- Run pipeline end-to-end.
- Assert all 7 files exist in the output directory: `normalized_samples.json`, `scored_samples.json`, `report.json`, `report.md`, `report.html`, `dashboard.json`, `frontend_dashboard.json`.
- Assert none of the original 6 files are empty (file size > 0).
- Assert `report.html` still contains valid HTML (starts with `<!DOCTYPE` or `<html`).

---

## Area 3: Data Source Switch (Frontend)

### VAL-BRIDGE-020 — Frontend Loads Pipeline-Generated JSON

**Title:** Dashboard loads `frontend_dashboard.json` (or pipeline-generated data) instead of mock `jade_dashboard.json`.

**Behavioral Description:** The dashboard's `js/data.js` (or equivalent data loader) is updated to load the pipeline-generated JSON. The data path references the streetwear dataset. When the dashboard is opened, it fetches and parses the pipeline-generated file without errors.

**Evidence Requirements:**
- Inspect `js/data.js` source: the fetch URL points to `frontend_dashboard.json` or a pipeline-generated file.
- Open `index.html` in browser: no JavaScript console errors related to data loading.
- Network tab shows successful fetch of the data file (HTTP 200).

---

### VAL-BRIDGE-021 — Homepage Renders With Real Streetwear Data

**Title:** Homepage displays 6+ real streetwear trend directions from pipeline data.

**Behavioral Description:** When the homepage (`index.html`) loads, the Movement Board table shows ≥ 6 rows, each corresponding to a real streetwear direction (not jade/翡翠 mock data). Direction names reflect streetwear concepts (e.g., silhouette, graphic, layering themes). The "今日判断" (Today's Judgments) section shows counts that sum to the number of actual directions.

**Evidence Requirements:**
- Load `index.html` with pipeline data.
- Assert Movement Board table has ≥ 6 rows.
- Assert direction names do NOT contain jade-specific terms (翡翠, 金镶, 冰种) — they should be streetwear terms.
- Assert "今日判断" counts sum to the number of directions in the data.
- Visual inspection: no "undefined", "null", or "NaN" visible in any module.

---

### VAL-BRIDGE-022 — All 5 Pages Work With Real Data

**Title:** All 5 dashboard pages render without broken references or empty sections using real data.

**Behavioral Description:** Each of the 5 pages—homepage (`index.html`), direction map (`direction-map.html`), direction detail (`direction-detail.html`), evidence library (`evidence.html`), product line watch (`product-line.html`)—loads successfully with the pipeline-generated JSON. No page shows empty content sections, broken references, or JavaScript errors.

**Evidence Requirements:**
- Load each page individually and verify:
  - `index.html`: All 7 modules populated (Movement Board, Today's Judgments, Featured Directions, Risk Alerts, Recent Evidence, Product Lines, 14-Day Changes).
  - `direction-map.html`: Direction list/grid populated with ≥ 6 entries.
  - `direction-detail.html?id=<first_direction_id>`: All detail sections populated (overview, recommendation, product line cards, risks, evidence).
  - `evidence.html`: Evidence cards displayed (≥ 1 entry), filters functional.
  - `product-line.html`: Product line cards displayed (≥ 1 product line).
- No JavaScript console errors on any page.
- No visible "undefined", "null", "NaN", empty tables, or placeholder text.

---

## Area 4: Trend Charts (Visual)

### VAL-VIS-001 — Homepage Movement Board Has Visible Area/Line Charts

**Title:** Movement board rows include enlarged trend area charts, replacing tiny sparklines.

**Behavioral Description:** Each row in the homepage Movement Board table includes a visible area chart or line chart rendered in SVG. The chart is at minimum 100px wide × 40px tall (larger than a tiny sparkline). The chart displays `movement_history` data (14 data points) as a continuous area or line shape.

**Evidence Requirements:**
- Inspect `index.html` DOM: each Movement Board row contains an `<svg>` element.
- Assert SVG dimensions: width ≥ 100px, height ≥ 40px.
- Assert SVG contains a `<path>` or `<polyline>` element representing the chart line/area.
- Assert the chart's data points correspond to the direction's `movement_history` array (14 points).
- Visual inspection: charts are clearly visible, not just 1px dots.

---

### VAL-VIS-002 — Direction Detail Page Has 14-Day Trend Area Chart

**Title:** Direction detail page shows a prominent 14-day trend area chart.

**Behavioral Description:** On `direction-detail.html`, a dedicated chart section displays the selected direction's `movement_history` as an area chart. The chart is prominently sized (≥ 300px wide × 150px tall), shows 14 data points connected by a smooth or straight-line path, and has an area fill beneath the line. Axis indicators (at minimum, start/end labels) are present.

**Evidence Requirements:**
- Load `direction-detail.html?id=<any_valid_id>`.
- Assert an `<svg>` element exists in the chart section with width ≥ 300px, height ≥ 150px.
- Assert SVG contains a `<path>` element with `fill` attribute (area chart).
- Assert the path's data points match the direction's `movement_history` values.
- Assert at least start and end labels or axis markings are visible.
- No external charting libraries loaded (no `<script>` tags referencing Chart.js, D3, Recharts, etc.).

---

### VAL-VIS-003 — Charts Are Pure SVG, No External Libraries

**Title:** All trend charts are implemented with inline/handcrafted SVG, no third-party charting libraries.

**Behavioral Description:** The trend area charts on the homepage and direction detail page are rendered using hand-written SVG elements generated by vanilla JavaScript. No external charting libraries (D3.js, Chart.js, Plotly, Recharts, Highcharts, ApexCharts, etc.) are included in the project.

**Evidence Requirements:**
- Search all HTML files for `<script src=` tags — none reference external charting libraries.
- Search `js/` directory — no charting library files present.
- Search `package.json` or equivalent — no charting dependencies.
- Inspect SVG generation code in JS files — SVG elements are created programmatically or as template strings.

---

## Area 5: Comparison Charts (Visual)

### VAL-VIS-010 — Product Line Page Has Visual Comparison Chart

**Title:** Product line page includes a radar/spider chart or grouped bar chart comparing all product lines.

**Behavioral Description:** On `product-line.html`, a visual chart compares all product lines side-by-side on opportunity and risk dimensions. The chart type is either a radar/spider chart (one axis per product line or per metric) or a grouped bar chart. All product lines from the data are represented.

**Evidence Requirements:**
- Load `product-line.html` with pipeline data.
- Assert an `<svg>` chart element exists on the page.
- Assert the chart contains visual elements (bars, polygons, or paths) for each product line.
- Assert the number of product lines in the chart matches the number of product lines in the data.
- Visual inspection: chart is readable and all product lines are distinguishable.

---

### VAL-VIS-011 — Comparison Chart Shows Opportunity and Risk

**Title:** Product line comparison chart displays both opportunity and risk metrics.

**Behavioral Description:** The comparison chart on the product line page encodes both the `opportunity_level` and `risk_level` for each product line. On a radar chart, these would be separate axes or overlaid shapes; on a grouped bar chart, these would be paired bars per product line. The visual clearly distinguishes opportunity from risk (e.g., different colors, separate series).

**Evidence Requirements:**
- Inspect SVG elements: identify two distinct visual series or dual encoding.
- Assert a legend or label distinguishes "opportunity" from "risk" (机会 vs 风险, or equivalent).
- Assert values in the chart correspond to the `opportunity_level` and `risk_level` data in the JSON.
- Assert opportunity and risk use different colors or fill patterns.

---

## Area 6: Judgment Distribution (Visual)

### VAL-VIS-020 — Donut/Pie Chart Shows Judgment State Distribution

**Title:** Homepage or direction map includes a donut or pie chart showing judgment state proportions.

**Behavioral Description:** A donut or pie chart is rendered on either `index.html` (in the Today's Judgments module) or `direction-map.html`. The chart has 4 segments corresponding to the 4 judgment states (值得跟, 观察中, 短热噪音, 需要补证据). Each segment's arc angle is proportional to its count.

**Evidence Requirements:**
- Locate an `<svg>` element containing arc paths (`<path>` with arc commands, e.g., `A` in `d` attribute).
- Assert 4 distinct arc segments exist (or 3 if one state has 0 count).
- Assert each arc segment's color matches the established color coding: 值得跟 = green, 观察中 = blue, 短热噪音 = orange, 需要补证据 = gray.
- Assert the chart has a legend or inline labels identifying each segment.

---

### VAL-VIS-021 — Judgment Chart Proportions Match Actual Data

**Title:** Donut chart segment sizes correctly reflect the `today_judgments` counts.

**Behavioral Description:** The angular proportion of each segment in the donut/pie chart matches the ratio `count / total_directions`. For example, if there are 3 "值得跟" directions out of 8 total, the green segment spans approximately 3/8 × 360° ≈ 135°.

**Evidence Requirements:**
- Read `today_judgments` from the loaded JSON data.
- Calculate expected proportions for each judgment state.
- Inspect SVG arc paths: extract arc angles (from `d` attribute arc commands).
- Assert each arc angle is within ±5° of the expected proportion.
- Alternatively: assert pixel area proportions are within ±10% of expected.

---

## Area 7: Bubble Matrix Enhancement (Visual)

### VAL-VIS-030 — Bubble Matrix Has Quadrant Background Shading

**Title:** Direction map bubble matrix includes colored quadrant zones.

**Behavioral Description:** The bubble matrix on `direction-map.html` has a two-axis layout (e.g., opportunity × risk, or heat × confidence). The background is divided into quadrant zones (e.g., top-left, top-right, bottom-left, bottom-right) with distinct shading colors indicating strategic meaning (e.g., green for high-opportunity/low-risk, red for high-risk/low-opportunity).

**Evidence Requirements:**
- Locate the bubble matrix SVG on `direction-map.html`.
- Assert ≥ 4 background `<rect>` elements with distinct fill colors creating quadrant zones.
- Assert quadrant colors follow intuitive logic: favorable = warm/green tones, unfavorable = cool/red tones.
- Assert quadrant shading does not obscure bubble elements (shading is behind bubbles in z-order).

---

### VAL-VIS-031 — Bubble Matrix Has Hover Tooltips

**Title:** Hovering over a bubble in the matrix shows a tooltip with direction details.

**Behavioral Description:** When a user hovers over any bubble (circle) in the bubble matrix, a tooltip appears showing: direction name, heat score, opportunity, risk, and judgment state. The tooltip disappears when the mouse moves away.

**Evidence Requirements:**
- Hover over each bubble in the matrix (manual or via automated browser test).
- Assert a tooltip element becomes visible on hover with: direction name, ≥ 2 numeric metrics, judgment state.
- Assert tooltip disappears on mouseout.
- Assert tooltip content matches the data for the hovered direction.
- Assert tooltip does not overflow the viewport or overlap other critical UI elements.

---

## Area 8: Evidence Statistics (Visual)

### VAL-VIS-040 — Evidence Library Has Summary Statistics

**Title:** Evidence library page shows summary statistics at the top.

**Behavioral Description:** At the top of `evidence.html` (above the evidence card list), a statistics section displays: (1) a type distribution chart (e.g., bar chart or mini donut showing count by evidence type: 笔记/图片/评论/视频), and (2) a per-direction bar chart showing evidence count per direction.

**Evidence Requirements:**
- Load `evidence.html` with pipeline data.
- Assert a statistics section exists above the evidence list.
- Assert ≥ 1 SVG chart showing evidence type distribution (with ≥ 2 evidence types represented).
- Assert ≥ 1 SVG chart or bar display showing evidence count per direction.
- Assert counts in the charts sum to the total number of evidence entries.

---

### VAL-VIS-041 — Evidence Statistics Update on Filter

**Title:** Summary statistics update dynamically when evidence filters are applied.

**Behavioral Description:** When a user applies a filter on `evidence.html` (e.g., filtering by direction, product line, or evidence type), the summary statistics at the top recalculate and re-render to reflect only the filtered subset. For example, filtering to a single direction shows that direction's evidence count and type breakdown.

**Evidence Requirements:**
- Load `evidence.html`, note initial statistics values.
- Apply a filter (e.g., select a specific direction).
- Assert statistics charts/numbers change to reflect the filtered subset.
- Assert the type distribution chart shows only types present in the filtered results.
- Assert the total count in statistics equals the number of visible evidence cards.
- Remove the filter and assert statistics return to the original totals.

---

## Cross-Area Flows

### VAL-BRIDGE-100 — End-to-End: Pipeline to Dashboard Rendering

**Title:** Full end-to-end flow: run streetwear pack → `frontend_dashboard.json` generated → dashboard loads → all 5 pages render.

**Behavioral Description:** Starting from the raw `streetwear_collected.jsonl` (293 posts), running the streetwear pack with direction clustering produces `frontend_dashboard.json`. Copying (or symlinking) this file to `dashboard/data/` and loading each of the 5 dashboard pages results in fully populated, error-free rendering with real streetwear data and all new visual elements.

**Evidence Requirements:**
1. Run: `python -m intelligence.workflows.streetwear_pack <output_dir> --input <streetwear_collected.jsonl>` (or equivalent CLI).
2. Assert `frontend_dashboard.json` exists in `<output_dir>`.
3. Copy `frontend_dashboard.json` to `dashboard/data/`.
4. Start local server: `python3 -m http.server 8765 --directory dashboard`.
5. Load each page: `index.html`, `direction-map.html`, `direction-detail.html?id=<first_id>`, `evidence.html`, `product-line.html`.
6. Assert: no JavaScript console errors, no empty sections, no "undefined"/"null"/"NaN", all new charts (area, comparison, donut, bubble tooltips, evidence stats) render.
7. Assert: all original 6 output files also exist in `<output_dir>`.

---

### VAL-BRIDGE-101 — Navigation: Bubble Matrix → Direction Detail With Real Data

**Title:** Clicking a direction on the bubble matrix navigates to the correct direction detail page.

**Behavioral Description:** On `direction-map.html`, clicking a bubble (or direction entry) in the matrix navigates to `direction-detail.html?id=<clicked_direction_id>`. The detail page loads the correct direction's data: name, heat, movement_history chart, product line breakdown, risks, and evidence all correspond to the clicked direction.

**Evidence Requirements:**
- Load `direction-map.html` with pipeline data.
- Click on a bubble/direction entry (note its `id` and `name`).
- Assert navigation occurs to `direction-detail.html?id=<id>`.
- On the detail page, assert:
  - Direction name matches the clicked bubble's direction name.
  - Heat score matches.
  - `movement_history` chart is present and populated.
  - Product line breakdown section has ≥ 1 entry.
  - Evidence summary is present and non-empty.
- Repeat for at least 2 different directions to confirm ID-based routing works generically.

---

### VAL-BRIDGE-102 — Evidence Linking: Evidence Entries Reference Correct Directions

**Title:** Evidence entries on the evidence page correctly link to their source directions from real data.

**Behavioral Description:** On `evidence.html`, each evidence card shows its linked direction. Clicking a direction name or link on an evidence card navigates to the correct `direction-detail.html?id=<direction_id>`. The direction IDs in evidence entries are valid references to entries in `trend_directions`.

**Evidence Requirements:**
- Load `evidence.html` with pipeline data.
- For ≥ 3 evidence cards, verify the displayed direction name matches a real direction in the data.
- Click the direction link on an evidence card.
- Assert navigation to `direction-detail.html?id=<direction_id>`.
- Assert the loaded detail page shows the correct direction (name matches).
- Assert no evidence card references a direction ID that doesn't exist in `trend_directions` (check via data inspection or console verification).

---

### VAL-BRIDGE-103 — All Text Remains Chinese Throughout All Pages

**Title:** All user-visible text on all 5 pages is in Chinese.

**Behavioral Description:** The dashboard is a Chinese-language product. All page titles, navigation labels, module headers, direction names, descriptions, judgment states, button labels, filter labels, chart labels, tooltips, and summary text are in Chinese (zh-CN). No English UI labels, headers, or placeholder text appear (technical field names in JSON are acceptable; user-visible rendered text must be Chinese).

**Evidence Requirements:**
- Load each of the 5 pages.
- Assert `<html lang="zh-CN">` on every page.
- Assert navigation bar labels are Chinese (首页, 方向地图, 方向详情, 证据库, 产品线观察 — or equivalent).
- Assert module titles are Chinese (实时异动榜, 今日判断, etc.).
- Assert judgment states appear in Chinese (值得跟, 观察中, 短热噪音, 需要补证据).
- Assert chart labels/legends are Chinese.
- Assert no English placeholder text like "Loading...", "No data", "undefined" appears.
- Assert executive summary, direction descriptions, and recommendations are Chinese strings.

---

## Summary Table

| ID | Area | Title | Type |
|---|---|---|---|
| VAL-BRIDGE-001 | Direction Clustering | 6–10 Directions | Data |
| VAL-BRIDGE-002 | Direction Clustering | Direction Schema Completeness | Data |
| VAL-BRIDGE-003 | Direction Clustering | Multi-Keyword Posts Not Lost | Data |
| VAL-BRIDGE-004 | Direction Clustering | Directions Ranked by Score | Data |
| VAL-BRIDGE-010 | Dashboard JSON | Frontend-Compatible JSON | Data |
| VAL-BRIDGE-011 | Dashboard JSON | trend_directions Full Fields | Data |
| VAL-BRIDGE-012 | Dashboard JSON | product_lines With Linkages | Data |
| VAL-BRIDGE-013 | Dashboard JSON | Evidence Entries Linked | Data |
| VAL-BRIDGE-014 | Dashboard JSON | Judgments + 14-Day + Summary | Data |
| VAL-BRIDGE-015 | Dashboard JSON | 6 Original Files Preserved | Data |
| VAL-BRIDGE-020 | Data Source Switch | Frontend Loads Pipeline JSON | Integration |
| VAL-BRIDGE-021 | Data Source Switch | Homepage Real Streetwear Data | Integration |
| VAL-BRIDGE-022 | Data Source Switch | All 5 Pages Work | Integration |
| VAL-VIS-001 | Trend Charts | Homepage Area/Line Charts | Visual |
| VAL-VIS-002 | Trend Charts | Detail Page 14-Day Chart | Visual |
| VAL-VIS-003 | Trend Charts | Pure SVG, No Libraries | Visual |
| VAL-VIS-010 | Comparison Charts | Product Line Comparison Chart | Visual |
| VAL-VIS-011 | Comparison Charts | Opportunity + Risk Shown | Visual |
| VAL-VIS-020 | Judgment Distribution | Donut/Pie Chart | Visual |
| VAL-VIS-021 | Judgment Distribution | Proportions Match Data | Visual |
| VAL-VIS-030 | Bubble Matrix | Quadrant Shading | Visual |
| VAL-VIS-031 | Bubble Matrix | Hover Tooltips | Visual |
| VAL-VIS-040 | Evidence Statistics | Summary Statistics | Visual |
| VAL-VIS-041 | Evidence Statistics | Stats Update on Filter | Visual |
| VAL-BRIDGE-100 | Cross-Area | End-to-End Flow | Integration |
| VAL-BRIDGE-101 | Cross-Area | Bubble → Detail Navigation | Integration |
| VAL-BRIDGE-102 | Cross-Area | Evidence → Direction Linking | Integration |
| VAL-BRIDGE-103 | Cross-Area | All Text Chinese | Integration |

**Total assertions: 28** (16 data/pipeline, 7 integration, 5 visual)
