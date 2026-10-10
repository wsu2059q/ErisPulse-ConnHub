from ErisPulse_Testing import create_command_event

from ErisPulse import connections


class FakeTakumi:
    def __init__(self):
        self.calls = []

    def render_html(self, body, stylesheets=None, width=None, height=None, lang=None, **kw):
        self.calls.append((body, stylesheets, width))
        return b"FAKEPNG"


def _register_fake(connbot, kind="server", groups=()):
    conn = connbot.make_fake_conn()
    cid = connections.register(conn, namespace="Demo", owner="Demo", kind=kind)
    for g in groups:
        connections.assign(cid, g)
    return conn, cid


async def test_list_card_html_content(connbot):
    _, cid = _register_fake(connbot, groups=["room:1"])
    html = connbot.hub._service.list_card_html(None, 20, connbot.hub._viz)
    assert cid in html
    assert "server" in html
    assert "room:1" in html
    assert "ns=Demo" in html


async def test_stats_card_html_content(connbot):
    _register_fake(connbot, kind="sse")
    html = connbot.hub._service.stats_card_html(connbot.hub._viz)
    assert "连接池统计" in html
    assert "按种类" in html
    assert "sse" in html


async def test_card_render_with_takumi(connbot):
    connbot.hub._viz._takumi_inst = FakeTakumi()
    cfg = connbot.hub.cfg
    cfg.render_card = True
    connbot.hub.cfg = cfg

    _, cid = _register_fake(connbot)
    await connbot.dispatch(create_command_event("conn list"))
    msg = connbot.last_reply
    assert any(seg.get("type") == "image" for seg in msg.segments)
    body, css, width = connbot.hub._viz._takumi_inst.calls[0]
    assert cid in body
    assert width == connbot.hub._viz.CARD_WIDTH


async def test_card_fallback_without_takumi(connbot):
    cfg = connbot.hub.cfg
    cfg.render_card = True
    connbot.hub.cfg = cfg

    _register_fake(connbot)
    await connbot.dispatch(create_command_event("conn stats"))
    connbot.assert_reply_contains("连接统计")


async def test_card_render_disabled(connbot):
    connbot.hub._viz._takumi_inst = FakeTakumi()
    await connbot.dispatch(create_command_event("conn stats"))
    assert connbot.hub._viz._takumi_inst.calls == []
    connbot.assert_reply_contains("连接统计")
