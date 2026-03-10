# Changelog

## 2026-03-11

### Changed
- Promoted the project from demo labeling to a formal Cyber Farm release across code, UI text, skill metadata, and references.
- Renamed the skill package from `skills/cyber-farm-demo/` to `skills/cyber-farm/` and updated all related paths.
- Updated the runtime startup and agent docs to use production-facing wording.

### Added
- Added runtime config endpoint `GET /api/config` for agent-safe startup behavior (`autoTickSeconds`).
- Added configurable runtime options: `--auto-tick-seconds` and `--save-debounce-ms`.
- Added minimal regression tests in `tests/test_app.py` for state normalization, fertilize bonus behavior, and session persistence settings.

### Improved
- Added debounced session persistence writes in `SessionStore` to reduce write amplification.
- Updated frontend boot flow to read runtime config before starting auto tick and prevent overlapping auto tick requests.
- Updated skill guidance with an explicit agent playbook for deterministic session handling and recovery.

## 2026-03-10

### Added
- Created the first playable Cyber Farm web application in `skills/cyber-farm/assets/site/`.
- Added a Python entrypoint in `app.py` to serve both the web UI and the farm API.
- Added Windows and Linux launch scripts: `run.bat`, `run.sh`, and `scripts/serve-cyber-farm.ps1`.
- Added the first `cyber-farm` skill package with `SKILL.md` and `agents/openai.yaml`.
- Added an agent-readable HTTP JSON API with endpoints for state, plot selection, actions, ticking, reset, and health checks.
- Added browser-side `window.cyberFarm` helpers that mirror the HTTP API.
- Added multi-session isolation with `X-Farm-Session` / `cyber_farm_session` support.
- Added disk persistence for farm sessions in `data/farm_sessions.json`.
- Added API reference documentation in `skills/cyber-farm/references/api.md`.
- Added open-source asset reference notes in `skills/cyber-farm/references/open-source-assets.md`.
- Added attribution records for crop sprites and UI font.
- Added `.gitignore` entries for runtime data and Python cache files.

### Changed
- Evolved the interface from a simple cyber landing page into a playable farm game layout.
- Reworked the main farm view to support plot selection, sowing, watering, harvesting, clearing, inventory, warehouse, and shop flows.
- Replaced placeholder crop art with a real CC0 pixel crop spritesheet from OpenGameArt.
- Fixed crop growth frame ordering so crops visually grow larger toward maturity.
- Switched the whole UI to a local pixel font (`Silkscreen`) for a consistent retro game style.
- Improved visual polish with pixel-like panels, controls, status ribbons, and footer hints.
- Updated the service model so browser users and agent users operate the same backend state instead of separate frontend-only logic.
- Updated launcher defaults to allow LAN access by binding to `0.0.0.0` where appropriate.
- Updated the skill instructions so agents prefer the JSON API over DOM scraping.

### Fixed
- Fixed incorrect sprite rendering caused by scaling the crop container instead of the source sprite frame size.
- Fixed reversed growth-stage rendering where mature crops appeared smaller than earlier stages.
- Fixed LAN accessibility issues caused by scripts binding only to `127.0.0.1`.
- Fixed the original single-user state design so multiple users no longer share one global farm state.

### Notes
- Current persistence is file-based and suitable for small deployments.
- For wider public distribution, the next likely upgrades are reverse proxy + HTTPS, stronger persistence such as SQLite/Postgres, and basic auth/rate limiting/observability.

### 2026-03-10 Continued
- Added a local pixel font (Silkscreen) and switched the whole UI to pixel-style text rendering.
- Added session/status ribbons and footer hints for better multi-user and agent awareness.
- Added a day/weather/time model to the farm state.
- Added weather-aware growth and moisture behavior in the backend tick loop.
- Added daily mission state and reward claiming through the API.
- Added front-end mission progress UI, reward button, and weather/time display.
- Added visual time-of-day and weather overlays to the page.
