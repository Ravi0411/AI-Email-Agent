import os

from pypdf import PdfReader


def extract_pdf_text(
    pdf_path
):

    if not os.path.exists(
        pdf_path
    ):

        print(
            "PDF file not found:"
        )

        print(
            pdf_path
        )

        return None


    try:

        reader = PdfReader(
            pdf_path
        )

        text = ""

        for page in reader.pages:

            page_text = page.extract_text()

            if page_text:

                text += page_text
                text += "\n"


        return text.strip()


    except Exception as error:

        print(
            "PDF reading error:",
            error
        )

        return None