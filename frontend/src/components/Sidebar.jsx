import { NavLink } from "react-router-dom";
import { useAuth } from "../hooks/useAuth.jsx";

const LINKS = [
  { to: "/", label: "Dashboard", end: true },
  { to: "/console", label: "Red Team Console" },
  { to: "/config", label: "Blue Team Config", blueOnly: true },
  { to: "/alerts", label: "Security Alerts" },
  { to: "/runs", label: "Run History" },
  { to: "/sessions", label: "Session Monitor" },
];

export default function Sidebar() {
  const { user } = useAuth();
  return (
    <aside className="w-60 shrink-0 border-r border-slate-800 bg-slate-900 p-4">
      <div className="mb-6 flex items-center gap-2 text-lg font-bold">
        <span className="inline-block h-7 w-7 rounded-lg bg-brand-500" /> Bayora
      </div>
      <nav className="space-y-1">
        {LINKS.filter((l) => !l.blueOnly || user.role === "blue").map((l) => (
          <NavLink
            key={l.to}
            to={l.to}
            end={l.end}
            className={({ isActive }) =>
              `block rounded-lg px-3 py-2 text-sm ${isActive ? "bg-brand-500/20 text-white" : "text-slate-300 hover:bg-slate-800"}`
            }
          >
            {l.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
