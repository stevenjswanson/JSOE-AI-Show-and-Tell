#!/usr/bin/env python3
"""Generate index.html from config.toml, sessions/*.toml and templates/page.html.

Usage: python3 scripts/build.py [--check]

--check exits non-zero if index.html is out of date instead of writing it.
"""

import html
import sys
from string import Template

from common import REPO, drive_view_url, load_config, load_sessions

# Write typographic characters as named entities, matching the hand-written page.
ENTITIES = {
    "’": "&rsquo;", "‘": "&lsquo;",
    "“": "&ldquo;", "”": "&rdquo;",
    "—": "&mdash;", "–": "&ndash;",
    "·": "&middot;", "…": "&hellip;",
}


def esc(text):
    text = html.escape(text, quote=True)
    for char, entity in ENTITIES.items():
        text = text.replace(char, entity)
    return text.encode("ascii", "xmlcharrefreplace").decode("ascii")


def link_url(link):
    if "url" in link:
        return link["url"]
    if "drive_id" in link:
        return drive_view_url(link["drive_id"])
    raise ValueError(f"link {link.get('label')!r} needs `url` or `drive_id`")


def render_talk(talk):
    lines = [
        '<div class="speaker">',
        f"  <h3>{esc(talk['presenter'])}</h3>",
    ]
    if talk.get("title"):
        lines.append(f'  <p class="title">{esc(talk["title"])}</p>')
    if talk.get("summary"):
        summary = " ".join(talk["summary"].split())
        lines.append(f'  <p class="summary">{esc(summary)}</p>')
    links = [l for l in talk.get("links", []) if "url" in l or "drive_id" in l]
    if links:
        lines.append('  <p class="links">')
        sep = '    <span class="sep">&middot;</span>'
        rendered = [
            f'    <a href="{esc(link_url(l))}">{esc(l["label"])}</a>' for l in links
        ]
        lines.append(f"\n{sep}\n".join(rendered))
        lines.append("  </p>")
    lines.append("</div>")
    return "\n".join(lines)


def render_session(session, config):
    d = session["date"]
    location = session.get("location", config["default_location"])
    heading = f"{d:%B} {d.day}, {d.year} · {location}"
    parts = [f"<h2>{esc(heading)}</h2>"]
    if session["talks"]:
        parts += [render_talk(t) for t in session["talks"]]
    else:
        parts.append('<p class="purpose">Speakers to be announced.</p>')
    return "\n\n".join(parts)


def build():
    config = load_config()
    sessions = load_sessions()
    template = Template((REPO / "templates" / "page.html").read_text())
    return template.substitute(
        title=esc(config["title"]),
        contact_email=esc(config["contact_email"]),
        tech_support=esc(config["tech_support"]),
        sessions="\n\n".join(render_session(s, config) for s in sessions),
    )


def main():
    out = REPO / "index.html"
    page = build()
    if "--check" in sys.argv:
        if not out.exists() or out.read_text() != page:
            print("index.html is out of date; run python3 scripts/build.py")
            sys.exit(1)
        print("index.html is up to date")
        return
    out.write_text(page)
    print(f"wrote {out.relative_to(REPO)}")


if __name__ == "__main__":
    main()
