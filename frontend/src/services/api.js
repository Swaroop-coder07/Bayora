const BASE = import.meta.env.VITE_API_URL || "/api";
let token = localStorage.getItem("bayora_token");

export function setToken(t) {
  token = t;
  if (t) localStorage.setItem("bayora_token", t);
  else localStorage.removeItem("bayora_token");
}
export const getToken = () => token;

async function request(path, { method = "GET", body } = {}) {
  const res = await fetch(BASE + path, {
    method,
    headers: { "Content-Type": "application/json", ...(token ? { Authorization: `Bearer ${token}` } : {}) },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (res.status === 401 && path !== "/auth/login") {
    setToken(null);
    window.dispatchEvent(new Event("bayora:logout"));
  }
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const j = await res.json();
      detail = typeof j.detail === "string" ? j.detail : JSON.stringify(j.detail);
    } catch (_) {}
    throw new Error(detail);
  }
  return res.json();
}

export const api = {
  login: (email, password) => request("/auth/login", { method: "POST", body: { email, password } }),
  me: () => request("/auth/me"),
  runTest: (prompt, category) => request("/tests/run", { method: "POST", body: { prompt, category } }),
  stats: () => request("/runs/stats"),
  runs: () => request("/runs"),
  run: (id) => request(`/runs/${id}`),
  verify: (id) => request(`/runs/${id}/verify`, { method: "POST" }),
  exportRun: (id) => request(`/runs/${id}/export`),
  configs: () => request("/configs"),
  activeConfig: () => request("/configs/active"),
  saveConfig: (body) => request("/configs", { method: "POST", body }),
  activate: (id) => request(`/configs/${id}/activate`, { method: "POST" }),
  alerts: () => request("/alerts"),
  ack: (id) => request(`/alerts/${id}/ack`, { method: "POST" }),
  sessions: () => request("/sessions"),
  currentSession: () => request("/sessions/current"),
  selftest: () => request("/sessions/selftest", { method: "POST" }),
};
