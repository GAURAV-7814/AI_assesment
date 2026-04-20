import streamlit as st
import plotly.graph_objects as go
import google.generativeai as genai
import yfinance as yf
from datetime import datetime

# --- CONFIGURATION ---
genai.configure(api_key="AIzaSyCyWUtjz1PESBRXCZXB2D57f20Uj9X-pm0")

st.set_page_config(page_title="Stock Insights AI", layout="wide")
st.title("📈 Stock Insights AI Agent")
st.caption("Powered by Google Gemini & Yahoo Finance")

# --- TOOL DEFINITIONS ---
def get_stock_price_and_fundamentals(ticker: str):
    """Fetches current price, PE ratio, and Market Cap for a ticker."""
    stock = yf.Ticker(ticker)
    info = stock.info
    
    # If info is empty, return an error message the LLM can understand
    if not info:
        return {"error": f"Could not find data for ticker {ticker}. Verify the ticker symbol."}

    # Safely get the summary
    raw_summary = info.get("longBusinessSummary")
    summary = (raw_summary[:200] + "...") if raw_summary else "No summary available."

    return {
        "price": info.get("currentPrice"),
        "currency": info.get("currency"),
        "pe_ratio": info.get("trailingPE"),
        "market_cap": info.get("marketCap"),
        "summary": summary
    }

import pandas as pd

def get_historical_data(ticker: str, period: str = "1mo"):
    """Fetches historical closing prices with safe date formatting."""
    stock = yf.Ticker(ticker)
    hist = stock.history(period=period)
    
    if hist.empty:
        return []

    # 1. Reset index to move 'Date' from Index to a Column
    hist_reset = hist.reset_index()
    
    # 2. Force conversion to datetime just in case
    hist_reset['Date'] = pd.to_datetime(hist_reset['Date'])
    
    # 3. Now .dt will work reliably. 
    # Also using .dt.date to remove the timestamp/timezone for the LLM
    hist_reset['Date'] = hist_reset['Date'].dt.strftime('%Y-%m-%d')
    
    # Return as a list of dictionaries for Gemini
    return hist_reset[['Date', 'Close']].to_dict(orient='records')

def get_stock_news(ticker: str):
    """Fetches the latest news for a specific stock."""
    stock = yf.Ticker(ticker)
    return stock.news[:5]

def get_financial_statements(ticker: str):
    """Fetches the annual income statement and balance sheet summary."""
    stock = yf.Ticker(ticker)
    
    # Financials returns a DataFrame, we convert to dict for the LLM
    income_stmt = stock.financials.head(5).to_dict() 
    balance_sheet = stock.balance_sheet.head(5).to_dict()
    
    return {
        "recent_income_statement": income_stmt,
        "recent_balance_sheet": balance_sheet
    }

def get_analyst_recommendations(ticker: str):
    """Fetches analyst ratings and price targets."""
    stock = yf.Ticker(ticker)
    info = stock.info
    
    return {
        "recommendation": info.get("recommendationKey"),
        "target_low": info.get("targetLowPrice"),
        "target_mean": info.get("targetMeanPrice"),
        "target_high": info.get("targetHighPrice"),
        "number_of_analysts": info.get("numberOfAnalystOpinions")
    }

def get_dividends_and_splits(ticker: str):
    """Fetches dividend yield and historical dividend/split events."""
    stock = yf.Ticker(ticker)
    info = stock.info
    
    return {
        "dividend_rate": info.get("dividendRate"),
        "dividend_yield": info.get("dividendYield"),
        "last_dividend_date": info.get("lastDividendDate"),
        "payout_ratio": info.get("payoutRatio"),
        "history": stock.actions.tail(5).to_dict() # Shows recent dividends/splits
    }

# --- AI AGENT SETUP ---
# Defining tools for Gemini to use
tools = [
    get_stock_price_and_fundamentals,
    get_historical_data,
    get_stock_news,
    get_financial_statements,   # New
    get_analyst_recommendations, # New
    get_dividends_and_splits     # New
]
model = genai.GenerativeModel(
    model_name='gemini-3-flash-preview',  # Use the preview version for better performance
    tools=tools,
    system_instruction="You are a financial AI agent. Use the provided tools to answer user queries. For Indian stocks, append .NS for NSE (e.g., RELIANCE.NS). Always summarize the data professionally."
)

# --- UI LOGIC ---
query = st.text_input("Ask me about a stock (e.g., 'What is the price of Reliance?' or 'Show me Apple vs Microsoft')")

# --- UI LOGIC ---
if query:
    chat = model.start_chat(enable_automatic_function_calling=True)
    
    with st.spinner("Analyzing..."):
        response = chat.send_message(query)
        st.markdown(response.text)
        
        # 1. Check if the user is asking for a chart
        if any(word in query.lower() for word in ["chart", "trend", "history", "graph"]):
            ticker_to_plot = query.split()[-1].upper() 
            # Note: You might want a more robust way to get the ticker from Gemini
            
            raw_data = get_historical_data(ticker_to_plot)
            
            # 2. SAFETY GATE: Only plot if data is NOT empty
            if raw_data: 
                import pandas as pd
                df_for_plot = pd.DataFrame(raw_data)
                
                # Check if 'Date' actually exists in the columns
                if 'Date' in df_for_plot.columns:
                    fig = go.Figure(data=[go.Scatter(
                        x=df_for_plot['Date'], 
                        y=df_for_plot['Close'], 
                        mode='lines',
                        line=dict(color='#00ffcc')
                    )])
                    fig.update_layout(title=f"{ticker_to_plot} Performance", template="plotly_dark")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Historical price columns are unavailable for this entity.")
            else:
                # This handles private companies like JMAN or typos
                st.info("📈 Charting unavailable: This entity is either private or the ticker was not found.")