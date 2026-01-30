import streamlit as st
import plotly.graph_objects as go
from data import get_stock_data, get_fundamental_metrics
from valuation import calculate_dcf, calculate_multiples
import pandas as pd
import numpy as np

# Premium styling
st.set_page_config(page_title="Equity Research", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * { font-family: 'Inter', sans-serif; }
    
    .stApp {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%);
    }
    
    h1, h2, h3 { 
        font-weight: 300 !important;
        letter-spacing: -0.02em;
        color: #ffffff !important;
    }
    
    .section-header {
        font-size: 13px;
        text-transform: uppercase;
        letter-spacing: 0.15em;
        color: #666;
        font-weight: 600;
        margin: 40px 0 20px 0;
        border-bottom: 1px solid rgba(255,255,255,0.05);
        padding-bottom: 10px;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 32px;
        border-bottom: 1px solid rgba(255,255,255,0.05);
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 16px 0px;
        background-color: transparent;
        border: none;
        color: #666;
        font-size: 12px;
        font-weight: 500;
        letter-spacing: 0.1em;
        text-transform: uppercase;
    }
    
    .stTabs [aria-selected="true"] {
        color: #fff;
        border-bottom: 2px solid #fff;
    }
    
    .ticker-display {
        font-size: 48px;
        font-weight: 200;
        letter-spacing: -0.03em;
        margin-bottom: 4px;
    }
    
    .company-name {
        font-size: 16px;
        color: #888;
        font-weight: 400;
        letter-spacing: 0.02em;
    }
    
    div[data-testid="stMetricValue"] {
        font-size: 28px;
        font-weight: 300;
    }
    
    div[data-testid="stMetricLabel"] {
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: #888;
    }
    
    .stTextInput>div>div>input {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.1);
        color: #fff;
        font-size: 14px;
        padding: 12px 16px;
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

# Header
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown("<div style='font-size: 14px; font-weight: 500; letter-spacing: 0.15em; color: #666; margin-bottom: 40px;'>EQUITY RESEARCH</div>", unsafe_allow_html=True)
with col2:
    ticker = st.text_input("", placeholder="Enter ticker...", label_visibility="collapsed").upper()

