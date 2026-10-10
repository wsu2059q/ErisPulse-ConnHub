from typing import Any, Optional

from ErisPulse import i18n

VALID_KINDS = ("server", "client", "sse")


class ConnHubService:

    def __init__(self, connections, logger):
        self._connections = connections
        self._logger = logger
        self.registered_total = 0
        self.unregistered_total = 0

    def list_dicts(self, kind: Optional[str] = None) -> list[dict[str, Any]]:
        conns = self._connections.list(kind=kind) if kind else self._connections.list()
        items = []
        for conn in sorted(conns, key=lambda c: c.id):
            items.append({
                "id": conn.id,
                "kind": conn.kind,
                "namespace": conn.namespace,
                "owner": conn.owner,
                "groups": sorted(conn.groups),
                "meta": dict(conn.meta),
            })
        return items

    def stats(self) -> dict[str, Any]:
        stats = dict(self._connections.stats())
        stats["registered_total"] = self.registered_total
        stats["unregistered_total"] = self.unregistered_total
        return stats

    def format_list(self, kind: Optional[str], top_max: int) -> str:
        items = self.list_dicts(kind=kind)
        if not items:
            return i18n.t("ConnHub.no_connections")
        lines = [i18n.t("ConnHub.list_header", count=len(items))]
        for item in items[:max(1, top_max)]:
            groups = ",".join(item["groups"]) or "-"
            ns = item["namespace"] or "-"
            lines.append(
                f"{item['id']} | {item['kind']} | ns={ns} | owner={item['owner'] or '-'} | groups={groups}"
            )
        hidden = len(items) - max(1, top_max)
        if hidden > 0:
            lines.append(i18n.t("ConnHub.list_truncated", count=hidden))
        return "\n".join(lines)

    def format_stats(self) -> str:
        stats = self.stats()
        lines = [i18n.t("ConnHub.stats_header", total=stats["total"])]
        for key in ("by_kind", "by_namespace", "by_owner"):
            part = stats.get(key) or {}
            rendered = " ".join(f"{k}={v}" for k, v in sorted(part.items()))
            lines.append(f"{key}: {rendered or '-'}")
        groups = stats.get("groups") or {}
        rendered = " ".join(f"{k}={v}" for k, v in sorted(groups.items()))
        lines.append(f"groups: {rendered or '-'}")
        lines.append(f"registered_total: {stats['registered_total']}")
        lines.append(f"unregistered_total: {stats['unregistered_total']}")
        return "\n".join(lines)

    async def broadcast(self, group: Optional[str], data: Any, timeout: float):
        kwargs = {"timeout": timeout}
        if group and group != "*":
            kwargs["group"] = group
        return await self._connections.broadcast(data, **kwargs)

    async def close(self, connection_id: str, force: bool = False) -> bool:
        return await self._connections.close(connection_id, force=force)

    def assign(self, connection_id: str, *groups: str) -> None:
        self._connections.assign(connection_id, *groups)

    def dismiss(self, connection_id: str, *groups: str) -> None:
        self._connections.dismiss(connection_id, *groups)

    def snapshot_payload(self) -> dict[str, Any]:
        return {
            "type": "snapshot",
            "stats": self.stats(),
            "connections": self.list_dicts(),
        }

    def list_card_html(self, kind: Optional[str], top_max: int, viz) -> str:
        import datetime

        items = self.list_dicts(kind=kind)
        total_all = len(self.list_dicts())
        if kind:
            title = f"连接列表 · {kind}"
            subtitle = f"过滤 kind={kind}，命中 {len(items)} 条 / 全部 {total_all} 条"
        else:
            title = "连接列表"
            subtitle = f"共 {len(items)} 条登记中的连接"
        by_kind: dict[str, int] = {}
        for item in self._connections.list():
            by_kind[item.kind] = by_kind.get(item.kind, 0) + 1
        overview = viz.kv_section(
            "按种类",
            [(k, v) for k, v in sorted(by_kind.items())] or [("-", "0")],
        )
        rows = "".join(viz.conn_row(item) for item in items[:max(1, top_max)])
        hidden = len(items) - max(1, top_max)
        more = f"<div class='dim' style='text-align:center;margin-top:8px'>…其余 {hidden} 条已省略</div>" if hidden > 0 else ""
        stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return (
            viz.head(title, subtitle)
            + f"<div class='body'>{overview}<div class='section'>"
            + f"<div class='section-title'>连接</div>{rows}{more}</div></div>"
            + viz.foot(f"ConnHub · {stamp}", f"展示上限 {max(1, top_max)}")
        )

    def stats_card_html(self, viz) -> str:
        import datetime

        stats = self.stats()
        by_kind = sorted((stats.get("by_kind") or {}).items())
        by_ns = sorted((stats.get("by_namespace") or {}).items())
        by_owner = sorted((stats.get("by_owner") or {}).items())
        groups = sorted((stats.get("groups") or {}).items())
        stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return (
            viz.head("连接池统计", f"共 {stats['total']} 条登记中的连接")
            + "<div class='body'>"
            + viz.nums([
                ("当前总数", stats["total"]),
                ("累计登记", stats["registered_total"]),
                ("累计注销", stats["unregistered_total"]),
                ("分组数", len(groups)),
            ])
            + viz.kv_section("按种类", by_kind or [("-", "0")])
            + viz.kv_section("按命名空间", by_ns or [("-", "0")])
            + viz.kv_section("按归属", by_owner or [("-", "0")])
            + viz.kv_section("业务分组", groups or [("-", "0")])
            + "</div>"
            + viz.foot(f"ConnHub · {stamp}", "server / client / sse")
        )

    @staticmethod
    def event_payload(action: str, data: dict) -> dict[str, Any]:
        payload = {"type": "connection", "action": action}
        payload.update({k: v for k, v in data.items() if not str(k).startswith("_")})
        return payload

    def on_connection_event(self, action: str) -> None:
        if action == "registered":
            self.registered_total += 1
        elif action == "unregistered":
            self.unregistered_total += 1
