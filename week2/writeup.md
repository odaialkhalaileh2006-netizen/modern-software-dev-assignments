# Week 2 Write-up

## Part I: The Server

**API chosen**, and why:
> Google Calendar. I already have a Google account, so there was nothing new to sign up for, and I could test the write tool safely by creating a test event and deleting it afterwards. The tools also chain in a natural way: an event ID from one tool is the input of the next. Google's Python libraries handle most of the OAuth token exchange, so I could spend my time on tool design, which is what this week grades.

**How to run it** (one command):
```
python server.py
```
Run it from `week2/` with the project's virtual environment active. Before the first run, log in once with `python auth.py`, which opens a browser and saves `token.json`. Claude Code starts the server itself from `.mcp.json`.

| Tool | What it does | Read/Write | Composes with |
|---|---|---|---|
| `list_events(days_ahead=7, max_results=10)` | Lists upcoming events from the primary calendar, soonest first. Returns only `event_id`, `title`, `start` and `end`, or a message when there are none. | Read | Its `event_id` is the input of `get_event`. |
| `get_event(event_id)` | Returns one event's `event_id`, `title`, `start`, `end`, `description` and `location` (empty strings when missing). | Read | Takes the `event_id` that `list_events` returns. |
| `create_event(title, start, end, description, location, timezone, dry_run=True)` | By default returns only a preview. With `dry_run=false` it creates the event and returns its `event_id`, `title`, `start`, `end` and `link`. | Write (only adds events) | The `event_id` it returns can be passed to `get_event` to check the new event. |


## Part II: Agent Ergonomics

For each, point at the code (`file:line`) and say what it buys.

References below point to functions in `server.py`.

