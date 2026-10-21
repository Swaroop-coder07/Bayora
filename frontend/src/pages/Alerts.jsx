import SecurityAlert from "../components/SecurityAlert.jsx";
import { useAuth } from "../hooks/useAuth.jsx";
import { usePolling } from "../hooks/usePolling.js";
import { api } from "../services/api.js";

export default function Alerts() {
  const { user } = useAuth();
  const { data: alerts, error, reload } = usePolling(api.alerts, 8000);
  const ack = async (id) => { await api.ack(id); reload(); };

  return (
    <div className="mx-auto max-w-3xl space-y-4">
      <h1 className="text-2xl font-bold">Security Alerts</h1>
      <p className="text-sm text-slate-400">Canary leaks, repeated probing, guardrail violations and session cleanup failures.</p>
      {error && <p className="text-sm text-red-300">{error}</p>}
      {alerts?.map((a) => <SecurityAlert key={a.id} alert={a} onAck={user.role === "blue" ? ack : undefined} />)}
      {alerts && alerts.length === 0 && <p className="text-slate-400">No alerts. Everything looks quiet.</p>}
    </div>
  );
}
