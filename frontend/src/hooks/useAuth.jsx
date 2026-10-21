import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { api, getToken, setToken } from "../services/api.js";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(!!getToken());

  const logout = useCallback(() => {
    setToken(null);
    setUser(null);
  }, []);

  useEffect(() => {
    if (getToken()) api.me().then(setUser).catch(logout).finally(() => setLoading(false));
    window.addEventListener("bayora:logout", logout);
    return () => window.removeEventListener("bayora:logout", logout);
  }, [logout]);

  const login = async (email, password) => {
    const res = await api.login(email, password);
    setToken(res.access_token);
    setUser({ email: res.email, role: res.role });
  };

  return <AuthContext.Provider value={{ user, loading, login, logout }}>{children}</AuthContext.Provider>;
}

export const useAuth = () => useContext(AuthContext);
