from gmail_auth import get_gmail_service
import base64
from bs4 import BeautifulSoup


def decode_data(data):
    """Decode Gmail's base64url encoded data."""
    return base64.urlsafe_b64decode(data).decode(
        "utf-8",
        errors="ignore"
    )


def extract_body(payload):
    """
    Recursively extract the readable email body.
    Prefer plain text, otherwise convert HTML to text.
    """

    plain_text = ""
    html_text = ""

    # Check direct body
    body_data = payload.get("body", {}).get("data")

    if body_data:
        content = decode_data(body_data)

        mime_type = payload.get("mimeType", "")

        if mime_type == "text/plain":
            return content

        elif mime_type == "text/html":
            html_text = content

    # Check nested parts recursively
    for part in payload.get("parts", []):

        result = extract_body(part)

        if not result:
            continue

        # If we find plain text, return it immediately
        if result.startswith("__PLAIN__"):
            return result

        # Otherwise keep HTML result as fallback
        if result.startswith("__HTML__"):
            html_text = result

    # Return HTML as cleaned text
    if html_text:

        html = html_text.replace("__HTML__", "")

        soup = BeautifulSoup(
            html,
            "html.parser"
        )

        # Remove unnecessary elements
        for element in soup(
            ["script", "style", "head"]
        ):
            element.decompose()

        text = soup.get_text(
            separator=" ",
            strip=True
        )

        return "__PLAIN__" + text

    return ""


def get_email_body(payload):
    """Return clean readable email text."""

    result = extract_body(payload)

    return result.replace(
        "__PLAIN__",
        ""
    ).strip()


def read_emails():

    service = get_gmail_service()

    # Get latest 5 emails
    results = service.users().messages().list(
        userId="me",
        maxResults=5
    ).execute()

    messages = results.get(
        "messages",
        []
    )

    print(
        f"Found {len(messages)} emails"
    )

    for message in messages:

        email = service.users().messages().get(
            userId="me",
            id=message["id"],
            format="full"
        ).execute()

        payload = email.get(
            "payload",
            {}
        )

        headers = payload.get(
            "headers",
            []
        )

        sender = ""
        subject = ""

        # Get email headers
        for header in headers:

            name = header.get(
                "name",
                ""
            ).lower()

            value = header.get(
                "value",
                ""
            )

            if name == "from":
                sender = value

            elif name == "subject":
                subject = value

        # Get email body
        body = get_email_body(
            payload
        )

        print("\n" + "=" * 60)

        print(
            "From:",
            sender
        )

        print(
            "Subject:",
            subject
        )

        print("\nBody:")

        if body:
            print(
                body[:2000]
            )
        else:
            print(
                "[No readable text body found]"
            )


if __name__ == "__main__":
    read_emails()