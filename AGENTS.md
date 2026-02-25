# AGENTS.md

## Cursor Cloud specific instructions

### Project Overview
AI-driven Cultivation World Simulator (修仙世界模拟器) — a xianxia open-world simulator with a Python/FastAPI backend and Vue 3/PixiJS frontend. See `README.md` and `docs/QUICK_START_AI.md` for full details.

### Services

| Service | Command | Port | Notes |
|---------|---------|------|-------|
| Backend (FastAPI) | `python src/server/main.py` | 8002 | Binds to `127.0.0.1`. Add `--dev` to also auto-start frontend. |
| Frontend (Vite) | `cd web && npx vite --host 0.0.0.0` | 5173 | Proxies `/api`, `/ws`, `/assets` to backend on 8002. Use `--host 0.0.0.0` for external access. |

### Running Tests
- **Backend**: `pytest -v --cov=src --cov-report=term --cov-fail-under=60` (from repo root)
- **Frontend**: `cd web && npm run test:run`
- See `CONTRIBUTING.md` for full test requirements.

### Known Gotchas
- The backend's `start()` function binds to `127.0.0.1:8002`. If you need it accessible externally, run via uvicorn directly: `uvicorn src.server.main:app --host 0.0.0.0 --port 8002`.
- `python src/server/main.py` (without `--dev`) tries to serve the built frontend from `web/dist/`. In dev, use `--dev` flag or run the Vite dev server separately.
- `webbrowser.open()` is called on startup; in headless environments this produces harmless dbus errors.
- The game requires LLM configuration (API Key + Base URL) before a new game can start. Without a real LLM, the world initializes fine but the simulation loop will log errors for AI-driven NPC decisions.
- `npm run build` (and `tsc --noEmit`) has pre-existing TypeScript errors related to i18n types. The Vite dev server (which uses esbuild) is not affected and runs fine.
- Python packages install to `~/.local/` by default; ensure `~/.local/bin` is on `PATH` (e.g. for `pytest`, `uvicorn`).
- No ESLint config exists for the frontend; linting is limited to TypeScript type-checking.
