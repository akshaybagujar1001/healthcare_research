"""Generate summary charts from LIT REV.xlsx and a detailed browser dashboard."""

import json
import shutil
import webbrowser
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

EXCEL_PATH = Path(__file__).parent / "LIT REV.xlsx"
OUTPUT_DIR = Path(__file__).parent / "graphs"
HTML_PATH = Path(__file__).parent / "index.html"
REACT_PUBLIC = Path(__file__).parent / "dashboard" / "public"
REACT_GRAPHS = REACT_PUBLIC / "graphs"
REACT_DATA = REACT_PUBLIC / "charts-data.json"

CHART_META = {
    "publications_by_year": {
        "category": "Overview",
        "type": "Bar Chart",
        "source": "Year",
        "description": (
            "Timeline of reviewed publications from 2018 to 2026. "
            "Shows research momentum and recent growth in your review topic."
        ),
    },
    "tech_adoption_summary": {
        "category": "Overview",
        "type": "Bar Chart",
        "source": "FL / Edge / Cloud columns",
        "description": (
            "Combined comparison of three key infrastructure choices across all papers. "
            "Useful for summarising adoption in your thesis or report."
        ),
    },
    "domain_top15": {
        "category": "Research Focus",
        "type": "Horizontal Bar",
        "source": "DOMAIN",
        "description": "Top 15 research domains. Healthcare and smart health monitoring dominate the reviewed literature.",
    },
    "subdomains_top15": {
        "category": "Research Focus",
        "type": "Horizontal Bar",
        "source": "SUB-DOMAINS",
        "description": "Fine-grained sub-domains within the broader research areas covered by the papers.",
    },
    "lifestyle_behaviours_top12": {
        "category": "Research Focus",
        "type": "Horizontal Bar",
        "source": "LIFESTYLE BEHAVIOURS",
        "description": "Lifestyle behaviours under study — sleep, physical activity, nutrition, mental health, etc.",
    },
    "data_type": {
        "category": "Research Focus",
        "type": "Horizontal Bar",
        "source": "Physiological data or Behavioral",
        "description": "Split between physiological sensing (ECG, glucose, vitals) and behavioural data (activity, apps, surveys).",
    },
    "user_involvement": {
        "category": "Research Focus",
        "type": "Horizontal Bar",
        "source": "User Involvement",
        "description": "How participants engage with systems — passive monitoring, feedback loops, co-design, or clinical involvement.",
    },
    "ai_techniques_top15": {
        "category": "AI & Models",
        "type": "Horizontal Bar",
        "source": "Ai techniques",
        "description": "Most common AI/ML methods used — deep learning, federated setups, classical ML, NLP, etc.",
    },
    "model_types_top12": {
        "category": "AI & Models",
        "type": "Horizontal Bar",
        "source": "Type of model used",
        "description": "Specific model architectures and frameworks referenced in the reviewed papers.",
    },
    "publication_type": {
        "category": "AI & Models",
        "type": "Horizontal Bar",
        "source": "Type of publication",
        "description": "Where findings were published — journals, conferences, workshops, preprints, or books.",
    },
    "inference_location": {
        "category": "Infrastructure",
        "type": "Horizontal Bar",
        "source": "Inference location (on-device/Edge/cloud)",
        "description": "Where real-time predictions run — on wearable/device, edge server, or cloud. Critical for privacy and latency.",
    },
    "training_location": {
        "category": "Infrastructure",
        "type": "Horizontal Bar",
        "source": "Training location(central or federated)",
        "description": "Whether models are trained centrally on a server or via federated/distributed training.",
    },
    "sensing_technologies_top12": {
        "category": "Infrastructure",
        "type": "Horizontal Bar",
        "source": "Sensing Technologies",
        "description": "Hardware and sensors used — wearables, smartphones, IoT devices, medical-grade monitors.",
    },
    "federated_learning": {
        "category": "Technology Adoption",
        "type": "Bar Chart",
        "source": "FL used? (Yes/No)",
        "description": "Federated Learning (FL) adoption — trains models across devices without sharing raw patient data.",
    },
    "federated_learning_pie": {
        "category": "Technology Adoption",
        "type": "Pie Chart",
        "source": "FL used? (Yes/No)",
        "description": "Percentage view of FL usage — Yes, No, and not-reported responses across the review.",
    },
    "edge_computing": {
        "category": "Technology Adoption",
        "type": "Bar Chart",
        "source": "Edge Computing used? (Yes/No)",
        "description": "Edge computing processes data near the user instead of sending everything to the cloud.",
    },
    "edge_computing_pie": {
        "category": "Technology Adoption",
        "type": "Pie Chart",
        "source": "Edge Computing used? (Yes/No)",
        "description": "Proportional breakdown of edge computing adoption in the literature.",
    },
    "cloud_computing": {
        "category": "Technology Adoption",
        "type": "Bar Chart",
        "source": "On Cloud? (Yes/No)",
        "description": "Cloud-based training or inference usage across reviewed studies.",
    },
    "cloud_computing_pie": {
        "category": "Technology Adoption",
        "type": "Pie Chart",
        "source": "On Cloud? (Yes/No)",
        "description": "Share of papers using cloud infrastructure vs local/edge-only approaches.",
    },
}

