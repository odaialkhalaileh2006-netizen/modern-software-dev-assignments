#CallToolResult(content=[], structured_content=None, meta={'io.modelcontextprotocol/serverInfo': {'name': 'calendar', 'version': '4.1.2'}}, data=None, is_error=False)
from datetime import datetime, timedelta, timezone
from googleapiclient.errors import HttpError
from fastmcp import FastMCP
from googleapiclient.discovery import build
from typing import Annotated
from pydantic import Field
from auth import AuthRequired, get_credentials

mcp = FastMCP(
    "calendar",
    instructions=(
        "Tools for the user's Google Calendar. Call list_events first: it returns "
        "event IDs that get_event accepts. create_event previews by default; "
        "only set dry_run to false after the user agrees to the preview."
    ),
)


@mcp.tool(annotations={"readOnlyHint": True})
def list_events(
    days_ahead: Annotated[int, Field(ge=1, le=30)] = 7,
    max_results: Annotated[int, Field(ge=1, le=25)] = 10,
):
    """List upcoming events from the user's Google Calendar, soonest first.
    days_ahead: how many days to look ahead (1 to 30).
    max_results: the most events to return (1 to 25).
    Each event has an event_id that can be passed to get_event.
    Returns a dictionary with an "events" list (each event has event_id, title, start, end), and a "message" when there are no events.
    """
    try:
        creds = get_credentials(interactive=False)
    except AuthRequired as e:
        return {"error": str(e), "retryable": False, "hint": "Run `python auth.py` to authenticate."}

    service = build("calendar", "v3", credentials=creds)
    now = datetime.now(timezone.utc)
    end_time = now + timedelta(days=days_ahead)

    try:
        result = service.events().list(
            calendarId="primary",
            timeMin=now.isoformat(),
            timeMax=end_time.isoformat(),
            maxResults=max_results,
            singleEvents=True,
            orderBy="startTime",
        ).execute()
    except HttpError as e:
        status = e.resp.status
        retryable = status == 429 or 500 <= status <= 599
        if retryable:
            hint = "Wait a few seconds, then call list_events again."
        else:
            hint = "Do not repeat the same call. Tell the user what went wrong."
        return {
            "error": f"Google Calendar request failed with status {status}.",
            "retryable": retryable,
            "hint": hint,
        }

    events = []
    for item in result.get("items", []):
        events.append({
            "event_id": item["id"],
            "title": item.get("summary", "(no title)"),
            "start": item["start"].get("dateTime", item["start"].get("date")),
            "end": item["end"].get("dateTime", item["end"].get("date")),
        })
    if not events:
        return {"events": [], "message": f"No events found in the next {days_ahead} days."}
    return {"events": events}

@mcp.tool(annotations={"readOnlyHint": True})
def get_event(event_id: str):
    """Get full details of one event.

    event_id: the event_id returned by list_events.
    Returns: the event's event_id, title, start, end, description and location. Both description and location are empty strings if the event has no description or location.
    """
    try:
        creds = get_credentials(interactive=False)
    except AuthRequired as e:
        return {"error": str(e), "retryable": False, "hint": "Run `python auth.py` to authenticate."}

    service = build("calendar", "v3", credentials=creds)

    try:
        item = service.events().get(calendarId="primary", eventId=event_id).execute()
    except HttpError as e:
        status = e.resp.status
        if status == 404:
            return {
                "error": "Event not found, do not retry this ID; call list_events to get a valid ID.",
                "retryable": False,
                "hint": "Use list_events to find a valid event ID.",
            }
        retryable = status == 429 or 500 <= status <= 599
        if retryable:
            hint = "Wait a few seconds, then call get_event again."
        else:
            hint = "Do not repeat the same call. Tell the user what went wrong."       
        return {
            "error": f"Google Calendar request failed with status {status}.",
            "retryable": retryable,
            "hint": hint,
        }

    return {
        "event_id": item["id"],
        "title": item.get("summary", "(no title)"),
        "start": item["start"].get("dateTime", item["start"].get("date")),
        "end": item["end"].get("dateTime", item["end"].get("date")),
        "description": item.get("description", ""),
        "location": item.get("location",""),
    }

