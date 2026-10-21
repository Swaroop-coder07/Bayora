import { useState } from "react";
import StatusBadge from "../components/StatusBadge.jsx";
import { usePolling } from "../hooks/usePolling.js";
import { api } from "../services/api.js";

const STEPS = ["created", "running", "cleaned"];

function Lifecycle({ state }) {
  const failed = state === "failed";
  const reached = failed ? 2 : STEPS.indexOf(state);
  return (
    <div className="flex items-center gap-2">
      {STEPS.map((s, i) => {
        const label = failed && s === "cleaned" ? "failed" : s;
        const done = i <= reached;
        const tone = failed && s === "cleaned" ? "bg-red-500" : done ? "bg-emerald-500" : "bg-slate-700";
        return (
          <div key={s} className="flex items-center gap-2">
            <span className={`flex h-7 w-7 items-center justify-center rounded-full text-xs font-bold text-white ${tone}`}>{i + 1}</span>
            <span className="text-sm capitalize">{label}</span>
            {i < STEPS.length - 1 && <span className="mx-1 text-slate-600">&rarr;</span>}
          </div>
        );
      })}
    </div>
  );
}

export default function SessionMonitor() {
  const { data: current } = usePolling(api.currentSession, 5000);
  const { data: sessions } = usePolling(api.sessions, 5000);
  const [test, setTest] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const selftest = async () => {
    setBusy(true);
    setError("");
    try { setTest(await api.selftest()); } catch (e) { setError(e.message); } finally { setBusy(false); }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Session Isolation Monitor</h1>

      <div className="card space-y-4">
        <h2 className="font-semibold">Current session</h2>
        {current ? (
          <>
            <div className="font-mono text-sm">{current.id}</div>
            <Lifecycle state={current.state} />
            <dl className="grid gap-4 text-sm sm:grid-cols-4">
              <div><dt className="label">Fresh context</dt><dd>{current.fresh_context ? "Verified" : "NOT verified"}</dd></div>
              <div><dt className="label">Isolation mode</dt><dd>{current.isolation_mode}</dd></div>
              <div><dt className="label">Cleanup result</dt><dd>{current.cleanup_ok === null ? "pending" : current.cleanup_ok ? "Clean" : "Failed"}</dd></div>
              <div><dt className="label">Error indicator</dt><dd className={current.cleanup_error ? "text-red-300" : "text-slate-400"}>{current.cleanup_error || "none"}</dd></div>
            </dl>
          </>
        ) : <p className="text-sm text-slate-400">No sessions yet. Run a test first.</p>}
      </div>

      <div className="card space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="font-semibold">Context reuse test</h2>
            <p className="text-sm text-slate-400">Runs two jobs back to back and checks that the second cannot see the first.</p>
          </div>
          <button className="btn" disabled={busy} onClick={selftest}>{busy ? "Testing..." : "Run isolation test"}</button>
        </div>
        {error && <p className="text-sm text-red-300">{error}</p>}
        {test && (
          <div className="space-y-2">
            <div className="flex items-center gap-2"><span className="text-sm">Result</span><StatusBadge value={test.passed ? "pass" : "fail"} /></div>
            <ul className="space-y-1 text-sm">
              {test.checks.map((c) => (
                <li key={c.name} className="flex items-start gap-2">
                  <span className={c.ok ? "text-emerald-300" : "text-red-300"}>{c.ok ? "PASS" : "FAIL"}</span>
                  <span>{c.name} <span className="text-slate-500">({c.detail})</span></span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      <div className="card overflow-x-auto">
        <h2 className="mb-3 font-semibold">Recent sessions</h2>
        <table className="w-full text-left text-sm">
          <thead className="text-xs uppercase text-slate-400">
            <tr><th className="py-2 pr-4">Session</th><th className="pr-4">State</th><th className="pr-4">Mode</th><th className="pr-4">Fresh</th><th className="pr-4">Cleanup</th><th>Run</th></tr>
          </thead>
          <tbody>
            {sessions?.map((s) => (
              <tr key={s.id} className="border-t border-slate-800">
                <td className="py-2 pr-4 font-mono text-xs">{s.id}</td>
                <td className="pr-4"><StatusBadge value={s.state} /></td>
                <td className="pr-4">{s.isolation_mode}</td>
                <td className="pr-4">{s.fresh_context ? "yes" : "no"}</td>
                <td className="pr-4">{s.cleanup_ok === null ? "-" : s.cleanup_ok ? "ok" : "failed"}</td>
                <td className="font-mono text-xs">{s.run_id || "self-test"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
