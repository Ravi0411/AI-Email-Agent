from database import (
    create_tables,
    get_connection
)


create_tables()


invoice = {
    "invoice_number": "C90156T260350133",
    "vendor": "BLINK COMMERCE PRIVATE LIMITED",
    "invoice_date": "14-Sep-2026",
    "due_date": "",
    "total_amount": "3226.00",
    "currency": "INR",
    "filename": "ForwardInvoice_ORD79373594012.pdf",
    "email_id": "test-email-001",
    "drive_link": "https://drive.google.com/"
}


connection = get_connection()

cursor = connection.cursor()


cursor.execute(
    """
    INSERT INTO invoices (
        invoice_number,
        vendor,
        invoice_date,
        due_date,
        total_amount,
        currency,
        filename,
        email_id,
        drive_link
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
    (
        invoice["invoice_number"],
        invoice["vendor"],
        invoice["invoice_date"],
        invoice["due_date"],
        invoice["total_amount"],
        invoice["currency"],
        invoice["filename"],
        invoice["email_id"],
        invoice["drive_link"]
    )
)


connection.commit()

connection.close()


print(
    "Invoice record saved successfully."
)
