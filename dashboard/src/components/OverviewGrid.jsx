export default function OverviewGrid({ charts, onSelect }) {
  return (
    <div className="overview-grid">
      {charts.map((c) => (
        <button
          type="button"
          key={c.slug}
          className="overview-card"
          onClick={() => onSelect(c.slug)}
        >
          <img src={`/graphs/${c.slug}.png`} alt={c.title} loading="lazy" />
          <div className="overview-card-body">
            <h3>{c.title}</h3>
            <p>
              {c.category} · {c.chartType} · {c.data.length} categories
            </p>
          </div>
        </button>
      ))}
    </div>
  );
}
