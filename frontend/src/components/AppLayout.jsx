import { NavLink, Outlet } from "react-router-dom";
import { useWorkbench } from "../context/WorkbenchContext";

const navigation = [
  ["/", "Executive Overview"],
  ["/attack-paths", "Attack Paths"],
  ["/risk-simulator", "Risk Simulator"],
  ["/control-planner", "Control Planner"],
];

export default function AppLayout() {
  const { status } = useWorkbench();
  const statusLabel = {
    loading: "Running model…",
    ready: "Model connected",
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
          <span className="status-dot" />
          Model status
          <strong>{statusLabel}</strong>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <span>Launch Risk Program</span>
          <span className="evidence-pill">Evidence-aware model</span>
        </header>
        <Outlet />
      </main>
    </div>
  );
}

