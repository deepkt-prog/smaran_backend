import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging

# Set up logging to simulate "sending" if no SMTP creds
logging.basicConfig(filename='notification_logs.txt', level=logging.INFO, format='%(asctime)s - %(message)s')

class NotificationService:
    def __init__(self):
        # In a real app, load these from environment variables
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))
        self.smtp_user = os.getenv("SMTP_USER", "test@example.com")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "password")
        self.simulation_mode = True # For now, default to simulation to avoid crashing

    def send_email(self, to_email: str, subject: str, message_body: str):
        if self.simulation_mode:
            self._log_notification("EMAIL", to_email, subject, message_body)
            return True

        try:
            msg = MIMEMultipart()
            msg['From'] = self.smtp_user
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(message_body, 'plain'))

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            return True
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False

    def send_whatsapp(self, mobile_number: str, message_body: str):
        # Placeholder for WhatsApp logic (e.g. via Twilio or Meta API)
        # For now, simulate it
        self._log_notification("WHATSAPP", mobile_number, "Smaran Reminder", message_body)
        return True

    def _log_notification(self, type, recipient, subject, body):
        log_message = f"[{type}] To: {recipient} | Subject: {subject} | Body: {body}"
        print(log_message) # Print to console for immediate visibility
        logging.info(log_message) # Log to file for verification

notification_service = NotificationService()
