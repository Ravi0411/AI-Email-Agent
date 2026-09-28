import os
import sys

from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build


SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/drive.file"
]


# --------------------------------------------------
# Application Root
# --------------------------------------------------

if getattr(
    sys,
    "frozen",
    False
):

    # Packaged .exe
    #
    # Example:
    # dist/
    # ├── AI Email Agent/
    # │   └── AI Email Agent.exe
    # └── AI Email Agent Monitor/
    #     └── AI Email Agent Monitor.exe
    #
    # Application root = dist/

    APPLICATION_ROOT = os.path.dirname(
        os.path.dirname(
            os.path.abspath(
                sys.executable
            )
        )
    )

else:

    # Normal Python execution
    #
    # Project/
    # └── src/
    #     └── gmail_auth.py
    #
    # Application root = Project/

    APPLICATION_ROOT = os.path.dirname(
        os.path.dirname(
            os.path.abspath(
                __file__
            )
        )
    )


# --------------------------------------------------
# File Paths
# --------------------------------------------------

TOKEN_FILE = os.path.join(
    APPLICATION_ROOT,
    "token.json"
)

CREDENTIALS_FILE = os.path.join(
    APPLICATION_ROOT,
    "credentials",
    "credentials.json"
)


# --------------------------------------------------
# Gmail Authentication
# --------------------------------------------------

def get_gmail_service():

    creds = None

    if os.path.exists(
        TOKEN_FILE
    ):

        creds = Credentials.from_authorized_user_file(
            TOKEN_FILE,
            SCOPES
        )

    if (
        not creds
        or not creds.valid
        or not creds.has_scopes(SCOPES)
    ):

        if (
            creds
            and creds.expired
            and creds.refresh_token
            and creds.has_scopes(SCOPES)
        ):

            creds.refresh(
                Request()
            )

        else:

            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE,
                SCOPES
            )

            creds = flow.run_local_server(
                port=0
            )

        with open(
            TOKEN_FILE,
            "w"
        ) as token:

            token.write(
                creds.to_json()
            )

    service = build(
        "gmail",
        "v1",
        credentials=creds
    )

    return service


# --------------------------------------------------
# Google Drive Authentication
# --------------------------------------------------

def get_drive_service():

    creds = None

    if os.path.exists(
        TOKEN_FILE
    ):

        creds = Credentials.from_authorized_user_file(
            TOKEN_FILE,
            SCOPES
        )

    if (
        not creds
        or not creds.valid
        or not creds.has_scopes(SCOPES)
    ):

        flow = InstalledAppFlow.from_client_secrets_file(
            CREDENTIALS_FILE,
            SCOPES
        )

        creds = flow.run_local_server(
            port=0
        )

        with open(
            TOKEN_FILE,
            "w"
        ) as token:

            token.write(
                creds.to_json()
            )

    service = build(
        "drive",
        "v3",
        credentials=creds
    )

    return service


# --------------------------------------------------
# Authentication Test
# --------------------------------------------------

if __name__ == "__main__":

    gmail_service = get_gmail_service()

    print(
        "Gmail authentication successful!"
    )

    drive_service = get_drive_service()

    print(
        "Google Drive authentication successful!"
    )