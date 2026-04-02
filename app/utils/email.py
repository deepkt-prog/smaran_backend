import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import random
import string
from datetime import datetime, timedelta

# Configuration (Load from Environment Variables)
SMTP_HOST = os.getenv("SMTP_HOST", "mail.smtp2go.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "2525"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")

def generate_otp():
    """Generate a 6-digit OTP."""
    return ''.join(random.choices(string.digits, k=6))

def send_email(to_email, subject, body_html):
    """
    Send an email using the configured SMTP server.
    Returns True if successful, False otherwise.
    """
    if not (SMTP_USERNAME and SMTP_PASSWORD and SENDER_EMAIL):
        print("Email configuration missing. Skipping email send.")
        print(f"Would have sent email to {to_email} with subject: {subject}")
        return False

    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = to_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body_html, 'html'))

        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        text = msg.as_string()
        server.sendmail(SENDER_EMAIL, to_email, text)
        server.quit()
        print(f"Email sent successfully to {to_email}")
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

def send_otp_email(to_email, otp_code):
    subject = "Smaran - Verify your email"
    body = f"""
    <h2>Verify your Email</h2>
    <p>Your OTP code is: <strong>{otp_code}</strong></p>
    <p>This code is valid for 10 minutes.</p>
    """
    return send_email(to_email, subject, body)

def send_reminder_email(to_email, event_name, event_date):
    subject = f"Reminder: {event_name} is coming up!"
    body = f"""
    <h2>Smaran Event Reminder</h2>
    <p>The event <strong>{event_name}</strong> is scheduled for <strong>{event_date}</strong>.</p>
    """
    return send_email(to_email, subject, body)
