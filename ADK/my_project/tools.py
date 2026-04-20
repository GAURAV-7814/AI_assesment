import yfinance as yf
import pandas as pd

def get_stock_price_and_fundamentals(ticker: str):
    """Fetches current price, PE ratio, and Market Cap for a ticker."""
    stock = yf.Ticker(ticker)
    info = stock.info
    if not info:
        return {"error": f"Could not find data for ticker {ticker}."}

    raw_summary = info.get("longBusinessSummary")
    summary = (raw_summary[:200] + "...") if raw_summary else "No summary available."

    return {
        "price": info.get("currentPrice"),
        "currency": info.get("currency"),
        "pe_ratio": info.get("trailingPE"),
        "market_cap": info.get("marketCap"),
        "summary": summary
    }

def get_historical_data(ticker: str, period: str = "1mo"):
    """Fetches historical closing prices for charts."""
    stock = yf.Ticker(ticker)
    hist = stock.history(period=period)
    if hist.empty:
        return []

    hist_reset = hist.reset_index()
    hist_reset['Date'] = pd.to_datetime(hist_reset['Date']).dt.strftime('%Y-%m-%d')
    return hist_reset[['Date', 'Close']].to_dict(orient='records')

def get_stock_news(ticker: str):
    """Fetches the latest news for a specific stock."""
    stock = yf.Ticker(ticker)
    return stock.news[:5]

def get_financial_statements(ticker: str):
    """Fetches the annual income statement and balance sheet summary."""
    stock = yf.Ticker(ticker)
    try:
        income_stmt = stock.financials.head(5).to_dict() 
        balance_sheet = stock.balance_sheet.head(5).to_dict()
        return {"income_statement": income_stmt, "balance_sheet": balance_sheet}
    except:
        return {"error": "Financial statements unavailable."}

def get_analyst_recommendations(ticker: str):
    """Fetches analyst ratings and price targets."""
    stock = yf.Ticker(ticker)
    info = stock.info
    return {
        "recommendation": info.get("recommendationKey"),
        "target_mean": info.get("targetMeanPrice"),
        "analyst_count": info.get("numberOfAnalystOpinions")
    }

def get_dividends_and_splits(ticker: str):
    """Fetches dividend yield and historical dividend/split events."""
    stock = yf.Ticker(ticker)
    info = stock.info
    return {
        "dividend_yield": info.get("dividendYield"),
        "payout_ratio": info.get("payoutRatio"),
        "history": stock.actions.tail(5).to_dict()
    }

# Export list of tools for the agent
FINANCIAL_TOOLS = [
    get_stock_price_and_fundamentals,
    get_historical_data,
    get_stock_news,
    get_financial_statements,
    get_analyst_recommendations,
    get_dividends_and_splits
]