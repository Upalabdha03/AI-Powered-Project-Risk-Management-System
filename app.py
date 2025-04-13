"""Streamlit application for the AI-powered risk management system."""

import streamlit as st
import pandas as pd
import os
from main import RiskManagementSystem
from utils.pdf_processor import save_uploaded_pdf
from config import HIGH_RISK_THRESHOLD, MEDIUM_RISK_THRESHOLD
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Initialize the risk management system
risk_system = RiskManagementSystem()

# Set page configuration
st.set_page_config(
    page_title="AI Risk Management System",
    page_icon="🛡️",
    layout="wide"
)

# Main title
st.title("🛡️ AI-Powered Project Risk Management System")
st.markdown("Analyze project risks using AI agents and get real-time alerts")

# Sidebar for inputs
with st.sidebar:
    st.header("Project Information")
    
    # Project details form
    with st.form("project_details_form"):
        project_id = st.text_input("Project ID", value="P12345")
        project_name = st.text_input("Project Name", value="New Construction Project")
        
        # Location with predefined options
        location_options = ["US", "UK", "India", "China", "Africa", "Middle East"]
        project_location = st.selectbox("Project Location", options=location_options)
        
        # Project size
        project_size = st.number_input("Project Size (in millions $)", min_value=1, max_value=200, value=30)
        
        # Technology options
        tech_options = ["New/Emerging Technology", "Established Technology", "Legacy Technology"]
        technology = st.selectbox("Technology Type", options=tech_options)
        
        # Risk indicators
        col1, col2 = st.columns(2)
        with col1:
            employee_resignation = st.checkbox("Key Employee Resignation")
            missed_milestone = st.checkbox("Key Milestone Missed")
        with col2:
            budget_problem = st.checkbox("Budget Problems")
        
        # Project manager email
        pm_email = st.text_input("Project Manager Email", value="manager@example.com")
        
        # Project document upload
        project_doc = st.file_uploader("Upload Project Document (PDF)", type=["pdf"])
        
        # Submit button
        submitted = st.form_submit_button("Analyze Risk")

