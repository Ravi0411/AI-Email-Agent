import os

from read_invoice import extract_pdf_text
from extract_invoice import extract_invoice_info


invoice_path = os.path.join(
    os.path.expanduser("~"),
    "Desktop",
    "Invoices",
    "ForwardInvoice_ORD79373594012.pdf"
)


print(
    "Reading real invoice PDF..."
)


invoice_text = extract_pdf_text(
    invoice_path
)


if not invoice_text:

    print(
        "Could not read invoice PDF."
    )

    exit()


print(
    "PDF text extracted successfully."
)

print(
    "Sending invoice text to Gemini..."
)


result = extract_invoice_info(
    invoice_text
)


print()
print(
    "Extracted Invoice Information:"
)

print(
    result
)