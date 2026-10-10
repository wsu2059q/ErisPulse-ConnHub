from ErisPulse import sdk

_ICON = (
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">'
    '<circle cx="5" cy="12" r="2.5"/><circle cx="19" cy="6" r="2.5"/>'
    '<circle cx="19" cy="18" r="2.5"/><path d="M7.5 12h4M13.5 10.8l3-3.2M13.5 13.2l3 3.2"/></svg>'
)

_VIEW_HTML = '''
<h1 class="page-title">连接中心</h1>
<p class="ch-subtitle">框架登记的全部 WS/SSE/出站连接，实时更新</p>

<div class="ch-cards" id="ch-cards"></div>

<div class="card">
    <div class="card-body" style="padding:0">
        <table class="ch-table">
            <thead>
                <tr><th>ID</th><th>种类</th><th>命名空间</th><th>归属</th><th>分组</th></tr>
            </thead>
            <tbody id="ch-tbody">
                <tr><td colspan="5" class="ch-empty">加载中...</td></tr>
            </tbody>
        </table>
    </div>
</div>

<h1 class="page-title" style="margin-top:24px;font-size:16px">事件流</h1>
<div class="card"><div class="card-body"><div id="ch-events" class="ch-events"></div></div></div>
'''

_VIEW_CSS = '''
.ch-subtitle { color: var(--tx-s); margin-bottom: 16px; font-size: 14px; }
.ch-cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px; margin-bottom: 16px; }
.ch-card { background: var(--bg-s); border: 1px solid var(--bd); border-radius: 8px; padding: 12px 14px; }
.ch-card .label { font-size: 12px; color: var(--tx-t); }
.ch-card .value { font-size: 22px; font-weight: 700; color: var(--accent); margin-top: 4px; }
.ch-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.ch-table th {
    text-align: left; padding: 10px 12px; font-weight: 600;
    color: var(--tx-s); border-bottom: 2px solid var(--bd); background: var(--bg-s); white-space: nowrap;
}
.ch-table td { padding: 8px 12px; border-bottom: 1px solid var(--bd); color: var(--tx-p); vertical-align: middle; }
.ch-table tbody tr:hover { background: var(--bg-s); }
.ch-empty { text-align: center; color: var(--tx-t); padding: 32px 12px !important; }
.ch-cid { font-family: monospace; font-size: 12px; }
.ch-badge {
    display: inline-block; padding: 2px 8px; border-radius: 4px;
    font-size: 11px; font-weight: 600;
}
.ch-badge-server { background: rgba(59,130,246,0.15); color: #3b82f6; }
.ch-badge-client { background: rgba(34,197,94,0.15); color: #22c55e; }
.ch-badge-sse { background: rgba(234,179,8,0.15); color: #eab308; }
.ch-dim { color: var(--tx-t); }
.ch-group { background: var(--bg-t); border-radius: 4px; padding: 1px 8px; font-size: 12px; margin-right: 4px; }
.ch-events {
    font-family: monospace; font-size: 12px; height: 200px; overflow-y: auto;
    color: var(--tx-s); background: var(--bg-t); border-radius: 6px; padding: 8px 12px;
}
.ch-events div { padding: 2px 0; border-bottom: 1px dashed var(--bd); word-break: break-all; }
'''

