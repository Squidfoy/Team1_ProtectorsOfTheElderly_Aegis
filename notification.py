# Sends fall alert notifications via email (Gmail)
# Last edited by: Alianna
# Last updated date: Wed Apr 8 2026
import os
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

EMAIL_ADDRESS  = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")


def validate_email(email):
    """Check if email address format is valid."""
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(pattern, email) is not None


def build_message(camera_name, video_file_name):
    """Build the notification message with timestamp and camera info."""
    now = datetime.now()
    date_str = now.strftime("%B %d, %Y")
    time_str = now.strftime("%I:%M %p")
    return (
        f"AEGIS FALL ALERT\n\n"
        f"A fall was detected!\n"
        f"Date: {date_str}\n"
        f"Time: {time_str}\n"
        f"Camera: {camera_name}\n"
        f"File: {video_file_name}"
    )


def send_notif(email, video_file_name, camera_name="webcam"):
    """Send fall alert via Gmail."""
    if not validate_email(email):
        print(f"[NOTIFICATIONS]Invalid email format: {email}")
        return False

    message = build_message(camera_name, video_file_name)

    try:
        msg = MIMEMultipart()
        msg["From"]    = EMAIL_ADDRESS
        msg["To"]      = email
        msg["Subject"] = "Aegis Fall Alert"
        msg.attach(MIMEText(message, "plain"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, email, msg.as_string())

        print(f"[NOTIFICATIONS]Email sent to: {email}")
        return True
    except Exception as e:
        print(f"[NOTIFICATIONS]Failed to send email: {e}")
        return False
