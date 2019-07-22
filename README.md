# Calendar sync

Objective: Make sure all events on Outlook calendar are available on Google Calendar

## Pseudocode

fetch outlook calendar as list of events: oEvents
fetch google calendar as list of events : gEvents

Check all events on oEvents are in gEvents
Check all events on gEvents are still in oEvents (remove cancelations)

# Google calendar API
See https://developers.google.com/calendar/quickstart/python for more details
