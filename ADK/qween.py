import streamlit as st
import plotly.graph_objects as go
import ollama
import yfinance as yf
import pandas as pd
from datetime import datetime
from curl_cffi import requests as curl_requests

# --- CONFIGURATION & PATCH ---
# Using a patched session to avoid 'Connection closed abruptly' errors
session = curl_requests.Session(impersonate="chrome")

st.set_page_config(page_title="Qwen Financial Agent", layout="wide")
st.title("Qwen Financial AI Agent")
st.caption("Running locally via Ollama (Qwen 2.5)")

# --- TOOL DEFINITIONS ---

def get_stock_price_and_fundamentals(ticker: str,**kwargs):
    """Fetches current price, PE ratio, and Market Cap for a ticker."""
    stock = yf.Ticker(ticker, session=session)
    info = stock.info
    if not info or "currentPrice" not in info:
        return {"error": f"No data found for {ticker}."}
    return {
        "price": info.get("currentPrice"),
        "currency": info.get("currency"),
        "pe": info.get("trailingPE"),
        "market_cap": info.get("marketCap"),
        "summary": (info.get("longBusinessSummary", "")[:150] + "...")
    }

def get_historical_data(ticker: str, period: str = "1mo"):
    """Fetches historical closing prices for charts."""
    stock = yf.Ticker(ticker, session=session)
    hist = stock.history(period=period)
    if hist.empty: return []
    hist_reset = hist.reset_index()
    hist_reset['Date'] = pd.to_datetime(hist_reset['Date']).dt.strftime('%Y-%m-%d')
    return hist_reset[['Date', 'Close']].to_dict(orient='records')

def get_stock_news(ticker: str,**kwargs):
    """Fetches the latest 5 news headlines safely."""
    stock = yf.Ticker(ticker, session=session)
    news = stock.news
    
    if not news:
        return {"message": "No recent news found for this ticker."}
    
    # We use .get() to avoid KeyErrors if Yahoo changes their field names
    formatted_news = []
    for n in news[:5]:
        item = {
            "title": n.get('title') or n.get('headline') or "No Title Available",
            "publisher": n.get('publisher') or n.get('source') or "Unknown Source",
            "link": n.get('link') or n.get('url') or "#"
        }
        formatted_news.append(item)
        
    return formatted_news

def get_financial_statements(ticker: str,**kwargs):
    """Fetches key items from the Income Statement and Balance Sheet."""
    stock = yf.Ticker(ticker, session=session)
    # Getting only the most recent year to keep output small for the LLM
    try:
        financials = stock.financials.iloc[:, 0].to_dict()
        balance = stock.balance_sheet.iloc[:, 0].to_dict()
        return {"income_statement_recent": financials, "balance_sheet_recent": balance}
    except:
        return {"error": "Financial statements not available."}

def get_analyst_recommendations(ticker: str):
    """Fetches analyst buy/sell ratings and price targets."""
    stock = yf.Ticker(ticker, session=session)
    info = stock.info
    return {
        "rating": info.get("recommendationKey"),
        "target_mean": info.get("targetMeanPrice"),
        "target_high": info.get("targetHighPrice"),
        "analyst_count": info.get("numberOfAnalystOpinions")
    }

def get_dividends_and_splits(ticker: str):
    """Fetches dividend yield and recent corporate actions."""
    stock = yf.Ticker(ticker, session=session)
    info = stock.info
    return {
        "dividend_yield": info.get("dividendYield"),
        "dividend_rate": info.get("dividendRate"),
        "payout_ratio": info.get("payoutRatio"),
        "recent_actions": stock.actions.tail(3).to_dict()
    }

# Mapping for the execution loop
available_functions = {
    'get_stock_price_and_fundamentals': get_stock_price_and_fundamentals,
    'get_historical_data': get_historical_data,
    'get_stock_news': get_stock_news,
    'get_financial_statements': get_financial_statements,
    'get_analyst_recommendations': get_analyst_recommendations,
    'get_dividends_and_splits': get_dividends_and_splits
}

# --- UI LOGIC ---
query = st.text_input("Ask me anything about a stock (e.g., 'Is Reliance a good buy?' or 'Show me Apple news')")

if query:
    # Defining the model name (ensure you pulled this in Ollama)
    MODEL_NAME = 'qwen2.5:0.5b' 

    with st.spinner("Qwen is analyzing..."):
        # 1. Initial Request
        messages = [
            {'role': 'system', 'content': 'You are a helpful assistant with access to tools. Use tools for EVERY financial query. If a user asks for a price, news, or chart, you MUST call the appropriate function.'},
            {'role': 'user', 'content': query}
        ]
        response = ollama.chat(
            model=MODEL_NAME,
            messages=messages,
            tools=list(available_functions.values()),
        )

        # 2. Tool Execution Loop
        if response.message.tool_calls:
            for call in response.message.tool_calls:
                func_name = call.function.name
                args = call.function.arguments
                
                if func_name in available_functions:
                    result = available_functions[func_name](**args)
                    
                    messages.append(response.message)
                    messages.append({'role': 'tool', 'content': str(result)})

            # 3. Final Summary
            final_response = ollama.chat(model=MODEL_NAME, messages=messages)
            st.markdown(final_response.message.content)
            
            # --- AUTOMATIC CHARTING ---
            # If the LLM called historical data, we auto-plot it
            if "get_historical_data" in [c.function.name for c in response.message.tool_calls]:
                # Extract ticker from arguments of the tool call
                ticker = response.message.tool_calls[0].function.arguments.get('ticker', '').upper()
                data = get_historical_data(ticker)
                if data:
                    df = pd.DataFrame(data)
                    fig = go.Figure(data=[go.Scatter(x=df['Date'], y=df['Close'], line=dict(color='#00ffcc'))])
                    fig.update_layout(title=f"{ticker} Price Trend", template="plotly_dark")
                    st.plotly_chart(fig)
        else:
            st.markdown(response.message.content)