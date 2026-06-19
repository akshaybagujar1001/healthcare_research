import { useEffect, useState } from 'react';
import Sidebar from './components/Sidebar';
import StatsRow from './components/StatsRow';
import OverviewGrid from './components/OverviewGrid';
import ChartDetail from './components/ChartDetail';

export default function App() {
  const [meta, setMeta] = useState({ totalPapers: 0, yearRange: '—', charts: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeSlug, setActiveSlug] = useState(null);
  const [search, setSearch] = useState('');
  const [sidebarOpen, setSidebarOpen] = useState(false);

  useEffect(() => {
    fetch('/charts-data.json')
      .then((r) => {
        if (!r.ok) throw new Error('charts-data.json not found. Run: python make_graphs.py');
        return r.json();
      })
      .then((data) => {
        setMeta(data);
        setLoading(false);
      })
      .catch((e) => {
        setError(e.message);
        setLoading(false);
      });
  }, []);

  const charts = meta.charts || [];
  const activeChart = charts.find((c) => c.slug === activeSlug);

  const handleSelect = (slug) => {
    setActiveSlug(slug);
    setSidebarOpen(false);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  if (loading) {
    return (
      <div className="loading-screen">
        <div className="spinner" />
        <p>Loading literature review data…</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="loading-screen error">
        <h2>Data not ready</h2>
        <p>{error}</p>
        <code>python make_graphs.py</code>
      </div>
    );
  }

  return (
    <div className="app">
      <Sidebar
        charts={charts}
        activeSlug={activeSlug}
        search={search}
        onSearch={setSearch}
        onSelect={handleSelect}
        meta={meta}
        open={sidebarOpen}
      />

      <div className="main">
        <header className="topbar">
          <button
            type="button"
            className="menu-btn"
            onClick={() => setSidebarOpen((v) => !v)}
            aria-label="Toggle menu"
          >
            ☰
          </button>
          <div>
            <h2>{activeChart ? activeChart.title : 'Overview'}</h2>
            <div className="topbar-meta">
              {activeChart
                ? `${activeChart.category} · ${activeChart.chartType} · ${activeChart.sourceColumn}`
                : 'Click any chart card or use the sidebar to explore details'}
            </div>
          </div>
        </header>

        <StatsRow meta={meta} charts={charts} />

        <div className="content">
          {!activeSlug ? (
            <OverviewGrid charts={charts} onSelect={handleSelect} />
          ) : activeChart ? (
            <ChartDetail chart={activeChart} />
          ) : null}
        </div>
      </div>

      {sidebarOpen && (
        <button
          type="button"
          className="sidebar-backdrop"
          aria-label="Close menu"
          onClick={() => setSidebarOpen(false)}
        />
      )}
    </div>
  );
}
