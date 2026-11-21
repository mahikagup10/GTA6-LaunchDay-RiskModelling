import Plot from "./Plot";
import { axisStyle, baseLayout, plotConfig } from "./chartTheme";

const levels = ["Very low", "Low", "Moderate", "High", "Very high"];
const matrix = levels.map((_, impactIndex) => (
  levels.map((__, likelihoodIndex) => (impactIndex + 1) * (likelihoodIndex + 1))
));

const scenarioPositions = [
  { name: "Launch DDoS", x: 4, y: 5 },
  { name: "Source theft", x: 3, y: 4 },
  { name: "Insider leak", x: 3, y: 4 },
  { name: "Fake downloads", x: 4, y: 3 },
];

export default function ScenarioHeatMap() {
  return (
    <div className="plot-container" role="img" aria-label="Interactive team-assessed likelihood and business-impact heat map for four cyber scenarios">
      <Plot
        data={[
          {
            type: "heatmap",
            x: [1, 2, 3, 4, 5],
            y: [1, 2, 3, 4, 5],
            z: matrix,
            showscale: false,
            hovertemplate: "Likelihood: %{x}<br>Impact: %{y}<br>Relative score: %{z}<extra></extra>",
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
            x: scenarioPositions.map((item) => item.x),
            y: scenarioPositions.map((item) => item.y),
            text: scenarioPositions.map((item) => item.name),
            textposition: ["top center", "bottom left", "top right", "bottom center"],
            textfont: { color: "#ffffff", size: 10 },
            marker: {
              color: "#07101d",
              size: 11,
              line: { color: "#ffffff", width: 2 },
              symbol: "diamond",
            },
            hovertemplate: "%{text}<br>Likelihood: %{x}/5<br>Impact: %{y}/5<extra></extra>",
          },
        ]}
        layout={{
          ...baseLayout,
          height: 310,
          showlegend: false,
          margin: { l: 92, r: 22, t: 25, b: 72 },
          xaxis: {
            ...axisStyle,
            title: { text: "Likelihood", standoff: 14 },
            tickmode: "array",
            tickvals: [1, 2, 3, 4, 5],
            ticktext: levels,
            range: [0.5, 5.5],
            fixedrange: true,
          },
          yaxis: {
            ...axisStyle,
            title: { text: "Business impact", standoff: 14 },
            tickmode: "array",
            tickvals: [1, 2, 3, 4, 5],
            ticktext: levels,
            range: [0.5, 5.5],
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

