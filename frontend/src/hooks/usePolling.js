import { useCallback, useEffect, useState } from "react";

/** Loads data once and re-fetches every `ms` milliseconds. */
export function usePolling(fn, ms = 10000) {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const reload = useCallback(() => fn().then((d) => { setData(d); setError(""); }).catch((e) => setError(e.message)), [fn]);
  useEffect(() => {
    reload();
    if (!ms) return undefined;
    const t = setInterval(reload, ms);
    return () => clearInterval(t);
  }, [reload, ms]);
  return { data, error, reload };
}
