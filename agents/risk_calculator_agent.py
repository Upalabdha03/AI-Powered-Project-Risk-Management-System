"""Agent for calculating overall project risk."""

import google.generativeai as genai
from crewai import Agent
from langchain_google_genai import ChatGoogleGenerativeAI
from config import GEMINI_API_KEY, HIGH_RISK_THRESHOLD, MEDIUM_RISK_THRESHOLD, STATIC_RISK_WEIGHT, NEWS_RISK_WEIGHT

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)

class RiskCalculatorAgent:
    def __init__(self):
        """Initialize the risk calculator agent."""
        self.llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", google_api_key=GEMINI_API_KEY)
        
        # Create CrewAI agent
        self.agent = Agent(
            role="Risk Calculator",
            goal="Calculate overall project risk by combining static and dynamic risk factors",
            backstory="I am a sophisticated risk analyst capable of weighing various risk factors to determine overall project risk levels.",
            verbose=True,
            llm=self.llm,
            allow_delegation=False
        )
        
    def calculate_overall_risk(self, static_risk_analysis, news_risk_analysis):
        """Calculate overall project risk by combining static and news risks."""
        # Extract risk scores
        static_risk_score = static_risk_analysis.get("risk_score", 0)
        news_risk_score = news_risk_analysis.get("risk_score", 0)
        
        # Calculate weighted average
        overall_score = (static_risk_score * STATIC_RISK_WEIGHT) + (news_risk_score * NEWS_RISK_WEIGHT)
        
        # Determine overall risk level
        if overall_score >= HIGH_RISK_THRESHOLD:
            risk_level = "High"
        elif overall_score >= MEDIUM_RISK_THRESHOLD:
            risk_level = "Medium"
        else:
            risk_level = "Low"
            
        # Combine risk factors
        risk_factors = static_risk_analysis.get("risk_factors", []) + news_risk_analysis.get("risk_factors", [])
        
        # Sort risk factors by score (highest first)
        risk_factors.sort(key=lambda x: x.get("score", 0), reverse=True)
        
        # LLM analysis for additional insights
        risk_insights = self._generate_risk_insights(
            overall_score, 
            risk_level, 
            risk_factors, 
            static_risk_analysis, 
            news_risk_analysis
        )
        
        return {
            "risk_score": round(overall_score, 2),
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "insights": risk_insights,
            "static_risk_score": static_risk_score,
            "news_risk_score": news_risk_score
        }
        
    def _generate_risk_insights(self, overall_score, risk_level, risk_factors, static_risk_analysis, news_risk_analysis):
        """Generate additional risk insights using LLM."""
        # Create a summary of the top risk factors
        top_factors = risk_factors[:5] if len(risk_factors) > 5 else risk_factors
        
        factors_summary = "\n".join([
            f"- {factor.get('name')}: {factor.get('description', '')}" 
            for factor in top_factors
        ])
        
        # Create prompt for the LLM
        prompt = f"""
        As a risk management expert, provide insights and recommendations based on the following project risk analysis:
        
        Overall Risk Score: {overall_score}
        Risk Level: {risk_level}
        
        Top Risk Factors:
        {factors_summary}
        
        Static Risk Score: {static_risk_analysis.get("risk_score", 0)}
        News-based Risk Score: {news_risk_analysis.get("risk_score", 0)}
        
        Please provide:
        1. A brief summary of the key risk drivers
        2. 2-3 specific recommendations to mitigate the identified risks
        3. Potential impact if these risks are not addressed
        
        Keep your response concise and actionable.
        """
        
        # Get LLM response
        model = genai.GenerativeModel('gemini-1.5-pro')
        response = model.generate_content(prompt)
        
        return response.text