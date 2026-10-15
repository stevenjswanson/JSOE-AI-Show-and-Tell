#!/usr/bin/env python3
"""Cross-check sessions/*.toml against the media in Google Drive.

Usage: python3 scripts/check_media.py

For every link with a `file`, confirms the file exists under drive_root and
that its Drive ID matches `drive_id` (printing the ID to paste in if it is
missing). Also lists files in each session's Drive folder that no session
file mentions. Needs Google Drive for desktop with the shared drive synced.
"""

import sys

from common import drive_id_of, drive_root, load_sessions

IGNORED = {".DS_Store"}


def main():
    root = drive_root()
    if not root.is_dir():
        sys.exit(f"Drive folder not found: {root}")

    problems = 0
    for session in load_sessions():
        name = session["path"].name
        referenced = set()

        for key in ("video", "transcript", "chat"):
            rel = session.get("recording", {}).get(key)
            if rel:
                referenced.add(rel)
                if not (root / rel).exists():
                    print(f"{name}: recording {key} missing: {rel}")
                    problems += 1

        for talk in session["talks"]:
            for link in talk.get("links", []):
                rel = link.get("file")
                if not rel:
                    continue
                referenced.add(rel)
                label = f"{name}: {talk['presenter']} / {link['label']}"
                path = root / rel
                if not path.exists():
                    print(f"{label}: file missing: {rel}")
                    problems += 1
                    continue
                actual = drive_id_of(path)
                expected = link.get("drive_id")
                if actual is None:
                    print(f"{label}: could not read Drive ID (not synced yet?)")
                    problems += 1
                elif expected is None:
                    print(f'{label}: add  drive_id = "{actual}"')
                    problems += 1
                elif expected != actual:
                    print(f'{label}: drive_id is {expected}, Drive says "{actual}"')
                    problems += 1

        folder = session.get("drive_folder")
        if folder:
            folder_path = root / folder
            if not folder_path.is_dir():
                print(f"{name}: drive_folder missing: {folder}")
                problems += 1
                continue
            for f in sorted(folder_path.iterdir()):
                rel = f"{folder}/{f.name}"
                if f.name not in IGNORED and rel not in referenced:
                    print(f"{name}: unreferenced in Drive: {rel}")

    print("OK" if problems == 0 else f"{problems} problem(s)")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
