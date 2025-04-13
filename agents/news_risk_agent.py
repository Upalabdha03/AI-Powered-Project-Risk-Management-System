"""Agent for analyzing news-based dynamic risks."""

import google.generativeai as genai
from crewai import Agent
from langchain_google_genai import ChatGoogleGenerativeAI
from config import GEMINI_API_KEY, HIGH_RISK_THRESHOLD, MEDIUM_RISK_THRESHOLD
from utils.news_scraper import NewsScraper

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)

class NewsRiskAgent:
    def __init__(self):
        """Initialize the news risk analysis agent."""
        self.news_scraper = NewsScraper()
        self.llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", google_api_key=GEMINI_API_KEY)
        
        # Create CrewAI agent
        self.agent = Agent(
            role="News Risk Analyzer",
            goal="Monitor and analyze global news for project-relevant risk factors",
            backstory="I am an expert in identifying emerging risks from global news sources that might impact ongoing projects.",
            verbose=True,
            llm=self.llm,
            allow_delegation=False
        )
        
    def get_relevant_news(self, project_data):
        """Gather news relevant to the project."""
        # Define keywords based on project data
        keywords = ["tariff", "exchange rate", "currency", "import ban", "export ban"]
        
        # Add location-specific keywords
        if project_data.get("project_location"):
            keywords.append(project_data["project_location"])
            
        # Add industry-specific keywords based on technology
        if project_data.get("technology"):
            keywords.append(project_data["technology"])
            
        # Scrape economic and geopolitical news
        economic_news = self.news_scraper.get_economic_news()
        geopolitical_news = self.news_scraper.get_geopolitical_news()
        
        # Filter relevant news
        relevant_economic = self.news_scraper.filter_relevant_news(economic_news, keywords)
        relevant_geopolitical = self.news_scraper.filter_relevant_news(geopolitical_news, keywords)
        
        return relevant_economic + relevant_geopolitical
        
    def analyze_news_risks(self, project_data):
        """Analyze dynamic risks from news for a project."""
        # Get relevant news
        relevant_news = self.get_relevant_news(project_data)
        
        if not relevant_news:
            return {
                "risk_factors": [],
                "risk_score": 0,
                "risk_level": "Low",
                "news_items": []
            }
            
        # Analyze news significance with the LLM
        news_risks = []
        total_score = 0
        
        for news in relevant_news[:10]:  # Limit to top 10 news items
            # Create a prompt for the LLM to evaluate news significance
            prompt = f"""
            Analyze the following news headline and determine its risk impact on a project with these details:
            - Project location: {project_data.get('project_location', 'Unknown')}
            - Project size: {project_data.get('project_size', 'Unknown')}
            - Technology: {project_data.get('technology', 'Unknown')}
            
            News headline: "{news['title']}" from {news['source']}
            
            Assign a risk score from 0-100, where:
            - 0-39: Low risk impact
            - 40-69: Medium risk impact
            - 70-100: High risk impact
            
            Provide your assessment in this format:
            Score: [0-100]
            Risk level: [Low/Medium/High]
            Explanation: [Brief explanation]
            """
            
            # Get LLM response
            model = genai.GenerativeModel('gemini-1.5-pro')
            response = model.generate_content(prompt)
            response_text = response.text
            
            # Parse the response
            try:
                lines = response_text.strip().split('\n')
                score_line = [line for line in lines if line.startswith("Score:")][0]
                level_line = [line for line in lines if line.startswith("Risk level:")][0]
                explanation_lines = [line for line in lines if line.startswith("Explanation:")]
                
                score = int(score_line.split("Score:")[1].strip().split()[0])
                risk_level = level_line.split("Risk level:")[1].strip()
                explanation = explanation_lines[0].split("Explanation:")[1].strip() if explanation_lines else ""
                
                news_risks.append({
                    "name": "News Risk",
                    "value": news['title'],
                    "score": score,
                    "risk_level": risk_level,
                    "description": explanation,
                    "source": news['source'],
                    "link": news.get('link', '')
                })
                
                total_score += score
                
            except (IndexError, ValueError) as e:
                print(f"Error parsing LLM response for news risk: {e}")
        
        # Calculate average risk score
        avg_score = total_score / len(news_risks) if news_risks else 0
        
        # Determine overall risk level
        if avg_score >= HIGH_RISK_THRESHOLD:
            risk_level = "High"
        elif avg_score >= MEDIUM_RISK_THRESHOLD:
            risk_level = "Medium"
        else:
            risk_level = "Low"
            
        return {
            "risk_factors": news_risks,
            "risk_score": round(avg_score, 2),
            "risk_level": risk_level,
            "news_items": relevant_news
        }