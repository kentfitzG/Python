import smtplib
from email.mime.text import MIMEText

def send_email(report_html, recipient):
    msg = MIMEText(report_html, 'html')
    msg['Subject'] = f"Daily Critical CVE Briefing - {datetime.now().strftime('%Y-%m-%d')}"
    msg['From'] = "agent@yourdomain.com"
    msg['To'] = recipient

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login("your_email@gmail.com", "your_app_password")
        server.send_message(msg)