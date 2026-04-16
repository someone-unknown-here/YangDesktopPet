import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "config.json"


DEFAULT_CONFIG = {
    "window": {
        "default_width": 260,
        "min_width": 120,
        "max_width": 500,
        "start_x": 120,
        "start_y": 120,
        "always_on_top": True
    },
    "timing": {
        "auto_change_action": True,
        "action_change_minutes": 5,
        "auto_sleep_enabled": True,
        "sleep_hour": 22,
        "meal_hours": [12, 19],
        "meal_minute_window": 20,
        "random_speech_minutes": 4,
        "speech_probability": 0.35,
        "bug_state_probability": 0.08,
        "bug_state_cooldown_minutes": 25,
        "annoy_click_threshold": 8,
        "annoy_click_window_seconds": 18,
        "sad_meal_delay_minutes": 35
    },
    "behavior": {
        "state": "normal",
        "fixed_action": "",
        "manual_override": False,
        "locked_action": False
    },
    "speech": {
        "enabled": True
    }
}


def deep_merge(defaults, loaded):
    if not isinstance(defaults, dict) or not isinstance(loaded, dict):
        return loaded
    result = dict(defaults)
    for key, value in loaded.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def load_config():
    if not CONFIG_PATH.exists():
        save_config(DEFAULT_CONFIG)
        return json.loads(json.dumps(DEFAULT_CONFIG))
    try:
        loaded = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        return deep_merge(DEFAULT_CONFIG, loaded)
    except Exception:
        save_config(DEFAULT_CONFIG)
        return json.loads(json.dumps(DEFAULT_CONFIG))


def save_config(config):
    CONFIG_PATH.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
