# OpenClaw / Agent Installation Guide (Cyber Farm)

This guide is for OpenClaw or any HTTP-capable agent runtime to self-install, connect, and start operating Cyber Farm.

## 0. Clone the repository first

If the project is not already local, clone it before any setup:

```bash
git clone https://github.com/aqiu817/cyber-farm.git
cd cyber-farm
```

Then continue with the steps below.

## 1. Prerequisites

- Git
- Python 3.10+
- Available port (default `4173`)


## 2. Start the service

### Windows (PowerShell)

```powershell
python .\app.py --host 127.0.0.1 --port 4173 --auto-tick-seconds 20 --save-debounce-ms 600
```

### Linux/macOS

```bash
python3 ./app.py --host 127.0.0.1 --port 4173 --auto-tick-seconds 20 --save-debounce-ms 600
```

## 3. Health checks

```bash
curl http://127.0.0.1:4173/api/health
curl http://127.0.0.1:4173/api/config
curl -i http://127.0.0.1:4173/api/state
```

Expected:

- `/api/health` returns `ok=true`
- `/api/config` includes `config.autoTickSeconds`
- `/api/state` includes `session` and `state`

## 4. Agent tool endpoints

Expose these endpoints to your agent:

1. `GET /api/config`
2. `GET /api/state`
3. `POST /api/select`
4. `POST /api/action`
5. `POST /api/tick`
6. `POST /api/reset`

Base URL: `http://127.0.0.1:4173`

Session rule:

- First call `GET /api/state` and capture `session`
- Reuse it in header: `X-Farm-Session: <session_id>`

## 5. System prompt snippet

```text
You are operating Cyber Farm through JSON API only.
Base URL: http://127.0.0.1:4173

Rules:
1) Call GET /api/config first, then GET /api/state.
2) Persist and reuse one session id via X-Farm-Session.
3) Prefer API calls over DOM/browser clicks.
4) After every mutating API call, use returned state as source of truth.
5) Before critical decisions, refresh state (especially when auto tick > 0).
6) If an action fails, read error and recover using returned state.
```

## 6. First successful operation flow

1. `GET /api/config`
2. `GET /api/state`
3. `POST /api/select` with `{ "plot": 4 }`
4. `POST /api/action` with `{ "type": "plant", "seed": "turnip" }`
5. `POST /api/action` with `{ "type": "water" }`

Done when all calls return `ok=true` and returned `state` updates as expected.
