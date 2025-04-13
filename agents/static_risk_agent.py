"""Agent for analyzing static project risks."""

import os
import google.generativeai as genai
from crewai import Agent
from langchain_google_genai import ChatGoogleGenerativeAI
from config import GEMINI_API_KEY, HIGH_RISK_THRESHOLD, MEDIUM_RISK_THRESHOLD
from utils.pdf_processor import extract_text_from_pdf
from utils.vector_store import VectorStore

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)

class StaticRiskAgent:
    def __init__(self):
        """Initialize the static risk analysis agent."""
        self.vector_store = VectorStore(collection_name="project_risks")
        self.llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", google_api_key=GEMINI_API_KEY)
        
        # Create CrewAI agent
        self.agent = Agent(
            role="Static Risk Analyzer",
            goal="Analyze project documents and identify static risk factors",
            backstory="I am an expert in project risk assessment with years of experience in identifying risk factors from project documentation.",
            verbose=True,
            llm=self.llm,
            allow_delegation=False
        )
        
    def vectorize_project_document(self, pdf_path, project_id):
        """Extract text from PDF and store in vector database."""
        if not pdf_path or not os.path.exists(pdf_path):
            return False
            
        # Extract text from PDF
        document_text = extract_text_from_pdf(pdf_path)
        
        if not document_text:
            return False
            
        # Store in vector database
        self.vector_store.add_document(
            doc_id=f"project_{project_id}",
            text=document_text,
            metadata={"project_id": project_id, "type": "project_document"}
        )
        
        return True
        
    def _evaluate_risk_category(self, category, value):
        """Evaluate risk level for a specific category."""
        risk_score = 0
        
        if category == "project_location":
            if value.lower() in ["us", "uk", "united states", "united kingdom"]:
                risk_score = 30  # Low risk
            elif value.lower() in ["india", "asia", "china", "japan", "southeast asia", "south asia"]:
                risk_score = 60  # Medium risk
            elif value.lower() in ["africa", "middle east", "afghanistan", "iraq", "syria"]:
                risk_score = 85  # High risk
            else:
                risk_score = 50  # Default to medium
                
        elif category == "project_size":
            try:
                size = float(value)
                if size < 20:
                    risk_score = 30  # Low risk
                elif size < 50:
                    risk_score = 60  # Medium risk
                else:
                    risk_score = 85  # High risk
            except ValueError:
                risk_score = 50  # Default to medium
                
        elif category == "technology":
            if "new" in value.lower() or "emerging" in value.lower() or "innovative" in value.lower():
                risk_score = 85  # High risk
            elif "established" in value.lower() or "proven" in value.lower() or "old" in value.lower():
                risk_score = 30  # Low risk
            else:
                risk_score = 50  # Default to medium
                
        elif category == "employee_resignation":
            risk_score = 85 if value.lower() == "yes" else 30
            
        elif category == "missed_milestone":
            risk_score = 85 if value.lower() == "yes" else 30
            
        elif category == "budget_problem":
            risk_score = 85 if value.lower() == "yes" else 30
            
        return risk_score
        
    def analyze_project_risks(self, project_data):
        """Analyze static risk factors for a project."""
        risk_factors = []
        total_score = 0
        factor_count = 0
        
        # Evaluate each risk category
        for category, value in project_data.items():
            if value and category in [
                "project_location", "project_size", "technology", 
                "employee_resignation", "missed_milestone", "budget_problem"
            ]:
                score = self._evaluate_risk_category(category, value)
                
                # Format category name for display
                display_name = category.replace("_", " ").title()
                
                # Determine risk level description
                if score >= HIGH_RISK_THRESHOLD:
                    risk_level = "High"
                elif score >= MEDIUM_RISK_THRESHOLD:
                    risk_level = "Medium"
                else:
                    risk_level = "Low"
                
                risk_factors.append({
                    "name": display_name,
                    "value": value,
                    "score": score,
                    "risk_level": risk_level,
                    "description": f"{display_name} ({value}) - {risk_level} Risk"
                })
                
                total_score += score
                factor_count += 1
        
        # Calculate average risk score
        avg_score = total_score / factor_count if factor_count > 0 else 0
        
        # Determine overall risk level
        if avg_score >= HIGH_RISK_THRESHOLD:
            risk_level = "High"
        elif avg_score >= MEDIUM_RISK_THRESHOLD:
            risk_level = "Medium"
        else:
            risk_level = "Low"
            
        return {
            "risk_factors": risk_factors,
            "risk_score": round(avg_score, 2),
            "risk_level": risk_level
        }