_VIEW_JS = '''
var ConnHubView = {
    es: null,
    _timer: null,
    _reconnectDelay: 2000,

    init: function() {
        this.refresh();
        this.connectSse();
        var self = this;
        this._timer = setInterval(function() { self.refresh(); }, 5000);
    },

    destroy: function() {
        if (this._timer) { clearInterval(this._timer); this._timer = null; }
        if (this.es) { try { this.es.close(); } catch(e) {} this.es = null; }
    },

    refresh: function() {
        var self = this;
        this._fetch('/ConnHub/api/stats').then(function(stats) { self.renderStats(stats); });
        this._fetch('/ConnHub/api/connections').then(function(conns) { self.renderRows(conns || []); });
    },

    renderStats: function(stats) {
        var parts = Object.entries(stats.by_kind || {}).map(function(kv) { return kv[0] + ': ' + kv[1]; }).join(' · ') || '-';
        var cards = [
            ['当前总数', stats.total],
            ['种类', parts],
            ['累计登记', stats.registered_total],
            ['累计注销', stats.unregistered_total]
        ];
        var el = document.getElementById('ch-cards');
        if (!el) return;
        el.innerHTML = cards.map(function(c) {
            return '<div class="ch-card"><div class="label">' + c[0] + '</div>'
                + '<div class="ch-value value">' + ConnHubView._esc(String(c[1])) + '</div></div>';
        }).join('');
    },

    renderRows: function(conns) {
        var tbody = document.getElementById('ch-tbody');
        if (!tbody) return;
        if (!conns.length) {
            tbody.innerHTML = '<tr><td colspan="5" class="ch-empty">暂无连接</td></tr>';
            return;
        }
        tbody.innerHTML = conns.map(function(c) {
            var groups = (c.groups || []).length
                ? c.groups.map(function(g) { return '<span class="ch-group">' + ConnHubView._esc(g) + '</span>'; }).join('')
                : '<span class="ch-dim">-</span>';
            return '<tr>'
                + '<td class="ch-cid">' + ConnHubView._esc(c.id) + '</td>'
                + '<td><span class="ch-badge ch-badge-' + ConnHubView._esc(c.kind) + '">' + ConnHubView._esc(c.kind) + '</span></td>'
                + '<td>' + (c.namespace ? ConnHubView._esc(c.namespace) : '<span class="ch-dim">-</span>') + '</td>'
                + '<td>' + (c.owner ? ConnHubView._esc(c.owner) : '<span class="ch-dim">-</span>') + '</td>'
                + '<td>' + groups + '</td>'
                + '</tr>';
        }).join('');
    },

    connectSse: function() {
        var self = this;
        try { this.es = new EventSource('/ConnHub/events'); } catch(e) { return; }
        this.es.onmessage = function(ev) {
            var data;
            try { data = JSON.parse(ev.data); } catch(e) { return; }
            if (data.type === 'snapshot') {
                self.renderStats(data.stats || {});
                self.renderRows(data.connections || []);
                return;
            }
            if (data.type === 'connection') { self.logEvent(ev.data); self.refresh(); }
        };
        this.es.onerror = function() {
            if (self.es) { try { self.es.close(); } catch(e) {} self.es = null; }
            setTimeout(function() { self.connectSse(); }, self._reconnectDelay);
            self._reconnectDelay = Math.min(self._reconnectDelay * 1.5, 15000);
        };
    },

    logEvent: function(text) {
        var box = document.getElementById('ch-events');
        if (!box) return;
        var div = document.createElement('div');
        var now = new Date().toLocaleTimeString();
        div.textContent = '[' + now + '] ' + text;
        box.prepend(div);
        while (box.childElementCount > 100) box.lastChild.remove();
    },

    _esc: function(s) { var d = document.createElement('div'); d.textContent = s; return d.innerHTML; },

    _fetch: function(url) {
        return fetch(url, { headers: { 'Authorization': 'Bearer ' + (localStorage.getItem('__ep_tk__') || '') } })
            .then(function(r) { return r.json(); });
    }
};

function ConnHubViewInit() { ConnHubView.init(); }
'''


class DashboardIntegration:

    GROUP = "connhub"
    GROUP_TITLE = "连接中心"
    GROUP_TITLE_EN = "ConnHub"

    def __init__(self, logger):
        self.logger = logger
        self._registered = False

    def setup(self):
        try:
            if not (hasattr(sdk, "Dashboard") and sdk.Dashboard):
                self.logger.debug("Dashboard not available, skipping integration")
                return
            sdk.Dashboard.register_view(
                id="ConnHubPanel",
                title="连接面板", title_en="Connections",
                icon_svg=_ICON,
                html_content=_VIEW_HTML,
                js_content=_VIEW_JS,
                css_content=_VIEW_CSS,
                loader="ConnHubViewInit",
                group=self.GROUP,
                group_title=self.GROUP_TITLE,
                group_title_en=self.GROUP_TITLE_EN,
            )
            self._registered = True
            self.logger.info("ConnHub Dashboard view ready")
        except Exception as e:
            self.logger.warning(f"Dashboard view setup failed: {e}")

    def teardown(self):
        if not self._registered:
            return
        try:
            sdk.Dashboard.unregister_view("ConnHubPanel")
        except Exception:
            pass
        self._registered = False
