import os
import json
import time
import requests

from dotenv import load_dotenv


load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env")


GEMINI_URL = (
    "https://generativelanguage.googleapis.com/"
    "v1beta/models/gemini-3-flash-preview:generateContent"
)


MAX_RETRIES = 3

RETRY_DELAY = 5


def analyze_email(email):

    prompt = f"""
You are an intelligent email management assistant.

Analyze the following email carefully.

Sender: {email["sender"]}
Subject: {email["subject"]}
Body: {email["body"]}

Your most important task is to correctly determine whether this email
should be treated as IMPORTANT for the user.

IMPORTANT RULES:

Set importance to "High" when the email contains one or more strong
signals such as:

- Urgent or emergency language
- "Urgent", "Important", "Action Required", "Immediate Action"
- A deadline that requires the user's attention
- A meeting, interview, exam, test, appointment, or event that requires attendance
- A request that requires the user to respond or take action
- Financial/payment/invoice issues requiring attention
- Security alerts or account-related warnings
- Job/interview-related actions or deadlines
- Work-related tasks with a deadline
- Any other situation where ignoring the email could cause the user
  to miss an important task, deadline, meeting, payment, test, or opportunity

Set importance to "Medium" when the email is useful or relevant but
does not require immediate attention.

Set importance to "Low" for:

- Marketing emails
- Advertisements
- Promotional offers
- Newsletters
- General informational emails
- Unimportant social notifications
- Emails that do not require the user's attention

IMPORTANT:
Do not classify an email as Low simply because it is forwarded,
automatically generated, or contains promotional content.

Consider the actual message content and the action the user needs to take.

Urgency and importance are different:

- Urgency = how soon the user needs to act.
- Importance = how significant it is for the user to act.

For example, an email about an exam tomorrow can be both High importance
and High urgency.

Return ONLY valid JSON.

Use exactly this structure:

{{
  "category": "Work",
  "importance": "High",
  "urgency": "High",
  "action_required": true,
  "summary": "short summary",
  "recommended_action": "what the user should do"
}}

Category must be one of:

Work
Finance
Travel
Shopping
Job
Education
Social
Promotion
Security
Invoice
Other

Importance must be:

High
Medium
Low

Urgency must be:

High
Medium
Low

action_required must be:

true
false

Do not add Markdown.
Do not add explanations outside the JSON.
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


    for attempt in range(
        1,
        MAX_RETRIES + 1
    ):

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


            if response.status_code == 200:

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

                    return json.loads(text)

                except json.JSONDecodeError:

                    print(
                        "Gemini returned invalid JSON:"
                    )

                    print(text)

                    return None


            if response.status_code == 503:

                print(
                    f"Gemini temporarily unavailable "
                    f"(attempt {attempt}/{MAX_RETRIES})."
                )

                if attempt < MAX_RETRIES:

                    print(
                        f"Retrying in {RETRY_DELAY} seconds..."
                    )

                    time.sleep(
                        RETRY_DELAY
                    )

                    continue

                print(
                    "Gemini remained unavailable "
                    "after all retry attempts."
                )

                return None


            if response.status_code == 429:

                print(
                    "Gemini quota exceeded."
                )

                print(
                    response.text
                )

                return None


            print(
                "Gemini error:",
                response.status_code
            )

            print(
                response.text
            )

            return None


        except requests.exceptions.Timeout:

            print(
                f"Gemini request timed out "
                f"(attempt {attempt}/{MAX_RETRIES})."
            )

            if attempt < MAX_RETRIES:

                print(
                    f"Retrying in {RETRY_DELAY} seconds..."
                )

                time.sleep(
                    RETRY_DELAY
                )

                continue

            print(
                "Gemini request failed after "
                "all retry attempts."
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
                "Gemini error:",
                error
            )

            return None