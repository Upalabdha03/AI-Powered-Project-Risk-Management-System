"""Agent for sending risk notifications."""

import google.generativeai as genai
from crewai import Agent
from langchain_google_genai import ChatGoogleGenerativeAI
from config import GEMINI_API_KEY, HIGH_RISK_THRESHOLD
from utils.email_sender import EmailSender

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)

class NotificationAgent:
    def __init__(self):
        """Initialize the notification agent."""
        self.email_sender = EmailSender()
        self.llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", google_api_key=GEMINI_API_KEY)
        
        # Create CrewAI agent
        self.agent = Agent(
            role="Risk Notification Manager",
            goal="Notify project stakeholders of high-risk situations",
            backstory="I am responsible for ensuring that project managers are promptly informed of high-risk situations that require immediate attention.",
            verbose=True,
            llm=self.llm,
            allow_delegation=False
        )
        
    def handle_risk_notification(self, project_data, risk_analysis):
        """Handle risk notification based on risk level."""
        # Check if risk level is high
        if risk_analysis.get("risk_level") == "High":
            return self._send_high_risk_notification(project_data, risk_analysis)
        else:
            return {
                "notification_sent": False,
                "reason": f"Risk level is {risk_analysis.get('risk_level')}, notification threshold not met"
            }
            
    def _send_high_risk_notification(self, project_data, risk_analysis):
        """Send notification for high-risk projects."""
        project_name = project_data.get("project_name", "Unnamed Project")
        project_manager_email = project_data.get("project_manager_email")
        
        if not project_manager_email:
            return {
                "notification_sent": False,
                "reason": "Project manager email not provided"
            }
            
        # Get top risk factors
        risk_factors = risk_analysis.get("risk_factors", [])
        top_factors = risk_factors[:5] if len(risk_factors) > 5 else risk_factors
        
        # Prepare risk factors for email
        email_risk_factors = []
        for factor in top_factors:
            
            email_risk_factors.append({
                "name": factor.get("name", "Unknown"),
                "description": factor.get("description", "No description available")
            })
        
        # Send email notification
        notification_success = self.email_sender.send_risk_notification(
            recipient=project_manager_email,
            project_name=project_name,
            risk_score=risk_analysis.get("risk_score", 0),
            risk_factors=email_risk_factors
        )
        
        if notification_success:
            return {
                "notification_sent": True,
                "recipient": project_manager_email,
                "project": project_name,
                "timestamp": genai.utils.get_current_time()
            }
        else:
            return {
                "notification_sent": False,
                "reason": "Failed to send email notification"
            }