import { useAuth } from "../hooks/useAuth.jsx";

export default function Navbar() {
  const { user, logout } = useAuth();
  return (
    <header className="flex items-center justify-between border-b border-slate-800 bg-slate-900 px-6 py-3">
      <div className="text-sm text-slate-400">Secure AI red-team testing with proof</div>
      <div className="flex items-center gap-3 text-sm">
        <span className={`rounded-full px-2.5 py-0.5 text-xs font-semibold ${user.role === "blue" ? "bg-sky-500/20 text-sky-300" : "bg-red-500/20 text-red-300"}`}>
          {user.role === "blue" ? "Blue Team" : "Red Team"}
        </span>
        <span className="text-slate-300">{user.email}</span>
        <button className="btn-ghost" onClick={logout}>Log out</button>
      </div>
    </header>
  );
}