if ticker:
    data = get_stock_data(ticker)
    info = data['info']
    fundamentals = get_fundamental_metrics(data)
    
    # Ticker header
    st.markdown(f"<div class='ticker-display'>{ticker}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='company-name'>{info.get('longName', '')}</div>", unsafe_allow_html=True)
    
    st.markdown("<div style='height: 40px'></div>", unsafe_allow_html=True)
    
    # Key metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    price = info.get('currentPrice', 0)
    change_pct = info.get('regularMarketChangePercent', 0)
    
    with col1:
        st.metric("PRICE", f"${price:.2f}", f"{change_pct:+.2f}%")
    with col2:
        st.metric("MARKET CAP", f"${info.get('marketCap', 0)/1e9:.1f}B")
    with col3:
        st.metric("P / E", f"{info.get('trailingPE', 0):.1f}")
    with col4:
        st.metric("REV GROWTH", f"{fundamentals['revenue_growth']:.1f}%")
    with col5:
        st.metric("MARGIN", f"{fundamentals['profit_margin']:.1f}%")
    
    # TABS
    tab1, tab2, tab3, tab4 = st.tabs(["OVERVIEW", "COMPARATIVE ANALYSIS", "VALUATION", "PROJECTIONS"])
    
    with tab1:
        st.markdown("<div class='section-header'>Historical Performance (Max)</div>", unsafe_allow_html=True)
        
        # Get maximum available data
        import yfinance as yf
        stock = yf.Ticker(ticker)
        hist_max = stock.history(period="max")
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=hist_max.index,
            y=hist_max['Close'],
            mode='lines',
            name='',
            line=dict(color='#ffffff', width=1.5),
            fill='tozeroy',
            fillcolor='rgba(255,255,255,0.03)',
            hovertemplate='%{y:$.2f}<extra></extra>'
        ))
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=400,
            margin=dict(l=0, r=0, t=20, b=0),
            xaxis=dict(
                showgrid=False,
                gridcolor='rgba(255,255,255,0.05)',
                tickfont=dict(size=10, color='#666')
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='rgba(255,255,255,0.05)',
                tickfont=dict(size=10, color='#666')
            ),
            showlegend=False,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Stats
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("ALL-TIME HIGH", f"${hist_max['High'].max():.2f}")
        with col2:
            st.metric("ALL-TIME LOW", f"${hist_max['Low'].min():.2f}")
        with col3:
            all_time_return = ((hist_max['Close'].iloc[-1] - hist_max['Close'].iloc[0]) / hist_max['Close'].iloc[0] * 100)
            st.metric("ALL-TIME RETURN", f"{all_time_return:+.1f}%")
        with col4:
            ytd_data = hist_max[hist_max.index.year == hist_max.index[-1].year]
            if len(ytd_data) > 0:
                ytd_return = ((ytd_data['Close'].iloc[-1] - ytd_data['Close'].iloc[0]) / ytd_data['Close'].iloc[0] * 100)
                st.metric("YTD RETURN", f"{ytd_return:+.1f}%")
    
    with tab2:
        st.markdown("<div class='section-header'>Comparative Analysis</div>", unsafe_allow_html=True)
        
        comparison_tickers = st.text_input("Enter tickers to compare (comma-separated)", 
                                          placeholder=f"{ticker}, AAPL, MSFT").upper()
        
        if comparison_tickers:
            tickers_list = [t.strip() for t in comparison_tickers.split(",")]
            
            # Fetch all data
            all_data = {}
            for t in tickers_list:
                try:
                    stock = yf.Ticker(t)
                    all_data[t] = stock.history(period="max")
                except:
                    pass
            
            if all_data:
                # Normalize to 100 at start date
                st.markdown("<div style='font-size: 12px; color: #666; margin-bottom: 20px;'>NORMALIZED PERFORMANCE (BASE 100)</div>", unsafe_allow_html=True)
                
                fig_comp = go.Figure()
                
                colors = ['#ffffff', '#00ff88', '#ff4444', '#ffa500', '#00bfff', '#ff69b4']
                
                for idx, (t, hist) in enumerate(all_data.items()):
                    normalized = (hist['Close'] / hist['Close'].iloc[0]) * 100
                    
                    fig_comp.add_trace(go.Scatter(
                        x=normalized.index,
                        y=normalized,
                        mode='lines',
                        name=t,
                        line=dict(color=colors[idx % len(colors)], width=2),
                        hovertemplate=f'{t}: %{{y:.1f}}<extra></extra>'
                    ))
                
                fig_comp.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    height=450,
                    margin=dict(l=0, r=0, t=20, b=0),
                    xaxis=dict(
                        showgrid=False,
                        gridcolor='rgba(255,255,255,0.05)',
                        tickfont=dict(size=10, color='#666')
                    ),
                    yaxis=dict(
                        showgrid=True,
                        gridcolor='rgba(255,255,255,0.05)',
                        tickfont=dict(size=10, color='#666')
                    ),
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1,
                        font=dict(size=11, color='#888')
                    ),
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig_comp, use_container_width=True)
                
                # Performance comparison table
                st.markdown("<div class='section-header'>Return Comparison</div>", unsafe_allow_html=True)
                
                perf_data = []
                for t, hist in all_data.items():
                    ytd = hist[hist.index.year == hist.index[-1].year]
                    one_year = hist.last('1Y')
                    five_year = hist.last('5Y')
                    
                    perf_data.append({
                        'Ticker': t,
                        'YTD': f"{((ytd['Close'].iloc[-1] / ytd['Close'].iloc[0] - 1) * 100):+.1f}%" if len(ytd) > 0 else 'N/A',
                        '1Y': f"{((one_year['Close'].iloc[-1] / one_year['Close'].iloc[0] - 1) * 100):+.1f}%" if len(one_year) > 0 else 'N/A',
                        '5Y': f"{((five_year['Close'].iloc[-1] / five_year['Close'].iloc[0] - 1) * 100):+.1f}%" if len(five_year) > 0 else 'N/A',
                        'All-Time': f"{((hist['Close'].iloc[-1] / hist['Close'].iloc[0] - 1) * 100):+.1f}%"
                    })
                
                df_perf = pd.DataFrame(perf_data)
                st.dataframe(df_perf, use_container_width=True, hide_index=True)
    
    with tab3:
        st.markdown("<div class='section-header'>Valuation Multiples</div>", unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 3])
        
        with col1:
            multiples = calculate_multiples(data)
            
            for metric, value in multiples.items():
                if value and value != 0:
                    st.markdown(f"""
                    <div style='display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid rgba(255,255,255,0.03);'>
                        <span style='color: #888; font-size: 12px; letter-spacing: 0.05em;'>{metric}</span>
                        <span style='color: #fff; font-size: 14px; font-weight: 400;'>{value:.2f}</span>
                    </div>
                    """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("<div style='font-size: 12px; color: #666; letter-spacing: 0.05em; margin-bottom: 16px;'>DCF MODEL</div>", unsafe_allow_html=True)
            
            growth = st.slider("GROWTH RATE (%)", 0, 30, 10, label_visibility="collapsed") / 100
            discount = st.slider("DISCOUNT RATE (%)", 5, 15, 10, label_visibility="collapsed") / 100
            
            fcf = info.get('freeCashflow', 1e9)
            projected = [fcf * ((1 + growth) ** i) for i in range(1, 6)]
            shares = info.get('sharesOutstanding', 1e9)
            
            dcf = calculate_dcf(projected, 0.02, discount, shares)
            fair_value = dcf['price_per_share']
            upside = ((fair_value - price) / price * 100)
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("FAIR VALUE", f"${fair_value:.2f}")
            with col_b:
                st.metric("IMPLIED RETURN", f"{upside:+.1f}%")
    
    with tab4:
        st.markdown("<div class='section-header'>Price Projections</div>", unsafe_allow_html=True)
        
        # Calculate projections based on historical growth
        hist = data['price_history']
        current_price = hist['Close'].iloc[-1]
        
        # Calculate different growth scenarios
        historical_cagr = ((hist['Close'].iloc[-1] / hist['Close'].iloc[0]) ** (1 / len(hist.index.year.unique())) - 1)
        
        col1, col2 = st.columns(2)
        with col1:
            bull_growth = st.slider("BULL CASE GROWTH (%)", 10, 50, 25) / 100
        with col2:
            bear_growth = st.slider("BEAR CASE GROWTH (%)", -20, 10, 5) / 100
        
        # Project 5 years out
        years = np.arange(0, 6)
        dates = pd.date_range(start=hist.index[-1], periods=6, freq='YE')
        
        bull_case = [current_price * ((1 + bull_growth) ** year) for year in years]
        base_case = [current_price * ((1 + historical_cagr) ** year) for year in years]
        bear_case = [current_price * ((1 + bear_growth) ** year) for year in years]
        
        fig_proj = go.Figure()
        
        # Historical
        fig_proj.add_trace(go.Scatter(
            x=hist.index,
            y=hist['Close'],
            mode='lines',
            name='Historical',
            line=dict(color='rgba(255,255,255,0.3)', width=1),
        ))
        
        # Projections
        fig_proj.add_trace(go.Scatter(
            x=dates, y=bull_case,
            mode='lines+markers',
            name='Bull Case',
            line=dict(color='#00ff88', width=2, dash='dash'),
            marker=dict(size=6)
        ))
        
        fig_proj.add_trace(go.Scatter(
            x=dates, y=base_case,
            mode='lines+markers',
            name='Base Case',
            line=dict(color='#ffffff', width=2, dash='dash'),
            marker=dict(size=6)
        ))
        
        fig_proj.add_trace(go.Scatter(
            x=dates, y=bear_case,
            mode='lines+markers',
            name='Bear Case',
            line=dict(color='#ff4444', width=2, dash='dash'),
            marker=dict(size=6)
        ))
        
        fig_proj.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=450,
            margin=dict(l=0, r=0, t=20, b=0),
            xaxis=dict(showgrid=False, tickfont=dict(size=10, color='#666')),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', tickfont=dict(size=10, color='#666')),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=11, color='#888')),
            hovermode='x unified'
        )
        
        st.plotly_chart(fig_proj, use_container_width=True)
        
        # Projection targets
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("5Y BULL TARGET", f"${bull_case[-1]:.2f}", f"+{((bull_case[-1]/current_price - 1) * 100):.0f}%")
        with col2:
            st.metric("5Y BASE TARGET", f"${base_case[-1]:.2f}", f"+{((base_case[-1]/current_price - 1) * 100):.0f}%")
        with col3:
            st.metric("5Y BEAR TARGET", f"${bear_case[-1]:.2f}", f"{((bear_case[-1]/current_price - 1) * 100):+.0f}%")

else:
    st.markdown("<div style='height: 200px'></div>", unsafe_allow_html=True)
    st.markdown("<div style='text-align: center; font-size: 14px; color: #444; letter-spacing: 0.1em;'>ENTER A TICKER TO BEGIN ANALYSIS</div>", unsafe_allow_html=True)