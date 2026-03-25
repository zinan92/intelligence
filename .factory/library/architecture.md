# Architecture

Architectural decisions, patterns discovered, and design rationale.

**What belongs here:** Key architectural choices, component patterns, data flow decisions.

---

## Dashboard Architecture

The Jade Signal Atlas dashboard is a static HTML/CSS/JS prototype that sits alongside the existing Python intelligence engine.

### Data Flow
```
jade_dashboard.json (static mock data)
    ↓ fetch()
HTML pages (homepage, direction-detail, direction-map, evidence, product-line)
    ↓ render via JS
DOM (cards, modules, panels)
```

### Page Architecture
- Each HTML page is a standalone document that references shared CSS and JS
- Data is loaded once per page from `data/jade_dashboard.json`
- Navigation between pages uses standard `<a href>` links with query parameters for context (e.g., `direction-detail.html?id=18k-gold-jade`)
- No client-side routing — each page is a separate HTML file

### Design System
- CSS custom properties define the color palette, typography, and spacing
- Shared component patterns: cards, badges, grid layouts, nav bar
- Judgment state colors are defined once in CSS custom properties and used everywhere

### Relationship to Existing Report
- The dashboard is a NEW product layer, not a replacement for `report.html`
- `report.html` remains as a compact evaluation surface
- The dashboard uses richer mock data than the thin `Report`/`ReportBlock` model
- Eventually, the intelligence engine may generate dashboard-ready JSON, but for now, mock data is hand-crafted
