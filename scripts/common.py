"""Shared helpers: load config and session files, locate media in Google Drive."""

import subprocess
import tomllib
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SESSIONS_DIR = REPO / "sessions"

# Google Drive for desktop stores each synced file's Drive ID in this xattr.
DRIVE_ID_XATTR = "com.google.drivefs.item-id#S"


def load_config():
    with open(REPO / "config.toml", "rb") as f:
        return tomllib.load(f)


def load_sessions():
    """All sessions, oldest first. Each gets a `path` key naming its file."""
    sessions = []
    for path in sorted(SESSIONS_DIR.glob("*.toml")):
        with open(path, "rb") as f:
            session = tomllib.load(f)
        session["path"] = path
        session.setdefault("talks", [])
        sessions.append(session)
    return sessions


def load_session(arg):
    """Load one session by date (2026-05-26) or by path."""
    path = Path(arg)
    if not path.exists():
        path = SESSIONS_DIR / f"{arg}.toml"
    with open(path, "rb") as f:
        session = tomllib.load(f)
    session["path"] = path
    session.setdefault("talks", [])
    return session


def drive_root(config=None):
    config = config or load_config()
    return Path(config["drive_root"]).expanduser()


def drive_id_of(path):
    """Drive file ID of a locally synced file, or None if unavailable."""
    result = subprocess.run(
        ["xattr", "-p", DRIVE_ID_XATTR, str(path)],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip() or None


def drive_view_url(drive_id):
    return f"https://drive.google.com/file/d/{drive_id}/view"
