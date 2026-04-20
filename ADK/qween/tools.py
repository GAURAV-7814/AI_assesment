import yfinance as yf
import pandas as pd
from curl_cffi import requests as curl_requests

# Patched session to avoid connection issues
session = curl_requests.Session(impersonate="chrome")

def get_stock_price_and_fundamentals(ticker: str, **kwargs):
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

def get_historical_data(ticker: str, period: str = "1mo", **kwargs):
    """Fetches historical closing prices for charts."""
    stock = yf.Ticker(ticker, session=session)
    hist = stock.history(period=period)
    if hist.empty: return []
    hist_reset = hist.reset_index()
    hist_reset['Date'] = pd.to_datetime(hist_reset['Date']).dt.strftime('%Y-%m-%d')
    return hist_reset[['Date', 'Close']].to_dict(orient='records')

def get_stock_news(ticker: str, **kwargs):
    """Fetches the latest 5 news headlines safely."""
    stock = yf.Ticker(ticker, session=session)
    news = stock.news
    if not news: return {"message": "No recent news found."}
    
    formatted_news = []
    for n in news[:5]:
        formatted_news.append({
            "title": n.get('title') or n.get('headline') or "No Title",
            "publisher": n.get('publisher') or "Unknown",
            "link": n.get('link') or "#"
        })
    return formatted_news

def get_financial_statements(ticker: str, **kwargs):
    """Fetches income statement and balance sheet summary."""
    stock = yf.Ticker(ticker, session=session)
    try:
        financials = stock.financials.iloc[:, 0].to_dict()
        balance = stock.balance_sheet.iloc[:, 0].to_dict()
        return {"income_statement_recent": financials, "balance_sheet_recent": balance}
    except:
        return {"error": "Financials not available."}

def get_analyst_recommendations(ticker: str, **kwargs):
    """Fetches analyst ratings and targets."""
    stock = yf.Ticker(ticker, session=session)
    info = stock.info
    return {
        "rating": info.get("recommendationKey"),
        "target_mean": info.get("targetMeanPrice"),
        "analyst_count": info.get("numberOfAnalystOpinions")
    }

def get_dividends_and_splits(ticker: str, **kwargs):
    """Fetches dividend data and recent splits."""
    stock = yf.Ticker(ticker, session=session)
    info = stock.info
    return {
        "dividend_yield": info.get("dividendYield"),
        "recent_actions": stock.actions.tail(3).to_dict()
    }

# Registry for the Agent
AVAILABLE_TOOLS = {
    'get_stock_price_and_fundamentals': get_stock_price_and_fundamentals,
    'get_historical_data': get_historical_data,
    'get_stock_news': get_stock_news,
    'get_financial_statements': get_financial_statements,
    'get_analyst_recommendations': get_analyst_recommendations,
    'get_dividends_and_splits': get_dividends_and_splits
}