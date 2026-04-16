# Design System — GoodWork Forensic AI

**Author:** Designer agent, Session 017
**Source:** thegoodwork.online CSS extraction + BA logic + Streamlit constraints
**Consumed by:** /ux agent, junior-dev (Phase 8 pages)

---

## 1. Brand Personality

| IS | IS NOT |
|---|---|
| Authoritative | Aggressive |
| Precise | Bureaucratic |
| Calm under pressure | Cold or clinical |
| Executive-grade | Technical or academic |
| Trustworthy | Flashy or decorative |

---

## 2. Color Palette

All hex values extracted directly from thegoodwork.online CSS variables.

### Primary — GoodWork Red

| Token | Hex | Use |
|---|---|---|
| `red-900` | `#470011` | Extreme emphasis |
| `red-800` | `#8E0021` | Hover states |
| `red-700` | `#761E2F` | Secondary button hover |
| `red-600` | `#D50032` | **Primary — buttons, links, accents** |
| `red-500` | `#ED1C24` | Error / destructive |
| `red-400` | `#E37284` | Muted accent |
| `red-300` | `#F1A1B4` | Subtle highlight |
| `red-100` | `#DDC4BC` | Background tint |

### Neutrals

| Token | Hex | Use |
|---|---|---|
| `neutral-950` | `#282827` | Primary text |
| `neutral-800` | `#4F4F4E` | Secondary text, labels |
| `neutral-600` | `#727272` | Muted text, captions |
| `neutral-400` | `#B0B0B0` | Disabled, placeholders |
| `neutral-200` | `#D5D5D5` | Borders, dividers |
| `neutral-100` | `#F5F2F0` | Secondary background (warm white) |
| `neutral-000` | `#FFFFFF` | Primary background |

### Warm Neutrals (brand beige family)

| Token | Hex | Use |
|---|---|---|
| `warm-900` | `#322D28` | Dark warm surfaces |
| `warm-500` | `#958677` | Warm muted text |
| `warm-100` | `#E3D7CC` | Sidebar tint, card backgrounds |

### Semantic Colors

| Token | Hex | Use |
|---|---|---|
| `success` | `#1A7340` | Live mode, completed |
| `warning` | `#B8860B` | Knowledge-only mode, caution |
| `error` | `#D50032` | Critical severity, empty findings |
| `info` | `#0088CB` | Progress, informational (brand blue) |
| `gold` | `#FFCB05` | Premium badge (brand gold) |

---

## 3. Typography

**Primary:** Montserrat (Google Fonts) — extracted from thegoodwork.online as primary typeface.
**Stack:** `'Montserrat', 'Helvetica Neue', Arial, sans-serif`
**Mono:** `'JetBrains Mono', 'Fira Code', 'Courier New', monospace`

### Type Scale

| Role | Size | Weight | Use |
|---|---|---|---|
| display | 28px | 700 | Page titles |
| heading-1 | 22px | 600 | Section headers |
| heading-2 | 18px | 600 | Card headers |
| heading-3 | 15px | 600 | Sub-section labels |
| body | 14px | 400 | Body copy |
| body-sm | 13px | 400 | Metadata, captions |
| label | 12px | 500 | Badges, status chips |
| mono | 13px | 400 | Case IDs, file paths |

---

## 4. Design Tokens

### Spacing Scale (8px base)
```
4px  — xs
8px  — sm
12px — md
16px — lg
24px — xl
32px — 2xl
48px — 3xl
```

### Border Radius
```
2px — sharp  (tables, grids)
4px — sm     (badges, inputs)
6px — md     (cards, buttons)
8px — lg     (panels, modals)
```

### Shadow / Elevation
```
none — flat (inputs at rest)
sm   — 0 1px 3px rgba(0,0,0,0.08)
md   — 0 4px 12px rgba(0,0,0,0.10)
```

### Motion
```
fast     — 100ms ease-out       hover states
standard — 200ms ease-in-out    panel transitions
slow     — 350ms ease-in-out    page transitions
```

---

## 5. Streamlit Configuration

### .streamlit/config.toml
```toml
[theme]
base                     = "light"
primaryColor             = "#D50032"
backgroundColor          = "#FFFFFF"
secondaryBackgroundColor = "#F5F2F0"
textColor                = "#282827"
font                     = "sans serif"
```

### Custom CSS (inject via st.markdown in session.py bootstrap)
```css
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&display=swap');

* { font-family: 'Montserrat', 'Helvetica Neue', Arial, sans-serif !important; }

[data-testid="stSidebar"] { padding-top: 1rem; }

.stButton > button[kind="primary"] {
  background-color: #D50032;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  letter-spacing: 0.02em;
}
.stButton > button[kind="primary"]:hover { background-color: #761E2F; }

.severity-critical { border-left: 4px solid #D50032; background: #FFF0F2; padding: 12px 16px; border-radius: 0 6px 6px 0; }
.severity-warning  { border-left: 4px solid #B8860B; background: #FFFBEA; padding: 12px 16px; border-radius: 0 6px 6px 0; }
.severity-info     { border-left: 4px solid #0088CB; background: #F0F8FF; padding: 12px 16px; border-radius: 0 6px 6px 0; }

.case-id-chip {
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  background: #F5F2F0;
  border: 1px solid #D5D5D5;
  border-radius: 4px;
  padding: 2px 8px;
  color: #4F4F4E;
}

h2 { color: #282827; font-weight: 600; border-bottom: 2px solid #D50032; padding-bottom: 8px; }
```

---

## 6. Page-by-Page Design Direction

| Page | Layout | Tone |
|---|---|---|
| Landing (app.py) | Logo + tagline above fold, 3-col workflow menu | Calm, ready |
| FRM (6_FRM.py) | 4-stage linear, expander per risk item, severity banners | Methodical |
| All workflow pages (2,3,4,5,7,8,0,11,12,13) | Intake → Pipeline → Download shell, consistent | Efficient |
| Case Tracker (9) | Full-width table, colored status badges, expandable rows | Control panel |
| Settings | Two-column form, Save anchored at bottom | Administrative |

---

## 7. Visual Rules

- `#D50032` used only for primary CTAs and CRITICAL severity — never decorative
- Severity: CRITICAL=red, WARNING=amber, INFO=blue — consistent everywhere
- Case IDs always in monospace chip style, never plain text
- No hardcoded firm name — always from `session.firm_name`
- Date format: DD MMM YYYY (16 Apr 2026)
- Currency: AED/USD — not INR

---

## 8. Quality Checklist

- [ ] Contrast ratio ≥ 4.5:1 for all body text (WCAG AA)
- [ ] Montserrat loads — verify Network tab in browser DevTools
- [ ] Primary red only on CTAs and CRITICAL states
- [ ] All severity banners use correct token color
- [ ] Case IDs in monospace chip
- [ ] Logo visible at 180px in sidebar on white background
- [ ] Empty state defined for every list/table
- [ ] Loading state defined for every pipeline trigger
- [ ] Download buttons only appear after pipeline completes
- [ ] Sidebar readable at 1280px desktop viewport
- [ ] Date format DD MMM YYYY on all timestamps
- [ ] Currency AED/USD on all fee/pricing fields
