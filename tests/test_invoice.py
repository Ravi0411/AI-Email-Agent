from extract_invoice import extract_invoice_info


invoice_text = """
INVOICE

Invoice Number: INV-2026-001
Vendor: ABC Technologies Pvt Ltd
Invoice Date: 25 September 2026
Due Date: 10 October 2026
Total Amount: 25,000
Currency: INR

Thank you for your business.
"""


print(
    "Sending invoice information to Gemini..."
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