saved_charts = []


def clean_yes_no(value):
    if pd.isna(value):
        return "Not reported"
    text = str(value).strip().lower()
    if text in {"yes", "y"}:
        return "Yes"
    if text in {"no", "n"}:
        return "No"
    if text in {"not specified", "not reported", "not mentioned", "not explicitly stated"}:
        return "Not reported"
    if text.startswith("yes"):
        return "Yes"
    if text.startswith("no"):
        return "No"
    return str(value).strip()


def clean_year(value):
    if pd.isna(value):
        return None
    text = str(value).strip()
    if text.lower() in {"not reported", "n/a", "na", ""}:
        return None
    try:
        year = int(float(text))
        if 1990 <= year <= 2030:
            return year
    except ValueError:
        pass
    return None


def count_column(series, top_n=None):
    counts = series.dropna().astype(str).str.strip()
    counts = counts[counts != ""]
    counts = counts.value_counts()
    if top_n:
        counts = counts.head(top_n)
    return counts


def counts_to_records(counts, total_papers=171):
    total = int(counts.sum()) or 1
    records = []
    for label, count in counts.items():
        records.append(
            {
                "label": str(label),
                "count": int(count),
                "percent": round(100 * count / total, 1),
            }
        )
    return records


def build_insights(title, records):
    if not records:
        return ["No data available for this chart."]
    top = records[0]
    insights = [f"Highest category: \"{top['label']}\" with {top['count']} papers ({top['percent']}%)."]
    if len(records) > 1:
        second = records[1]
        insights.append(
            f"Second: \"{second['label']}\" — {second['count']} papers ({second['percent']}%)."
        )
    insights.append(f"Total categories shown: {len(records)}.")
    if len(records) >= 3:
        top3 = sum(r["count"] for r in records[:3])
        top3_pct = round(100 * top3 / sum(r["count"] for r in records), 1)
        insights.append(f"Top 3 categories account for {top3_pct}% of this chart's data.")
    return insights


def save_chart(fig, slug, title, counts, total_papers):
    png_path = OUTPUT_DIR / f"{slug}.png"
    jpg_path = OUTPUT_DIR / f"{slug}.jpg"
    fig.savefig(png_path, dpi=150, bbox_inches="tight")
    fig.savefig(jpg_path, dpi=150, bbox_inches="tight", format="jpeg")
    plt.close(fig)

    meta = CHART_META.get(slug, {})
    records = counts_to_records(counts, total_papers)
    saved_charts.append(
        {
            "slug": slug,
            "title": title,
            "category": meta.get("category", "Other"),
            "chartType": meta.get("type", "Chart"),
            "sourceColumn": meta.get("source", "—"),
            "description": meta.get(
                "description",
                "Summary chart generated from the literature review dataset.",
            ),
            "insights": build_insights(title, records),
            "data": records,
            "totalCount": int(counts.sum()),
        }
    )


