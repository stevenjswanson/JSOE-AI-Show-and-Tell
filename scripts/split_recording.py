#!/usr/bin/env python3
"""Cut a session's full recording into one clip per talk, written to Drive.

Usage: python3 scripts/split_recording.py 2026-05-26 [--copy] [--dry-run] [--force]

Reads [recording].video and each talk's `start` / `end` (e.g. "14:05" or
"1:02:30", offsets into the recording) from sessions/<date>.toml. A talk
with no `end` runs until the next talk's `start` (or the end of the video).
Clips are named NN_First_Last.mp4 in the session's drive_folder.

--copy     stream-copy instead of re-encoding: fast, but cuts snap to keyframes
--dry-run  print the ffmpeg commands without running them
--force    overwrite existing clips

After Drive syncs the new clips, add a link for each one
(label = "video", file = "...") and run scripts/check_media.py to get the
drive_id values to paste in.
"""

import re
import subprocess
import sys

from common import drive_root, load_session


def seconds(ts):
    parts = [float(p) for p in str(ts).split(":")]
    total = 0.0
    for p in parts:
        total = total * 60 + p
    return total


def clip_name(index, presenter):
    words = re.sub(r"[^\w\s-]", "", presenter).split()
    return f"{index:02d}_{'_'.join(words)}.mp4"


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) != 1:
        sys.exit(__doc__)
    copy = "--copy" in sys.argv
    dry_run = "--dry-run" in sys.argv
    force = "--force" in sys.argv

    session = load_session(args[0])
    root = drive_root()
    source = session.get("recording", {}).get("video")
    if not source:
        sys.exit("session has no [recording] video")
    source = root / source
    out_dir = root / session["drive_folder"]

    talks = [t for t in session["talks"] if "start" in t]
    if not talks:
        sys.exit("no talks have a `start` time")

    for i, talk in enumerate(talks):
        start = seconds(talk["start"])
        end = talk.get("end") or (talks[i + 1]["start"] if i + 1 < len(talks) else None)
        out = out_dir / clip_name(i + 1, talk["presenter"])
        if out.exists() and not force:
            print(f"skip (exists): {out.name}")
            continue

        cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
               "-ss", str(start), "-i", str(source)]
        if end is not None:
            cmd += ["-t", str(seconds(end) - start)]
        if copy:
            cmd += ["-c", "copy"]
        else:
            cmd += ["-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
                    "-c:a", "aac", "-b:a", "128k"]
        cmd += ["-movflags", "+faststart", str(out)]

        print(f"{out.name}: {talk['start']} -> {end or 'end'}")
        if dry_run:
            print("  " + " ".join(f'"{c}"' if " " in c else c for c in cmd))
        else:
            subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()
