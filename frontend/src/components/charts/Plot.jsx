import { lazy, Suspense } from "react";

const LazyPlot = lazy(async () => {
  const [{ default: createPlotlyComponent }, { default: Plotly }] = await Promise.all([
    import("react-plotly.js/factory"),
    import("plotly.js-dist-min"),
  ]);

  return { default: createPlotlyComponent(Plotly) };
});

export default function Plot(props) {
  return (
    <Suspense fallback={<div className="chart-loading"><span className="loading-spinner" />Loading interactive chart…</div>}>
      <LazyPlot {...props} />
    </Suspense>
  );
}

