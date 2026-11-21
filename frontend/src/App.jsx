import { Navigate, Route, Routes } from "react-router-dom";
import AppLayout from "./components/AppLayout";
import AttackPaths from "./pages/AttackPaths";
import ControlPlanner from "./pages/ControlPlanner";
import ExecutiveOverview from "./pages/ExecutiveOverview";
import RiskSimulator from "./pages/RiskSimulator";

export default function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route path="/" element={<ExecutiveOverview />} />
        <Route path="/attack-paths" element={<AttackPaths />} />
        <Route path="/risk-simulator" element={<RiskSimulator />} />
        <Route path="/control-planner" element={<ControlPlanner />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}

