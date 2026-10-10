<div align="center">

<img src=".github/assets/ErisPulseLogo.png" width="180" alt="ErisPulse ConnHub" />

# ErisPulse ConnHub

**Connections hub module — manage all registered WS/SSE connections.**

A connection management module built on the ErisPulse 2.10 connection registry, providing chat commands, HTTP API, SSE event stream and a live panel.

<p>
  <a href="https://pypi.org/project/ErisPulse-ConnHub/"><img src="https://img.shields.io/pypi/v/ErisPulse-ConnHub?style=for-the-badge&logo=pypi&logoColor=white" alt="PyPI"></a>
  <a href="https://pypi.org/project/ErisPulse-ConnHub/"><img src="https://img.shields.io/badge/Python-3.10+-FFD43B?style=for-the-badge&logo=python&logoColor=blue" alt="Python"></a>
  <a href="./LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue?style=for-the-badge" alt="License"></a>
  <a href="https://github.com/ErisPulse/ErisPulse-ConnHub"><img src="https://img.shields.io/github/stars/ErisPulse/ErisPulse-ConnHub?style=for-the-badge&logo=github&color=brightgreen" alt="Stars"></a>
  <a href="https://pepy.tech/project/ErisPulse-ConnHub"><img src="https://img.shields.io/pepy/dt/ErisPulse-ConnHub?style=for-the-badge&color=blue" alt="Downloads"></a>
  <a href="https://github.com/ErisPulse/ErisPulse"><img src="https://img.shields.io/badge/Powered_by-ErisPulse-FF6B9D?style=for-the-badge&logo=bookstack&logoColor=white" alt="ErisPulse"></a>
</p>

<p>
  <a href="./README.md">简体中文</a> | <a href="./README.en.md">English</a>
</p>

</div>

---

## Introduction

ConnHub is a connection management module for the [ErisPulse](https://github.com/ErisPulse/ErisPulse/) framework. Since ErisPulse 2.10, connections (server-side WS / SSE / outbound WS) are registered in the framework connection registry. This module provides:

- Connection listing and stats (id / kind / namespace / owner / groups)
- Group management and targeted broadcast
- Connection close (subject to ownership checks)
- HTTP API and SSE live event stream
- Dashboard view: connections panel (live table + event stream)

Requires ErisPulse >= 2.10.0.

---

## Installation

```bash
epsdk install ErisPulse-ConnHub
```

---

## Commands

| Command | Description |
|---------|-------------|
| `/conn` | Show usage |
| `/conn list [kind]` | List connections, kind: `server` / `client` / `sse` |
| `/conn stats` | Registry stats by dimension |
| `/conn group add <id> <group>` | Add a connection to a group |
| `/conn group remove <id> <group>` | Remove a connection from a group |
| `/conn broadcast <group\|*> <message>` | Broadcast to a group (`*` = all) |
| `/conn close <id>` | Close a connection |

All commands require framework master permission.

---

## HTTP API

| Method | Path | Description |
|--------|------|-------------|
| GET | `/connhub/api/connections` | Connection list |
| GET | `/connhub/api/stats` | Connection stats |
| POST | `/connhub/api/broadcast` | Broadcast, body: `{"group": "...", "data": {...}, "timeout": 10}` |
| POST | `/connhub/api/close` | Close, body: `{"id": "...", "force": false}` |
| GET | `/connhub/events` | SSE stream (register/unregister/group changes + periodic snapshots) |

---

## Usage

```python
from ErisPulse import connections

# Any module: inspect current connections
for conn in connections.list():
    print(conn.id, conn.kind, conn.owner, conn.groups)

# Broadcast to a group (equivalent to the commands and API above)
result = await connections.broadcast({"text": "notice"}, group="room:1")
print(result.sent, result.failed)
```

---

## Configuration

```toml
[ConnHub]
enabled = true                  # enable module
api_enabled = true              # enable HTTP API and SSE
view_enabled = true             # register Dashboard view
allow_force_close = false       # allow force-closing connections owned by other modules
snapshot_interval_secs = 15     # panel snapshot interval in seconds (0 = off)
broadcast_timeout = 10.0        # per-connection send timeout for broadcast (seconds)
top_max = 20                    # max entries per list
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enabled` | bool | `true` | Enable module |
| `api_enabled` | bool | `true` | Enable HTTP API and SSE stream |
| `view_enabled` | bool | `true` | Register Dashboard connections view |
| `allow_force_close` | bool | `false` | Allow closing connections owned by other modules |
| `snapshot_interval_secs` | int | `15` | Panel snapshot push interval (seconds, 0 = off) |
| `broadcast_timeout` | float | `10.0` | Per-connection broadcast send timeout (seconds) |
| `top_max` | int | `20` | Max entries per list |

---

## Notes

1. Close permission belongs to the owning module; closing other modules' connections requires `allow_force_close`
2. The panel is provided as a Dashboard view (requires the Dashboard module); SSE stream at `/connhub/events`
3. Connections owned by a module are closed by the framework on module unload (2.10 behavior)

---

## References

- [ErisPulse](https://github.com/ErisPulse/ErisPulse/)
- [Connections & Broadcast docs](https://github.com/ErisPulse/ErisPulse/tree/main/docs/zh-CN/advanced/connections.md)
