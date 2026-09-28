from gmail_auth import get_drive_service


ROOT_FOLDER_NAME = "AI Email Agent"
INVOICE_FOLDER_NAME = "Invoices"


def find_folder(service, folder_name, parent_id=None):

    query = (
        "mimeType = 'application/vnd.google-apps.folder' "
        f"and name = '{folder_name}' "
        "and trashed = false"
    )

    if parent_id:
        query += f" and '{parent_id}' in parents"

    results = service.files().list(
        q=query,
        spaces="drive",
        fields="files(id, name)"
    ).execute()

    folders = results.get(
        "files",
        []
    )

    if folders:
        return folders[0]["id"]

    return None


def create_folder(
    service,
    folder_name,
    parent_id=None
):

    metadata = {
        "name": folder_name,
        "mimeType": "application/vnd.google-apps.folder"
    }

    if parent_id:
        metadata["parents"] = [
            parent_id
        ]

    folder = service.files().create(
        body=metadata,
        fields="id, name"
    ).execute()

    return folder["id"]


def get_invoice_folder(service):

    root_folder_id = find_folder(
        service,
        ROOT_FOLDER_NAME
    )

    if not root_folder_id:

        root_folder_id = create_folder(
            service,
            ROOT_FOLDER_NAME
        )

        print(
            "Created Google Drive folder:",
            ROOT_FOLDER_NAME
        )

    invoice_folder_id = find_folder(
        service,
        INVOICE_FOLDER_NAME,
        root_folder_id
    )

    if not invoice_folder_id:

        invoice_folder_id = create_folder(
            service,
            INVOICE_FOLDER_NAME,
            root_folder_id
        )

        print(
            "Created Google Drive folder:",
            f"{ROOT_FOLDER_NAME}/{INVOICE_FOLDER_NAME}"
        )

    return invoice_folder_id


if __name__ == "__main__":

    service = get_drive_service()

    folder_id = get_invoice_folder(
        service
    )

    print()
    print(
        "Invoice folder is ready."
    )

    print(
        "Folder ID:",
        folder_id
    )