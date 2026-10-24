# Google Calendar MCP Server

## Setup
Create a virtual environment and install dependencies:
```bash
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Credentials
Put your own Google OAuth Desktop client file in this folder as `credentials.json`. **Never commit it.** The app reads `GOOGLE_CREDENTIALS_FILE` and `GOOGLE_TOKEN_FILE` from the environment if they are set, and otherwise uses `credentials.json` and `token.json` in this folder.

## Login
Run `python auth.py` once; a browser opens for authentication.

## Run the server
```bash
python server.py
```
It runs over stdio.

## Use with Claude Code
Copy `.mcp.json.example` to `.mcp.json` and replace the paths.

## Tests
```bash
python -m pytest test_protocol.py -v
```