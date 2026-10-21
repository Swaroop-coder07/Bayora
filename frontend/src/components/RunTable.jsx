import StatusBadge from "./StatusBadge.jsx";

export default function RunTable({ runs, onSelect, onVerify, verifyResults = {}, compact = false }) {
  if (!runs?.length) return <p className="text-sm text-slate-400">No runs yet.</p>;
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left text-sm">
        <thead className="text-xs uppercase text-slate-400">
          <tr>
            <th className="py-2 pr-4">Run ID</th>
            <th className="pr-4">Time</th>
            {!compact && <th className="pr-4">Category</th>}
            <th className="pr-4">Verdict</th>
            {!compact && <th className="pr-4">Prompt hash</th>}
            {!compact && <th className="pr-4">Config</th>}
            {!compact && <th className="pr-4">Model</th>}
            {onVerify && <th>Verification</th>}
          </tr>
        </thead>
        <tbody>
          {runs.map((r) => (
            <tr key={r.id} className="cursor-pointer border-t border-slate-800 hover:bg-slate-800/50" onClick={() => onSelect?.(r.id)}>
              <td className="py-2 pr-4 font-mono text-xs">{r.id}</td>
              <td className="pr-4 text-slate-300">{new Date(r.created_at).toLocaleTimeString()}</td>
              {!compact && <td className="pr-4 text-slate-300">{r.category.replaceAll("_", " ")}</td>}
              <td className="pr-4"><StatusBadge value={r.verdict} /></td>
              {!compact && <td className="pr-4 font-mono text-xs text-slate-400">{r.prompt_hash.slice(0, 10)}...</td>}
              {!compact && <td className="pr-4 text-slate-300">v{r.config_version} <span className="font-mono text-xs text-slate-500">{r.config_hash.slice(0, 8)}</span></td>}
              {!compact && <td className="pr-4 text-slate-300">{r.model_version}</td>}
              {onVerify && (
                <td onClick={(e) => e.stopPropagation()}>
                  {verifyResults[r.id] ? <StatusBadge value={verifyResults[r.id]} /> : <button className="btn-ghost" onClick={() => onVerify(r.id)}>Verify Run</button>}
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
