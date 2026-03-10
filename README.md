# Cyber Farm

[English](./README.md) | [简体中文](./README_cn.md)

## For Humans

Copy this to your AI agent:

```text
Help me install cyber-farm: https://github.com/aqiu817/cyber-farm.git
Follow this install guide after cloning: https://raw.githubusercontent.com/aqiu817/cyber-farm/master/AGENT_INSTALL.md
```

Chinese prompt example:

```text
帮我安装 cyber-farm：https://github.com/aqiu817/cyber-farm.git
克隆后按这个安装指南继续执行：https://raw.githubusercontent.com/aqiu817/cyber-farm/master/AGENT_INSTALL_CN.md
```

> Agent-oriented setup docs:
> - English: [AGENT_INSTALL.md](./AGENT_INSTALL.md)
> - Chinese: [AGENT_INSTALL_CN.md](./AGENT_INSTALL_CN.md)

Cyber Farm is a lightweight farming game service with a browser UI and a JSON API for agents.

- Multi-session state isolation (`X-Farm-Session` / `cyber_farm_session`)
- Persistent session storage (`data/farm_sessions.json`)
- Agent-first API (`/api/state`, `/api/select`, `/api/action`, `/api/tick`, `/api/reset`, `/api/config`)
- Runtime tunables (`--auto-tick-seconds`, `--save-debounce-ms`)
- Minimal regression tests with `unittest`

## Quick Start

### Windows

```powershell
python .\app.py --host 0.0.0.0 --port 4173 --auto-tick-seconds 20 --save-debounce-ms 600
```

### Linux/macOS

```bash
python3 ./app.py --host 0.0.0.0 --port 4173 --auto-tick-seconds 20 --save-debounce-ms 600
```

Open:

- UI: `http://127.0.0.1:4173/`
- API state: `http://127.0.0.1:4173/api/state`
- Runtime config: `http://127.0.0.1:4173/api/config`

## View Agent Sessions In Browser

1. URL switch (recommended)
- Open: `http://127.0.0.1:4173/?s=<agent_session_id>`
- The page will bind that session and then remove `s` from the URL.

2. Hidden shortcut switch
- Focus the page and press `Ctrl+Shift+K`
- Paste the Agent `session_id` in the prompt and confirm.

## Development

```bash
python -m py_compile app.py
python -m unittest tests/test_app.py -v
```

## References

- Detailed API guide: `skills/cyber-farm/references/api.md`
- Agent install (EN): [AGENT_INSTALL.md](./AGENT_INSTALL.md)
- Agent install (CN): [AGENT_INSTALL_CN.md](./AGENT_INSTALL_CN.md)
