export const plotConfig = {
  responsive: true,
  displaylogo: false,
  modeBarButtonsToRemove: ["lasso2d", "select2d", "autoScale2d"],
};

export const baseLayout = {
  paper_bgcolor: "rgba(0,0,0,0)",
  plot_bgcolor: "rgba(0,0,0,0)",
  font: {
    family: "DM Sans, system-ui, sans-serif",
    color: "#8fa0b8",
    size: 11,
  },
  margin: { l: 58, r: 18, t: 18, b: 50 },
  hoverlabel: {
    bgcolor: "#122238",
    bordercolor: "#35d8c1",
    font: { color: "#e8edf6" },
  },
};

export const axisStyle = {
  gridcolor: "rgba(143, 160, 184, 0.13)",
  linecolor: "#263750",
  tickcolor: "#263750",
  zerolinecolor: "#263750",
  fixedrange: false,
  automargin: true,
};

