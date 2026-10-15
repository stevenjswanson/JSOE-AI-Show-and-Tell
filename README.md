# JSOE AI Show and Tell

Website and management scripts for the Jacobs School of Engineering AI Show and Tell,
an informal meeting where faculty demo how they use AI in teaching, research and
administration.

- **Site:** https://stevenjswanson.github.io/JSOE-AI-Show-and-Tell/ (GitHub Pages, `main` branch, repo root)
- **Media:** videos, slides, recordings, transcripts and chat logs stay in the shared Google Drive
  folder [JSOE AI Show and Tell](https://drive.google.com/drive/folders/1l3ryxssGB9ZuWXnhJLVxIasrqIqiaQf3),
  one subfolder per meeting. This repo only stores paths and Drive IDs.
- **Sign-ups:** the Google Form and its Responses sheet in that Drive folder (links in `config.toml`).

## Layout

```
config.toml            series-wide settings: title, contact, form link, Drive location
sessions/YYYY-MM-DD.toml   one file per meeting: talks, summaries, links, recording
templates/page.html    page shell (CSS, intro text); $placeholders filled by build.py
index.html             GENERATED: do not edit by hand
scripts/
  build.py             sessions + template -> index.html  (--check to verify it's current)
  check_media.py       verify every `file`/`drive_id` against the synced Drive folder
  split_recording.py   cut a full recording into NN_First_Last.mp4 clips in Drive
  responses.py         summarize form responses: RSVPs, dietary needs, unscheduled demos
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
# email = "..."   # optional; matches form responses. Repo is public, so usually omit
aka = ["Rose Q. Yu"]                         # optional: other names used on the sign-up form
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

## Running a meeting

1. **Before:** download the Responses sheet as CSV and run
   `python3 scripts/responses.py` to see RSVPs since the last meeting, dietary needs
   for the food order, and demo proposals not yet scheduled. Pick the lineup and create
   `sessions/YYYY-MM-DD.toml` with presenters, titles and times. Run
   `python3 scripts/build.py` and push to announce the lineup.
2. **After:** put the Zoom recording, transcript and chat in a new Drive folder
   `YYYY-MM-DD Show and Tell/` and list them under `[recording]`. Add a `start` to
   each talk (the transcript's timestamps help), then
   `python3 scripts/split_recording.py YYYY-MM-DD` (try `--dry-run` first).
3. Once Drive has synced the clips, add a `video` link with `file = ...` to each talk,
   run `python3 scripts/check_media.py`, and paste in the `drive_id` values it prints.
   Make sure the clips are shared so UCSD (or anyone with the link) can view them.
4. Write the summaries (from the transcript), `python3 scripts/build.py`, commit, push.
