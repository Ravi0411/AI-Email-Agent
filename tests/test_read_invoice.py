import os

from read_invoice import extract_pdf_text


invoice_path = os.path.join(
    os.path.expanduser("~"),
    "Desktop",
    "Invoices",
    "ForwardInvoice_ORD79373594012.pdf"
)


print(
    "Reading invoice PDF..."
)

print(
    invoice_path
)


text = extract_pdf_text(
    invoice_path
)


if text:

    print()
    print(
        "Invoice text extracted successfully:"
    )

    print()
    print(
        text
    )

else:

    print(
        "Could not extract text from invoice."
    )