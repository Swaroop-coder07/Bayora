import { Navigate, Route, Routes } from "react-router-dom";
import AppLayout from "./layouts/AppLayout.jsx";
import { useAuth } from "./hooks/useAuth.jsx";
import Alerts from "./pages/Alerts.jsx";
import BlueTeamConfig from "./pages/BlueTeamConfig.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import Login from "./pages/Login.jsx";
import RedTeamConsole from "./pages/RedTeamConsole.jsx";
import RunHistory from "./pages/RunHistory.jsx";
import SessionMonitor from "./pages/SessionMonitor.jsx";

export default function App() {
  const { user, loading } = useAuth();
  if (loading) return <div className="p-10 text-slate-400">Loading...</div>;
  if (!user) return <Login />;
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route index element={<Dashboard />} />
        <Route path="console" element={<RedTeamConsole />} />
        <Route path="config" element={user.role === "blue" ? <BlueTeamConfig /> : <Navigate to="/" replace />} />
        <Route path="alerts" element={<Alerts />} />
        <Route path="runs" element={<RunHistory />} />
        <Route path="sessions" element={<SessionMonitor />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}