# Main content area
if submitted:
    # Show loading spinner
    with st.spinner("AI agents are analyzing project risks..."):
        # Process the uploaded PDF if provided
        pdf_path = None
        if project_doc:
            pdf_path = save_uploaded_pdf(project_doc)
        
        # Prepare project data
        project_data = {
            "project_id": project_id,
            "project_name": project_name,
            "project_location": project_location,
            "project_size": str(project_size),
            "technology": technology,
            "employee_resignation": "yes" if employee_resignation else "no",
            "missed_milestone": "yes" if missed_milestone else "no",
            "budget_problem": "yes" if budget_problem else "no",
            "project_manager_email": pm_email
        }
        
        # Run the risk analysis
        results = risk_system.analyze_project_risk(project_data, pdf_path)
    
    # Display results in tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Overall Risk", "Static Risks", "News Risks", "Notification Status"])
    
    # Tab 1: Overall Risk
    with tab1:
        overall_risk = results["overall_risk"]
        risk_level = overall_risk["risk_level"]
        risk_score = overall_risk["risk_score"]
        
        # Display risk score with color
        col1, col2 = st.columns([1, 2])
        with col1:
            # Show risk score in a circle with color
            if risk_level == "High":
                st.markdown(
                    f"""
                    <div style="background-color:#FF5A5A; width:150px; height:150px; border-radius:50%; display:flex; 
                    align-items:center; justify-content:center; color:white; font-size:24px; font-weight:bold;">
                    {risk_score}
                    </div>
                    <p style="text-align:center; font-weight:bold; color:#FF5A5A; font-size:20px; margin-top:10px;">
                    HIGH RISK
                    </p>
                    """, 
                    unsafe_allow_html=True
                )
            elif risk_level == "Medium":
                st.markdown(
                    f"""
                    <div style="background-color:#FFC55A; width:150px; height:150px; border-radius:50%; display:flex; 
                    align-items:center; justify-content:center; color:white; font-size:24px; font-weight:bold;">
                    {risk_score}
                    </div>
                    <p style="text-align:center; font-weight:bold; color:#FFC55A; font-size:20px; margin-top:10px;">
                    MEDIUM RISK
                    </p>
                    """, 
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f"""
                    <div style="background-color:#5AFF5A; width:150px; height:150px; border-radius:50%; display:flex; 
                    align-items:center; justify-content:center; color:white; font-size:24px; font-weight:bold;">
                    {risk_score}
                    </div>
                    <p style="text-align:center; font-weight:bold; color:#5AFF5A; font-size:20px; margin-top:10px;">
                    LOW RISK
                    </p>
                    """, 
                    unsafe_allow_html=True
                )
        
        with col2:
            # Show insights
            st.subheader("Risk Insights")
            st.markdown(overall_risk.get("insights", "No insights available"))
        
        # Show top risk factors
        st.subheader("Top Risk Factors")
        risk_factors = overall_risk.get("risk_factors", [])
        
        if risk_factors:
            # Convert to DataFrame for display
            risk_df = pd.DataFrame([
                {
                    "Risk Factor": factor.get("name", ""),
                    "Description": factor.get("description", ""),
                    "Score": factor.get("score", 0),
                    "Level": factor.get("risk_level", "")
                }
                for factor in risk_factors[:5]  # Show top 5
            ])
            
            # Display as table with conditional formatting
            st.dataframe(
                risk_df,
                column_config={
                    "Risk Factor": st.column_config.TextColumn("Risk Factor"),
                    "Description": st.column_config.TextColumn("Description"),
                    "Score": st.column_config.NumberColumn(
                        "Score", 
                        format="%.1f"
                    ),
                    "Level": st.column_config.TextColumn("Level")
                },
                use_container_width=True
            )
    
    # Tab 2: Static Risks
    with tab2:
        static_risks = results["static_risk_analysis"]
        
        # Show static risk score
        st.subheader(f"Static Risk Score: {static_risks['risk_score']} ({static_risks['risk_level']})")
        
        # Show risk factors
        static_factors = static_risks.get("risk_factors", [])
        
        if static_factors:
            # Create columns for each risk category
            cols = st.columns(3)
            
            for i, factor in enumerate(static_factors):
                with cols[i % 3]:
                    # Determine color based on risk level
                    if factor.get("risk_level") == "High":
                        color = "#FF5A5A"
                    elif factor.get("risk_level") == "Medium":
                        color = "#FFC55A"
                    else:
                        color = "#5AFF5A"
                    
                    # Display risk factor in a card
                    st.markdown(
                        f"""
                        <div style="border:1px solid {color}; border-radius:5px; padding:10px; margin-bottom:10px;">
                            <h4 style="color:{color};">{factor.get('name', '')}</h4>
                            <p><strong>Value:</strong> {factor.get('value', '')}</p>
                            <p><strong>Risk Level:</strong> {factor.get('risk_level', '')}</p>
                            <p><strong>Risk Score:</strong> {factor.get('score', 0)}</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
    
    # Tab 3: News Risks
    with tab3:
        news_risks = results["news_risk_analysis"]
        
        # Show news risk score
        st.subheader(f"News-based Risk Score: {news_risks['risk_score']} ({news_risks['risk_level']})")
        
        # Show news items
        news_items = news_risks.get("news_items", [])
        
        if news_items:
            st.markdown("### Relevant News Articles")
            
            # Display news items
            for news in news_items[:10]:  # Show top 10
                st.markdown(
                    f"""
                    <div style="border:1px solid #DDDDDD; border-radius:5px; padding:10px; margin-bottom:10px;">
                        <h4>{news.get('title', '')}</h4>
                        <p><strong>Source:</strong> {news.get('source', '')}</p>
                        <p><strong>Date:</strong> {news.get('date', '')}</p>
                        <p><a href="{news.get('link', '#')}" target="_blank">Read more</a></p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.info("No relevant news found for this project.")
    
    # Tab 4: Notification Status
    with tab4:
        notification = results["notification"]
        
        if notification.get("notification_sent", False):
            st.success(f"✅ Notification sent to {notification.get('recipient', '')}")
            
            # Show notification details
            st.markdown("### Notification Details")
            st.markdown(f"**Project:** {notification.get('project', '')}")
            st.markdown(f"**Timestamp:** {notification.get('timestamp', '')}")
            
            # Show preview of the email
            st.markdown("### Email Preview")
            st.markdown(
                f"""
                <div style="border:1px solid #DDDDDD; border-radius:5px; padding:20px; background-color:#F9F9F9;">
                    <h3>HIGH RISK ALERT: Project {project_name}</h3>
                    <p>The risk analysis system has identified <strong>HIGH RISK</strong> for project: <strong>{project_name}</strong>.</p>
                    <p>Current risk score: <strong>{risk_score}</strong></p>
                    <h4>Risk Factors:</h4>
                    <ul>
                        {''.join([f'<li><strong>{factor.get("name")}:</strong> {factor.get("description")}</li>' for factor in overall_risk.get("risk_factors", [])[:3]])}
                    </ul>
                    <p>Please review the project status and take appropriate action.</p>
                    <p>This is an automated message from the Risk Management System.</p>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.info(f"ℹ️ No notification sent. Reason: {notification.get('reason', 'Unknown')}")

# Show help information if no analysis has been run
if not submitted:
    st.info("""
    ### How to use this system
    
    1. Enter your project details in the sidebar
    2. Upload a project document (optional)
    3. Click "Analyze Risk" to run the AI analysis
    4. View the results in the tabs above
    
    The system uses four AI agents working together:
    - Static Risk Agent: Analyzes project attributes and documents
    - News Risk Agent: Monitors global news for relevant risks
    - Risk Calculator Agent: Combines all risk factors
    - Notification Agent: Sends alerts when risk levels are high
    """)
    
    # Show sample risk visualization
    st.subheader("Sample Risk Visualization")
    
    # Create sample data
    sample_data = pd.DataFrame({
        "Risk Factor": ["Project Location", "Technology", "Budget Issues", "Market Volatility", "Team Experience"],
        "Score": [85, 75, 65, 55, 45],
        "Level": ["High", "High", "Medium", "Medium", "Medium"]
    })
    
    # Display sample data
    st.bar_chart(sample_data.set_index("Risk Factor")["Score"])