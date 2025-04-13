"""Utilities for sending email notifications."""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import SMTP_SERVER, SMTP_PORT, EMAIL_SENDER, EMAIL_PASSWORD

class EmailSender:
    def __init__(self):
        """Initialize the email sender with SMTP configuration."""
        self.server = SMTP_SERVER
        self.port = SMTP_PORT
        self.sender = EMAIL_SENDER
        self.password = EMAIL_PASSWORD
        
    def send_risk_notification(self, recipient, project_name, risk_score, risk_factors):
        """Send a high-risk notification email to the project manager."""
        if not self.sender or not self.password:
            print("Email credentials not configured. Skipping notification.")
            return False
            
        # Create message
        message = MIMEMultipart()
        message["From"] = self.sender
        message["To"] = recipient
        message["Subject"] = f"HIGH RISK ALERT: Project {project_name}"
        
        # Email body
        body = f"""
        <html>
        <body>
            <h2>Project Risk Alert</h2>
            <p>The risk analysis system has identified <strong>HIGH RISK</strong> for project: <strong>{project_name}</strong>.</p>
            <p>Current risk score: <strong>{risk_score}</strong> </p>
            
            <h3>Risk Factors:</h3>
            <ul>
        """
        
        # Add risk factors
        for factor in risk_factors:
            body += f"<li><strong>{factor['name']}:</strong> {factor['description']}</li>"
            
        body += """
            </ul>
            
            <p>Please review the project status and take appropriate action.</p>
            <p>This is an automated message from the Risk Management System.</p>
        </body>
        </html>
        """
        
        # Attach HTML content
        message.attach(MIMEText(body, "html"))
        
        # Send email
        try:
            with smtplib.SMTP(self.server, self.port) as server:
                server.starttls()
                server.login(self.sender, self.password)
                server.send_message(message)
            return True
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False