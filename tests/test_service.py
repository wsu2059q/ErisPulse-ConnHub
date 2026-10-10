import pytest
from ErisPulse import connections
from ErisPulse.Core.Bases.errors import ConnectionNotFoundError

from ConnHub.Service import ConnHubService


@pytest.fixture
async def service(connbot):
    return connbot.hub._service


async def test_register_and_list(connbot, service):
    conn = connbot.make_fake_conn()
    cid = connections.register(conn, namespace="Demo", owner="Demo", kind="server")
    items = service.list_dicts()
    assert len(items) == 1
    assert items[0]["id"] == cid
    assert items[0]["kind"] == "server"
    assert items[0]["namespace"] == "Demo"
    assert items[0]["owner"] == "Demo"
    connections.unregister(conn)


async def test_list_kind_filter(connbot, service):
    server = connbot.make_fake_conn()
    sse = connbot.make_fake_conn()
    connections.register(server, namespace="A", owner="A", kind="server")
    connections.register(sse, namespace="B", owner="B", kind="sse")
    assert [i["kind"] for i in service.list_dicts(kind="sse")] == ["sse"]
    assert len(service.list_dicts()) == 2


async def test_format_list_empty(connbot, service):
    text = service.format_list(None, 20)
    assert "没有" in text


async def test_format_list_rows(connbot, service):
    conn = connbot.make_fake_conn()
    cid = connections.register(conn, namespace="Demo", owner="Demo", kind="server")
    text = service.format_list(None, 20)
    assert "共 1 条连接" in text
    assert cid in text
    assert "server" in text


async def test_format_list_truncation(connbot, service):
    for i in range(5):
        connections.register(connbot.make_fake_conn(), namespace="N", owner="N", kind="server")
    text = service.format_list(None, 2)
    assert "其余 3 条已省略" in text


async def test_stats_dimensions(connbot, service):
    connections.register(connbot.make_fake_conn(), namespace="X", owner="OwnerX", kind="client")
    connections.register(connbot.make_fake_conn(), namespace="X", owner="OwnerX", kind="client")
    stats = service.stats()
    assert stats["total"] == 2
    assert stats["by_kind"] == {"client": 2}
    assert stats["by_namespace"] == {"X": 2}
    assert stats["by_owner"] == {"OwnerX": 2}
    text = service.format_stats()
    assert "by_kind: client=2" in text


async def test_group_assign_and_broadcast(connbot, service):
    conn = connbot.make_fake_conn()
    other = connbot.make_fake_conn()
    cid = connections.register(conn, namespace="A", owner="A", kind="server")
    other_id = connections.register(other, namespace="A", owner="A", kind="server")

    service.assign(cid, "room:1")
    assert service.list_dicts(kind="server")[0]["groups"] == ["room:1"] or \
        any(i["groups"] == ["room:1"] for i in service.list_dicts())

    result = await service.broadcast("room:1", {"hello": 1}, timeout=2)
    assert result.sent == [cid]
    assert conn.sent == [{"hello": 1}]
    assert other.sent == []

    result_all = await service.broadcast("*", {"all": 1}, timeout=2)
    assert set(result_all.sent) == {cid, other_id}

    service.dismiss(cid, "room:1")
    result = await service.broadcast("room:1", {"hello": 2}, timeout=2)
    assert result.total == 0


async def test_broadcast_to_sse_uses_send(connbot, service):
    sse = connbot.make_fake_conn()
    cid = connections.register(sse, namespace="ConnHub", owner="ConnHub", kind="sse")
    result = await service.broadcast(None, {"type": "ping"}, timeout=2)
    assert cid in result.sent
    assert {"type": "ping"} in sse.sent


async def test_close_and_unregister(connbot, service):
    conn = connbot.make_fake_conn()
    cid = connections.register(conn, namespace="A", owner="A", kind="server")

    ok = await service.close(cid)
    assert ok is True
    assert conn.closed is True
    assert service.list_dicts() == []
    with pytest.raises(ConnectionNotFoundError):
        await service.close(cid)


async def test_snapshot_and_event_payload(connbot, service):
    connections.register(connbot.make_fake_conn(), namespace="A", owner="A", kind="server")
    payload = service.snapshot_payload()
    assert payload["type"] == "snapshot"
    assert payload["stats"]["total"] == 1
    assert len(payload["connections"]) == 1

    event = ConnHubService.event_payload("registered", {"connection_id": "x", "_trace_id": "t"})
    assert event == {"type": "connection", "action": "registered", "connection_id": "x"}


async def test_lifecycle_counters(connbot, service):
    from ErisPulse import sdk as sdk_mod

    await sdk_mod.lifecycle.emit("connection.registered", {"connection_id": "a"})
    await sdk_mod.lifecycle.emit("connection.registered", {"connection_id": "b"})
    await sdk_mod.lifecycle.emit("connection.unregistered", {"connection_id": "a"})
    assert service.registered_total == 2
    assert service.unregistered_total == 1
    text = service.format_stats()
    assert "registered_total: 2" in text
    assert "unregistered_total: 1" in text
