# Cyber Farm

[English](./README.md) | [简体中文](./README_cn.md)

Cyber Farm 是一个轻量级农场游戏服务，提供浏览器 UI 和面向 Agent 的 JSON API。

- 多会话状态隔离（`X-Farm-Session` / `cyber_farm_session`）
- 会话状态持久化（`data/farm_sessions.json`）
- Agent 优先 API（`/api/state`、`/api/select`、`/api/action`、`/api/tick`、`/api/reset`、`/api/config`）
- 运行参数可配置（`--auto-tick-seconds`、`--save-debounce-ms`）
- 使用 `unittest` 的最小回归测试

## 项目结构

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
   └─ farm_sessions.json（运行时生成）
```

## 环境要求

- Python 3.10+
- Windows / macOS / Linux

## 快速开始

### Windows

```powershell
python .\app.py --host 0.0.0.0 --port 4173 --auto-tick-seconds 20 --save-debounce-ms 600
```

或

```powershell
.\run.bat 4173
```

### Linux/macOS

```bash
python3 app.py --host 0.0.0.0 --port 4173 --auto-tick-seconds 20 --save-debounce-ms 600
```

或

```bash
./run.sh 4173
```

访问地址：

- UI：`http://127.0.0.1:4173/`
- API 状态：`http://127.0.0.1:4173/api/state`
- 运行配置：`http://127.0.0.1:4173/api/config`

## 运行参数

- `--host`：绑定地址（默认 `0.0.0.0`）
- `--port`：监听端口（默认 `4173`）
- `--auto-tick-seconds`：前端自动推进间隔；`0` 表示关闭（默认 `20`）
- `--save-debounce-ms`：会话写盘防抖时间（默认 `600`）

## API 概览

- `GET /api/health`
- `GET /api/config`
- `GET /api/state`
- `POST /api/select`，请求体 `{ "plot": number }`
- `POST /api/action`，支持：
  - `plant`（带 `seed`）
  - `water`
  - `harvest`
  - `clear`
  - `buy`（带 `seed`）
  - `sell`（带 `amount`）
  - `fertilize`
  - `upgrade_plot`
  - `claim_reward`
- `POST /api/tick`
- `POST /api/reset`

详细 API 文档：`skills/cyber-farm/references/api.md`

## Agent 接入

对于 Agent（例如 OpenClaw），建议直接调用 API，而不是操作页面 DOM。

推荐启动流程：

1. 调用 `GET /api/config`
2. 调用 `GET /api/state`
3. 保存 `session`，后续通过 `X-Farm-Session` 复用
4. 每次变更请求后，以返回的 `state` 作为最新事实来源

## 开发

语法检查：

```bash
python -m py_compile app.py
```

运行测试：

```bash
python -m unittest tests/test_app.py -v
```

## 许可证 / 素材归属

代码遵循仓库策略。素材归属文件：

- `skills/cyber-farm/assets/site/img/ATTRIBUTION.txt`
- `skills/cyber-farm/assets/site/img/FONT_ATTRIBUTION.txt`

## ?????? Agent ??

???????? Agent ???????????????????

1. URL ????????
- ?????`http://127.0.0.1:4173/?s=<agent_session_id>`
- ??????????????????? `s` ??????

2. ???????
- ?????? `Ctrl+Shift+K`
- ?????? Agent ? `session_id` ????

???

- ????????????????????
- ??????????????????? cookie ???
- ??????????????????????????

