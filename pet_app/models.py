from dataclasses import dataclass
from PySide6.QtCore import QPoint


@dataclass
class RuntimeState:
    current_state: str = "normal"
    current_action: str = ""
    current_variant_index: int = 0
    drag_offset: QPoint | None = None
    manual_override: bool = False
    action_locked: bool = False
    last_bug_trigger_minute: int = -10**9
    last_meal_key: str = ""
    click_timestamps: list[float] = None
    last_head_special_ts: float = 0.0
    last_body_special_ts: float = 0.0
    active_special_base: str = ""
    special_restore_state: str = ""
    special_restore_action: str = ""

    def __post_init__(self):
        if self.click_timestamps is None:
            self.click_timestamps = []
