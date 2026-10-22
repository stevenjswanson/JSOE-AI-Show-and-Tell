# Notes for Claude

See README.md for layout and the per-meeting workflow.

- `index.html` is generated. Change `sessions/*.toml`, `config.toml` or
  `templates/page.html`, then run `python3 scripts/build.py`. Never edit index.html directly.
- Media lives in Google Drive, never in this repo. Drive files are reachable locally at
  `drive_root` (config.toml); `scripts/common.py:drive_id_of` reads a file's Drive ID.
- RSVP/proposal details (names, emails, dietary needs) are personal data. Keep them
  out of the repo (`*.csv` is gitignored) and don't paste them into session files.
- `status/index.html` is a Jekyll page fed by `_data/status/*.yml`; keep email addresses,
  passwords and per-person dietary info out of that data (it is public, just unlinked).
- Pushing to `main` publishes the site immediately; ask before pushing.
