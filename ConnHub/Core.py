import asyncio

from ErisPulse import connections, i18n, respond, router, sdk
from ErisPulse.Core.Bases import BaseModule, ModuleMeta
from ErisPulse.Core.Event import command
from ErisPulse.loaders import ModuleLoadStrategy

from .Config import ConnHubConfig
from .I18n import ConnHubI18n
from .Panel import PANEL_HTML
from .Service import VALID_KINDS, ConnHubService
from .Visualizer import CardVisualizer


class Main(BaseModule):

    ConfigClass = ConnHubConfig
    I18nClass = ConnHubI18n

    def __init__(self):
        self.sdk = sdk
        self.logger = sdk.logger.get_child("ConnHub")
        self._service = ConnHubService(connections, self.logger)
        self._viz = CardVisualizer(sdk, self.logger)
        self._snapshot_task = None

    @staticmethod
    def get_load_strategy() -> ModuleLoadStrategy:
        return ModuleLoadStrategy(lazy_load=False, priority=30)

    @staticmethod
    def get_meta() -> ModuleMeta:
        return ModuleMeta(
            name="ConnHub",
            description="连接中心：查看/广播/关闭框架登记的 WS/SSE 连接，提供 HTTP API 与实时面板",
            version="0.1.0",
            author="ErisPulse-devs",
            group="运维",
            tags=["连接池", "广播", "SSE", "面板"],
            min_sdk_version="2.10.0",
        )

    async def on_load(self, event: dict) -> bool:
        if not self.cfg.enabled:
            self.logger.info("连接中心未启用（enabled=false）")
            return True

        self._register_lifecycle()
        self._register_commands()
        if self.cfg.api_enabled:
            self._register_routes()
        self._snapshot_task = self.spawn(self._snapshot_loop())
        self.logger.info(i18n.t("ConnHub.module_loaded", event=event))
        return True

    async def on_unload(self, event: dict) -> bool:
        if self._snapshot_task is not None:
            self._snapshot_task.cancel()
            await asyncio.gather(self._snapshot_task, return_exceptions=True)
            self._snapshot_task = None
        self.logger.info(i18n.t("ConnHub.module_unloaded", event=event))
        return True

    def _register_lifecycle(self):
        @sdk.lifecycle.on("connection.registered")
        async def _on_registered(data):
            self._service.on_connection_event("registered")
            await self._push_event("registered", data)

        @sdk.lifecycle.on("connection.unregistered")
        async def _on_unregistered(data):
            self._service.on_connection_event("unregistered")
            await self._push_event("unregistered", data)

        @sdk.lifecycle.on("connection.group.joined")
        async def _on_group_joined(data):
            await self._push_event("group.joined", data)

        @sdk.lifecycle.on("connection.group.left")
        async def _on_group_left(data):
            await self._push_event("group.left", data)

    async def _push_event(self, action: str, data: dict):
        payload = ConnHubService.event_payload(action, data)
        await self._broadcast_to_watchers(payload)

    async def _broadcast_to_watchers(self, payload):
        try:
            await connections.broadcast(
                payload,
                namespace="ConnHub",
                kind="sse",
                timeout=self.cfg.broadcast_timeout,
            )
        except Exception as e:
            self.logger.warning(f"推送事件到面板失败: {e}")

    async def _snapshot_loop(self):
        while True:
            try:
                interval = int(self.cfg.snapshot_interval_secs)
                if interval <= 0:
                    await asyncio.sleep(5)
                    continue
                await asyncio.sleep(interval)
                await self._broadcast_to_watchers(self._service.snapshot_payload())
            except asyncio.CancelledError:
                raise
            except Exception as e:
                self.logger.warning(f"快照推送异常: {e}")
                await asyncio.sleep(5)

    def _register_commands(self):
        @command("conn", master=True, help="连接中心管理")
        async def conn_handler(event):
            await event.reply(
                "用法: /conn list [kind] | /conn stats | /conn group add|remove <id> <组名> | "
                "/conn broadcast <组名|*> <消息> | /conn close <id>"
            )

        @command("conn list", master=True, help="列出登记中的连接", args="[kind:str]")
        async def conn_list_handler(event, kind: str = ""):
            if kind and kind not in VALID_KINDS:
                await event.reply(i18n.t("ConnHub.invalid_kind", kind=kind))
                return
            await self._reply_card(
                event,
                lambda: self._service.list_card_html(kind or None, self.cfg.top_max, self._viz),
                self._service.format_list(kind or None, self.cfg.top_max),
            )

        @command("conn stats", master=True, help="查看连接池统计")
        async def conn_stats_handler(event):
            await self._reply_card(
                event,
                lambda: self._service.stats_card_html(self._viz),
                self._service.format_stats(),
            )

        @command("conn group add", master=True, help="把连接加入分组", args="<cid:str> <group:str>")
        async def conn_group_add_handler(event, cid: str, group: str):
            try:
                self._service.assign(cid, group)
            except Exception as e:
                await event.reply(self._conn_error_text(e, cid))
                return
            await event.reply(i18n.t("ConnHub.group_assigned", id=cid, group=group))

        @command("conn group remove", master=True, help="把连接移出分组", args="<cid:str> <group:str>")
        async def conn_group_remove_handler(event, cid: str, group: str):
            try:
                self._service.dismiss(cid, group)
            except Exception as e:
                await event.reply(self._conn_error_text(e, cid))
                return
            await event.reply(i18n.t("ConnHub.group_dismissed", id=cid, group=group))

        @command("conn broadcast", master=True, help="向分组广播消息", args="<group:str> <text:rest>")
        async def conn_broadcast_handler(event, group: str, text: str):
            result = await self._service.broadcast(group, {"type": "message", "from": "conn", "text": text},
                                                   self.cfg.broadcast_timeout)
            await event.reply(i18n.t(
                "ConnHub.broadcast_done",
                total=result.total,
                sent=len(result.sent),
                failed=len(result.failed),
            ))

        @command("conn close", master=True, help="关闭连接", args="<cid:str>")
        async def conn_close_handler(event, cid: str):
            try:
                await self._service.close(cid, force=self.cfg.allow_force_close)
            except Exception as e:
                await event.reply(self._conn_error_text(e, cid))
                return
            await event.reply(i18n.t("ConnHub.close_done", id=cid))

    async def _reply_card(self, event, html_fn, fallback_text: str):
        if self.cfg.render_card:
            png = await self._viz.render(html_fn(), theme=self.cfg.theme)
            if png is not None:
                try:
                    await event.reply(png, method="Image")
                    return
                except Exception as e:
                    self.logger.warning(f"图片回复失败，降级文本: {e}")
        await event.reply(fallback_text)

    def _conn_error_text(self, error: Exception, cid: str) -> str:
        from ErisPulse import ConnectionNotFoundError, ConnectionPermissionError

        if isinstance(error, ConnectionNotFoundError):
            return i18n.t("ConnHub.close_not_found", id=cid)
        if isinstance(error, ConnectionPermissionError):
            owner = getattr(error, "owner", "") or ""
            return i18n.t("ConnHub.close_forbidden", id=cid, owner=owner)
        return f"{type(error).__name__}: {error}"

    def _register_routes(self):
        @router.get("/api/connections")
        async def api_connections():
            return respond(self._service.list_dicts())

        @router.get("/api/stats")
        async def api_stats():
            return respond(self._service.stats())

        @router.post("/api/broadcast")
        async def api_broadcast(request):
            try:
                body = await request.json()
            except Exception:
                return respond({"error": "invalid_json"}, status_code=400)
            data = body.get("data") if isinstance(body, dict) else None
            if data is None:
                return respond({"error": "data_required"}, status_code=400)
            group = body.get("group") or None
            try:
                timeout = float(body.get("timeout", self.cfg.broadcast_timeout))
            except (TypeError, ValueError):
                timeout = self.cfg.broadcast_timeout
            result = await self._service.broadcast(group, data, timeout)
            return respond({
                "total": result.total,
                "sent": result.sent,
                "failed": {cid: str(exc) for cid, exc in result.failed.items()},
                "excluded": result.excluded,
                "ok": result.ok,
            })

        @router.post("/api/close")
        async def api_close(request):
            try:
                body = await request.json()
            except Exception:
                return respond({"error": "invalid_json"}, status_code=400)
            cid = body.get("id") if isinstance(body, dict) else None
            if not cid:
                return respond({"error": "id_required"}, status_code=400)
            force = bool(body.get("force")) and self.cfg.allow_force_close
            try:
                await self._service.close(cid, force=force)
            except Exception as e:
                from ErisPulse import ConnectionNotFoundError, ConnectionPermissionError

                if isinstance(e, ConnectionNotFoundError):
                    return respond({"error": "not_found", "id": cid}, status_code=404)
                if isinstance(e, ConnectionPermissionError):
                    return respond({"error": "permission_denied", "id": cid}, status_code=403)
                return respond({"error": str(e)}, status_code=500)
            return respond({"closed": cid})

        @router.sse("/events")
        async def event_stream(sse):
            sse.join_group("connhub:watchers")
            try:
                await sse.send(self._service.snapshot_payload(), event="snapshot")
            except Exception:
                return
            while True:
                await asyncio.sleep(60)

        if self.cfg.panel_enabled:
            @router.get("/panel")
            async def panel():
                return PANEL_HTML, 200, {"Content-Type": "text/html; charset=utf-8"}

            router.register_home_entry(
                name={"i18n": "ConnHub.panel_title", "default": "ConnHub 连接面板"},
                url="/connhub/panel",
                icon_svg='<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="5" cy="12" r="2.5"/><circle cx="19" cy="6" r="2.5"/><circle cx="19" cy="18" r="2.5"/><path d="M7.5 12h4M13.5 10.8 16.5 7.6M13.5 13.2l3 3.2"/></svg>',
            )
