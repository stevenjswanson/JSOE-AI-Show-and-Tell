# JSOE AI Show and Tell

Website and management scripts for the Jacobs School of Engineering AI Show and Tell,
an informal meeting where faculty demo how they use AI in teaching, research and
administration.

- **Site:** https://stevenjswanson.github.io/JSOE-AI-Show-and-Tell/ (GitHub Pages, `main` branch, repo root)
- **Media:** videos, slides, recordings, transcripts and chat logs stay in the shared Google Drive
  folder [JSOE AI Show and Tell](https://drive.google.com/drive/folders/1l3ryxssGB9ZuWXnhJLVxIasrqIqiaQf3),
  one subfolder per meeting. This repo only stores paths and Drive IDs.
- **Sign-ups and RSVPs:** by email reply to the call/announcement (see `runbook/`); the 2026 Google Form is retired.

## Layout

```
config.toml            series-wide settings: title, contact, Drive location
sessions/YYYY-MM-DD.toml   one file per meeting: talks, summaries, links, recording
templates/page.html    page shell (CSS, intro text); $placeholders filled by build.py
index.html             GENERATED: do not edit by hand
_config.yml            Jekyll settings (GitHub Pages copies index.html as is, renders status/)
status/index.html      unlinked planning status page, rendered from _data/status/*.yml
_data/status/          per-meeting planning status + action log (written by the runbook agent)
runbook/               planning runbook, step windows, email templates
scripts/
  build.py             sessions + template -> index.html  (--check to verify it's current)
  check_media.py       verify every `file`/`drive_id` against the synced Drive folder
  split_recording.py   fallback: cut a full recording into clips with ffmpeg (OctoEdit is the default; see runbook s15)
  runbook.py           planning steps, status data and action log for one meeting
```

Everything is Python 3.11+ standard library; `split_recording.py` also needs `ffmpeg`.
The Drive-touching scripts expect Google Drive for desktop with the shared drive synced
at `drive_root` in `config.toml`.

## Session file format

```toml
date = 2026-05-26
drive_folder = "2026-05-26 Show and Tell"   # relative to drive_root
# location = "..."                          # defaults to config.default_location

[recording]                                 # optional: the full meeting recording
video = "2026-05-26 Show and Tell/GMT..._Recording.mp4"
transcript = "2026-05-26 Show and Tell/GMT..._Recording.transcript.vtt"

[[talks]]
presenter = "Rose Yu"
# email = "..."   # optional. Repo is public, so usually omit
aka = ["Rose Q. Yu"]                         # optional: other names the presenter goes by
time = "12:15"                              # scheduled slot
start = "26:30"                             # offset into the recording (for splitting)
title = "Using AI in a Research Group"
summary = """..."""                         # plain text; curly quotes/dashes are fine

  [[talks.links]]
  label = "video"
  file = "2026-05-26 Show and Tell/02_Rose_Yu.mp4"   # Drive path (for checking)
  drive_id = "1L6H_a0-77ckhOj27MprW7EJ2YdJ-mpCc"      # what the page links to

  [[talks.links]]
  label = "slides"
  url = "https://..."                       # any non-Drive link
```

Talks appear on the page in file order; sessions in date order. A session with no
talks shows "Speakers to be announced."

## Planning a meeting

`runbook/RUNBOOK.md` is a day-by-day procedure (written for an AI agent on a daily
schedule) that covers booking, the call for presenters, recruiting, the announcement,
lunch count, reminders, recording and the post-event write-up. It produces email drafts
for Steve to send; it never sends anything itself. `python3 scripts/runbook.py status`
shows what is due; step windows are in `runbook/steps.toml`, email wording in
`runbook/templates/`. Per-instance state and drafts live in `runbook/instances/`
(gitignored, like `runbook/contacts.toml`, because they name people).

## Running a meeting

1. **Before:** follow `runbook/RUNBOOK.md` (RSVPs and proposals arrive by email and are
   tallied in `_data/status/YYYY-MM-DD.yml`). Pick the lineup and create
   `sessions/YYYY-MM-DD.toml` with presenters, titles and times. Run
   `python3 scripts/build.py` and push to announce the lineup.
2. **After:** put the Zoom recording, transcript and chat in a new Drive folder
   `YYYY-MM-DD Show and Tell/` and list them under `[recording]`. Cut one clip per talk
   with OctoEdit (`runbook/RUNBOOK.md` step s15: `octoedit init`, mark clips in
   `transcript.md`, `octoedit render --dest <Drive folder>`). Fallback: add a `start` to
   each talk and run `python3 scripts/split_recording.py YYYY-MM-DD` (try `--dry-run` first).
3. Once Drive has synced the clips, add a `video` link with `file = ...` to each talk,
   run `python3 scripts/check_media.py`, and paste in the `drive_id` values it prints.
   Make sure the clips are shared so UCSD (or anyone with the link) can view them.
4. Write the summaries (from the transcript), `python3 scripts/build.py`, commit, push.
