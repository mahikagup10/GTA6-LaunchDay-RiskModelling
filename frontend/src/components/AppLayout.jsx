import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useWorkbench } from "../context/WorkbenchContext";
import ModelStatusBanner from "./ModelStatusBanner";

const navigation = [
  ["/", "Executive Overview"],
  ["/attack-paths", "Attack Paths"],
  ["/risk-simulator", "Risk Simulator"],
  ["/control-planner", "Control Planner"],
];

export default function AppLayout() {
  const { status, resetDemo } = useWorkbench();
  const navigate = useNavigate();
  const statusLabel = {
    loading: "Running model…",
    refreshing: "Updating model…",
    ready: "Model connected",
    cached: "Saved result shown",
    error: "Model unavailable",
    unavailable: "Scenario model planned",
  }[status];

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-mark">CA</span>
          <div>
            <strong>Cyber Attack</strong>
            <span>Decision Workbench</span>
          </div>
        </div>

        <nav aria-label="Primary navigation">
          {navigation.map(([path, label], index) => (
            <NavLink
              key={path}
              to={path}
              end={path === "/"}
              className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}
            >
              <span>0{index + 1}</span>
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-note">
          <span className={`status-dot ${status}`} />
          Model status
          <strong>{statusLabel}</strong>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <span>Launch Risk Program</span>
          <div className="topbar-actions">
            <span className="evidence-pill">Evidence-aware model</span>
            <button className="demo-reset" onClick={() => { resetDemo(); navigate("/"); }}>Reset demo</button>
          </div>
        </header>
        <ModelStatusBanner />
        <Outlet />
      </main>
    </div>
  );
}

