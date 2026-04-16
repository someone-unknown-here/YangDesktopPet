from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
STATES_DIR = BASE_DIR / "states"


def scan_states():
    """
    Folder structure:
    states/
      normal/
        idle/
          a.gif
          b.gif
        happy/
          c.gif
      special_head/
        shy/
          x.gif
    """
    states = {}
    if not STATES_DIR.exists():
        return states

    for state_dir in sorted(STATES_DIR.iterdir()):
        if not state_dir.is_dir():
            continue
        action_map = {}
        for action_dir in sorted(state_dir.iterdir()):
            if not action_dir.is_dir():
                continue
            gifs = sorted(
                [p for p in action_dir.iterdir() if p.suffix.lower() in {".gif", ".webp"}]
            )
            if gifs:
                action_map[action_dir.name] = gifs
        if action_map:
            states[state_dir.name] = action_map
    return states
