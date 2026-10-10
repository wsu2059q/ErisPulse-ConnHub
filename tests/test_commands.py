from ErisPulse_Testing import create_command_event

from ErisPulse import connections


def _register_fake(connbot, namespace="Demo", owner="Demo", kind="server", groups=()):
    conn = connbot.make_fake_conn()
    cid = connections.register(conn, namespace=namespace, owner=owner, kind=kind)
    for g in groups:
        connections.assign(cid, g)
    return conn, cid


async def test_conn_usage_hint(connbot):
    await connbot.dispatch(create_command_event("conn"))
    connbot.assert_reply_contains("用法")


async def test_conn_list_empty(connbot):
    await connbot.dispatch(create_command_event("conn list"))
    connbot.assert_reply_contains("没有")


async def test_conn_list_shows_connection(connbot):
    _, cid = _register_fake(connbot)
    await connbot.dispatch(create_command_event("conn list"))
    connbot.assert_reply_contains("共 1 条连接")
    connbot.assert_reply_contains(cid)


async def test_conn_list_kind_filter(connbot):
    _register_fake(connbot, kind="server")
    _register_fake(connbot, kind="sse")
    await connbot.dispatch(create_command_event("conn list sse"))
    reply = connbot.last_reply.text
    assert "共 1 条连接" in reply
    assert "| sse |" in reply


async def test_conn_list_invalid_kind(connbot):
    await connbot.dispatch(create_command_event("conn list bogus"))
    connbot.assert_reply_contains("未知的连接种类")


async def test_conn_stats(connbot):
    _register_fake(connbot)
    _register_fake(connbot)
    await connbot.dispatch(create_command_event("conn stats"))
    connbot.assert_reply_contains("共 2 条")
    connbot.assert_reply_contains("by_kind: server=2")


async def test_conn_group_add_remove(connbot):
    _, cid = _register_fake(connbot)
    await connbot.dispatch(create_command_event(f"conn group add {cid} room:1"))
    connbot.assert_reply_contains("已加入分组 room:1")
    assert connections.list(group="room:1")

    await connbot.dispatch(create_command_event(f"conn group remove {cid} room:1"))
    connbot.assert_reply_contains("已移出分组 room:1")
    assert connections.list(group="room:1") == []


async def test_conn_group_add_not_found(connbot):
    await connbot.dispatch(create_command_event("conn group add nope:dead room:1"))
    connbot.assert_reply_contains("不存在或已断开")


async def test_conn_broadcast(connbot):
    conn, cid = _register_fake(connbot, groups=["room:9"])
    await connbot.dispatch(create_command_event("conn broadcast room:9 你好"))
    connbot.assert_reply_contains("目标 1 条")
    connbot.assert_reply_contains("成功 1")
    assert conn.sent


async def test_conn_broadcast_star(connbot):
    conn, _ = _register_fake(connbot)
    await connbot.dispatch(create_command_event("conn broadcast * 全员通知"))
    connbot.assert_reply_contains("目标 1 条")
    assert conn.sent


async def test_conn_close(connbot):
    conn, cid = _register_fake(connbot)
    await connbot.dispatch(create_command_event(f"conn close {cid}"))
    connbot.assert_reply_contains("连接已关闭")
    assert conn.closed is True
    assert connections.list() == []


async def test_conn_close_not_found(connbot):
    await connbot.dispatch(create_command_event("conn close nope:dead"))
    connbot.assert_reply_contains("不存在或已断开")


async def test_non_master_denied(connbot):
    from ErisPulse_Testing import create_message_event

    _register_fake(connbot)
    await connbot.dispatch(create_message_event("/conn list", user_id="stranger"))
    assert all("共 1 条连接" not in (r.text or "") for r in connbot.replies)
