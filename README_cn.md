# Cyber Farm

[English](./README.md) | [简体中文](./README_cn.md)

Cyber Farm 是一个轻量级农场游戏服务，提供浏览器 UI 和面向 Agent 的 JSON API。

- 多会话状态隔离（`X-Farm-Session` / `cyber_farm_session`）
- 会话状态持久化（`data/farm_sessions.json`）
- Agent 优先 API（`/api/state`、`/api/select`、`/api/action`、`/api/tick`、`/api/reset`、`/api/config`）
- 运行参数可配置（`--auto-tick-seconds`、`--save-debounce-ms`）
- 使用 `unittest` 的最小回归测试

## Agent 安装指南

- OpenClaw / 通用 Agent 接入（中文）：[`AGENT_INSTALL_CN.md`](./AGENT_INSTALL_CN.md)
- OpenClaw / General Agent onboarding (English): [`AGENT_INSTALL.md`](./AGENT_INSTALL.md)

## 快速开始

### Windows

```powershell
python .\app.py --host 0.0.0.0 --port 4173 --auto-tick-seconds 20 --save-debounce-ms 600
```

### Linux/macOS

```bash
python3 ./app.py --host 0.0.0.0 --port 4173 --auto-tick-seconds 20 --save-debounce-ms 600
```

访问地址：

- UI：`http://127.0.0.1:4173/`
- API 状态：`http://127.0.0.1:4173/api/state`
- 运行配置：`http://127.0.0.1:4173/api/config`

## 在浏览器查看 Agent 会话

可使用以下两种隐藏切换方式：

1. URL 参数切换（推荐）
- 直接打开：`http://127.0.0.1:4173/?s=<agent_session_id>`
- 页面会自动绑定该会话，然后把地址栏中的 `s` 参数清理掉。

2. 隐藏快捷键切换
- 聚焦页面后按 `Ctrl+Shift+K`
- 在弹窗中粘贴 Agent 的 `session_id` 并确认。

说明：

- 切换成功后，页面顶部“会话”标识会变化。
- 同一个浏览器配置文件同一时间只持有一个 cookie 会话。
- 如需并行观察多个会话，建议使用不同浏览器或无痕窗口。

## 开发

语法检查：

```bash
python -m py_compile app.py
```

运行测试：

```bash
python -m unittest tests/test_app.py -v
```

详细 API 文档：`skills/cyber-farm/references/api.md`
