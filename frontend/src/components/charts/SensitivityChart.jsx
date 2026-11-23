import Plot from "./Plot";
import { axisStyle, baseLayout, plotConfig } from "./chartTheme";

export default function SensitivityChart({ drivers = [] }) {
  if (!drivers.length) {
    return <div className="chart-loading">Waiting for sensitivity results…</div>;
  }

  const ordered = [...drivers].reverse();
  const values = ordered.map((driver) => Math.abs(driver.correlation));
  const maximum = Math.max(0.1, ...values) * 1.2;
  const height = 60 + ordered.length * 34;

  return (
    <div className="plot-container" role="img" aria-label="Chart of the top baseline loss sensitivity drivers by Spearman rank correlation">
      <Plot
        data={[
          {
            type: "bar",
            orientation: "h",
            y: ordered.map((driver) => driver.name),
            x: values,
            text: values.map((value) => value.toFixed(2)),
            textposition: "outside",
            cliponaxis: false,
            customdata: ordered.map((driver) => driver.correlation),
            marker: {
              color: ordered.map((_, index) => (index === ordered.length - 1 ? "rgba(53, 216, 193, .85)" : "rgba(95, 141, 255, .7)")),
              line: { width: 0 },
            },
            hovertemplate: "%{y}<br>Spearman ρ: %{customdata:.3f}<extra></extra>",
          },
        ]}
        layout={{
          ...baseLayout,
          height,
          showlegend: false,
          margin: { l: 230, r: 42, t: 8, b: 40 },
          xaxis: {
            ...axisStyle,
            title: { text: "Absolute Spearman rank correlation with loss", standoff: 10 },
            range: [0, maximum],
          },
          yaxis: { ...axisStyle, gridcolor: "rgba(0,0,0,0)" },
        }}
        config={{ ...plotConfig, displayModeBar: false }}
        useResizeHandler
        style={{ width: "100%", height: `${height}px` }}
      />
    </div>
  );
}
