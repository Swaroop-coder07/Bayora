import { useCallback, useEffect, useState } from "react";
import StatusBadge from "../components/StatusBadge.jsx";
import { api } from "../services/api.js";

const split = (s) => s.split(",").map((x) => x.trim()).filter(Boolean);

export default function BlueTeamConfig() {
  const [configs, setConfigs] = useState([]);
  const [form, setForm] = useState({ system_prompt: "", allowed: "", blocked: "", rules: "", canaries: "" });
  const [active, setActive] = useState(null);
  const [msg, setMsg] = useState({ type: "", text: "" });
  const [busy, setBusy] = useState(false);

  const load = useCallback(async () => {
    const list = await api.configs();
    setConfigs(list);
    const act = list.find((c) => c.is_active) || list[0];
    setActive(act || null);
    if (act) {
      setForm({
        system_prompt: act.system_prompt,
        allowed: act.allowed_topics.join(", "),
        blocked: act.blocked_topics.join(", "),
        rules: act.guardrail_rules.map((r) => `${r.name}::${r.pattern}`).join("\n"),
        canaries: "",
      });
    }
  }, []);

  useEffect(() => { load().catch((e) => setMsg({ type: "error", text: e.message })); }, [load]);

  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  const save = async (activate) => {
    setBusy(true);
    setMsg({ type: "", text: "" });
    try {
      const rules = form.rules.split("\n").map((l) => l.trim()).filter(Boolean).map((l) => {
        const [name, ...rest] = l.split("::");
        return { name: name.trim(), pattern: rest.join("::").trim() };
      });
      if (rules.some((r) => !r.pattern)) throw new Error("Guardrail rules must look like  name::regex");
      const saved = await api.saveConfig({
        system_prompt: form.system_prompt,
        allowed_topics: split(form.allowed),
        blocked_topics: split(form.blocked),
        guardrail_rules: rules,
        canaries: form.canaries.split("\n").map((c) => c.trim()).filter(Boolean),
        activate,
      });
      setMsg({ type: "ok", text: `Saved version ${saved.version}${activate ? " and activated it" : ""}.` });
      await load();
    } catch (e) {
      setMsg({ type: "error", text: e.message });
    } finally {
      setBusy(false);
    }
  };

  const activate = async (id) => {
    try { await api.activate(id); await load(); } catch (e) { setMsg({ type: "error", text: e.message }); }
  };

  return (
    <div className="mx-auto grid max-w-6xl gap-6 lg:grid-cols-3">
      <div className="card space-y-4 lg:col-span-2">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold">Blue Team Configuration</h1>
          {active && <span className="text-sm text-slate-400">Editing from v{active.version}</span>}
        </div>

        <div>
          <label className="label">Protected system instructions</label>
          <textarea className="input h-32" value={form.system_prompt} onChange={set("system_prompt")} />
        </div>
        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <label className="label">Allowed topics (comma separated)</label>
            <input className="input" value={form.allowed} onChange={set("allowed")} />
          </div>
          <div>
            <label className="label">Blocked topics (comma separated)</label>
            <input className="input" value={form.blocked} onChange={set("blocked")} />
          </div>
        </div>
        <div>
          <label className="label">Guardrail rules (one per line: name::regex)</label>
          <textarea className="input h-20 font-mono" value={form.rules} onChange={set("rules")} />
        </div>
        <div>
          <label className="label">Canary secrets (one per line, min 8 characters)</label>
          <textarea className="input h-20 font-mono" value={form.canaries} onChange={set("canaries")}
            placeholder={active?.canaries_masked?.length ? `Current: ${active.canaries_masked.join(", ")} - leave empty to keep them` : "BAYORA-CANARY-XXXXXXXX"} />
          <p className="mt-1 text-xs text-slate-500">Canaries are write-only: after saving, only a masked preview is ever shown.</p>
        </div>

        {msg.text && <p className={`text-sm ${msg.type === "ok" ? "text-emerald-300" : "text-red-300"}`}>{msg.text}</p>}
        <div className="flex gap-3">
          <button className="btn-ghost" disabled={busy} onClick={() => save(false)}>Save as new version</button>
          <button className="btn" disabled={busy} onClick={() => save(true)}>Save and activate</button>
        </div>
      </div>

      <div className="card">
        <h2 className="mb-3 font-semibold">Configuration versions</h2>
        <ul className="space-y-3">
          {configs.map((c) => (
            <li key={c.id} className="rounded-lg border border-slate-800 p-3 text-sm">
              <div className="flex items-center justify-between">
                <span className="font-medium">v{c.version}</span>
                {c.is_active ? <StatusBadge value="running" /> : <button className="btn-ghost" onClick={() => activate(c.id)}>Activate</button>}
              </div>
              <div className="mt-1 font-mono text-xs text-slate-500">{c.config_hash.slice(0, 16)}...</div>
              <div className="text-xs text-slate-500">{c.created_by} | {new Date(c.created_at).toLocaleString()}</div>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
