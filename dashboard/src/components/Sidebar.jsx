export default function Sidebar({ charts, activeSlug, search, onSearch, onSelect, meta, open }) {
  const categories = [...new Set(charts.map((c) => c.category))];
  const q = search.toLowerCase();

  const filtered = (list) =>
    list.filter(
      (c) =>
        !q ||
        c.title.toLowerCase().includes(q) ||
        c.category.toLowerCase().includes(q)
    );

  return (
    <aside className={`sidebar ${open ? 'sidebar-open' : ''}`}>
      <div className="brand">
        <h1>Lit Review Analytics</h1>
        <p>
          {meta.totalPapers} papers · {meta.yearRange} · {charts.length} charts
        </p>
      </div>
      <div className="search-wrap">
        <input
          type="search"
          placeholder="Search charts…"
          value={search}
          onChange={(e) => onSearch(e.target.value)}
        />
      </div>
      <nav className="nav-scroll">
        <div className="nav-group">
          <div className="nav-group-label">Dashboard</div>
          <button
            type="button"
            className={`nav-item ${!activeSlug ? 'active' : ''}`}
            onClick={() => onSelect(null)}
          >
            <span className="nav-dot" />
            Overview (all charts)
          </button>
        </div>
        {categories.map((cat) => {
          const items = filtered(charts.filter((c) => c.category === cat));
          if (!items.length) return null;
          return (
            <div className="nav-group" key={cat}>
              <div className="nav-group-label">{cat}</div>
              {items.map((c) => (
                <button
                  type="button"
                  key={c.slug}
                  className={`nav-item ${activeSlug === c.slug ? 'active' : ''}`}
                  onClick={() => onSelect(c.slug)}
                >
                  <span className="nav-dot" />
                  {c.title}
                </button>
              ))}
            </div>
          );
        })}
      </nav>
    </aside>
  );
}
