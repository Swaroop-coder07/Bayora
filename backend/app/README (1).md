# Quick manual test plan

1. `GET /api/security/health` should return `{"ok": true, ...}`.
2. `POST /api/security/regression` should return six synthetic category results and a run ID.
3. Open the returned run's `/verify` endpoint; it should return `valid: true`.
4. Download `/api/security/report.json` and `/api/security/report.csv`.
5. In a local disposable environment only, edit one field in the stored JSON file without changing `sha256`, then verify again. It should return `valid: false`. Do not do this to production records.
6. Check the `note` field on regression results: the current suite is explicitly simulated demo mode.