| Decision | Where | Why |
|---|---|---|
| Schema-level constraint | `server.py:22-24` (`list_events` signature: `Annotated[int, Field(ge=1, le=30)]` for `days_ahead` and `le=25` for `max_results`) | The limits appear in the tool's schema as `minimum` and `maximum`, so the agent sees them before it calls. In one run the agent asked for `max_results: 50`, the schema rejected it with a clear message, and the agent corrected itself. Argument names the tool doesn't have are rejected too. |
| Output shaping (fields kept vs. dropped) | `server.py:62-71` (loop in `list_events`), `server.py:109-116` (`get_event` return), `server.py:163-174` and `server.py:192-199` (`create_event` preview and real returns) | Google returns dozens of fields per event. `list_events` keeps only `event_id`, `title`, `start` and `end`. `get_event` adds `description` and `location`. `start` and `end` are collapsed into one text value, because Google uses `dateTime` for normal events and `date` for all-day events. This keeps the output small and keeps my contract independent of Google's format. An empty calendar returns `{"events": [], "message": "No events found..."}`. |
| Structured errors (retry vs. don't-retry) | `server.py:32-34`, `49-60` (`list_events` AuthRequired and HttpError); `server.py:81-84`, `90-107` (`get_event` AuthRequired and HttpError); `server.py:147-150`, `179-190` (`create_event` AuthRequired and HttpError) | Every failure comes back as data in the shape `{"error", "retryable", "hint"}`, never a traceback. `retryable` is true only for status 429 and 5xx. `get_event` has a special 404 message that says not to retry the ID and to call `list_events`. The retry hint of `create_event` tells the agent to check `list_events` first, so a retry after a lost network reply cannot create a duplicate event. |
| Docstring that chains tools together | `server.py:10-17` (`FastMCP` instructions), `server.py:25-30` (`list_events` docstring), `server.py:76-80` (`get_event` docstring) | `list_events` says each event has an `event_id` that can be passed to `get_event`. `get_event` says `event_id` is the one returned by `list_events`. The server instructions say to call `list_events` first. The agent only sees the schemas and docstrings, so this is how it learns the tools connect. |
| Brake on the write tool | `server.py:118-127` (`create_event` decorator and signature with `dry_run`), `server.py:163-174` (preview return) | If the agent forgets the input, nothing is created: the default returns a preview with `created: false`. The docstring and the preview note both say to stop, show the preview to the user and wait for a reply. The tool is marked `destructiveHint: False` and not read-only, so Claude Code asks me to approve every call. In my `second test` run the agent went from the preview straight to creation without asking me in chat. I then strengthened the docstring and the preview note. In the `third test` run the agent showed the preview, said nothing was created, and waited for my reply. That is one run before and one after, so it is weak evidence, and a free model may behave differently next time. In both runs I read the `dry_run` value on each approval screen, so my approval was the final brake. |

**One thing you changed after watching the agent misuse a tool:**
> `list_events` used to return each event with the key `id`, but `get_event` takes an input called `event_id`. In two separate Claude Code runs the agent copied the name it saw in the output and called `get_event(id: ...)`. The schema rejected it, and the agent had to retry with `event_id`, which cost an extra failed call and an extra approval each time. I renamed the key to `event_id` in the output of all three tools and updated the docstrings, so the same name travels from one tool's output to the next tool's input. After the rename, the approval screens showed `event_id` on the first call, including in the failure demo below. That is a small sample, but the mismatch was gone. A second, smaller change: an empty calendar used to return an empty list, which reached the agent as no text, and it guessed ("possibly meaning there are no events"). Now it returns a message, and in the next run the agent said plainly that there were no events.


## Part III: OAuth

**Flow**: how a token is obtained, cached, and refreshed:
> `python auth.py` calls `get_credentials(interactive=True)` in `auth.py`. With no token, it reads my Google client file `credentials.json` and starts `InstalledAppFlow`. That opens the browser on Google's Allow screen and starts a small web server on my computer, on a free port, to receive the one-time authorization code. The library exchanges the code for an access token and a refresh token, and I save them to `token.json`. This is the cache. On every later call, `get_credentials` loads `token.json`. If the access token is still valid, it uses it. If it is expired and a refresh token exists, it refreshes it silently and rewrites `token.json`. If the refresh fails (for example, access was revoked) or there is no token, it opens the browser only when `interactive=True`. Otherwise it raises `AuthRequired`. My consent screen is in Testing mode, and as far as I know, refresh tokens then expire after about 7 days, so I log in again with `python auth.py` when that happens. I tested the silent refresh: my token from an earlier day was refreshed without opening a browser when I ran my test script.

**Scopes requested**, and why each is necessary:
> One scope: `https://www.googleapis.com/auth/calendar.events`. It lets the app view and edit events. `list_events` and `get_event` need to read events, and `create_event` needs to add them, so one scope covers all three tools. A read-only scope would not allow `create_event`. The full `calendar` scope would also give access to calendar settings and sharing, which none of my tools use. If I only had the two read tools, I would ask for a read-only scope instead.

**Secrets**: what's in env, what's gitignored:
> Two files hold secrets: `credentials.json` (the OAuth client ID and secret from Google Cloud Console) and `token.json` (my cached access and refresh tokens). Both are in `week2/.gitignore`, together with `.mcp.json` (my real config with local paths), `.env`, `__pycache__/` and `.venv/`. I checked `git status` before every commit to make sure none of them is listed. The code reads the two file paths from the environment variables `GOOGLE_CREDENTIALS_FILE` and `GOOGLE_TOKEN_FILE`, and falls back to `credentials.json` and `token.json` in the week2 folder when they are not set. No secret value is written in the code, and the committed `.mcp.json.example` shows the variables with placeholder paths.

**Token dies mid-session**: what the agent sees:
> The tools call `get_credentials(interactive=False)`. If there is no usable token and the refresh fails, it raises `AuthRequired`, and each tool catches it and returns `{"error": <message>, "retryable": false, "hint": "Run `python auth.py` to authenticate."}`. The agent gets a clear instruction to give the user, and no browser opens during a tool call, so the agent is never left waiting. I designed and unit-checked this path in code, but I did not capture a live Claude Code demo of an expired login.


## Part IV: Integration

**Registration config** (`.mcp.json.example`) and the client you used:
> Client: Claude Code, started with `fcc-claude` (the Free Claude Code launcher) and using a free NVIDIA-hosted model, `nemotron-3-super-120b-a12b`. I ran it in manual approval mode, so every tool call needed my approval. The committed config is `.mcp.json.example`. My real `.mcp.json` has my local paths and is gitignored.
> ```json
> {
>   "mcpServers": {
>     "calendar": {
>       "command": "C:/path/to/week2/.venv/Scripts/python.exe",
>       "args": ["C:/path/to/week2/server.py"]
>     }
>   }
> }
> ```

**End-to-end transcript**: the prompt, the tools that fired with their arguments, the result:

This run was recorded before the `id` to `event_id` rename described in Part II. It shows the chain and the mismatch that led to the change. The arguments of the first call were not captured in the log I saved.
```
Prompt: What events do I have in the next 14 days? Then show me the full details of the first one.

list_events(...)  ->  one event found, with ID 4vc9ocf1rd9leh28536qsa8tkv

get_event(id: "4vc9ocf1rd9leh28536qsa8tkv")
  -> Error: 2 validation errors for call[get_event]
     event_id: Missing required argument
     id: Unexpected keyword argument
Agent: "The parameter should be event_id not id. Let me try again."

get_event(event_id: "4vc9ocf1rd9leh28536qsa8tkv")
  -> {"id": "4vc9ocf1rd9leh28536qsa8tkv", "title": "testing the mcp server",
      "start": "2026-10-25T12:00:00+03:00", "end": "2026-10-25T13:00:00+03:00",
      "description": "", "location": ""}

Agent's answer: 1 event found in the next 14 days: "testing the mcp server",
2026-10-25 12:00 PM to 1:00 PM (UTC+3), no description, no location.
```

**A failure, handled**: what you provoked, what the agent saw, what it did next:

I provoked a bad ID with the prompt below, after the rename.
```
Prompt: Get the details of the event with ID abc.

get_event(event_id: "abc")
  -> {"error": "Event not found, do not retry this ID; call list_events to get a valid ID.",
      "retryable": false,
      "hint": "Use list_events to find a valid event ID."}
  (the server's response for an unknown ID, as printed by my test script)

Agent: "The event with ID "abc" was not found. The calendar system returned an error
indicating this ID doesn't exist. Would you like me to: 1. List your events to find
the correct ID, or 2. Try with a different event ID?"
```
The agent did not retry the same ID, and it offered to call `list_events`, which is what the hint says. I saw this once, so I would not call it guaranteed.

**Protocol-level test**: what it covers and how to run it:
> `test_protocol.py` has three tests, run with `python -m pytest test_protocol.py -v` (all three pass). They use FastMCP's `Client` connected to the server object, so each call goes through the MCP protocol and not just a direct Python function call. They check that the server lists exactly `list_events`, `get_event` and `create_event`; that `create_event` with an end time before the start time returns a structured error with `retryable: false` (this happens before any Google call); and that `list_events` with `days_ahead: 500` is rejected by the schema. None of them calls Google or needs a login. The connection is in-process, not over stdio.


## Submission
1. `Command (⌘) + F` for `TODO`. No results means you're done.
2. Confirm no tokens, client secrets, cached token file, or real `.mcp.json` are committed.
3. Push all changes to your remote repository and submit via Gradescope.
4. Clean up (optional): remove the server from your agent config, delete your cached token, and revoke the OAuth app's access.