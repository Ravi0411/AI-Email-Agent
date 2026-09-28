import os
import json
import requests

from dotenv import load_dotenv


load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError(
        "GEMINI_API_KEY not found in .env"
    )


GEMINI_URL = (
    "https://generativelanguage.googleapis.com/"
    "v1beta/models/gemini-3-flash-preview:generateContent"
)


def extract_invoice_info(
    invoice_text
):

    prompt = f"""
You are an invoice information extraction system.

Extract the important information from the invoice text below.

Invoice text:

{invoice_text}

Return ONLY valid JSON.

Use exactly this structure:

{{
  "invoice_number": "",
  "vendor": "",
  "invoice_date": "",
  "due_date": "",
  "total_amount": "",
  "currency": ""
}}

Rules:

- If a field is not available, use an empty string.
- Do not guess missing information.
- Keep the original values from the invoice.
- Do not add Markdown.
- Do not add explanations outside the JSON.
"""


    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    }


    try:

        response = requests.post(
            GEMINI_URL,
            params={
                "key": API_KEY
            },
            headers={
                "Content-Type": "application/json"
            },
            json=data,
            timeout=30
        )


        if response.status_code != 200:

            print(
                "Gemini error:",
                response.status_code
            )

            print(
                response.text
            )

            return None


        result = response.json()

        text = (
            result["candidates"][0]
            ["content"]["parts"][0]["text"]
            .strip()
        )


        if text.startswith("```json"):

            text = text[7:]

            if text.endswith("```"):

                text = text[:-3]

            text = text.strip()


        elif text.startswith("```"):

            text = text[3:]

            if text.endswith("```"):

                text = text[:-3]

            text = text.strip()


        try:

            return json.loads(
                text
            )

        except json.JSONDecodeError:

            print(
                "Gemini returned invalid JSON:"
            )

            print(
                text
            )

            return None


    except requests.exceptions.RequestException as error:

        print(
            "Gemini HTTP error:",
            error
        )

        return None


    except Exception as error:

        print(
            "Invoice extraction error:",
            error
        )

        return None