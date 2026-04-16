import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DIALOGUES_PATH = BASE_DIR / "dialogues" / "dialogues.json"

DEFAULT_DIALOGUES = {
    "normal": ["今天也一起努力吧", "先做一小步就很好", "喝点水吧"],
    "working": ["专心五分钟也很棒", "先把最难的开始一下"],
    "sleeping": ["zzz...", "晚安哦"],
    "eating": ["该吃饭啦", "不吃饭会没力气的"],
    "annoyed": ["不要一直戳我啦", "再点我要生气了"],
    "reward": ["谢谢奖励！", "真棒！"]
}


def load_dialogues():
    if not DIALOGUES_PATH.exists():
        DIALOGUES_PATH.parent.mkdir(parents=True, exist_ok=True)
        DIALOGUES_PATH.write_text(
            json.dumps(DEFAULT_DIALOGUES, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return DEFAULT_DIALOGUES
    try:
        return json.loads(DIALOGUES_PATH.read_text(encoding="utf-8"))
    except Exception:
        return DEFAULT_DIALOGUES
