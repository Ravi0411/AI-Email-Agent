from analyze_email import analyze_email


test_email = {
    "sender": "Ravi Dahiya <ravi@example.com>",
    "subject": "Urgent project meeting tomorrow",
    "body": """
Hi Ravi,

We have an important project meeting tomorrow at 10 AM.

Please make sure you attend the meeting.

This meeting is important because we need to
discuss the project deadline.

Regards,
Project Team
"""
}


print("Sending test email to AI...")

result = analyze_email(test_email)

print()
print("AI Analysis:")
print(result)