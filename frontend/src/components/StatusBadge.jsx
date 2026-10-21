const STYLES = {
  SAFE: "bg-emerald-500/15 text-emerald-300",
  Verified: "bg-emerald-500/15 text-emerald-300",
  cleaned: "bg-emerald-500/15 text-emerald-300",
  pass: "bg-emerald-500/15 text-emerald-300",
  LEAK: "bg-red-500/20 text-red-300",
  UNSAFE: "bg-red-500/20 text-red-300",
  critical: "bg-red-500/20 text-red-300",
  "Verification Failed": "bg-red-500/20 text-red-300",
  failed: "bg-red-500/20 text-red-300",
  fail: "bg-red-500/20 text-red-300",
  VIOLATION: "bg-orange-500/20 text-orange-300",
  high: "bg-orange-500/20 text-orange-300",
  SUSPICIOUS: "bg-amber-500/20 text-amber-300",
  medium: "bg-amber-500/20 text-amber-300",
  PAUSED: "bg-slate-500/25 text-slate-300",
  ERROR: "bg-slate-500/25 text-slate-300",
  running: "bg-sky-500/20 text-sky-300",
  created: "bg-sky-500/20 text-sky-300",
};

export default function StatusBadge({ value }) {
  return (
    <span className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-semibold ${STYLES[value] || "bg-slate-700 text-slate-300"}`}>
      {value}
    </span>
  );
}
