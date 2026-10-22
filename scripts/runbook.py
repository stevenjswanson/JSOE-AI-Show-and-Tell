#!/usr/bin/env python3
"""Track the planning steps for one show-and-tell instance (see runbook/RUNBOOK.md).

Usage:
  python3 scripts/runbook.py new YYYY-MM-DD [--start 12:00] [--end 13:30] [--location "..."]
        create runbook/instances/YYYY-MM-DD/ (private state, drafts, briefs) and the public
        status data _data/status/YYYY-MM-DD.yml
  python3 scripts/runbook.py status [YYYY-MM-DD] [--today YYYY-MM-DD]
        event variables, T-offset, each step's state, drafts on disk
  python3 scripts/runbook.py done YYYY-MM-DD STEP_ID [note...]
  python3 scripts/runbook.py reopen YYYY-MM-DD STEP_ID
  python3 scripts/runbook.py log YYYY-MM-DD "drafted CFP"
        append one line to the status data's log (always the last key in the file)

With no date, `status` picks the active instance: the next upcoming event, or the most
recent one while its wrap-up window (21 days) is open. Step definitions: runbook/steps.toml.
"""

import sys
import tomllib
from datetime import date, timedelta
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
STEPS_FILE = REPO / "runbook" / "steps.toml"
INSTANCES = REPO / "runbook" / "instances"
STATUS_DIR = REPO / "_data" / "status"

DEFAULTS = {"start": "12:00", "end": "13:30", "location": "CSE Building, Room 1242"}


def load_steps():
    with open(STEPS_FILE, "rb") as f:
        return tomllib.load(f)["step"]


def instance_dir(day):
    return INSTANCES / day.isoformat()


def status_file(day):
    return STATUS_DIR / f"{day.isoformat()}.yml"


def load_state(day):
    with open(instance_dir(day) / "state.toml", "rb") as f:
        return tomllib.load(f)


def q(s):
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"') + '"'


def save_state(day, state):
    lines = [f"event_date = {state['event_date']}",
             f"created = {state['created']}",
             f"start = {q(state['start'])}",
             f"end = {q(state['end'])}",
             f"location = {q(state['location'])}",
             f"extra_recipients = {state.get('extra_recipients', [])!r}".replace("'", '"'),
             f"last_slack_read = {q(state.get('last_slack_read', ''))}  # Slack ts of the newest message already handled",
             "", "[threads]  # subject -> Gmail thread id, filled in when a draft is detected as sent"]
    for subj, tid in state.get("threads", {}).items():
        lines.append(f"{q(subj)} = {q(tid)}")
    lines += ["", "[steps]"]
    for sid, info in sorted(state.get("steps", {}).items()):
        lines.append(f"{sid} = {{ done = {info['done']}, note = {q(info.get('note', ''))} }}")
    (instance_dir(day) / "state.toml").write_text("\n".join(lines) + "\n")


def active_instance(today):
    days = sorted(date.fromisoformat(p.name) for p in INSTANCES.glob("????-??-??")
                  if (p / "state.toml").exists())
    if not days:
        sys.exit("no instances: run `runbook.py new YYYY-MM-DD`")
    upcoming = [d for d in days if d >= today]
    recent = [d for d in days if today - timedelta(days=21) <= d < today]
    if recent and (not upcoming or (upcoming[0] - today).days > 7):
        return recent[-1]
    return upcoming[0] if upcoming else days[-1]


def opt(args, flag, default):
    if flag in args:
        i = args.index(flag)
        value = args[i + 1]
        del args[i:i + 2]
        return value
    return default


def cmd_new(args):
    start = opt(args, "--start", DEFAULTS["start"])
    end = opt(args, "--end", DEFAULTS["end"])
    location = opt(args, "--location", DEFAULTS["location"])
    day = date.fromisoformat(args[0])
    d = instance_dir(day)
    if d.exists() or status_file(day).exists():
        sys.exit(f"{day} already exists")
    for sub in ("drafts", "daily", "inputs"):
        (d / sub).mkdir(parents=True)
    save_state(day, {"event_date": day.isoformat(), "created": date.today().isoformat(),
                     "start": start, "end": end, "location": location})
    (d / "notes.md").write_text(
        f"# Planning notes for {day} ({start}-{end}, {location})\n\n"
        "## Presenter pipeline\n\n| name | dept | topic | source | status | constraints |\n|---|---|---|---|---|---|\n\n"
        "## Zoom (private)\n\n## Dietary notes (private)\n\n"
        "## Decisions / things Steve said\n\n## Feedback received\n\n## Overflow for next time\n")
    STATUS_DIR.mkdir(parents=True, exist_ok=True)
    status_file(day).write_text(
        "event:\n"
        f"  date: {day.isoformat()}\n  start: {q(start)}\n  end: {q(end)}\n"
        f"  location: {q(location)}\n  zoom: \"\"\n"
        "phase: planning\n"
        "needs_steve: []\n"
        "lineup: []\n"
        "proposals: []\n"
        "rsvps: []\n"
        "counts: {in_person: 0, zoom: 0, presenters: 0, dietary_notes: 0}\n"
        "log:\n"
        f"  - {{date: {date.today().isoformat()}, action: \"instance opened\"}}\n")
    print(f"created {d} and {status_file(day)}")


