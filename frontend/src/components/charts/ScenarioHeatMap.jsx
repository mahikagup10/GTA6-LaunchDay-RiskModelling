import Plot from "./Plot";
import { axisStyle, baseLayout, plotConfig } from "./chartTheme";
import { basisSuffix, formatCurrency, formatProbability } from "../../utils/formatters";

const levels = ["Very low", "Low", "Moderate", "High", "Very high"];
const matrix = levels.map((_, impactIndex) => (
  levels.map((__, likelihoodIndex) => (impactIndex + 1) * (likelihoodIndex + 1))
));
const shortNames = {
  "launch-ddos": "Launch DDoS",
  "source-code-theft": "Build theft",
  "insider-leak": "Insider leak",
  "fake-downloads": "Fake downloads",
};

export default function ScenarioHeatMap({ overview, selectedScenarioId }) {
  const items = overview?.scenarios || [];
  if (!items.length) {
    return <div className="chart-loading">Waiting for model-derived placement…</div>;
  }

  // Nudge scenarios that share a cell so labels stay readable.
  const seen = {};
  const points = items.map((item) => {
    const cell = `${item.likelihoodLevel}-${item.impactLevel}`;
    const offset = (seen[cell] || 0) * 0.22;
    seen[cell] = (seen[cell] || 0) + 1;
    return { ...item, x: item.likelihoodLevel + offset, y: item.impactLevel - offset };
  });

  return (
    <div className="plot-container" role="img" aria-label="Model-derived likelihood and impact heat map for four cyber scenarios">
      <Plot
        data={[
          {
            type: "heatmap",
            x: [1, 2, 3, 4, 5],
            y: [1, 2, 3, 4, 5],
            z: matrix,
            showscale: false,
            hoverinfo: "skip",
            colorscale: [
              [0, "#183a43"],
              [0.28, "#275e65"],
              [0.5, "#736f46"],
              [0.72, "#9b5e45"],
              [1, "#a63f4c"],
            ],
            xgap: 3,
            ygap: 3,
          },
          {
            type: "scatter",
            mode: "markers+text",
            x: points.map((item) => item.x),
            y: points.map((item) => item.y),
            text: points.map((item) => shortNames[item.scenarioId] || item.name),
            customdata: points.map((item) => [
              item.name,
              formatProbability(item.metrics.probabilityOfLoss),
              formatCurrency(item.metrics.meanGivenLoss),
              formatCurrency(item.metrics.mean),
              basisSuffix(item.timeBasis),
            ]),
            textposition: points.map((item) => (item.x >= 4.5 ? "top left" : item.x <= 1.5 ? "top right" : "top center")),
            textfont: { color: "#ffffff", size: 10 },
            marker: {
              color: points.map((item) => (item.scenarioId === selectedScenarioId ? "#35d8c1" : "#07101d")),
              size: 12,
              line: { color: "#ffffff", width: 2 },
              symbol: "diamond",
            },
            hovertemplate: "<b>%{customdata[0]}</b><br>P(loss in period): %{customdata[1]}<br>Mean loss when it happens: %{customdata[2]}<br>Expected loss: %{customdata[3]} %{customdata[4]}<extra></extra>",
          },
        ]}
        layout={{
          ...baseLayout,
          height: 310,
          showlegend: false,
          margin: { l: 92, r: 22, t: 25, b: 72 },
          xaxis: {
            ...axisStyle,
            title: { text: "Likelihood (P of a loss event in the period)", standoff: 14 },
            tickmode: "array",
            tickvals: [1, 2, 3, 4, 5],
            ticktext: levels,
            range: [0.5, 5.6],
            fixedrange: true,
          },
          yaxis: {
            ...axisStyle,
            title: { text: "Impact (mean loss given a loss)", standoff: 14 },
            tickmode: "array",
            tickvals: [1, 2, 3, 4, 5],
            ticktext: levels,
            range: [0.5, 5.6],
            fixedrange: true,
          },
        }}
        config={{ ...plotConfig, displayModeBar: false }}
        useResizeHandler
        style={{ width: "100%", height: "310px" }}
      />
    </div>
  );
}
