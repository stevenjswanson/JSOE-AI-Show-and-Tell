#!/usr/bin/env python3
"""Summarize the sign-up form's responses for planning the next meeting.

Usage: python3 scripts/responses.py [responses.csv] [--since YYYY-MM-DD]

Get the CSV from the responses sheet (File > Download > CSV); with no path,
the newest "*Responses*.csv" in ~/Downloads is used. The CSV holds personal
data, so keep it out of this repo.

Prints, for responses submitted after --since (default: the most recent
session date that has already passed):
  - attendance counts and the dietary restrictions to plan food around
  - comments and questions
and, across all responses, demo proposals not yet scheduled: a proposal is
treated as done if its author (matched against sessions/*.toml by email or
name) presented on or after the date they submitted it.
"""

import csv
import re
import sys
from collections import Counter
from datetime import date, datetime
from pathlib import Path

from common import load_sessions

EMAIL_RE = re.compile(r"[\w.+-]+@ucsd\.edu", re.I)
NO_ANSWERS = {"", "no", "no.", "n/a", "none"}

# Form questions, matched by header prefix so small wording edits still work.
ATTENDING = "Will you be attending"
DIETARY = "Do you have any dietary restrictions"
DEMO = "Would you like to propose a demo"
COMMENTS = "Other comments"
NAME = "Presenter"


def column(row, prefix):
    for key, value in row.items():
        if key and key.startswith(prefix):
            return (value or "").strip()
    return ""


def email_of(row):
    # The sheet's columns have been hand-edited, so search every cell.
    for value in row.values():
        m = EMAIL_RE.search(value or "")
        if m:
            return m.group(0).lower()
    return ""


def name_of(row):
    name = column(row, NAME)
    if name and "@" not in name and not name.startswith("#"):
        return name
    return email_of(row)


def submitted(row):
    stamp = next(iter(row.values()), "") or ""
    try:
        return datetime.strptime(stamp.strip(), "%m/%d/%Y %H:%M:%S").date()
    except ValueError:
        return None


def default_csv():
    found = sorted(Path("~/Downloads").expanduser().glob("*Responses*.csv"),
                   key=lambda p: p.stat().st_mtime)
    if not found:
        sys.exit("no CSV given and no *Responses*.csv in ~/Downloads")
    return found[-1]


def main():
    args = sys.argv[1:]
    since = None
    if "--since" in args:
        i = args.index("--since")
        since = date.fromisoformat(args[i + 1])
        del args[i:i + 2]
    path = Path(args[0]) if args else default_csv()

    sessions = load_sessions()
    if since is None:
        past = [s["date"] for s in sessions if s["date"] <= date.today()]
        since = max(past) if past else date.min

    # Most recent date each person presented, keyed by email and by name.
    presented = {}
    for s in sessions:
        for t in s["talks"]:
            keys = [t.get("email", ""), t["presenter"], *t.get("aka", [])]
            for key in (k.lower() for k in keys):
                if key:
                    presented[key] = max(presented.get(key, s["date"]), s["date"])

    with open(path, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    print(f"{path.name}: {len(rows)} responses")

    recent = [r for r in rows if (submitted(r) or date.min) > since]
    print(f"\n== Since {since}: {len(recent)} responses ==")

    # Count each person once, using their latest response.
    latest = {}
    for r in recent:
        latest[email_of(r) or name_of(r)] = r
    attending = Counter(column(r, ATTENDING) or "(blank)" for r in latest.values())
    for answer, n in attending.most_common():
        print(f"  {answer}: {n}")

    diets = [(name_of(r), column(r, DIETARY)) for r in latest.values()
             if column(r, ATTENDING) != "Via Zoom"
             and column(r, DIETARY).lower() not in NO_ANSWERS | {"no restrictions"}]
    print("\nDietary restrictions (excluding Zoom attendees):")
    for who, diet in diets or [("", "none")]:
        print(f"  {diet}" + (f"  - {who}" if who else ""))

    comments = [(name_of(r), column(r, COMMENTS)) for r in recent if column(r, COMMENTS)]
    if comments:
        print("\nComments:")
        for who, text in comments:
            print(f"  {who}: {' '.join(text.split())}")

    print("\n== Demo proposals not yet scheduled ==")
    for r in rows:
        demo = column(r, DEMO)
        if demo.lower() in NO_ANSWERS:
            continue
        email, name = email_of(r), name_of(r)
        when = submitted(r) or date.min
        last = presented.get(email) or presented.get(name.lower())
        if last and last >= when:
            continue  # presumably this proposal is the talk they gave
        note = f"  (last presented {last})" if last else ""
        print(f"  {submitted(r)}  {name} <{email}>{note}\n    {' '.join(demo.split())}")


if __name__ == "__main__":
    main()