def save_bar(counts, title, slug, horizontal=True, color="#4C72B0", total_papers=171):
    if counts.empty:
        return
    fig, ax = plt.subplots(figsize=(10, max(4, 0.35 * len(counts))))
    if horizontal:
        counts.plot(kind="barh", ax=ax, color=color)
        ax.invert_yaxis()
    else:
        counts.plot(kind="bar", ax=ax, color=color)
        plt.xticks(rotation=45, ha="right")
    ax.set_title(title, fontsize=12, fontweight="bold")
    ax.set_xlabel("Number of papers")
    ax.grid(axis="x" if horizontal else "y", alpha=0.3)
    plt.tight_layout()
    save_chart(fig, slug, title, counts, total_papers)


def save_pie(counts, title, slug, total_papers=171):
    if counts.empty:
        return
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.pie(counts.values, labels=counts.index, autopct="%1.1f%%", startangle=90)
    ax.set_title(title, fontsize=12, fontweight="bold")
    plt.tight_layout()
    save_chart(fig, slug, title, counts, total_papers)


def build_html(total_papers, year_min, year_max):
    dashboard_json = json.dumps(
        {
            "totalPapers": total_papers,
            "yearRange": f"{year_min}–{year_max}" if year_min else "N/A",
            "charts": saved_charts,
        },
        ensure_ascii=False,
    )

    template = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Literature Review Analytics</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #0f1419;
      --sidebar: #161b22;
      --surface: #1c2333;
      --surface2: #242d3d;
      --border: #2d3848;
      --text: #e6edf3;
      --muted: #8b949e;
      --accent: #58a6ff;
      --accent2: #3fb950;
      --warn: #d29922;
      --danger: #f85149;
      --radius: 12px;
      --sidebar-w: 300px;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    html { scroll-behavior: smooth; }
    body {
      font-family: "DM Sans", system-ui, sans-serif;
      background: var(--bg);
      color: var(--text);
      min-height: 100vh;
      display: flex;
    }

    /* Sidebar */
    .sidebar {
      width: var(--sidebar-w);
      min-height: 100vh;
      background: var(--sidebar);
      border-right: 1px solid var(--border);
      display: flex;
      flex-direction: column;
      position: fixed;
      left: 0; top: 0; bottom: 0;
      z-index: 100;
    }
    .brand {
      padding: 1.5rem 1.25rem 1rem;
      border-bottom: 1px solid var(--border);
    }
    .brand h1 { font-size: 1.1rem; font-weight: 700; letter-spacing: -0.02em; }
    .brand p { font-size: 0.78rem; color: var(--muted); margin-top: 0.35rem; }
    .search-wrap { padding: 1rem 1.25rem; }
    .search-wrap input {
      width: 100%;
      padding: 0.65rem 0.85rem;
      border-radius: 8px;
      border: 1px solid var(--border);
      background: var(--surface);
      color: var(--text);
      font-family: inherit;
      font-size: 0.85rem;
      outline: none;
    }
    .search-wrap input:focus { border-color: var(--accent); }
    .nav-scroll { flex: 1; overflow-y: auto; padding: 0 0.75rem 1rem; }
    .nav-group { margin-bottom: 1rem; }
    .nav-group-label {
      font-size: 0.68rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--muted);
      padding: 0.5rem 0.5rem 0.35rem;
    }
    .nav-item {
      display: flex;
      align-items: center;
      gap: 0.6rem;
      padding: 0.55rem 0.65rem;
      border-radius: 8px;
      cursor: pointer;
      font-size: 0.82rem;
      color: var(--muted);
      transition: all 0.15s;
      border: 1px solid transparent;
    }
    .nav-item:hover { background: var(--surface); color: var(--text); }
    .nav-item.active {
      background: rgba(88,166,255,0.12);
      color: var(--accent);
      border-color: rgba(88,166,255,0.25);
    }
    .nav-dot {
      width: 8px; height: 8px;
      border-radius: 50%;
      background: var(--border);
      flex-shrink: 0;
    }
    .nav-item.active .nav-dot { background: var(--accent); }

    /* Main */
    .main {
      margin-left: var(--sidebar-w);
      flex: 1;
      min-width: 0;
    }
    .topbar {
      position: sticky;
      top: 0;
      z-index: 50;
      background: rgba(15,20,25,0.85);
      backdrop-filter: blur(12px);
      border-bottom: 1px solid var(--border);
      padding: 1rem 2rem;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 1rem;
    }
    .topbar h2 { font-size: 1.25rem; font-weight: 600; }
    .topbar-meta { font-size: 0.82rem; color: var(--muted); }
    .stats-row {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 1rem;
      padding: 1.5rem 2rem 0;
    }
    .stat-card {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 1.1rem 1.25rem;
    }
    .stat-card .label { font-size: 0.75rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.05em; }
    .stat-card .value { font-size: 1.75rem; font-weight: 700; margin-top: 0.25rem; }
    .stat-card .sub { font-size: 0.78rem; color: var(--muted); margin-top: 0.2rem; }

    .content { padding: 1.5rem 2rem 3rem; }

    /* Detail panel */
    .detail-panel { display: none; animation: fadeIn 0.25s ease; }
    .detail-panel.visible { display: block; }
    @keyframes fadeIn { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: none; } }

    .badges { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 1rem; }
    .badge {
      font-size: 0.72rem;
      font-weight: 600;
      padding: 0.3rem 0.65rem;
      border-radius: 999px;
      border: 1px solid var(--border);
      background: var(--surface2);
    }
    .badge.blue { color: var(--accent); border-color: rgba(88,166,255,0.3); background: rgba(88,166,255,0.08); }
    .badge.green { color: var(--accent2); border-color: rgba(63,185,80,0.3); background: rgba(63,185,80,0.08); }

    .detail-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 1.25rem;
      margin-bottom: 1.25rem;
    }
    @media (max-width: 1100px) { .detail-grid { grid-template-columns: 1fr; } }

    .panel {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      overflow: hidden;
    }
    .panel-head {
      padding: 0.85rem 1.15rem;
      border-bottom: 1px solid var(--border);
      font-size: 0.85rem;
      font-weight: 600;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }
    .panel-body { padding: 1.15rem; }

    .chart-frame {
      background: #fff;
      border-radius: 8px;
      padding: 0.5rem;
      cursor: zoom-in;
      position: relative;
    }
    .chart-frame img { width: 100%; height: auto; display: block; border-radius: 4px; }
    .zoom-hint {
      position: absolute;
      bottom: 0.75rem; right: 0.75rem;
      background: rgba(0,0,0,0.65);
      color: #fff;
      font-size: 0.72rem;
      padding: 0.3rem 0.6rem;
      border-radius: 6px;
    }

    .desc-text { font-size: 0.92rem; line-height: 1.7; color: #c9d1d9; margin-bottom: 1rem; }
    .insights-list { list-style: none; }
    .insights-list li {
      padding: 0.55rem 0;
      border-bottom: 1px solid var(--border);
      font-size: 0.88rem;
      color: #c9d1d9;
      display: flex;
      gap: 0.6rem;
    }
    .insights-list li:last-child { border-bottom: none; }
    .insights-list li::before { content: "→"; color: var(--accent); flex-shrink: 0; }

    .actions { display: flex; flex-wrap: wrap; gap: 0.6rem; margin-top: 1rem; }
    .btn {
      display: inline-flex;
      align-items: center;
      gap: 0.4rem;
      padding: 0.55rem 1rem;
      border-radius: 8px;
      font-size: 0.82rem;
      font-weight: 600;
      font-family: inherit;
      cursor: pointer;
      text-decoration: none;
      border: 1px solid var(--border);
      background: var(--surface2);
      color: var(--text);
      transition: all 0.15s;
    }
    .btn:hover { border-color: var(--accent); color: var(--accent); }
    .btn.primary { background: var(--accent); color: #0d1117; border-color: var(--accent); }
    .btn.primary:hover { filter: brightness(1.1); color: #0d1117; }

    /* Data table */
    .data-table { width: 100%; border-collapse: collapse; font-size: 0.84rem; }
    .data-table th {
      text-align: left;
      padding: 0.6rem 0.75rem;
      color: var(--muted);
      font-weight: 600;
      font-size: 0.72rem;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      border-bottom: 1px solid var(--border);
    }
    .data-table td { padding: 0.65rem 0.75rem; border-bottom: 1px solid var(--border); vertical-align: middle; }
    .data-table tr:last-child td { border-bottom: none; }
    .data-table tr:hover td { background: rgba(255,255,255,0.02); }
    .bar-cell { display: flex; align-items: center; gap: 0.75rem; }
    .mini-bar {
      flex: 1;
      height: 6px;
      background: var(--surface2);
      border-radius: 3px;
      overflow: hidden;
      min-width: 60px;
    }
    .mini-bar-fill { height: 100%; background: linear-gradient(90deg, var(--accent), #79c0ff); border-radius: 3px; }
    .count-mono { font-family: "JetBrains Mono", monospace; font-size: 0.8rem; color: var(--accent2); }
    .pct-mono { font-family: "JetBrains Mono", monospace; font-size: 0.78rem; color: var(--muted); }

    /* Overview grid */
    .overview-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
      gap: 1rem;
    }
    .overview-card {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      overflow: hidden;
      cursor: pointer;
      transition: border-color 0.15s, transform 0.15s;
    }
    .overview-card:hover { border-color: var(--accent); transform: translateY(-2px); }
    .overview-card img { width: 100%; height: 140px; object-fit: cover; object-position: left center; background: #fff; }
    .overview-card-body { padding: 0.85rem 1rem 1rem; }
    .overview-card-body h3 { font-size: 0.88rem; font-weight: 600; margin-bottom: 0.35rem; }
    .overview-card-body p { font-size: 0.75rem; color: var(--muted); }

    /* Lightbox */
    .lightbox {
      display: none;
      position: fixed;
      inset: 0;
      background: rgba(0,0,0,0.92);
      z-index: 1000;
      align-items: center;
      justify-content: center;
      padding: 2rem;
      cursor: zoom-out;
    }
    .lightbox.open { display: flex; }
    .lightbox img { max-width: 95vw; max-height: 90vh; border-radius: 8px; box-shadow: 0 8px 40px rgba(0,0,0,0.5); }
    .lightbox-close {
      position: absolute;
      top: 1.25rem; right: 1.5rem;
      background: var(--surface2);
      border: 1px solid var(--border);
      color: var(--text);
      width: 40px; height: 40px;
      border-radius: 8px;
      font-size: 1.25rem;
      cursor: pointer;
    }

    .empty-state { text-align: center; padding: 4rem 2rem; color: var(--muted); }

    @media (max-width: 900px) {
      .sidebar { transform: translateX(-100%); }
      .main { margin-left: 0; }
      .stats-row { grid-template-columns: repeat(2, 1fr); }
    }
  </style>
</head>
<body>
  <aside class="sidebar">
    <div class="brand">
      <h1>Lit Review Analytics</h1>
      <p id="brand-sub">Loading dataset…</p>
    </div>
    <div class="search-wrap">
      <input type="search" id="search" placeholder="Search charts…" autocomplete="off">
    </div>
    <nav class="nav-scroll" id="nav"></nav>
  </aside>

  <div class="main">
    <header class="topbar">
      <div>
        <h2 id="page-title">Overview</h2>
        <div class="topbar-meta" id="page-sub">Select a chart from the sidebar to view full details</div>
      </div>
    </header>

    <div class="stats-row" id="stats"></div>

    <div class="content">
      <div id="overview-view">
        <div class="overview-grid" id="overview-grid"></div>
      </div>
      <div id="detail-view" class="detail-panel"></div>
    </div>
  </div>

  <div class="lightbox" id="lightbox">
    <button class="lightbox-close" id="lightbox-close" aria-label="Close">×</button>
    <img id="lightbox-img" src="" alt="">
  </div>

  <script>
    const DASHBOARD = __DASHBOARD_JSON__;
    const nav = document.getElementById('nav');
    const detailView = document.getElementById('detail-view');
    const overviewView = document.getElementById('overview-view');
    const overviewGrid = document.getElementById('overview-grid');
    const pageTitle = document.getElementById('page-title');
    const pageSub = document.getElementById('page-sub');
    const statsEl = document.getElementById('stats');
    const searchInput = document.getElementById('search');
    const lightbox = document.getElementById('lightbox');
    const lightboxImg = document.getElementById('lightbox-img');

    let activeSlug = null;

    const categories = [...new Set(DASHBOARD.charts.map(c => c.category))];

    document.getElementById('brand-sub').textContent =
      `${DASHBOARD.totalPapers} papers · ${DASHBOARD.yearRange} · ${DASHBOARD.charts.length} charts`;

    function renderStats() {
      const fl = DASHBOARD.charts.find(c => c.slug === 'federated_learning');
      const edge = DASHBOARD.charts.find(c => c.slug === 'edge_computing');
      const cloud = DASHBOARD.charts.find(c => c.slug === 'cloud_computing');
      const yes = (chart) => chart?.data.find(d => d.label === 'Yes')?.count ?? '—';
      const pct = (chart) => chart?.data.find(d => d.label === 'Yes')?.percent ?? '—';

      statsEl.innerHTML = `
        <div class="stat-card"><div class="label">Total Papers</div><div class="value">${DASHBOARD.totalPapers}</div><div class="sub">Literature review corpus</div></div>
        <div class="stat-card"><div class="label">Year Range</div><div class="value" style="font-size:1.4rem">${DASHBOARD.yearRange}</div><div class="sub">Publication timeline</div></div>
        <div class="stat-card"><div class="label">Federated Learning</div><div class="value">${pct(fl)}%</div><div class="sub">${yes(fl)} papers use FL</div></div>
        <div class="stat-card"><div class="label">Edge Computing</div><div class="value">${pct(edge)}%</div><div class="sub">${yes(edge)} papers use edge</div></div>
      `;
    }

    function renderNav(filter = '') {
      const q = filter.toLowerCase();
      nav.innerHTML = `
        <div class="nav-group">
          <div class="nav-group-label">Dashboard</div>
          <div class="nav-item ${!activeSlug ? 'active' : ''}" data-slug="">
            <span class="nav-dot"></span> Overview (all charts)
          </div>
        </div>
        ${categories.map(cat => {
          const items = DASHBOARD.charts.filter(c =>
            c.category === cat &&
            (!q || c.title.toLowerCase().includes(q) || c.category.toLowerCase().includes(q))
          );
          if (!items.length) return '';
          return `
            <div class="nav-group">
              <div class="nav-group-label">${cat}</div>
              ${items.map(c => `
                <div class="nav-item ${activeSlug === c.slug ? 'active' : ''}" data-slug="${c.slug}">
                  <span class="nav-dot"></span> ${c.title}
                </div>
              `).join('')}
            </div>`;
        }).join('')}
      `;
      nav.querySelectorAll('.nav-item').forEach(el => {
        el.addEventListener('click', () => showChart(el.dataset.slug || null));
      });
    }

    function renderOverview() {
      overviewGrid.innerHTML = DASHBOARD.charts.map(c => `
        <div class="overview-card" data-slug="${c.slug}">
          <img src="graphs/${c.slug}.png" alt="${c.title}" loading="lazy">
          <div class="overview-card-body">
            <h3>${c.title}</h3>
            <p>${c.category} · ${c.chartType} · ${c.data.length} categories</p>
          </div>
        </div>
      `).join('');
      overviewGrid.querySelectorAll('.overview-card').forEach(el => {
        el.addEventListener('click', () => showChart(el.dataset.slug));
      });
    }

    function renderDetail(chart) {
      const maxCount = Math.max(...chart.data.map(d => d.count), 1);
      const tableRows = chart.data.map((d, i) => `
        <tr>
          <td>${i + 1}</td>
          <td>${escapeHtml(d.label)}</td>
          <td class="count-mono">${d.count}</td>
          <td class="pct-mono">${d.percent}%</td>
          <td>
            <div class="bar-cell">
              <div class="mini-bar"><div class="mini-bar-fill" style="width:${(d.count/maxCount)*100}%"></div></div>
            </div>
          </td>
        </tr>
      `).join('');

      detailView.innerHTML = `
        <div class="badges">
          <span class="badge blue">${chart.category}</span>
          <span class="badge green">${chart.chartType}</span>
          <span class="badge">Source: ${escapeHtml(chart.sourceColumn)}</span>
          <span class="badge">${chart.totalCount} data points</span>
        </div>

        <div class="detail-grid">
          <div class="panel">
            <div class="panel-head">Chart Visualization</div>
            <div class="panel-body">
              <div class="chart-frame" id="chart-zoom">
                <img src="graphs/${chart.slug}.png" alt="${escapeHtml(chart.title)}">
                <span class="zoom-hint">Click to enlarge</span>
              </div>
              <div class="actions">
                <a class="btn primary" href="graphs/${chart.slug}.jpg" download="${chart.slug}.jpg">⬇ Download JPG</a>
                <a class="btn" href="graphs/${chart.slug}.png" download="${chart.slug}.png">⬇ Download PNG</a>
              </div>
            </div>
          </div>

          <div class="panel">
            <div class="panel-head">Description & Key Insights</div>
            <div class="panel-body">
              <p class="desc-text">${escapeHtml(chart.description)}</p>
              <ul class="insights-list">
                ${chart.insights.map(i => `<li>${escapeHtml(i)}</li>`).join('')}
              </ul>
            </div>
          </div>
        </div>

        <div class="panel">
          <div class="panel-head">Full Data Breakdown — ${chart.data.length} Categories</div>
          <div class="panel-body" style="padding:0; overflow-x:auto">
            <table class="data-table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Category</th>
                  <th>Count</th>
                  <th>Share</th>
                  <th>Distribution</th>
                </tr>
              </thead>
              <tbody>${tableRows}</tbody>
            </table>
          </div>
        </div>
      `;

      document.getElementById('chart-zoom').addEventListener('click', () => {
        lightboxImg.src = `graphs/${chart.slug}.png`;
        lightboxImg.alt = chart.title;
        lightbox.classList.add('open');
      });
    }

    function escapeHtml(str) {
      const d = document.createElement('div');
      d.textContent = str;
      return d.innerHTML;
    }

    function showChart(slug) {
      activeSlug = slug;
      renderNav(searchInput.value);

      if (!slug) {
        overviewView.style.display = 'block';
        detailView.classList.remove('visible');
        pageTitle.textContent = 'Overview';
        pageSub.textContent = 'Click any chart card or use the sidebar to explore details';
        return;
      }

      const chart = DASHBOARD.charts.find(c => c.slug === slug);
      if (!chart) return;

      overviewView.style.display = 'none';
      detailView.classList.add('visible');
      pageTitle.textContent = chart.title;
      pageSub.textContent = `${chart.category} · ${chart.chartType} · ${chart.sourceColumn}`;
      renderDetail(chart);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    searchInput.addEventListener('input', e => renderNav(e.target.value));

    lightbox.addEventListener('click', () => lightbox.classList.remove('open'));
    document.getElementById('lightbox-close').addEventListener('click', e => {
      e.stopPropagation();
      lightbox.classList.remove('open');
    });
    document.addEventListener('keydown', e => {
      if (e.key === 'Escape') lightbox.classList.remove('open');
    });

    renderStats();
    renderNav();
    renderOverview();
  </script>
</body>
</html>"""

    html_content = template.replace("__DASHBOARD_JSON__", dashboard_json)
    HTML_PATH.write_text(html_content, encoding="utf-8")


def export_for_react(total_papers, year_min, year_max):
    REACT_GRAPHS.mkdir(parents=True, exist_ok=True)
    payload = {
        "totalPapers": total_papers,
        "yearRange": f"{year_min}–{year_max}" if year_min else "N/A",
        "charts": saved_charts,
    }
    REACT_DATA.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    for path in OUTPUT_DIR.glob("*"):
        if path.suffix.lower() in {".png", ".jpg"}:
            shutil.copy2(path, REACT_GRAPHS / path.name)


def main():
    global saved_charts
    saved_charts = []
    OUTPUT_DIR.mkdir(exist_ok=True)
    df = pd.read_excel(EXCEL_PATH)
    total_papers = len(df)
    df["Year_clean"] = df["Year"].apply(clean_year)
    years = df["Year_clean"].dropna()
    year_min = int(years.min()) if len(years) else None
    year_max = int(years.max()) if len(years) else None

    yes_no_cols = {
        "FL used? (Yes/No)": "federated_learning",
        "Edge Computing used? (Yes/No)": "edge_computing",
        "On Cloud? (Yes/No)": "cloud_computing",
    }
    for col, slug in yes_no_cols.items():
        cleaned = df[col].apply(clean_yes_no)
        bar_title = (
            "Federated Learning Usage"
            if "FL" in col
            else f"{col.split('?')[0].strip()} Usage"
        )
        save_bar(cleaned.value_counts(), bar_title, slug, color="#55A868", total_papers=total_papers)
        save_pie(
            cleaned.value_counts(),
            f"{col.split('?')[0].strip()} (Pie)",
            f"{slug}_pie",
            total_papers=total_papers,
        )

    year_counts = df["Year_clean"].dropna().astype(int).value_counts().sort_index()
    save_bar(
        year_counts,
        "Publications by Year",
        "publications_by_year",
        horizontal=False,
        color="#8172B3",
        total_papers=total_papers,
    )

    categorical = {
        "DOMAIN": ("Research Domain (Top 15)", "domain_top15", 15),
        "SUB-DOMAINS": ("Sub-Domains (Top 15)", "subdomains_top15", 15),
        "Ai techniques": ("AI Techniques (Top 15)", "ai_techniques_top15", 15),
        "Type of publication": ("Publication Type", "publication_type", None),
        "Type of model used": ("Model Types (Top 12)", "model_types_top12", 12),
        "LIFESTYLE BEHAVIOURS": (
            "Lifestyle Behaviours (Top 12)",
            "lifestyle_behaviours_top12",
            12,
        ),
        "Physiological data or Behavioral ": (
            "Data Type (Physiological vs Behavioral)",
            "data_type",
            None,
        ),
        "Inference location (on-device/Edge/cloud)": (
            "Inference Location",
            "inference_location",
            None,
        ),
        "Training location(central or federated)": (
            "Training Location",
            "training_location",
            None,
        ),
        "Sensing Technologies": (
            "Sensing Technologies (Top 12)",
            "sensing_technologies_top12",
            12,
        ),
        "User Involvement": ("User Involvement", "user_involvement", None),
    }

    for col, (title, slug, top_n) in categorical.items():
        if col in df.columns:
            save_bar(count_column(df[col], top_n=top_n), title, slug, total_papers=total_papers)

    adoption = pd.DataFrame(
        {
            "Federated Learning": df["FL used? (Yes/No)"].apply(clean_yes_no).eq("Yes").sum(),
            "Edge Computing": df["Edge Computing used? (Yes/No)"].apply(clean_yes_no).eq("Yes").sum(),
            "Cloud": df["On Cloud? (Yes/No)"].apply(clean_yes_no).eq("Yes").sum(),
        },
        index=["Yes"],
    ).T["Yes"]
    save_bar(
        adoption,
        "Technology Adoption (Yes counts)",
        "tech_adoption_summary",
        horizontal=False,
        color="#C44E52",
        total_papers=total_papers,
    )

    build_html(total_papers, year_min, year_max)
    export_for_react(total_papers, year_min, year_max)

    react_index = Path(__file__).parent / "dashboard" / "index.html"
    url = react_index.as_uri() if react_index.exists() else HTML_PATH.as_uri()
    print(f"Charts: {len(saved_charts)} (PNG + JPG) in {OUTPUT_DIR}")
    print(f"React data: {REACT_DATA}")
    print(f"Run React app: cd dashboard && npm install && npm run dev")


if __name__ == "__main__":
    main()
