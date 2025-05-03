import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config.settings import EMAIL_CONFIG

def send_email_notification(to_email, subject, body):
    try:
        # Set up the email server and login
        smtp_server = EMAIL_CONFIG["smtp_server"]
        port = EMAIL_CONFIG["port"]
        sender_email = EMAIL_CONFIG["EMAIL_ADDRESS"]
        password = EMAIL_CONFIG["EMAIL_PASSWORD"]

        # Create the email message
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        # Connect to the server and send the email
        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, to_email, msg.as_string())

        print(f"Email sent to {to_email}: {subject}")
    except Exception as e:
        print(f"Failed to send email to {to_email}: {e}")

def send_sms_notification(to_phone, message):
    # Placeholder for SMS sending logic
    print(f"SMS sent to {to_phone}: {message}")