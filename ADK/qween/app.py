import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from agent import FinancialAgent
from tools import get_historical_data

st.set_page_config(page_title="ADK Financial AI", layout="wide")
st.title("AI Financial Agent")

# Initialize Agent
if "agent" not in st.session_state:
    st.session_state.agent = FinancialAgent()

query = st.text_input("Ask about any stock:")

if query:
    with st.spinner("Analyzing..."):
        answer, tool_calls = st.session_state.agent.run(query)
        st.markdown(answer)

        # Plotting Logic based on tool results
        for call in tool_calls:
            if call['name'] == 'get_historical_data':
                ticker = call['args'].get('ticker', '').upper()
                if ticker:
                    data = get_historical_data(ticker)
                    if data:
                        df = pd.DataFrame(data)
                        fig = go.Figure(data=[go.Scatter(x=df['Date'], y=df['Close'], line=dict(color='#00ffcc'))])
                        fig.update_layout(title=f"{ticker} Trend", template="plotly_dark")
                        st.plotly_chart(fig, use_container_width=True)