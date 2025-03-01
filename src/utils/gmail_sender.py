import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os

class GmailSender:
    def __init__(self):
        self.origin_gmail_address = os.getenv('OTP_GMAIL', '').strip().lower()
        self.gmail_password = os.getenv('GMAIL_PASSWORD', '').strip()
        self.smtp_server = 'smtp.gmail.com'
        self.smtp_port = 587

    def login_to_smtp_server(self):
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.origin_gmail_address, self.gmail_password)
            return server
        except Exception as e:
            raise Exception(f'SMTP Connection Error: {str(e)}')

    def send_gmail_message(self, dest_gmail_address, server, body, subject):
        msg = MIMEMultipart()
        msg['From'] = self.origin_gmail_address
        msg['To'] = dest_gmail_address
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        try:
            server.sendmail(self.origin_gmail_address, dest_gmail_address, msg.as_string())
        except Exception as e:
            raise Exception(f"Email sending error: {str(e)}")

    def send(self, subject, body, dest_gmail_address):
        try:
            server = self.login_to_smtp_server()
            self.send_gmail_message(dest_gmail_address, server, body, subject)
            server.quit()
            return {'status': "success"}
        except Exception as e:
            return {'status': "error", 'message': str(e)}
