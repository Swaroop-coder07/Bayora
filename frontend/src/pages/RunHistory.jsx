import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import RunTable from "../components/RunTable.jsx";
import StatusBadge from "../components/StatusBadge.jsx";
import { useAuth } from "../hooks/useAuth.jsx";
import { usePolling } from "../hooks/usePolling.js";
import { api } from "../services/api.js";

export default function RunHistory() {
  const { user } = useAuth();
  const [params, setParams] = useSearchParams();
  const { data: runs, error, reload } = usePolling(api.runs, 0);
  const [detail, setDetail] = useState(null);
  const [verifyResults, setVerifyResults] = useState({});
  const [msg, setMsg] = useState("");

  const open = async (id) => {
    setParams({ open: id });
    try { setDetail(await api.run(id)); } catch (e) { setMsg(e.message); }
  };

  useEffect(() => {
    const id = params.get("open");
    if (id) api.run(id).then(setDetail).catch((e) => setMsg(e.message));
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const verify = async (id) => {
    try {
      const res = await api.verify(id);
      setVerifyResults((v) => ({ ...v, [id]: res.status }));
      if (detail?.id === id) setDetail(await api.run(id)); // refresh audit log with the verification event
    } catch (e) { setMsg(e.message); }
  };

  const exportRun = async (id) => {
    try {
      const data = await api.exportRun(id);
      const url = URL.createObjectURL(new Blob([JSON.stringify(data, null, 2)], { type: "application/json" }));
      const a = Object.assign(document.createElement("a"), { href: url, download: `${id}.json` });
      a.click();
      URL.revokeObjectURL(url);
    } catch (e) { setMsg(e.message); }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Run History and Verification</h1>
        <button className="btn-ghost" onClick={reload}>Refresh</button>
      </div>
      {(error || msg) && <p className="text-sm text-red-300">{error || msg}</p>}

      <div className="card">
        <RunTable runs={runs} onSelect={open} onVerify={verify} verifyResults={verifyResults} />
      </div>

      {detail && (
        <div className="card space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="flex items-center gap-3">
              <h2 className="font-mono text-lg">{detail.id}</h2>
              <StatusBadge value={detail.verdict} />
              {verifyResults[detail.id] && <StatusBadge value={verifyResults[detail.id]} />}
            </div>
            <div className="flex gap-2">
              <button className="btn-ghost" onClick={() => verify(detail.id)}>Verify Run</button>
              {user.role === "blue" && <button className="btn-ghost" onClick={() => exportRun(detail.id)}>Export record</button>}
            </div>
          </div>

          <dl className="grid gap-3 text-sm sm:grid-cols-2">
            {[
              ["Prompt hash (SHA-256)", detail.prompt_hash],
              ["Configuration hash", detail.config_hash],
              ["Record fingerprint", detail.fingerprint],
              ["Model version", detail.model_version],
              ["Configuration version", `v${detail.config_version}`],
              ["Session", detail.session_id],
            ].map(([k, v]) => (
              <div key={k}><dt className="label">{k}</dt><dd className="break-all font-mono text-xs text-slate-300">{v}</dd></div>
            ))}
          </dl>

          <div>
            <div className="label">Prompt</div>
            <pre className="whitespace-pre-wrap rounded-lg bg-slate-950 p-3 text-sm">{detail.prompt}</pre>
          </div>
          <div>
            <div className="label">Response (secrets masked)</div>
            <pre className="whitespace-pre-wrap rounded-lg bg-slate-950 p-3 text-sm">{detail.response ?? "Not available at this feedback level."}</pre>
          </div>

          {user.role === "blue" && (
            <div>
              <div className="label">Audit log {detail.audit_chain_ok ? "(hash chain intact)" : "(HASH CHAIN BROKEN)"}</div>
              <ul className="space-y-1 rounded-lg bg-slate-950 p-3 font-mono text-xs text-slate-300">
                {detail.audit_log.map((e) => (
                  <li key={e.hash}>{new Date(e.ts).toLocaleTimeString()} {e.event} {JSON.stringify(e.data)}</li>
                ))}
              </ul>
            </div>
          )}
          <p className="text-xs text-slate-500">Verification checks that the stored record was not altered. It does not prove the model output is reproducible.</p>
        </div>
      )}
    </div>
  );
}
