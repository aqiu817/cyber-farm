# Cyber Farm

[English](./README.md) | [简体中文](./README_cn.md)

Cyber Farm is a lightweight farming game service with a browser UI and a JSON API for agents.

- Multi-session state isolation (`X-Farm-Session` / `cyber_farm_session`)
- Persistent session storage (`data/farm_sessions.json`)
- Agent-first API (`/api/state`, `/api/select`, `/api/action`, `/api/tick`, `/api/reset`, `/api/config`)
- Runtime tunables (`--auto-tick-seconds`, `--save-debounce-ms`)
- Minimal regression tests with `unittest`

## Project Structure

```text
.
├─ app.py
├─ run.bat
├─ run.sh
├─ scripts/
│  └─ serve-cyber-farm.ps1
├─ skills/
│  └─ cyber-farm/
│     ├─ SKILL.md
│     ├─ agents/openai.yaml
│     ├─ assets/site/
│     └─ references/
├─ tests/
│  └─ test_app.py
└─ data/
   └─ farm_sessions.json (runtime generated)
```

## Requirements

- Python 3.10+
- Windows / macOS / Linux

## Quick Start

### Windows

```powershell
python .\app.py --host 0.0.0.0 --port 4173 --auto-tick-seconds 20 --save-debounce-ms 600
```

or

```powershell
.\run.bat 4173
```

### Linux/macOS

```bash
python3 app.py --host 0.0.0.0 --port 4173 --auto-tick-seconds 20 --save-debounce-ms 600
```

or

```bash
./run.sh 4173
```

Open:

- UI: `http://127.0.0.1:4173/`
- API state: `http://127.0.0.1:4173/api/state`
- Runtime config: `http://127.0.0.1:4173/api/config`

## Runtime Options

- `--host`: bind address (default `0.0.0.0`)
- `--port`: listen port (default `4173`)
- `--auto-tick-seconds`: frontend auto tick interval; `0` disables auto tick (default `20`)
- `--save-debounce-ms`: debounce window for persistence writes (default `600`)

## API Overview

- `GET /api/health`
- `GET /api/config`
- `GET /api/state`
- `POST /api/select` with `{ "plot": number }`
- `POST /api/action` with:
  - `plant` (`seed`)
  - `water`
  - `harvest`
  - `clear`
  - `buy` (`seed`)
  - `sell` (`amount`)
  - `fertilize`
  - `upgrade_plot`
  - `claim_reward`
- `POST /api/tick`
- `POST /api/reset`

Detailed API guide: `skills/cyber-farm/references/api.md`

## Agent Integration

For agents (e.g. OpenClaw), use API directly instead of UI automation.

Recommended startup flow:

1. `GET /api/config`
2. `GET /api/state`
3. Store `session` and reuse it via `X-Farm-Session`
4. Use returned `state` from each mutation response as source of truth

## Development

Syntax check:

```bash
python -m py_compile app.py
```

Run tests:

```bash
python -m unittest tests/test_app.py -v
```

## License / Assets

Project code follows repository policy.
Asset attribution files:

- `skills/cyber-farm/assets/site/img/ATTRIBUTION.txt`
- `skills/cyber-farm/assets/site/img/FONT_ATTRIBUTION.txt`