@mcp.tool(annotations={"destructiveHint": False})
def create_event(
    title: str, 
    start: str, 
    end: str, 
    description: str = "", 
    location: str = "", 
    timezone: str = "Asia/Amman", 
    dry_run: bool = True
    ):
    """Create a new event in the user's Google Calendar.
    start and end should be in ISO 8601 format (e.g., 2026-10-25T14:00:00) 
    without timezone offset; the timezone input applies.
    end must be after start.
    timezone should be an IANA timezone name (e.g., "Europe/London").
    If dry_run is true, the event is not created; a preview is returned instead.
    After a preview, STOP. Show it to the user and wait for their reply in a new message.
    Never set dry_run to false in the same turn as the preview, 
    even if the user already asked you to create the event.
    """

    try:
        start_dt = datetime.fromisoformat(start)
        end_dt = datetime.fromisoformat(end)
        if end_dt <= start_dt:
            return {"error": "End time must be after start time.", "retryable": False, "hint": "Please provide a valid end time."}
    except (ValueError, TypeError):
        return {"error": "Invalid date format.", "retryable": False, "hint": "Please provide dates in ISO 8601 format. Use YYYY-MM-DDTHH:MM:SS, for example 2026-10-25T14:00:00, with no timezone offset."}

    try:
        creds = get_credentials(interactive=False)
    except AuthRequired as e:
        return {"error": str(e), "retryable": False, "hint": "Run `python auth.py` to authenticate."}

    body = {
        "summary": title,
        "start": {"dateTime": start, "timeZone": timezone},
        "end": {"dateTime": end, "timeZone": timezone},
    }
    if description:
        body["description"] = description
    if location:
        body["location"] = location

    if dry_run:
        return {
            "dry_run": True,
            "created": False,
            "preview": {
                "title": title,
                "start": start,
                "end": end,
                "timezone": timezone,
                "description": description,
                "location": location,
            },
            "note": "This is a preview only. The event has NOT been created. Do not call create_event again yet: show this to the user and wait for them to confirm.",        }

    service = build("calendar", "v3", credentials=creds)
    try:
        item = service.events().insert(calendarId="primary", body=body).execute()
    except HttpError as e:
        status = e.resp.status
        retryable = status == 429 or 500 <= status <= 599
        if retryable:
            hint = "Wait a few seconds. Then call list_events to check whether the event was already created. Only call create_event again if the event is not found."
        else:
            hint = "Do not repeat the same call. Tell the user what went wrong."
        return {
            "error": f"Google Calendar request failed with status {status}.",
            "retryable": retryable,
            "hint": hint,
        }

    return {
        "created": True,
        "event_id": item["id"],
        "title": item.get("summary", ""),
        "start": item["start"].get("dateTime", item["start"].get("date")),
        "end": item["end"].get("dateTime", item["end"].get("date")),
        "link": item.get("htmlLink"),
    }


if __name__ == "__main__":
    mcp.run()


# TOOL 1: list_events
# inputs:
#   days_ahead: int, default 7, allowed 1 to 30
#   max_results: int, default 10, allowed 1 to 25
# returns: a list of events, soonest first. Each event has only:
#   id     - the event ID, so the AI can pass it to get_event
#   title  - what the event is called
#   start  - start as one piece of text (all-day events have only a date)
#   end    - end as one piece of text
# if login is missing or expired: return an error message (not a crash)
#   telling the AI the user must run `python auth.py`


# TOOL 2: get_event
# Inputs:
#   id: str — required; the event ID returned by list_events.
#
# Returns:
#   A dictionary containing the event's full details:
#     id          — the event ID
#     title       — the event title
#     start       — the start date and time as a string; all-day events
#                   contain only the date
#     end         — the end date and time as a string; all-day events
#                   contain only the date
#     description — the event description, if available
#     location    — the event location, if available
#
# Authentication handling:
#   If the token is missing or expired, including when refreshing it fails,
#   do not crash or launch a browser during an AI tool call. Return a clear
#   error message instructing the user to run `python auth.py` and retry
#   the tool call after authentication succeeds.
# errors: if the event ID does not exist -> return an error that says
#   "event not found, do not retry this ID; call list_events to get a valid ID"


# TOOL 3: create_event
# inputs:
#   title: str, required
#   start: str, required, ISO 8601 like 2026-10-25T14:00:00 (no offset; the timezone input applies)
#   end: str, required, same format, must be after start
#   description: str, optional
#   location: str, optional
#   timezone: str, default "Asia/Amman" (IANA name, e.g. "Europe/London")
#   dry_run: bool, default True
#     reason: the safe case must be the default. If the AI forgets this input,
#     nothing is created on the real calendar.
# returns, when dry_run is true:
#   a preview of the event (title, start, end, timezone, description, location)
#   and a note that nothing was created. Does not change the calendar.
# returns, when dry_run is false:
#   the event is really created. Returns the new event's id and its link,
#   so the AI can show the user and can call get_event with the id.

# ERRORS (shared by all tools)
# every error is returned as data, never as a crash, in this shape:
#   {"error": "<what went wrong>", "retryable": true or false, "hint": "<what to do next>"}
# login missing or expired:       don't retry until the user runs `python auth.py`, then retry
# event ID not found:             don't retry the same ID; call list_events for a valid one
# Google says too many requests:  retry after waiting (include how long, if Google says)
# network problem:                retry
# end time is before start time:  don't retry as is; fix the times first

# TIMEZONE CHOICE: Option B, a timezone input with a default.
#   Why: the AI only has to send the plain time, and the timezone is named in one
#   separate field with a clear default. An offset like +03:00 is easier to get wrong,
#   and it changes with daylight saving. Change the default if your calendar is in
#   a different timezone.