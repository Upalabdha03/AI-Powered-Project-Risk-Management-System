"""Main module for the AI-powered risk management system."""

import os
import google.generativeai as genai
from crewai import Crew, Task
from config import GEMINI_API_KEY
from agents.static_risk_agent import StaticRiskAgent
from agents.news_risk_agent import NewsRiskAgent
from agents.risk_calculator_agent import RiskCalculatorAgent
from agents.notification_agent import NotificationAgent

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)

class RiskManagementSystem:
    def __init__(self):
        """Initialize the risk management system with all agents."""
        # Initialize all agents
        self.static_risk_agent = StaticRiskAgent()
        self.news_risk_agent = NewsRiskAgent()
        self.risk_calculator_agent = RiskCalculatorAgent()
        self.notification_agent = NotificationAgent()
        
        # Setup CrewAI
        self.agents = [
            self.static_risk_agent.agent,
            self.news_risk_agent.agent,
            self.risk_calculator_agent.agent,
            self.notification_agent.agent
        ]
        
    def analyze_project_risk(self, project_data, pdf_path=None):
        """Analyze project risk with the full agent crew."""
        # Step 1: Analyze static risks
        if pdf_path:
            self.static_risk_agent.vectorize_project_document(pdf_path, project_data.get("project_id", "unknown"))
            
        static_risk_analysis = self.static_risk_agent.analyze_project_risks(project_data)
        
        # Step 2: Analyze news risks
        news_risk_analysis = self.news_risk_agent.analyze_news_risks(project_data)
        
        # Step 3: Calculate overall risk
        overall_risk = self.risk_calculator_agent.calculate_overall_risk(
            static_risk_analysis, 
            news_risk_analysis
        )
        
        # Step 4: Handle notifications if needed
        notification_result = self.notification_agent.handle_risk_notification(
            project_data, 
            overall_risk
        )
        
        # Combine all results
        return {
            "project_data": project_data,
            "static_risk_analysis": static_risk_analysis,
            "news_risk_analysis": news_risk_analysis,
            "overall_risk": overall_risk,
            "notification": notification_result
        }
        
    def run_crew_workflow(self, project_data, pdf_path=None):
        """Run the full CrewAI workflow for risk analysis."""
        # Define tasks for each agent
        static_risk_task = Task(
            description=f"Analyze static risks for project {project_data.get('project_name', 'Unknown')}",
            agent=self.static_risk_agent.agent,
            expected_output="Detailed static risk analysis with risk factors and scores"
        )
        
        news_risk_task = Task(
            description=f"Analyze news-based risks for project {project_data.get('project_name', 'Unknown')}",
            agent=self.news_risk_agent.agent,
            expected_output="Detailed news risk analysis with risk factors and scores"
        )
        
        risk_calculator_task = Task(
            description="Calculate overall project risk by combining static and news risks",
            agent=self.risk_calculator_agent.agent,
            expected_output="Overall risk assessment with combined risk factors and recommendations",
            context=[static_risk_task, news_risk_task]
        )
        
        notification_task = Task(
            description="Send notifications if project risk is high",
            agent=self.notification_agent.agent,
            expected_output="Notification status and details",
            context=[risk_calculator_task]
        )
        
        # Create the crew
        risk_crew = Crew(
            agents=self.agents,
            tasks=[static_risk_task, news_risk_task, risk_calculator_task, notification_task],
            verbose=True
        )
        
        # Run the crew
        crew_result = risk_crew.kickoff()
        
        return crew_result

# Example usage
if __name__ == "__main__":
    # Initialize system
    risk_system = RiskManagementSystem()
    
    # Example project data
    project_data = {
        "project_id": "P12345",
        "project_name": "New Solar Power Plant",
        "project_location": "Middle East",
        "project_size": "75",
        "technology": "new solar panel technology",
        "employee_resignation": "no",
        "missed_milestone": "yes",
        "budget_problem": "yes",
        "project_manager_email": "pm@example.com"
    }
    
    # Run analysis
    result = risk_system.analyze_project_risk(project_data)
    
    # Print result
    print(f"Overall Risk Level: {result['overall_risk']['risk_level']}")
    print(f"Risk Score: {result['overall_risk']['risk_score']}")
    
    if result['notification']['notification_sent']:
        print(f"Notification sent to: {result['notification']['recipient']}")
    else:
        print(f"No notification sent. Reason: {result['notification'].get('reason', 'Unknown')}")