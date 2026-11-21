import { useWorkbench } from "../context/WorkbenchContext";

function formatSavedTime(value) {
  if (!value) return "an earlier session";
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

export default function ModelStatusBanner() {
  const { status, error, lastUpdatedAt, retryConnection } = useWorkbench();

  if (status === "ready") return null;

  const content = {
    loading: {
      title: "Starting the risk model",
      detail: "Loading the selected 10,000-run analysis…",
    },
    refreshing: {
      title: "Updating the analysis",
      detail: "The previous matching result remains visible while the model recalculates.",
    },
    cached: {
      title: "Showing a saved matching calculation",
      detail: `${error} Saved ${formatSavedTime(lastUpdatedAt)}.`,
    },
    error: {
      title: "Live risk model unavailable",
      detail: `${error} The scenario content remains available, but financial results need Flask.`,
    },
  }[status];

  if (!content) return null;

  return (
    <section className={`model-status-banner ${status}`} role={status === "error" ? "alert" : "status"}>
      <span className="model-status-icon" aria-hidden="true" />
      <div>
        <strong>{content.title}</strong>
        <p>{content.detail}</p>
      </div>
      {(status === "cached" || status === "error") && (
        <button className="status-retry" onClick={retryConnection}>Retry connection</button>
      )}
    </section>
  );
}