def cmd_status(args):
    today = date.fromisoformat(opt(args, "--today", date.today().isoformat()))
    day = date.fromisoformat(args[0]) if args else active_instance(today)
    state = load_state(day)
    t = (today - day).days
    label = f"T{t:+d}" if t else "T-0 (EVENT DAY)"
    print(f"Instance {day} ({day.strftime('%A')}) {state['start']}-{state['end']}, {state['location']}")
    print(f"Today {today} ({today.strftime('%A')}) = {label}"
          + ("; Mauricio is remote Tue/Thu" if today.weekday() in (1, 3) else ""))
    if state.get("extra_recipients"):
        print(f"Extra recipients: {', '.join(state['extra_recipients'])}")
    print()
    done = state.get("steps", {})
    for s in load_steps():
        opens, due = day + timedelta(days=s["open"]), day + timedelta(days=s["due"])
        if s["id"] in done:
            status = f"done {done[s['id']]['done']}"
        elif today < opens:
            status = f"upcoming (opens {opens}, {(opens - today).days}d)"
        elif today <= due:
            status = f"OPEN      (due {due}, {(due - today).days}d left)"
        else:
            status = f"OVERDUE   (was due {due}, {(today - due).days}d ago)"
        flag = "  " if status.startswith(("done", "upcoming")) else "->"
        print(f"{flag} {s['id']:<24} {status:<40} {s['title']}")
        if s["id"] in done and done[s["id"]].get("note"):
            print(f"{'':29}note: {done[s['id']]['note']}")
    drafts = sorted((instance_dir(day) / "drafts").glob("*.md"))
    print(f"\nDrafts on disk ({len(drafts)}):")
    for p in drafts:
        first = p.read_text().splitlines()[0] if p.stat().st_size else ""
        print(f"  {p.name}  {first}")
    dailies = sorted((instance_dir(day) / "daily").glob("*.md"))
    print(f"Last daily brief: {dailies[-1].name if dailies else 'none'}")
    print(f"Status data: {status_file(day).relative_to(REPO)}"
          + ("" if status_file(day).exists() else "  (MISSING)"))


def cmd_done(args):
    day = date.fromisoformat(args[0])
    sid = args[1]
    if sid not in {s["id"] for s in load_steps()}:
        sys.exit(f"unknown step {sid}")
    state = load_state(day)
    state.setdefault("steps", {})[sid] = {"done": date.today().isoformat(), "note": " ".join(args[2:])}
    save_state(day, state)
    print(f"{sid} done")


def cmd_reopen(args):
    day = date.fromisoformat(args[0])
    state = load_state(day)
    state.get("steps", {}).pop(args[1], None)
    save_state(day, state)
    print(f"{args[1]} reopened")


def cmd_log(args):
    day = date.fromisoformat(args[0])
    action = " ".join(args[1:]).strip()
    if not action:
        sys.exit("log needs an action")
    path = status_file(day)
    text = path.read_text()
    if "\nlog:" not in text and not text.startswith("log:"):
        text = text.rstrip("\n") + "\nlog:\n"
    if not text.endswith("\n"):
        text += "\n"
    path.write_text(text + f"  - {{date: {date.today().isoformat()}, action: {q(action)}}}\n")
    print(f"logged: {action}")


if __name__ == "__main__":
    cmds = {"new": cmd_new, "status": cmd_status, "done": cmd_done, "reopen": cmd_reopen, "log": cmd_log}
    if len(sys.argv) < 2 or sys.argv[1] not in cmds:
        sys.exit(__doc__)
    cmds[sys.argv[1]](sys.argv[2:])
