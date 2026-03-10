---
name: cyber-farm
description: Run and operate a cyber farm web app through both a browser UI and a JSON API. Use this skill when the user wants an agent or CLI program to inspect farm state, select plots, plant crops, water, harvest, fertilize, upgrade plot soil, buy seeds, sell produce, or reset the farm.
---

# Cyber Farm

This skill maintains a cyber farm service served by the repo-level `app.py`. It supports both a browser interface and an agent-friendly HTTP JSON API.

## Use this skill when

- The user wants a lightweight cyber farm application
- The user wants a locally runnable web app without framework setup
- The user wants a starter that can grow into a richer farm simulation
- The user wants an agent or CLI to operate the farm programmatically
- The user wants session-isolated farm state for multiple concurrent users

## Workflow

1. Start the service from repo root:
   - `python app.py --host 127.0.0.1 --port 4173 --auto-tick-seconds 20 --save-debounce-ms 600`
2. For browser use, open `http://127.0.0.1:4173/`.
3. For agent use, call the HTTP API documented in `references/api.md`.
4. Capture the session id from `X-Farm-Session` or reuse the `cyber_farm_session` cookie.
5. Reuse the returned `state` payload after every action instead of scraping HTML.
6. When adding art, prefer sources listed in `references/open-source-assets.md`.

## Agent execution rules

- Prefer `GET /api/state` + `POST /api/select` + `POST /api/action` over DOM interaction.
- Always read `GET /api/config` once at startup and treat `config.autoTickSeconds` as authoritative.
- If auto tick is enabled, refresh state before every critical decision to avoid stale assumptions.
- Reuse a stable session id for a full task; do not mix sessions within one mission flow.
- Use `POST /api/reset` before deterministic checks or scripted checks.
- After each mutating call, trust and use the returned `state` in response body as the next source of truth.

## Files

- `assets/site/index.html`: page structure
- `assets/site/styles.css`: visuals and sprite rendering
- `assets/site/app.js`: browser client backed by the JSON API
- `references/api.md`: HTTP API contract and agent playbook
- `references/open-source-assets.md`: candidate art packs and license notes
- `agents/openai.yaml`: UI-facing metadata and default agent prompt
- `data/farm_sessions.json`: persisted multi-session farm state created at runtime

## Validation hints

- Syntax check: `python -m py_compile app.py`
- Minimal regression: `python -m unittest tests/test_app.py -v`
