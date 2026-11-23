import Plot from "./Plot";
import { axisStyle, baseLayout, plotConfig } from "./chartTheme";
import { formatCurrency } from "../../utils/formatters";

export default function TornadoChart({ rows = [], baselineMean }) {
  if (!rows.length || baselineMean == null) {
    return <div className="chart-loading">Waiting for tornado results…</div>;
  }

  const ordered = [...rows].reverse();
  const height = 60 + ordered.length * 34;
  const names = ordered.map((row) => row.name);

  return (
    <div className="plot-container" role="img" aria-label="Tornado chart of expected loss when each input is set to its low or high value">
      <Plot
        data={[
          {
            type: "bar",
            orientation: "h",
            name: "Input at low",
            y: names,
            x: ordered.map((row) => row.meanAtLow - baselineMean),
            base: baselineMean,
            marker: { color: "rgba(53, 216, 193, .75)" },
            customdata: ordered.map((row) => [formatCurrency(row.meanAtLow), row.lowValue]),
            hovertemplate: "%{y}<br>Input at low (%{customdata[1]:,}): expected loss %{customdata[0]}<extra></extra>",
          },
          {
            type: "bar",
            orientation: "h",
            name: "Input at high",
            y: names,
            x: ordered.map((row) => row.meanAtHigh - baselineMean),
            base: baselineMean,
            marker: { color: "rgba(255, 138, 91, .75)" },
            customdata: ordered.map((row) => [formatCurrency(row.meanAtHigh), row.highValue]),
            hovertemplate: "%{y}<br>Input at high (%{customdata[1]:,}): expected loss %{customdata[0]}<extra></extra>",
          },
        ]}
        layout={{
          ...baseLayout,
          height,
          barmode: "overlay",
          legend: { orientation: "h", x: 0, y: 1.15, font: { color: "#e8edf6", size: 11 } },
          margin: { l: 230, r: 24, t: 24, b: 40 },
          xaxis: {
            ...axisStyle,
            title: { text: "Expected loss (USD)", standoff: 10 },
            tickprefix: "$",
            tickformat: "~s",
          },
          yaxis: { ...axisStyle, gridcolor: "rgba(0,0,0,0)" },
          shapes: [{
            type: "line",
            x0: baselineMean,
            x1: baselineMean,
            yref: "paper",
            y0: 0,
            y1: 1,
            line: { color: "#e8edf6", width: 1, dash: "dot" },
          }],
        }}
        config={{ ...plotConfig, displayModeBar: false }}
        useResizeHandler
        style={{ width: "100%", height: `${height}px` }}
      />
    </div>
  );
}
