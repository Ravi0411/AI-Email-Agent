import os
import time
import base64
import json
import hashlib

from gmail_auth import (
    get_gmail_service,
    get_drive_service
)

from read_emails import get_email_body
from analyze_email import analyze_email
from extract_invoice import extract_invoice_info
from read_invoice import extract_pdf_text
from database import (
    create_tables,
    save_invoice
)
from drive_storage import get_invoice_folder


CHECK_INTERVAL = 10

INVOICE_FOLDER = os.path.join(
    os.path.expanduser("~"),
    "Desktop",
    "Invoices"
)

PROJECT_FOLDER = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

PROCESSED_EMAILS_FILE = os.path.join(
    PROJECT_FOLDER,
    "processed_emails.json"
)


def load_processed_emails():

    if not os.path.exists(
        PROCESSED_EMAILS_FILE
    ):

        return set()

    try:

        with open(
            PROCESSED_EMAILS_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        return set(data)

    except Exception as error:

        print(
            "Could not load processed emails:",
            error
        )

        return set()


def save_processed_emails(
    processed_emails
):

    with open(
        PROCESSED_EMAILS_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            list(processed_emails),
            file,
            indent=2
        )


def get_new_email_ids(
    service,
    start_time,
    processed_emails
):

    results = service.users().messages().list(
        userId="me",
        q=f"after:{start_time}",
        maxResults=20
    ).execute()

    messages = results.get(
        "messages",
        []
    )

    new_email_ids = []

    for message in messages:

        message_id = message["id"]

        if message_id not in processed_emails:

            new_email_ids.append(
                message_id
            )

    return new_email_ids


def get_email(
    service,
    message_id
):

    email = service.users().messages().get(
        userId="me",
        id=message_id,
        format="full"
    ).execute()

    payload = email.get(
        "payload",
        {}
    )

    sender = ""
    subject = ""

    for header in payload.get(
        "headers",
        []
    ):

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

    body = get_email_body(
        payload
    )

    return {
        "id": message_id,
        "sender": sender,
        "subject": subject,
        "body": body,
        "payload": payload
    }


def mark_as_important(
    service,
    message_id
):

    service.users().messages().modify(
        userId="me",
        id=message_id,
        body={
            "addLabelIds": [
                "IMPORTANT"
            ]
        }
    ).execute()


def get_or_create_label(
    service,
    label_name
):

    results = service.users().labels().list(
        userId="me"
    ).execute()

    labels = results.get(
        "labels",
        []
    )

    for label in labels:

        if label["name"].lower() == label_name.lower():

            return label["id"]

    label_object = {
        "name": label_name,
        "labelListVisibility": "labelShow",
        "messageListVisibility": "show"
    }

    created_label = service.users().labels().create(
        userId="me",
        body=label_object
    ).execute()

    return created_label["id"]


def apply_category_label(
    service,
    message_id,
    category
):

    label_name = f"AI/{category}"

    label_id = get_or_create_label(
        service,
        label_name
    )

    service.users().messages().modify(
        userId="me",
        id=message_id,
        body={
            "addLabelIds": [
                label_id
            ]
        }
    ).execute()

    return label_name


def find_attachments(
    payload
):

    attachments = []

    if not payload:

        return attachments

    filename = payload.get(
        "filename",
        ""
    )

    body = payload.get(
        "body",
        {}
    )

    attachment_id = body.get(
        "attachmentId"
    )

    if filename and attachment_id:

        attachments.append({
            "filename": filename,
            "attachment_id": attachment_id
        })

    for part in payload.get(
        "parts",
        []
    ):

        attachments.extend(
            find_attachments(part)
        )

    return attachments


def calculate_file_hash(
    file_path
):

    sha256 = hashlib.sha256()

    with open(
        file_path,
        "rb"
    ) as file:

        while True:

            chunk = file.read(
                1024 * 1024
            )

            if not chunk:

                break

            sha256.update(
                chunk
            )

    return sha256.hexdigest()


def get_existing_file_hashes():

    hashes = set()

    if not os.path.exists(
        INVOICE_FOLDER
    ):

        return hashes

    for filename in os.listdir(
        INVOICE_FOLDER
    ):

        file_path = os.path.join(
            INVOICE_FOLDER,
            filename
        )

        if os.path.isfile(
            file_path
        ):

            try:

                file_hash = calculate_file_hash(
                    file_path
                )

                hashes.add(
                    file_hash
                )

            except Exception:

                pass

    return hashes


def download_attachment(
    service,
    message_id,
    attachment_id,
    filename
):

    os.makedirs(
        INVOICE_FOLDER,
        exist_ok=True
    )

    attachment_data = (
        service.users()
        .messages()
        .attachments()
        .get(
            userId="me",
            messageId=message_id,
            id=attachment_id
        )
        .execute()
    )

    file_data = base64.urlsafe_b64decode(
        attachment_data["data"] + "=="
    )

    file_path = os.path.join(
        INVOICE_FOLDER,
        filename
    )

    with open(
        file_path,
        "wb"
    ) as file:

        file.write(
            file_data
        )

    return file_path


def upload_to_drive(
    drive_service,
    file_path,
    filename
):

    from googleapiclient.http import MediaFileUpload

    folder_id = get_invoice_folder(
        drive_service
    )

    file_metadata = {
        "name": filename,
        "parents": [
            folder_id
        ]
    }

    media = MediaFileUpload(
        file_path,
        resumable=True
    )

    uploaded_file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id, name, webViewLink"
    ).execute()

    return uploaded_file


