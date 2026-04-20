import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from agent import FinancialAgent
from tools import get_historical_data
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file
# --- CONFIGURATION ---
API_KEY = os.getenv("GEMINI_API_KEY") # Ideally use st.secrets or env vars

st.set_page_config(page_title="Stock Insights AI", layout="wide")
st.title("📈 Stock Insights AI Agent")
st.caption("Powered by Google Gemini & Yahoo Finance")

# Initialize Agent in Session State
if "financial_agent" not in st.session_state:
    st.session_state.financial_agent = FinancialAgent(API_KEY)

query = st.text_input("Ask me about a stock (e.g., 'What is the price of Reliance?' or 'Show me Apple vs Microsoft')")

if query:
    with st.spinner("Analyzing..."):
        # Get AI response
        response = st.session_state.financial_agent.ask(query)
        st.markdown(response.text)
        
        # --- UI ENHANCEMENT: PLOTTING ---
        # Logic to check if a chart was requested
        if any(word in query.lower() for word in ["chart", "trend", "history", "graph"]):
            # Use the last word as a probable ticker (Simple extraction)
            ticker_candidate = query.split()[-1].strip("?").upper()
            
            # Fetch data using the logic from tools.py
            raw_data = get_historical_data(ticker_candidate)
            
            if raw_data:
                df = pd.DataFrame(raw_data)
                fig = go.Figure(data=[go.Scatter(
                    x=df['Date'], 
                    y=df['Close'], 
                    mode='lines',
                    line=dict(color='#00ffcc')
                )])
                fig.update_layout(
                    title=f"{ticker_candidate} Performance Trend", 
                    template="plotly_dark",
                    xaxis_title="Date",
                    yaxis_title="Closing Price"
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("📊 Note: Could not generate chart. Please specify a valid ticker like 'AAPL' or 'RELIANCE.NS'.")