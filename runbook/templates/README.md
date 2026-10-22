# Email templates

One file per email the runbook produces. The wording is Steve's from the spring 2026
instances, lightly generalized; every `{placeholder}` must be filled before the Gmail draft is created.
Every draft carries `cc: sjswanson+claude@ucsd.edu` (plus anyone named in the template).

Placeholders: `{E_long}` = "Tuesday, January 12", `{E_short}` = "January 12th",
`{weekday}` = "Tuesday", `{time_range}` = "12-1:30", `{start}` = "12:00", `{location}` =
"CSE 1242" (short form of the state's location), `{nth}` = "third", `{site}` =
https://stevenjswanson.github.io/JSOE-AI-Show-and-Tell/, `{broadcast}` = the broadcast
lists plus `extra_recipients`, `{schedule_table}` = plain-text table "Presenter  Time  Title",
`{zoom_block}` = the block below from notes.md, `{rsvp_instructions}` = the paragraph below.

RSVP paragraph (RSVPs and proposals come by email; there is no form):

```
To RSVP, just reply to me (please don't reply-all) and say whether you'll be there in person
or on Zoom, and any dietary restrictions. If you'd like to present, add a line or two about
what you'd show.
```

Zoom block (dial-in numbers were the same both times in 2026):

```
Topic: JSOE AI Show-and-Tell
Time: {E_long}, {year} {start} PM Pacific Time (US and Canada)

Join Zoom Meeting
{zoom_url}

Meeting ID: {zoom_id}
Password: {zoom_pw}

One tap mobile
+16699006833,,{zoom_id_digits}# US (San Jose)
+12133388477,,{zoom_id_digits}# US (Los Angeles)
```
