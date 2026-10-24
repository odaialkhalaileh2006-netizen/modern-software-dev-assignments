# 1. if token.json exists and the token is still valid -> use it 
# 2. if token.json exists but the token is expired -> refresh it and save the new token in token.json
# 3. If token.json is missing OR refreshing the token fails
#    (e.g., revoked or expired refresh token) -> start the browser OAuth flow
#    if running the login script interactively.

# 4. If token.json is missing OR refreshing the token fails during an AI
#    tool call -> do not launch a browser or wait for user interaction.
#    Return an error telling the AI that authentication is required and
#    instructing the user to run the login script manually.

# 1) situation 3 needs the browser to open and the user to log in and authorize the app.
# This is not possible in a headless environment, so we need to handle this case differently.
#2 2) we need to save the refresh token in a file to be able to refresh the access token without user interaction.

from pathlib import Path
import os

from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/calendar.events"]
CREDENTIALS_FILE = Path(os.environ.get("GOOGLE_CREDENTIALS_FILE", Path(__file__).parent / "credentials.json"))
TOKEN_FILE = Path(os.environ.get("GOOGLE_TOKEN_FILE", Path(__file__).parent / "token.json"))

class AuthRequired(Exception):
    """Raised when authentication is required but cannot be performed automatically."""
    pass

def get_credentials(interactive=False) :
    creds = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    if creds and creds.valid:
        return creds

    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            TOKEN_FILE.write_text(creds.to_json())
            return creds
        except RefreshError:
            creds = None
    if not creds or not creds.valid:
        if not interactive:
            raise AuthRequired(
                "Not logged in, or the login has expired. "
                "Ask the user to run `python auth.py` in the week2 folder, then try again."
            )
        flow=InstalledAppFlow.from_client_secrets_file(
            str(CREDENTIALS_FILE), SCOPES)
        creds= flow.run_local_server(port=0)
        TOKEN_FILE.write_text(creds.to_json())

    return creds
    
if __name__ == "__main__":
    get_credentials(interactive=True)
    print("Login OK. Token saved to", TOKEN_FILE)