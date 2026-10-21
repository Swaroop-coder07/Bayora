import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Link, useNavigate } from "react-router-dom";
import RunTable from "../components/RunTable.jsx";
import SecurityAlert from "../components/SecurityAlert.jsx";
import StatCard from "../components/StatCard.jsx";
import StatusBadge from "../components/StatusBadge.jsx";
import { usePolling } from "../hooks/usePolling.js";
import { api } from "../services/api.js";

export default function Dashboard() {
  const navigate = useNavigate();
  const { data: stats, error } = usePolling(api.stats);
  const { data: runs } = usePolling(api.runs);
  const { data: alerts } = usePolling(api.alerts);
  const { data: session } = usePolling(api.currentSession);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <button className="btn" onClick={() => navigate("/console")}>Start New Test</button>
      </div>
      {error && <p className="text-sm text-red-300">{error}</p>}

      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <StatCard label="Total tests" value={stats?.total} />
        <StatCard label="Passed" value={stats?.passed} tone="good" />
        <StatCard label="Failed" value={stats?.failed} tone="warn" />
        <StatCard label="Detected leaks" value={stats?.leaks} tone="bad" />
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="card lg:col-span-2">
          <h2 className="mb-3 font-semibold">Leakage trend</h2>
          {stats?.trend?.length ? (
            <ResponsiveContainer width="100%" height={220}>
              <LineChart data={stats.trend}>
                <CartesianGrid stroke="#1e293b" />
                <XAxis dataKey="n" stroke="#64748b" fontSize={12} />
                <YAxis domain={[0, 1]} stroke="#64748b" fontSize={12} />
                <Tooltip contentStyle={{ background: "#0f172a", border: "1px solid #334155" }} />
                <Line type="monotone" dataKey="risk" name="Probing risk" stroke="#f59e0b" dot={false} />
                <Line type="monotone" dataKey="leak" name="Prompt leakage" stroke="#ef4444" dot={false} />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-sm text-slate-400">Run a test to see the trend.</p>
          )}
        </div>

        <div className="card">
          <h2 className="mb-3 font-semibold">Session status</h2>
          {session ? (
            <div className="space-y-2 text-sm">
              <div className="flex items-center justify-between"><span className="text-slate-400">Latest session</span><span className="font-mono text-xs">{session.id}</span></div>
              <div className="flex items-center justify-between"><span className="text-slate-400">State</span><StatusBadge value={session.state} /></div>
              <div className="flex items-center justify-between"><span className="text-slate-400">Fresh context</span><span>{session.fresh_context ? "Yes" : "No"}</span></div>
              <div className="flex items-center justify-between"><span className="text-slate-400">Isolation</span><span>{session.isolation_mode}</span></div>
              <Link to="/sessions" className="inline-block pt-2 text-brand-500 hover:underline">Open monitor</Link>
            </div>
          ) : (
            <p className="text-sm text-slate-400">No sessions yet.</p>
          )}
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="card">
          <h2 className="mb-3 font-semibold">Recent test activity</h2>
          <RunTable runs={runs?.slice(0, 6)} compact onSelect={(id) => navigate(`/runs?open=${id}`)} />
        </div>
        <div className="space-y-3">
          <h2 className="font-semibold">Security alerts</h2>
          {alerts?.slice(0, 4).map((a) => <SecurityAlert key={a.id} alert={a} />)}
          {alerts && alerts.length === 0 && <p className="text-sm text-slate-400">No alerts.</p>}
        </div>
      </div>
    </div>
  );
}
