import asyncio

import pytest

from ConnHub.Core import Main


def make_fake_conn():
    from ErisPulse.Core.Bases.websocket import _ConnectionIdentity

    class FakeConnImpl(_ConnectionIdentity):
        def __init__(self):
            super().__init__()
            self.sent = []
            self.closed = False

        async def send(self, data=None, **kwargs):
            self.sent.append(data)

        async def send_json(self, data, mode="text"):
            self.sent.append(data)

        async def send_text(self, data):
            self.sent.append(data)

        async def close(self, code=1000, reason=None, *, force=False):
            self.closed = True

    return FakeConnImpl()


@pytest.fixture
async def connbot(make_testbot):
    from ErisPulse import connections, i18n

    prev_lang = i18n.get_language()
    i18n.set_language("zh-CN")

    async with make_testbot(config={"ErisPulse.master.users": {"test": ["tester"]}}) as bot:
        await bot.load_module(Main)

        from ErisPulse import module as module_mgr

        hub = module_mgr.get("ConnHub")

        cfg = hub.cfg
        cfg.snapshot_interval_secs = 0
        cfg.top_max = 20
        cfg.render_card = False
        hub.cfg = cfg

        for conn in list(connections.list()):
            connections.unregister(conn)
        await asyncio.sleep(0.05)

        hub._service.registered_total = 0
        hub._service.unregistered_total = 0

        bot.hub = hub
        bot.make_fake_conn = make_fake_conn
        yield bot

    i18n.set_language(prev_lang)
