function getYes(chart) {
  return chart?.data.find((d) => d.label === 'Yes');
}

export default function StatsRow({ meta, charts }) {
  const fl = charts.find((c) => c.slug === 'federated_learning');
  const edge = charts.find((c) => c.slug === 'edge_computing');
  const flYes = getYes(fl);
  const edgeYes = getYes(edge);

  const items = [
    { label: 'Total Papers', value: meta.totalPapers, sub: 'Literature review corpus' },
    { label: 'Year Range', value: meta.yearRange, sub: 'Publication timeline', small: true },
    {
      label: 'Federated Learning',
      value: flYes ? `${flYes.percent}%` : '—',
      sub: flYes ? `${flYes.count} papers use FL` : 'No data',
    },
    {
      label: 'Edge Computing',
      value: edgeYes ? `${edgeYes.percent}%` : '—',
      sub: edgeYes ? `${edgeYes.count} papers use edge` : 'No data',
    },
  ];

  return (
    <div className="stats-row">
      {items.map((item) => (
        <div className="stat-card" key={item.label}>
          <div className="label">{item.label}</div>
          <div className={`value ${item.small ? 'value-sm' : ''}`}>{item.value}</div>
          <div className="sub">{item.sub}</div>
        </div>
      ))}
    </div>
  );
}
