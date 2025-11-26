"""
Alert Service - Email and Telegram notifications
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class AlertService:
    """Send email and telegram alerts"""
    
    def __init__(self, email_config=None):
        """Initialize alert service"""
        self.email_config = email_config or {}
        
    def send_email(self, subject, message):
        """Send email alert"""
        if not self.email_config:
            return False
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_config.get('from_email', '')
            msg['To'] = self.email_config.get('to_email', '')
            msg['Subject'] = subject
            
            msg.attach(MIMEText(message, 'plain'))
            
            server = smtplib.SMTP(
                self.email_config.get('smtp_server', 'smtp.gmail.com'),
                self.email_config.get('smtp_port', 587)
            )
            server.starttls()
            server.login(
                self.email_config.get('from_email', ''),
                self.email_config.get('from_password', '')
            )
            
            server.send_message(msg)
            server.quit()
            
            return True
        except Exception as e:
            print(f"Email alert failed: {str(e)}")
            return False
    
    def send_telegram(self, message):
        """Send Telegram alert (if configured)"""
        # Placeholder for Telegram bot implementation
        pass
