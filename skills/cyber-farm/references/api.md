# Agent API

Start the service from the repo root:

```bash
python3 app.py --host 127.0.0.1 --port 4173 --auto-tick-seconds 20 --save-debounce-ms 600
```

Base URL:

```text
http://127.0.0.1:4173
```

## Session model

The service is multi-session.

- Browsers receive a `cyber_farm_session` cookie automatically.
- Agents and CLI tools can reuse that cookie or pass `X-Farm-Session` explicitly.
- Each session gets an isolated farm state.
- Session state is persisted to `data/farm_sessions.json`.

## Health check

```bash
curl http://127.0.0.1:4173/api/health
```

## Runtime config

```bash
curl http://127.0.0.1:4173/api/config
```

The response includes:

- `config.autoTickSeconds`

## Read state

```bash
curl -i http://127.0.0.1:4173/api/state
```

The response includes:

- `session`
- `state.state.day`
- `state.state.tickInDay`
- `state.state.weather`
- `state.state.mission`
- `state.plots[*].soilLevel`
- `state.plots[*].fertilized`
- `state.meta.weatherLabel`
- `state.meta.ticksPerDay`

## Select a plot

```bash
curl -X POST http://127.0.0.1:4173/api/select \
  -H "Content-Type: application/json" \
  -H "X-Farm-Session: your-session-id" \
  -d '{"plot": 4}'
```

## Run an action

Supported action types:

- `plant` with `seed`
- `water`
- `harvest`
- `clear`
- `buy` with `seed`
- `sell` with `amount`
- `fertilize`
- `upgrade_plot`
- `claim_reward`

Examples:

```bash
curl -X POST http://127.0.0.1:4173/api/action \
  -H "Content-Type: application/json" \
  -H "X-Farm-Session: your-session-id" \
  -d '{"type": "plant", "seed": "turnip"}'
```

```bash
curl -X POST http://127.0.0.1:4173/api/action \
  -H "Content-Type: application/json" \
  -H "X-Farm-Session: your-session-id" \
  -d '{"type": "claim_reward"}'
```

## Tick and reset

```bash
curl -X POST http://127.0.0.1:4173/api/tick \
  -H "X-Farm-Session: your-session-id"

curl -X POST http://127.0.0.1:4173/api/reset \
  -H "X-Farm-Session: your-session-id"
```

## Agent workflow

1. `GET /api/state` and store the returned session id.
2. Reuse `X-Farm-Session` for all later requests.
3. Read `day`, `weather`, and `mission` before choosing actions.
4. Use `POST /api/select` plus `POST /api/action` to operate the farm.
5. Use `POST /api/tick` to advance time intentionally during tests.
6. Claim rewards only when `mission.progress >= mission.target`.
7. Use `POST /api/reset` before tests that require a known clean state.


## Agent playbook

### Startup checklist

1. `GET /api/config` and read `config.autoTickSeconds`.
2. `GET /api/state` and record `session`.
3. Reuse this session via `X-Farm-Session` for all later calls.

### Safe operation loop

1. Read latest state (`GET /api/state`) before major decisions, especially when auto tick is enabled.
2. Select target plot (`POST /api/select`).
3. Execute action (`POST /api/action`, or `POST /api/tick` / `POST /api/reset`).
4. Use returned `state` as the next truth source.

### Deterministic verification flow

1. `POST /api/reset`
2. `POST /api/select` with target plot
3. Run action sequence (`plant`, `fertilize`, `water`, `harvest`, etc.)
4. Assert against returned JSON fields, not rendered UI text

### Notes for robust agents

- For long-running workflows, refresh with `GET /api/state` between critical steps.
- Avoid mixing multiple sessions in one logical task.
- If an action fails with `ok=false`, use returned `error` and attached `state` to recover.

