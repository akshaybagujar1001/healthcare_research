import { useState } from 'react';
import Lightbox from './Lightbox';

export default function ChartDetail({ chart }) {
  const [lightbox, setLightbox] = useState(null);
  const maxCount = Math.max(...chart.data.map((d) => d.count), 1);

  return (
    <div className="detail-panel visible">
      <div className="badges">
        <span className="badge blue">{chart.category}</span>
        <span className="badge green">{chart.chartType}</span>
        <span className="badge">Source: {chart.sourceColumn}</span>
        <span className="badge">{chart.totalCount} data points</span>
      </div>

      <div className="detail-grid">
        <div className="panel">
          <div className="panel-head">Chart Visualization</div>
          <div className="panel-body">
            <button
              type="button"
              className="chart-frame"
              onClick={() => setLightbox(`/graphs/${chart.slug}.png`)}
            >
              <img src={`/graphs/${chart.slug}.png`} alt={chart.title} />
              <span className="zoom-hint">Click to enlarge</span>
            </button>
            <div className="actions">
              <a
                className="btn primary"
                href={`/graphs/${chart.slug}.jpg`}
                download={`${chart.slug}.jpg`}
              >
                Download JPG
              </a>
              <a
                className="btn"
                href={`/graphs/${chart.slug}.png`}
                download={`${chart.slug}.png`}
              >
                Download PNG
              </a>
            </div>
          </div>
        </div>

        <div className="panel">
          <div className="panel-head">Description & Key Insights</div>
          <div className="panel-body">
            <p className="desc-text">{chart.description}</p>
            <ul className="insights-list">
              {chart.insights.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </div>
        </div>
      </div>

      <div className="panel">
        <div className="panel-head">
          Full Data Breakdown — {chart.data.length} Categories
        </div>
        <div className="panel-body table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th>#</th>
                <th>Category</th>
                <th>Count</th>
                <th>Share</th>
                <th>Distribution</th>
              </tr>
            </thead>
            <tbody>
              {chart.data.map((row, i) => (
                <tr key={`${row.label}-${i}`}>
                  <td>{i + 1}</td>
                  <td className="label-cell">{row.label}</td>
                  <td className="count-mono">{row.count}</td>
                  <td className="pct-mono">{row.percent}%</td>
                  <td>
                    <div className="bar-cell">
                      <div className="mini-bar">
                        <div
                          className="mini-bar-fill"
                          style={{ width: `${(row.count / maxCount) * 100}%` }}
                        />
                      </div>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <Lightbox src={lightbox} alt={chart.title} onClose={() => setLightbox(null)} />
    </div>
  );
}
