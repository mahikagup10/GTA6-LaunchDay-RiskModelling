import { useMemo } from "react";
import Plot from "./Plot";
import { axisStyle, baseLayout, plotConfig } from "./chartTheme";

function histogramTrace(histogram, name, color) {
  const centers = histogram.counts.map((_, index) => (
    histogram.binEdges[index] + histogram.binEdges[index + 1]
  ) / 2);
  const widths = histogram.counts.map((_, index) => (
    histogram.binEdges[index + 1] - histogram.binEdges[index]
  ) * 0.88);

  return {
    type: "bar",
    name,
    x: centers,
    y: histogram.counts,
    width: widths,
    marker: { color, line: { width: 0 } },
    hovertemplate: `${name}<br>Loss: $%{x:,.0f}<br>Trials: %{y:,}<extra></extra>`,
  };
}

export default function LossDistributionChart({ baseline, residual }) {
  const data = useMemo(() => {
    if (!baseline || !residual) return [];
    return [
      histogramTrace(baseline, "Baseline", "rgba(255, 138, 91, 0.72)"),
      histogramTrace(residual, "Residual", "rgba(53, 216, 193, 0.72)"),
    ];
  }, [baseline, residual]);

  if (!data.length) {
    return <div className="chart-loading">Waiting for simulation results…</div>;
  }

  return (
    <div className="plot-container" role="img" aria-label="Interactive baseline and residual loss distribution histogram">
      <Plot
        data={data}
        layout={{
          ...baseLayout,
          height: 300,
          barmode: "overlay",
          bargap: 0.03,
          legend: {
            orientation: "h",
            x: 0,
            y: 1.12,
            font: { color: "#e8edf6", size: 11 },
          },
          xaxis: {
            ...axisStyle,
            title: { text: "Loss magnitude (USD)", standoff: 12 },
            tickprefix: "$",
            tickformat: "~s",
          },
          yaxis: {
            ...axisStyle,
            title: { text: "Simulation trials", standoff: 10 },
            rangemode: "tozero",
          },
        }}
        config={plotConfig}
        useResizeHandler
        style={{ width: "100%", height: "300px" }}
      />
    </div>
  );
}

