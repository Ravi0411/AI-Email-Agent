import os
import requests

from dotenv import load_dotenv


print("STEP 1: Python started")

load_dotenv()

print("STEP 2: .env loaded")


api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("ERROR: GEMINI_API_KEY not found in .env")
    raise SystemExit


print("STEP 3: API key found")


url = (
    "https://generativelanguage.googleapis.com/"
    "v1beta/models/gemini-3.5-flash:generateContent"
)


data = {
    "contents": [
        {
            "parts": [
                {
                    "text": "Reply with exactly: Gemini is working."
                }
            ]
        }
    ]
}


print("STEP 4: Sending request with API key...")


try:

    response = requests.post(
        url,
        params={
            "key": api_key
        },
        headers={
            "Content-Type": "application/json"
        },
        json=data,
        timeout=30
    )

    print("STEP 5: Response received")

    print("Status code:", response.status_code)

    print("Response:")

    print(response.text)


except requests.exceptions.Timeout:

    print("STEP 6: Request timed out after 30 seconds")


except requests.exceptions.RequestException as error:

    print("STEP 6: HTTP request failed")

    print(error)


except Exception as error:

    print("STEP 6: Unexpected error")

    print(error)