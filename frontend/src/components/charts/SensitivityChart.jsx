import Plot from "./Plot";
import { axisStyle, baseLayout, plotConfig } from "./chartTheme";

export default function SensitivityChart({ drivers = [] }) {
  if (!drivers.length) {
    return <div className="chart-loading">Waiting for sensitivity results…</div>;
  }

  const ordered = [...drivers].reverse();
  const values = ordered.map((driver) => Math.abs(driver.correlation));
  const maximum = Math.max(0.2, ...values) * 1.15;

  return (
    <div className="plot-container" role="img" aria-label="Interactive chart of the top three baseline loss sensitivity drivers">
      <Plot
        data={[
          {
            type: "bar",
            orientation: "h",
            y: ordered.map((driver) => driver.name),
            x: values,
            text: values.map((value) => `${Math.round(value * 100)}%`),
            textposition: "outside",
            cliponaxis: false,
            marker: {
              color: ["rgba(95, 141, 255, .62)", "rgba(95, 141, 255, .78)", "rgba(53, 216, 193, .85)"],
              line: { width: 0 },
            },
            hovertemplate: "%{y}<br>Rank correlation: %{x:.3f}<extra></extra>",
          },
        ]}
        layout={{
          ...baseLayout,
          height: 220,
          showlegend: false,
          margin: { l: 145, r: 42, t: 12, b: 40 },
          xaxis: {
            ...axisStyle,
            title: { text: "Absolute rank correlation", standoff: 10 },
            range: [0, maximum],
            tickformat: ".0%",
          },
          yaxis: {
            ...axisStyle,
            gridcolor: "rgba(0,0,0,0)",
          },
        }}
        config={{ ...plotConfig, displayModeBar: false }}
        useResizeHandler
        style={{ width: "100%", height: "220px" }}
      />
    </div>
  );
}

