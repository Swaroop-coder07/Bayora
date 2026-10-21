import { Link } from "react-router-dom";
import StatusBadge from "./StatusBadge.jsx";

export default function SecurityAlert({ alert, onAck }) {
  const border = alert.severity === "critical" ? "border-red-500/60 bg-red-500/10" : "border-slate-800 bg-slate-900";
  return (
    <div className={`flex items-start justify-between gap-3 rounded-xl border p-4 ${border} ${alert.acknowledged ? "opacity-60" : ""}`}>
      <div>
        <div className="flex items-center gap-2">
          <StatusBadge value={alert.severity} />
          <span className="font-medium">{alert.type}</span>
        </div>
        <p className="mt-1 text-sm text-slate-300">{alert.message}</p>
        <p className="mt-1 text-xs text-slate-500">
          {new Date(alert.created_at).toLocaleString()}
          {alert.run_id && (
            <>
              {" "}| Run <Link className="text-brand-500 hover:underline" to={`/runs?open=${alert.run_id}`}>{alert.run_id}</Link>
            </>
          )}
        </p>
      </div>
      {onAck && !alert.acknowledged && (
        <button className="btn-ghost shrink-0" onClick={() => onAck(alert.id)}>Acknowledge</button>
      )}
    </div>
  );
}
