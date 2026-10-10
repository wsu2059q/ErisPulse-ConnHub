PANEL_HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ConnHub</title>
<style>
:root { color-scheme: dark; }
* { box-sizing: border-box; }
body { margin: 0; font-family: system-ui, "Segoe UI", sans-serif; background: #14161a; color: #d7dae0; }
header { padding: 16px 24px; border-bottom: 1px solid #262a31; display: flex; align-items: baseline; gap: 12px; }
h1 { font-size: 18px; margin: 0; }
#live { font-size: 12px; color: #6f7783; }
main { padding: 20px 24px; max-width: 1080px; margin: 0 auto; }
.cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 12px; margin-bottom: 20px; }
.card { background: #1b1f26; border: 1px solid #262a31; border-radius: 8px; padding: 12px 14px; }
.card .label { font-size: 12px; color: #8b93a1; }
.card .value { font-size: 22px; margin-top: 4px; }
h2 { font-size: 14px; color: #8b93a1; margin: 20px 0 8px; font-weight: 600; }
table { width: 100%; border-collapse: collapse; font-size: 13px; }
th, td { text-align: left; padding: 7px 10px; border-bottom: 1px solid #262a31; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 320px; }
th { color: #8b93a1; font-weight: 600; }
#events { font-size: 12px; font-family: ui-monospace, Consolas, monospace; background: #1b1f26; border: 1px solid #262a31; border-radius: 8px; padding: 10px 12px; height: 180px; overflow-y: auto; }
#events div { padding: 2px 0; border-bottom: 1px dashed #22262d; }
.empty { color: #6f7783; font-size: 13px; }
</style>
</head>
<body>
<header><h1>ConnHub 连接面板</h1><span id="live">connecting...</span></header>
<main>
  <div class="cards" id="cards"></div>
  <h2>连接列表</h2>
  <table>
    <thead><tr><th>ID</th><th>种类</th><th>命名空间</th><th>归属</th><th>分组</th></tr></thead>
    <tbody id="rows"><tr><td colspan="5" class="empty">加载中...</td></tr></tbody>
  </table>
  <h2>事件流</h2>
  <div id="events"></div>
</main>
<script>
const fmt = (v) => v === undefined || v === null || v === "" ? "-" : v;
function renderStats(stats) {
  const cards = [["总计", stats.total], ["种类", Object.entries(stats.by_kind || {}).map(([k, v]) => k + ": " + v).join(" ") || "-"],
                 ["累计登记", stats.registered_total], ["累计注销", stats.unregistered_total]];
  document.getElementById("cards").innerHTML = cards.map(([l, v]) =>
    '<div class="card"><div class="label">' + l + '</div><div class="value">' + fmt(v) + "</div></div>").join("");
}
function renderRows(conns) {
  const rows = document.getElementById("rows");
  if (!conns.length) { rows.innerHTML = '<tr><td colspan="5" class="empty">暂无连接</td></tr>'; return; }
  rows.innerHTML = conns.map(c =>
    "<tr><td>" + c.id + "</td><td>" + c.kind + "</td><td>" + fmt(c.namespace) + "</td><td>" + fmt(c.owner) +
    "</td><td>" + (c.groups.length ? c.groups.join(", ") : "-") + "</td></tr>").join("");
}
async function refresh() {
  try {
    const res = await fetch("api/stats", {headers: {"Accept": "application/json"}});
    if (res.ok) renderStats(await res.json());
    const res2 = await fetch("api/connections", {headers: {"Accept": "application/json"}});
    if (res2.ok) renderRows(await res2.json());
  } catch (e) { document.getElementById("live").textContent = "fetch failed"; }
}
function logEvent(text) {
  const box = document.getElementById("events");
  const div = document.createElement("div");
  const now = new Date().toLocaleTimeString();
  div.textContent = "[" + now + "] " + text;
  box.prepend(div);
  while (box.childElementCount > 100) box.lastChild.remove();
}
refresh();
setInterval(refresh, 5000);
const es = new EventSource("events");
es.onopen = () => { document.getElementById("live").textContent = "live"; };
es.onerror = () => { document.getElementById("live").textContent = "reconnecting..."; };
es.onmessage = (ev) => {
  let data;
  try { data = JSON.parse(ev.data); } catch (e) { return; }
  if (data.type === "snapshot") { renderStats(data.stats); renderRows(data.connections); return; }
  if (data.type === "connection") { logEvent(ev.data); refresh(); }
};
</script>
</body>
</html>
"""
