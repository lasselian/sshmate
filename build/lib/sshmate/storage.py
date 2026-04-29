import json
from pathlib import Path

CONFIG_FILE = Path.home() / ".config" / "sshmate" / "connections.json"


def load():
    if not CONFIG_FILE.exists():
        return []
    return json.loads(CONFIG_FILE.read_text())


def save(connections):
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(connections, indent=2))
