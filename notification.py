import os
import smtplib
import requests
from dotenv import load_dotenv
from email.mime.text import MIMEText

# --------------------------------------------
# Load environment variables from .env
# --------------------------------------------
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# --------------------------------------------
# SEND EMAIL (Once at end)
# --------------------------------------------
def send_email_notification(subject, summary_text):
    try:
        sender = "kunalpathak25012004@gmail.com"
        
        receiver = "kunalpathak0125@gmail.com"
        password = EMAIL_APP_PASSWORD

        msg = MIMEText(summary_text)
        msg["Subject"] = subject
        msg["From"] = f"Kunal <{sender}>"
        msg["To"] = receiver

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender, password)
            server.send_message(msg)

        print("✅ Summary email sent successfully!")

    except Exception as e:
        print("❌ Email sending failed:", e)
        send_slack_notification("Email Notification Error", str(e))


# --------------------------------------------
# SEND SLACK (only on errors)
# --------------------------------------------
def send_slack_notification(title, message):
    try:
        payload = {
            "text": f"*{title}*\n{message}"
        }
        response = requests.post(WEBHOOK_URL, json=payload)

        if response.status_code == 200:
            print("✅ Slack notification sent successfully!")
        else:
            print("❌ Slack notification failed:", response.text)

    except Exception as e:
        print("❌ Slack notification error:", e)
