import Plot from "./Plot";
import { axisStyle, baseLayout, plotConfig } from "./chartTheme";
import { basisSuffix, formatCurrency, formatPercent } from "../../utils/formatters";

const levelValue = { none: 0, low: 1, medium: 2, high: 3 };
const shortScenario = {
  "launch-ddos": "Launch DDoS",
  "source-code-theft": "Build theft",
  "insider-leak": "Insider leak",
  "fake-downloads": "Fake downloads",
};
const levelLabel = { none: "Not covered", low: "Low", medium: "Medium", high: "High" };

export default function ControlHeatMap({ heatmap, onSelect, selectedCell }) {
  if (!heatmap) {
    return <div className="chart-loading">Waiting for control economics…</div>;
  }

  const scenarios = heatmap.scenarios;
  const controls = [...heatmap.controls].reverse();
  const cellFor = (controlId, scenarioId) => heatmap.cells.find((cell) => cell.controlId === controlId && cell.scenarioId === scenarioId);

  const z = controls.map((control) => scenarios.map((scenario) => levelValue[cellFor(control.id, scenario.id)?.level || "none"]));
  const text = controls.map((control) => scenarios.map((scenario) => {
    const cell = cellFor(control.id, scenario.id);
    return cell && cell.level !== "none" ? formatCurrency(cell.lossReduction) : "";
  }));
  const custom = controls.map((control) => scenarios.map((scenario) => {
    const cell = cellFor(control.id, scenario.id);
    return [
      control.name,
      scenario.name,
      levelLabel[cell?.level || "none"],
      cell && cell.level !== "none" ? `${formatCurrency(cell.lossReduction)} ${basisSuffix(cell.timeBasis)}` : "—",
      cell && cell.level !== "none" ? formatPercent(cell.reductionShare) : "—",
      control.id,
      scenario.id,
    ];
  }));
  const height = 70 + controls.length * 34;

  const shapes = selectedCell ? (() => {
    const row = controls.findIndex((control) => control.id === selectedCell.controlId);
    const column = scenarios.findIndex((scenario) => scenario.id === selectedCell.scenarioId);
    if (row < 0 || column < 0) return [];
    return [{ type: "rect", x0: column - 0.5, x1: column + 0.5, y0: row - 0.5, y1: row + 0.5, line: { color: "#ffffff", width: 2 } }];
  })() : [];

  return (
    <div className="plot-container" role="img" aria-label="Control-to-scenario benefit heat map">
      <Plot
        data={[{
          type: "heatmap",
          x: scenarios.map((_, index) => index),
          y: controls.map((_, index) => index),
          z,
          zmin: 0,
          zmax: 3,
          text,
          texttemplate: "%{text}",
          textfont: { color: "#ffffff", size: 10 },
          customdata: custom,
          hovertemplate: "<b>%{customdata[0]}</b><br>%{customdata[1]}<br>Benefit: %{customdata[2]}<br>Loss avoided: %{customdata[3]}<br>Share of scenario loss: %{customdata[4]}<br><i>Click for details</i><extra></extra>",
          colorscale: [
            [0, "#0a1524"],
            [0.249, "#0a1524"],
            [0.25, "#1d3b4a"],
            [0.5, "#1d3b4a"],
            [0.51, "#25706c"],
            [0.75, "#25706c"],
            [0.76, "#35d8c1"],
            [1, "#35d8c1"],
          ],
          showscale: false,
          xgap: 3,
          ygap: 3,
        }]}
        layout={{
          ...baseLayout,
          height,
          margin: { l: 190, r: 12, t: 12, b: 56 },
          xaxis: {
            ...axisStyle,
            tickmode: "array",
            tickvals: scenarios.map((_, index) => index),
            ticktext: scenarios.map((scenario) => `${shortScenario[scenario.id] || scenario.name}<br>${scenario.timeBasis === "launch-event" ? "per launch event" : "per year"}`),
            tickangle: 0,
            side: "bottom",
            fixedrange: true,
          },
          yaxis: {
            ...axisStyle,
            tickmode: "array",
            tickvals: controls.map((_, index) => index),
            ticktext: controls.map((control) => control.shortName || control.name),
            fixedrange: true,
          },
          shapes,
        }}
        config={{ ...plotConfig, displayModeBar: false }}
        useResizeHandler
        style={{ width: "100%", height: `${height}px` }}
        onClick={(event) => {
          const point = event?.points?.[0];
          if (!point || !onSelect) return;
          onSelect({ controlId: point.customdata[5], scenarioId: point.customdata[6] });
        }}
      />
    </div>
  );
}
