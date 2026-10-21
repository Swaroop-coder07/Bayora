const TONES = { default: "text-slate-100", good: "text-emerald-300", bad: "text-red-300", warn: "text-amber-300" };

export default function StatCard({ label, value, tone = "default" }) {
  return (
    <div className="card">
      <div className="text-xs uppercase tracking-wide text-slate-400">{label}</div>
      <div className={`mt-2 text-3xl font-bold ${TONES[tone]}`}>{value ?? "-"}</div>
    </div>
  );
}