def process_invoice(
    file_path,
    filename,
    message_id,
    drive_link
):

    print(
        "Reading invoice PDF..."
    )

    invoice_text = extract_pdf_text(
        file_path
    )

    if not invoice_text:

        print(
            "Could not extract text from invoice."
        )

        return

    print(
        "Invoice text extracted successfully."
    )

    print(
        "Sending invoice information to Gemini..."
    )

    invoice_info = extract_invoice_info(
        invoice_text
    )

    if not invoice_info:

        print(
            "Could not extract invoice information."
        )

        return

    print()
    print(
        "Extracted Invoice Information:"
    )

    print(
        invoice_info
    )

    save_invoice(
        invoice_number=invoice_info.get(
            "invoice_number",
            ""
        ),
        vendor=invoice_info.get(
            "vendor",
            ""
        ),
        invoice_date=invoice_info.get(
            "invoice_date",
            ""
        ),
        due_date=invoice_info.get(
            "due_date",
            ""
        ),
        total_amount=invoice_info.get(
            "total_amount",
            ""
        ),
        currency=invoice_info.get(
            "currency",
            ""
        ),
        filename=filename,
        email_id=message_id,
        drive_link=drive_link
    )

    print(
        "Invoice information saved to database."
    )


def process_new_email(
    service,
    drive_service,
    message_id
):

    print(
        "New email detected."
    )

    email = get_email(
        service,
        message_id
    )

    print(
        "Email received:"
    )

    print(
        "Sender:",
        email["sender"]
    )

    print(
        "Subject:",
        email["subject"]
    )

    print(
        "Sending email to Gemini..."
    )

    analysis = analyze_email(
        email
    )

    if analysis is None:

        print(
            "AI analysis failed."
        )

        return False

    print()
    print(
        "AI Analysis:"
    )

    print(
        analysis
    )

    category = analysis.get(
        "category",
        "Other"
    )

    importance = analysis.get(
        "importance",
        "Low"
    )

    print(
        "Category:",
        category
    )

    print(
        "Importance:",
        importance
    )

    print(
        "Applying Gmail label..."
    )

    label_name = apply_category_label(
        service,
        message_id,
        category
    )

    print(
        "Gmail label applied:",
        label_name
    )

    if importance == "High":

        print(
            "Marking email as Important..."
        )

        mark_as_important(
            service,
            message_id
        )

        print(
            "Email marked as Important."
        )

    else:

        print(
            "Email is not High importance."
        )

    attachments = find_attachments(
        email["payload"]
    )

    if not attachments:

        print(
            "No attachments found."
        )

        return True

    print(
        "Attachments found:",
        len(attachments)
    )

    existing_hashes = get_existing_file_hashes()

    for attachment in attachments:

        filename = attachment[
            "filename"
        ]

        attachment_id = attachment[
            "attachment_id"
        ]

        print(
            "Downloading attachment:",
            filename
        )

        file_path = download_attachment(
            service,
            message_id,
            attachment_id,
            filename
        )

        file_hash = calculate_file_hash(
            file_path
        )

        if file_hash in existing_hashes:

            print(
                "Duplicate attachment detected."
            )

            print(
                "Skipping Google Drive upload:",
                filename
            )

            continue

        print(
            "Invoice saved to:",
            file_path
        )

        print(
            "Uploading attachment to Google Drive..."
        )

        uploaded_file = upload_to_drive(
            drive_service,
            file_path,
            filename
        )

        existing_hashes.add(
            file_hash
        )

        drive_link = uploaded_file.get(
            "webViewLink",
            ""
        )

        print(
            "Uploaded to Google Drive:",
            uploaded_file["name"]
        )

        if drive_link:

            print(
                "Drive link:",
                drive_link
            )

        if category == "Invoice":

            process_invoice(
                file_path,
                filename,
                message_id,
                drive_link
            )

    return True


def main():

    create_tables()

    gmail_service = get_gmail_service()

    drive_service = get_drive_service()

    start_time = int(
        time.time()
    )

    processed_emails = load_processed_emails()

    print(
        "Gmail connected."
    )

    print(
        "Google Drive connected."
    )

    print(
        "Loaded processed emails:",
        len(processed_emails)
    )

    print(
        "Local invoice folder:"
    )

    print(
        INVOICE_FOLDER
    )

    print(
        "Monitoring for new emails..."
    )

    print(
        "Existing emails will be ignored."
    )

    while True:

        try:

            email_ids = get_new_email_ids(
                gmail_service,
                start_time,
                processed_emails
            )

            if email_ids:

                print(
                    "New emails detected:",
                    len(email_ids)
                )

            for email_id in email_ids:

                success = process_new_email(
                    gmail_service,
                    drive_service,
                    email_id
                )

                if success:

                    processed_emails.add(
                        email_id
                    )

                    save_processed_emails(
                        processed_emails
                    )

                    print(
                        "Email processing completed."
                    )

            time.sleep(
                CHECK_INTERVAL
            )

        except KeyboardInterrupt:

            print(
                "Monitoring stopped."
            )

            break

        except Exception as error:

            print(
                "Monitor error:",
                error
            )

            time.sleep(
                CHECK_INTERVAL
            )


if __name__ == "__main__":

    main()