# OpenClaw / Agent 安装与接入指南（Cyber Farm）

本文档面向 OpenClaw 或任意可发 HTTP 请求的 Agent。目标是让 Agent **自行完成接入并开始操作农场**。

## 1. 适用范围

- OpenClaw（或同类 Agent 框架）
- 自定义 Agent Runtime（支持 HTTP 工具调用）
- CLI Agent（可执行 curl / Invoke-RestMethod）

---

## 2. 前置条件

- Python 3.10+
- 本项目代码已在本机可访问
- 可用端口（默认 `4173`）

---

## 3. 启动服务

在项目根目录执行：

### Windows (PowerShell)

```powershell
python .\app.py --host 127.0.0.1 --port 4173 --auto-tick-seconds 20 --save-debounce-ms 600
```

### Linux/macOS

```bash
python3 ./app.py --host 127.0.0.1 --port 4173 --auto-tick-seconds 20 --save-debounce-ms 600
```

说明：

- `--auto-tick-seconds`：前端自动推进间隔（秒），`0` 表示关闭
- `--save-debounce-ms`：会话写盘防抖（毫秒）

---

## 4. 服务自检（必须）

### Windows (PowerShell)

```powershell
Invoke-RestMethod http://127.0.0.1:4173/api/health
Invoke-RestMethod http://127.0.0.1:4173/api/config
Invoke-RestMethod http://127.0.0.1:4173/api/state
```

### Linux/macOS

```bash
curl http://127.0.0.1:4173/api/health
curl http://127.0.0.1:4173/api/config
curl -i http://127.0.0.1:4173/api/state
```

通过标准：

- `/api/health` 返回 `ok=true`
- `/api/config` 有 `config.autoTickSeconds`
- `/api/state` 返回 `session` 和 `state`

---

## 5. 给 Agent 配置 HTTP 工具

建议至少暴露以下 6 个接口给 Agent：

1. `GET /api/config`
2. `GET /api/state`
3. `POST /api/select`
4. `POST /api/action`
5. `POST /api/tick`
6. `POST /api/reset`

统一基地址：`http://127.0.0.1:4173`

请求头规则：

- 首次 `GET /api/state` 拿到 `session`
- 后续所有请求带 `X-Farm-Session: <session>`

---

## 6. 给 Agent 的系统提示词（可直接粘贴）

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

---

## 7. Agent 首次可执行流程（自助）

目标：让 Agent 自己完成“选地 -> 播种 -> 浇水”的最小闭环。

1. `GET /api/config`
2. `GET /api/state`（保存 `session`）
3. `POST /api/select` body: `{ "plot": 4 }`
4. `POST /api/action` body: `{ "type": "plant", "seed": "turnip" }`
5. `POST /api/action` body: `{ "type": "water" }`

成功判定：

- 每步返回 `ok=true`
- 返回体中 `state` 连续可用
- 目标地块 `growth` 有增长

---

## 8. 可用动作速查

`POST /api/action` 的 `type` 支持：

- `plant`（需 `seed`）
- `water`
- `harvest`
- `clear`
- `buy`（需 `seed`）
- `sell`（需 `amount`）
- `fertilize`
- `upgrade_plot`
- `claim_reward`

---

## 9. 常见问题

### Q1: Agent 报 unknown action

- 检查 `type` 是否拼写正确（例如 `upgrade_plot` 不是 `upgradePlot`）

### Q2: 每次请求像是新用户

- 没有复用 `X-Farm-Session`
- 修复：首次拿到 `session` 后全程复用

### Q3: 状态变化太快

- `autoTickSeconds` 可能较小
- 修复：重启服务时设置 `--auto-tick-seconds 0`

### Q4: 重启后状态不一致

- 默认会持久化到 `data/farm_sessions.json`
- 需要可重复测试时，先执行 `POST /api/reset`

---

## 10. 完成标准（Done）

满足以下 4 项即接入完成：

1. Agent 能读取 `/api/config` 与 `/api/state`
2. Agent 能稳定复用同一个 `session`
3. Agent 能成功执行至少 3 个动作（如 `plant`/`water`/`sell`）
4. Agent 能在错误响应后继续恢复执行

---

## 11. 参考文档

- API 详细文档：`skills/cyber-farm/references/api.md`
- 技能说明：`skills/cyber-farm/SKILL.md`
- 项目说明：`README.md` / `README_cn.md`
