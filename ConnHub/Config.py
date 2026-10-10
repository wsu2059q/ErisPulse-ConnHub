from dataclasses import dataclass, field

from ErisPulse.Core.Bases import BaseConfig


@dataclass
class ConnHubConfig(BaseConfig):

    api_enabled: bool = field(
        default=True,
        metadata={
            "description": {"i18n": "ConnHub.api_enabled", "default": "启用 HTTP API 与 SSE 事件流"},
            "ui": {"widget": "switch", "group": "api", "order": 2},
        },
    )
    view_enabled: bool = field(
        default=True,
        metadata={
            "description": {"i18n": "ConnHub.view_enabled", "default": "注册 Dashboard 连接面板视图"},
            "ui": {"widget": "switch", "group": "api", "order": 3},
        },
    )
    allow_force_close: bool = field(
        default=False,
        metadata={
            "description": {"i18n": "ConnHub.allow_force_close", "default": "允许关闭其他模块归属的连接（跳过归属校验）"},
            "ui": {"widget": "switch", "group": "api", "order": 4},
        },
    )
    snapshot_interval_secs: int = field(
        default=15,
        metadata={
            "description": {"i18n": "ConnHub.snapshot_interval_secs", "default": "向面板推送全量快照的间隔秒数（0 关闭）"},
            "ui": {"widget": "number", "group": "api", "order": 5},
        },
    )
    broadcast_timeout: float = field(
        default=10.0,
        metadata={
            "description": {"i18n": "ConnHub.broadcast_timeout", "default": "广播时单条连接的发送超时秒数"},
            "ui": {"widget": "number", "group": "api", "order": 6},
        },
    )
    top_max: int = field(
        default=20,
        metadata={
            "description": {"i18n": "ConnHub.top_max", "default": "连接列表单次展示的最大条数"},
            "ui": {"widget": "number", "group": "basic", "order": 7},
        },
    )
    render_card: bool = field(
        default=True,
        metadata={
            "description": {"i18n": "ConnHub.render_card", "default": "命令输出用 Takumi 渲染为卡片（不可用时降级文本）"},
            "ui": {"widget": "switch", "group": "render", "order": 8},
        },
    )
    theme: str = field(
        default="auto",
        metadata={
            "description": {"i18n": "ConnHub.theme", "default": "卡片配色 (auto=按时间自动切深浅色)"},
            "ui": {
                "widget": "select",
                "options": ["auto", "light", "dark"],
                "group": "render",
                "order": 9,
            },
        },
    )
