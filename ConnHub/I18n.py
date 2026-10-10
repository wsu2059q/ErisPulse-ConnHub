from ErisPulse.Core.Bases import BaseI18n, I18nKey


class ConnHubI18n(BaseI18n):

    enabled: I18nKey = I18nKey(
        default="Enable module",
        zh_CN="是否启用模块",
        zh_TW="是否啟用模組",
        en="Enable module",
        ja="モジュールを有効化",
        ru="Включить модуль",
    )
    api_enabled: I18nKey = I18nKey(
        default="Enable HTTP API and SSE event stream",
        zh_CN="启用 HTTP API 与 SSE 事件流",
        zh_TW="啟用 HTTP API 與 SSE 事件流",
        en="Enable HTTP API and SSE event stream",
        ja="HTTP API と SSE イベントストリームを有効化",
        ru="Включить HTTP API и поток событий SSE",
    )
    panel_enabled: I18nKey = I18nKey(
        default="Enable built-in web panel",
        zh_CN="启用内置连接面板网页",
        zh_TW="啟用內建連線面板網頁",
        en="Enable built-in web panel",
        ja="内蔵ウェブパネルを有効化",
        ru="Включить встроенную веб-панель",
    )
    allow_force_close: I18nKey = I18nKey(
        default="Allow closing connections owned by other modules (skip ownership check)",
        zh_CN="允许关闭其他模块归属的连接（跳过归属校验）",
        zh_TW="允許關閉其他模組歸屬的連線（跳過歸屬校驗）",
        en="Allow closing connections owned by other modules (skip ownership check)",
        ja="他モジュール所有の接続を閉じることを許可（所有権チェックを省略）",
        ru="Разрешить закрытие соединений других модулей (без проверки владельца)",
    )
    snapshot_interval_secs: I18nKey = I18nKey(
        default="Snapshot push interval in seconds (0 = off)",
        zh_CN="向面板推送全量快照的间隔秒数（0 关闭）",
        zh_TW="向面板推送全量快照的間隔秒數（0 關閉）",
        en="Snapshot push interval in seconds (0 = off)",
        ja="スナップショット推送間隔（秒）（0 で無効）",
        ru="Интервал отправки снапшотов в секундах (0 = выкл.)",
    )
    broadcast_timeout: I18nKey = I18nKey(
        default="Per-connection send timeout for broadcast (seconds)",
        zh_CN="广播时单条连接的发送超时秒数",
        zh_TW="廣播時單條連線的傳送超時秒數",
        en="Per-connection send timeout for broadcast (seconds)",
        ja="ブロードキャストの接続ごとの送信タイムアウト（秒）",
        ru="Таймаут отправки на одно соединение при рассылке (сек.)",
    )
    top_max: I18nKey = I18nKey(
        default="Max connections shown in one list",
        zh_CN="连接列表单次展示的最大条数",
        zh_TW="連線列表單次展示的最大條數",
        en="Max connections shown in one list",
        ja="リスト1回の最大表示件数",
        ru="Максимум соединений в одном списке",
    )
    render_card: I18nKey = I18nKey(
        default="Render command output as image cards via Takumi (fallback to text)",
        zh_CN="命令输出用 Takumi 渲染为卡片（不可用时降级文本）",
        zh_TW="命令輸出用 Takumi 渲染為卡片（不可用時降級文本）",
        en="Render command output as image cards via Takumi (fallback to text)",
        ja="コマンド出力を Takumi でカード画像化（不可時はテキスト）",
        ru="Рендер вывода команд в карточки через Takumi (иначе текст)",
    )
    theme: I18nKey = I18nKey(
        default="Card color theme (auto = light/dark by time)",
        zh_CN="卡片配色 (auto=按时间自动切深浅色)",
        zh_TW="卡片配色 (auto=按時間自動切深淺色)",
        en="Card color theme (auto = light/dark by time)",
        ja="カード配色（auto=時間で自動切替）",
        ru="Тема карточек (auto = светлая/тёмная по времени)",
    )
    module_loaded: I18nKey = I18nKey(
        default="ConnHub loaded: {event}",
        zh_CN="连接中心已加载: {event}",
        zh_TW="連線中心已載入: {event}",
        en="ConnHub loaded: {event}",
        ja="ConnHub を読み込みました: {event}",
        ru="ConnHub загружен: {event}",
    )
    module_unloaded: I18nKey = I18nKey(
        default="ConnHub unloaded: {event}",
        zh_CN="连接中心已卸载: {event}",
        zh_TW="連線中心已卸載: {event}",
        en="ConnHub unloaded: {event}",
        ja="ConnHub を解除しました: {event}",
        ru="ConnHub выгружен: {event}",
    )
    no_connections: I18nKey = I18nKey(
        default="No connections registered",
        zh_CN="当前没有登记中的连接",
        zh_TW="當前沒有登記中的連線",
        en="No connections registered",
        ja="登録中の接続はありません",
        ru="Нет зарегистрированных соединений",
    )
    list_header: I18nKey = I18nKey(
        default="{count} connection(s):",
        zh_CN="共 {count} 条连接：",
        zh_TW="共 {count} 條連線：",
        en="{count} connection(s):",
        ja="{count} 件の接続：",
        ru="Соединений: {count}",
    )
    list_truncated: I18nKey = I18nKey(
        default="...and {count} more",
        zh_CN="…其余 {count} 条已省略",
        zh_TW="…其餘 {count} 條已省略",
        en="...and {count} more",
        ja="…他 {count} 件を省略",
        ru="…ещё {count}",
    )
    stats_header: I18nKey = I18nKey(
        default="Connection stats (total {total}):",
        zh_CN="连接统计（共 {total} 条）：",
        zh_TW="連線統計（共 {total} 條）：",
        en="Connection stats (total {total}):",
        ja="接続統計（合計 {total}）：",
        ru="Статистика соединений (всего {total}):",
    )
    broadcast_done: I18nKey = I18nKey(
        default="Broadcast finished: target {total}, sent {sent}, failed {failed}",
        zh_CN="广播完成：目标 {total} 条，成功 {sent}，失败 {failed}",
        zh_TW="廣播完成：目標 {total} 條，成功 {sent}，失敗 {failed}",
        en="Broadcast finished: target {total}, sent {sent}, failed {failed}",
        ja="ブロードキャスト完了：対象 {total}、成功 {sent}、失敗 {failed}",
        ru="Рассылка завершена: цель {total}, отправлено {sent}, ошибок {failed}",
    )
    close_done: I18nKey = I18nKey(
        default="Connection closed: {id}",
        zh_CN="连接已关闭: {id}",
        zh_TW="連線已關閉: {id}",
        en="Connection closed: {id}",
        ja="接続を閉じました: {id}",
        ru="Соединение закрыто: {id}",
    )
    close_not_found: I18nKey = I18nKey(
        default="Connection not found: {id}",
        zh_CN="连接不存在或已断开: {id}",
        zh_TW="連線不存在或已斷開: {id}",
        en="Connection not found: {id}",
        ja="接続が見つかりません: {id}",
        ru="Соединение не найдено: {id}",
    )
    close_forbidden: I18nKey = I18nKey(
        default="Permission denied: connection {id} is owned by {owner}",
        zh_CN="权限不足：连接 {id} 归属于 {owner}，可在配置中开启 allow_force_close",
        zh_TW="權限不足：連線 {id} 歸屬於 {owner}，可在配置中開啟 allow_force_close",
        en="Permission denied: connection {id} is owned by {owner}",
        ja="権限がありません: 接続 {id} は {owner} の所有です",
        ru="Доступ запрещён: соединение {id} принадлежит {owner}",
    )
    group_assigned: I18nKey = I18nKey(
        default="Connection {id} joined group {group}",
        zh_CN="连接 {id} 已加入分组 {group}",
        zh_TW="連線 {id} 已加入分組 {group}",
        en="Connection {id} joined group {group}",
        ja="接続 {id} をグループ {group} に追加しました",
        ru="Соединение {id} добавлено в группу {group}",
    )
    group_dismissed: I18nKey = I18nKey(
        default="Connection {id} left group {group}",
        zh_CN="连接 {id} 已移出分组 {group}",
        zh_TW="連線 {id} 已移出分組 {group}",
        en="Connection {id} left group {group}",
        ja="接続 {id} をグループ {group} から外しました",
        ru="Соединение {id} удалено из группы {group}",
    )
    panel_title: I18nKey = I18nKey(
        default="ConnHub connections panel",
        zh_CN="ConnHub 连接面板",
        zh_TW="ConnHub 連線面板",
        en="ConnHub connections panel",
        ja="ConnHub 接続パネル",
        ru="Панель соединений ConnHub",
    )
    invalid_kind: I18nKey = I18nKey(
        default="Unknown connection kind: {kind} (server/client/sse)",
        zh_CN="未知的连接种类: {kind}（可选 server/client/sse）",
        zh_TW="未知的連線種類: {kind}（可選 server/client/sse）",
        en="Unknown connection kind: {kind} (server/client/sse)",
        ja="不明な接続種別: {kind}（server/client/sse）",
        ru="Неизвестный тип соединения: {kind} (server/client/sse)",
    )
