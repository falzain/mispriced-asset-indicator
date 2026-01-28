import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf
from io import BytesIO
import warnings
import random
warnings.filterwarnings('ignore')

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title="MISPRICED MARKET | Forensic Investment Intelligence",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# THEME CONFIGURATION - Bloomberg Terminal Style
# ============================================================================
THEME = {
    # Backgrounds - Pure terminal black
    'bg_primary': '#000000',
    'bg_secondary': '#0a0a0a',
    'bg_card': '#0d0d0d',
    'bg_hover': '#141414',
    'card_bg': '#0d0d0d',

    # Accent colors - Bloomberg orange
    'accent_primary': '#FF6600',
    'accent_secondary': '#CC5200',
    'accent_tertiary': '#994000',

    # Signal colors - Muted professional
    'opportunity': '#FF6600',
    'bullish': '#00C853',
    'bearish': '#FF3D00',
    'warning': '#888888',
    'neutral': '#444444',
    'positive': '#00C853',
    'negative': '#FF3D00',
    'green': '#00C853',
    'red': '#FF3D00',

    # Text hierarchy - Terminal style
    'text_primary': '#E0E0E0',
    'text_secondary': '#888888',
    'text_muted': '#555555',

    # Borders and lines
    'border': '#1a1a1a',
    'border_light': '#252525',
    'grid': '#141414',

    # Chart colors
    'chart_up': '#00C853',
    'chart_down': '#FF3D00',
    'chart_line': '#E0E0E0',
    'chart_volume': '#333333',
    'chart_ma1': '#FF6600',
    'chart_ma2': '#666666',
    'chart_bb': '#555555',
    'chart_grid': '#141414',

    # No glows - flat terminal look
    'glow_primary': 'rgba(0, 0, 0, 0)',
    'glow_success': 'rgba(0, 0, 0, 0)',
    'glow_warning': 'rgba(0, 0, 0, 0)',
    'glow_opportunity': 'rgba(0, 0, 0, 0)',
}

# ============================================================================
# MASSIVE CSS STYLING
# ============================================================================
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Inter:wght@400;500;600;700;800;900&display=swap');

    * {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }}

    code, .mono {{
        font-family: 'JetBrains Mono', monospace;
    }}

    .stApp {{
        background: {THEME['bg_primary']};
        color: {THEME['text_primary']};
    }}

    /* Hide Streamlit branding */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}

    /* Scrollbar */
    ::-webkit-scrollbar {{
        width: 8px;
        height: 8px;
    }}
    ::-webkit-scrollbar-track {{
        background: {THEME['bg_primary']};
    }}
    ::-webkit-scrollbar-thumb {{
        background: {THEME['border']};
        border-radius: 4px;
    }}
    ::-webkit-scrollbar-thumb:hover {{
        background: {THEME['accent_primary']};
    }}

    /* Main Header */
    .main-header {{
        font-size: 38px;
        font-weight: 800;
        letter-spacing: -0.02em;
        background: linear-gradient(135deg, {THEME['accent_primary']} 0%, {THEME['accent_secondary']} 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 4px;
    }}

    .subtitle {{
        font-size: 13px;
        color: {THEME['text_secondary']};
        text-align: center;
        margin-bottom: 24px;
        font-weight: 500;
        letter-spacing: 0.15em;
        text-transform: uppercase;
    }}

    /* Section Headers */
    .section-header {{
        font-size: 16px;
        font-weight: 700;
        color: {THEME['text_primary']};
        margin: 24px 0 16px 0;
        padding-bottom: 8px;
        border-bottom: 2px solid {THEME['border']};
        display: flex;
        align-items: center;
        gap: 10px;
    }}

    .section-header::before {{
        content: '';
        width: 4px;
        height: 20px;
        background: linear-gradient(180deg, {THEME['accent_primary']}, {THEME['opportunity']});
        border-radius: 2px;
    }}

    .subsection-header {{
        font-size: 13px;
        font-weight: 600;
        color: {THEME['accent_primary']};
        margin: 16px 0 12px 0;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }}

    /* Cards */
    .metric-card {{
        background: {THEME['bg_card']};
        border: 1px solid {THEME['border']};
        border-radius: 12px;
        padding: 16px;
        transition: all 0.3s ease;
    }}

    .metric-card:hover {{
        border-color: {THEME['accent_primary']};
        transform: translateY(-2px);
        box-shadow: 0 8px 24px {THEME['glow_primary']};
    }}

    .opportunity-card {{
        background: linear-gradient(135deg, rgba(255, 109, 0, 0.1) 0%, rgba(255, 109, 0, 0.05) 100%);
        border: 1px solid {THEME['opportunity']};
        border-radius: 12px;
        padding: 20px;
        position: relative;
        overflow: hidden;
    }}

    .opportunity-card::before {{
        content: '🎯';
        position: absolute;
        top: 10px;
        right: 10px;
        font-size: 24px;
        opacity: 0.3;
    }}

    .danger-card {{
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(239, 68, 68, 0.05) 100%);
        border: 1px solid {THEME['bearish']};
        border-radius: 12px;
        padding: 20px;
    }}

    /* News Cards */
    .news-card {{
        background: {THEME['bg_card']};
        border: 1px solid {THEME['border']};
        border-radius: 12px;
        padding: 0;
        margin: 12px 0;
        overflow: hidden;
        transition: all 0.3s ease;
        display: flex;
    }}

    .news-card:hover {{
        border-color: {THEME['accent_primary']};
        transform: translateX(8px);
        box-shadow: 0 8px 32px {THEME['glow_primary']};
    }}

    .news-image {{
        width: 200px;
        height: 140px;
        object-fit: cover;
        flex-shrink: 0;
    }}

    .news-image-placeholder {{
        width: 200px;
        height: 140px;
        background: linear-gradient(135deg, {THEME['bg_secondary']} 0%, {THEME['bg_hover']} 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 48px;
        flex-shrink: 0;
    }}

    .news-content {{
        padding: 16px 20px;
        flex: 1;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }}

    .news-title {{
        font-size: 15px;
        font-weight: 600;
        color: {THEME['text_primary']};
        line-height: 1.4;
        margin-bottom: 8px;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }}

    .news-meta {{
        display: flex;
        align-items: center;
        gap: 12px;
        margin-top: auto;
    }}

    .news-publisher {{
        font-size: 11px;
        font-weight: 600;
        color: {THEME['accent_primary']};
        background: rgba(99, 102, 241, 0.15);
        padding: 4px 10px;
        border-radius: 4px;
    }}

    .news-time {{
        font-size: 11px;
        color: {THEME['text_muted']};
    }}

    .news-sentiment {{
        font-size: 10px;
        font-weight: 700;
        padding: 3px 8px;
        border-radius: 4px;
        text-transform: uppercase;
    }}

    .sentiment-bullish {{
        background: rgba(16, 185, 129, 0.2);
        color: {THEME['bullish']};
    }}

    .sentiment-bearish {{
        background: rgba(239, 68, 68, 0.2);
        color: {THEME['bearish']};
    }}

    .sentiment-neutral {{
        background: rgba(139, 148, 158, 0.2);
        color: {THEME['text_secondary']};
    }}

    /* Earnings Calendar */
    .earnings-card {{
        background: {THEME['bg_card']};
        border: 1px solid {THEME['border']};
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }}

    .earnings-date {{
        font-size: 36px;
        font-weight: 800;
        color: {THEME['opportunity']};
        text-shadow: 0 0 20px {THEME['glow_opportunity']};
    }}

    .earnings-countdown {{
        font-size: 14px;
        color: {THEME['text_secondary']};
        margin-top: 8px;
    }}

    /* Badges */
    .badge {{
        display: inline-block;
        padding: 4px 10px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}

    .badge-opportunity {{
        background: rgba(255, 109, 0, 0.2);
        color: {THEME['opportunity']};
        border: 1px solid {THEME['opportunity']};
    }}

    .badge-bullish {{
        background: rgba(16, 185, 129, 0.2);
        color: {THEME['bullish']};
    }}

    .badge-bearish {{
        background: rgba(239, 68, 68, 0.2);
        color: {THEME['bearish']};
    }}

    .badge-neutral {{
        background: rgba(139, 148, 158, 0.2);
        color: {THEME['text_secondary']};
    }}

    /* Score Display */
    .score-display {{
        text-align: center;
        padding: 24px;
    }}

    .score-value {{
        font-size: 72px;
        font-weight: 900;
        line-height: 1;
        text-shadow: 0 0 40px currentColor;
    }}

    .score-label {{
        font-size: 14px;
        font-weight: 700;
        letter-spacing: 0.1em;
        margin-top: 12px;
        text-transform: uppercase;
    }}

    /* Buttons */
    .stButton>button {{
        background: linear-gradient(135deg, {THEME['accent_primary']} 0%, {THEME['accent_secondary']} 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        padding: 12px 24px;
        font-size: 13px;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        transition: all 0.3s ease;
        box-shadow: 0 4px 16px {THEME['glow_primary']};
    }}

    .stButton>button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 24px {THEME['glow_primary']};
    }}

    /* Time selector buttons */
    .time-btn {{
        background: {THEME['bg_card']};
        border: 1px solid {THEME['border']};
        color: {THEME['text_secondary']};
        padding: 6px 12px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s;
    }}

    .time-btn:hover, .time-btn.active {{
        background: {THEME['accent_primary']};
        border-color: {THEME['accent_primary']};
        color: white;
    }}

    /* Inputs */
    .stTextInput>div>div>input,
    .stNumberInput>div>div>input,
    .stSelectbox>div>div,
    .stTextArea>div>div>textarea {{
        background: {THEME['bg_card']} !important;
        border: 1px solid {THEME['border']} !important;
        border-radius: 8px !important;
        color: {THEME['text_primary']} !important;
        font-size: 14px !important;
    }}

    .stTextInput>div>div>input:focus,
    .stNumberInput>div>div>input:focus {{
        border-color: {THEME['accent_primary']} !important;
        box-shadow: 0 0 0 2px {THEME['glow_primary']} !important;
    }}

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 4px;
        background: {THEME['bg_secondary']};
        padding: 4px;
        border-radius: 8px;
    }}

    .stTabs [data-baseweb="tab"] {{
        background: transparent;
        border: none;
        color: {THEME['text_secondary']};
        font-weight: 600;
        font-size: 12px;
        padding: 10px 16px;
        border-radius: 6px;
        letter-spacing: 0.03em;
    }}

    .stTabs [aria-selected="true"] {{
        background: {THEME['accent_primary']};
        color: white;
    }}

    /* Expanders */
    .streamlit-expanderHeader {{
        background: {THEME['bg_card']};
        border: 1px solid {THEME['border']};
        border-radius: 8px;
        font-weight: 600;
        font-size: 13px;
    }}

    /* Metrics */
    div[data-testid="stMetricValue"] {{
        font-size: 28px;
        font-weight: 700;
        color: {THEME['text_primary']};
    }}

    div[data-testid="stMetricLabel"] {{
        font-size: 11px;
        color: {THEME['text_secondary']};
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}

    div[data-testid="stMetricDelta"] {{
        font-size: 12px;
        font-weight: 600;
    }}

    /* Links */
    a {{
        color: {THEME['accent_primary']};
        text-decoration: none;
        transition: all 0.2s;
    }}

    a:hover {{
        color: {THEME['opportunity']};
        text-shadow: 0 0 10px {THEME['glow_opportunity']};
    }}

    /* Tables */
    .dataframe {{
        background: {THEME['bg_card']} !important;
        border: 1px solid {THEME['border']} !important;
        border-radius: 8px !important;
    }}

    /* Sidebar */
    [data-testid="stSidebar"] {{
        background: {THEME['bg_secondary']};
        border-right: 1px solid {THEME['border']};
    }}

    [data-testid="stSidebar"] .stMarkdown {{
        color: {THEME['text_primary']};
    }}

    /* Progress bars */
    .stProgress > div > div > div > div {{
        background: linear-gradient(90deg, {THEME['accent_primary']}, {THEME['opportunity']});
    }}

    /* Alert boxes */
    .forensic-alert {{
        background: linear-gradient(135deg, rgba(255, 109, 0, 0.15) 0%, rgba(255, 109, 0, 0.05) 100%);
        border: 1px solid {THEME['opportunity']};
        border-left: 4px solid {THEME['opportunity']};
        border-radius: 8px;
        padding: 16px 20px;
        margin: 12px 0;
    }}

    .whale-alert {{
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(99, 102, 241, 0.05) 100%);
        border: 1px solid {THEME['accent_primary']};
        border-left: 4px solid {THEME['accent_primary']};
        border-radius: 8px;
        padding: 16px 20px;
        margin: 12px 0;
    }}

    .danger-alert {{
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.15) 0%, rgba(239, 68, 68, 0.05) 100%);
        border: 1px solid {THEME['bearish']};
        border-left: 4px solid {THEME['bearish']};
        border-radius: 8px;
        padding: 16px 20px;
        margin: 12px 0;
    }}

    /* Indicator pills */
    .indicator-pill {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
    }}

    .indicator-bullish {{
        background: rgba(16, 185, 129, 0.15);
        color: {THEME['bullish']};
        border: 1px solid {THEME['bullish']};
    }}

    .indicator-bearish {{
        background: rgba(239, 68, 68, 0.15);
        color: {THEME['bearish']};
        border: 1px solid {THEME['bearish']};
    }}

    .indicator-neutral {{
        background: rgba(139, 148, 158, 0.15);
        color: {THEME['text_secondary']};
        border: 1px solid {THEME['text_secondary']};
    }}

    .indicator-opportunity {{
        background: rgba(255, 109, 0, 0.15);
        color: {THEME['opportunity']};
        border: 1px solid {THEME['opportunity']};
    }}

    /* Portfolio table */
    .portfolio-row {{
        display: flex;
        align-items: center;
        padding: 12px 16px;
        background: {THEME['bg_card']};
        border: 1px solid {THEME['border']};
        border-radius: 8px;
        margin: 8px 0;
        transition: all 0.2s;
    }}

    .portfolio-row:hover {{
        border-color: {THEME['accent_primary']};
        background: {THEME['bg_hover']};
    }}

    /* Dividers */
    hr {{
        border: none;
        border-top: 1px solid {THEME['border']};
        margin: 24px 0;
    }}

    /* Tooltips */
    .tooltip {{
        position: relative;
        cursor: help;
    }}

    .tooltip:hover::after {{
        content: attr(data-tip);
        position: absolute;
        bottom: 100%;
        left: 50%;
        transform: translateX(-50%);
        background: {THEME['bg_hover']};
        border: 1px solid {THEME['border']};
        padding: 8px 12px;
        border-radius: 6px;
        font-size: 12px;
        white-space: nowrap;
        z-index: 1000;
    }}
</style>
""", unsafe_allow_html=True)

# ============================================================================
# TIMEFRAME CONFIGURATIONS
# ============================================================================
TIMEFRAMES = {
    '1W': {'period': '5d', 'interval': '15m', 'label': '1 Week'},
    '1M': {'period': '1mo', 'interval': '1h', 'label': '1 Month'},
    '3M': {'period': '3mo', 'interval': '1d', 'label': '3 Months'},
    'YTD': {'period': 'ytd', 'interval': '1d', 'label': 'Year to Date'},
    '1Y': {'period': '1y', 'interval': '1d', 'label': '1 Year'},
    '3Y': {'period': '3y', 'interval': '1wk', 'label': '3 Years'},
    '5Y': {'period': '5y', 'interval': '1wk', 'label': '5 Years'},
    'MAX': {'period': 'max', 'interval': '1mo', 'label': 'Maximum'},
}

# ============================================================================
# CLASS: DataEngine - Core data fetching and caching
# ============================================================================
class DataEngine:
    """Centralized data fetching with robust error handling"""

    @staticmethod
    @st.cache_data(ttl=300)
    def get_stock(ticker: str):
        """Fetch stock object with caching"""
        try:
            stock = yf.Ticker(ticker)
            _ = stock.info  # Validate ticker
            return stock
        except Exception as e:
            return None

    @staticmethod
    @st.cache_data(ttl=300)
    def get_info(ticker: str) -> dict:
        """Fetch stock info with error handling"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            return info if info else {}
        except:
            return {}

    @staticmethod
    @st.cache_data(ttl=300)
    def get_history(ticker: str, period: str = '1y', interval: str = '1d') -> pd.DataFrame:
        """Fetch price history with caching"""
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period, interval=interval)
            return hist if len(hist) > 0 else pd.DataFrame()
        except:
            return pd.DataFrame()

    @staticmethod
    @st.cache_data(ttl=600)
    def get_financials(ticker: str) -> dict:
        """Fetch all financial statements"""
        try:
            stock = yf.Ticker(ticker)
            return {
                'income_stmt': stock.quarterly_income_stmt,
                'balance_sheet': stock.quarterly_balance_sheet,
                'cash_flow': stock.quarterly_cash_flow,
                'income_annual': stock.income_stmt,
                'balance_annual': stock.balance_sheet,
                'cash_flow_annual': stock.cash_flow,
            }
        except:
            return {}

    @staticmethod
    @st.cache_data(ttl=600)
    def get_earnings_dates(ticker: str) -> pd.DataFrame:
        """Fetch earnings dates with estimates"""
        try:
            stock = yf.Ticker(ticker)
            earnings = stock.earnings_dates
            return earnings if earnings is not None else pd.DataFrame()
        except:
            return pd.DataFrame()

    @staticmethod
    @st.cache_data(ttl=600)
    def get_recommendations(ticker: str) -> pd.DataFrame:
        """Fetch analyst recommendations"""
        try:
            stock = yf.Ticker(ticker)
            recs = stock.recommendations
            return recs if recs is not None else pd.DataFrame()
        except:
            return pd.DataFrame()

    @staticmethod
    @st.cache_data(ttl=600)
    def get_institutional_holders(ticker: str) -> pd.DataFrame:
        """Fetch institutional holders"""
        try:
            stock = yf.Ticker(ticker)
            holders = stock.institutional_holders
            return holders if holders is not None else pd.DataFrame()
        except:
            return pd.DataFrame()

    @staticmethod
    @st.cache_data(ttl=600)
    def get_insider_transactions(ticker: str) -> pd.DataFrame:
        """Fetch insider transactions"""
        try:
            stock = yf.Ticker(ticker)
            insiders = stock.insider_transactions
            return insiders if insiders is not None else pd.DataFrame()
        except:
            return pd.DataFrame()

    @staticmethod
    @st.cache_data(ttl=300)
    def get_options_chain(ticker: str, expiry: str = None) -> dict:
        """Fetch options chain data"""
        try:
            stock = yf.Ticker(ticker)
            expirations = stock.options
            if not expirations:
                return {'expirations': [], 'calls': pd.DataFrame(), 'puts': pd.DataFrame()}

            exp = expiry if expiry and expiry in expirations else expirations[0]
            chain = stock.option_chain(exp)
            return {
                'expirations': list(expirations),
                'selected_expiry': exp,
                'calls': chain.calls,
                'puts': chain.puts
            }
        except:
            return {'expirations': [], 'calls': pd.DataFrame(), 'puts': pd.DataFrame()}

    @staticmethod
    @st.cache_data(ttl=300)
    def get_news(ticker: str) -> list:
        """Fetch and clean news data"""
        try:
            stock = yf.Ticker(ticker)
            raw_news = stock.news
            clean_news = []

            for item in raw_news:
                title = item.get('title', '').strip()
                link = item.get('link', '').strip()

                if not title or not link:
                    continue

                thumbnail = None
                if 'thumbnail' in item and 'resolutions' in item['thumbnail']:
                    resolutions = item['thumbnail']['resolutions']
                    if resolutions:
                        # Get highest resolution
                        thumbnail = resolutions[-1].get('url', resolutions[0].get('url', ''))

                published = item.get('providerPublishTime', 0)
                if published > 0:
                    clean_news.append({
                        'title': title,
                        'publisher': item.get('publisher', 'Unknown').strip() or 'Financial News',
                        'link': link,
                        'thumbnail': thumbnail,
                        'published': published,
                        'type': item.get('type', 'STORY'),
                        'related_tickers': item.get('relatedTickers', [])
                    })

            return clean_news
        except:
            return []

# ============================================================================
# CLASS: ForensicLab - Distortion Thesis Analysis
# ============================================================================
class ForensicLab:
    """Forensic analysis engine for finding hidden value through distortion detection"""

    @staticmethod
    def analyze_distortion(ticker: str, info: dict, financials: dict) -> dict:
        """
        Core Distortion Thesis Analysis:
        - Isolate one-time charges from operating income
        - Calculate normalized run rate
        - Compare GAAP P/E vs Real Forward P/E
        """
        result = {
            'has_distortion': False,
            'distortion_score': 0,
            'gaap_pe': None,
            'real_pe': None,
            'pe_gap': 0,
            'normalized_earnings': None,
            'reported_earnings': None,
            'adjustments': [],
            'signal': 'NEUTRAL',
            'signal_strength': 0
        }

        try:
            income_stmt = financials.get('income_stmt')
            if income_stmt is None or income_stmt.empty:
                return result

            # Get most recent quarter data
            mrq = income_stmt.iloc[:, 0] if len(income_stmt.columns) > 0 else None
            if mrq is None:
                return result

            # Extract key items (handle various naming conventions)
            operating_income = None
            for name in ['Operating Income', 'OperatingIncome', 'EBIT']:
                if name in mrq.index:
                    operating_income = mrq[name]
                    break

            # Look for unusual/restructuring items
            restructuring = 0
            unusual_items = 0

            restructuring_names = ['Restructuring And Mergern Acquisition', 'RestructuringCharges',
                                   'Restructuring', 'Merger And Acquisition Expense']
            unusual_names = ['Other Special Charges', 'OtherUnusualItems', 'Special Income Charges',
                           'Write Off', 'Impairment Of Capital Assets', 'Asset Impairment Charge']

            adjustments = []

            for name in restructuring_names:
                if name in mrq.index and pd.notna(mrq[name]):
                    val = abs(float(mrq[name]))
                    restructuring += val
                    adjustments.append(('Restructuring', val))

            for name in unusual_names:
                if name in mrq.index and pd.notna(mrq[name]):
                    val = abs(float(mrq[name]))
                    unusual_items += val
                    adjustments.append(('Unusual Items', val))

            if operating_income is None:
                return result

            operating_income = float(operating_income)

            # Calculate normalized operating income (add back one-time charges)
            normalized_op_income = operating_income + restructuring + unusual_items

            # Annualized run rate (quarterly * 4)
            normalized_annual = normalized_op_income * 4
            reported_annual = operating_income * 4

            # Get market cap and shares for P/E calculation
            market_cap = info.get('marketCap', 0)
            shares = info.get('sharesOutstanding', 1)
            current_price = info.get('currentPrice', 0)

            # Approximate net income from operating income (apply typical tax rate)
            tax_rate = 0.21  # Federal corporate tax
            normalized_net_income = normalized_annual * (1 - tax_rate)
            reported_net_income = reported_annual * (1 - tax_rate)

            # Calculate P/E ratios
            if normalized_net_income > 0 and market_cap > 0:
                result['real_pe'] = market_cap / normalized_net_income

            if reported_net_income > 0 and market_cap > 0:
                result['gaap_pe'] = market_cap / reported_net_income

            # Also use trailing P/E from info if available
            trailing_pe = info.get('trailingPE')
            if trailing_pe and trailing_pe > 0:
                result['gaap_pe'] = trailing_pe

            # Calculate distortion
            if result['gaap_pe'] and result['real_pe'] and result['real_pe'] > 0:
                pe_gap = ((result['gaap_pe'] - result['real_pe']) / result['real_pe']) * 100
                result['pe_gap'] = pe_gap

                # Significant distortion if Real P/E is 15%+ lower than GAAP P/E
                if pe_gap > 15:
                    result['has_distortion'] = True
                    result['signal'] = 'DISTORTED VALUE'
                    result['signal_strength'] = min(100, pe_gap * 2)
                    result['distortion_score'] = min(100, pe_gap * 1.5)
                elif pe_gap > 10:
                    result['signal'] = 'MODERATE DISTORTION'
                    result['signal_strength'] = pe_gap * 1.5
                    result['distortion_score'] = pe_gap

            result['normalized_earnings'] = normalized_net_income
            result['reported_earnings'] = reported_net_income
            result['adjustments'] = adjustments

        except Exception as e:
            result['error'] = str(e)

        return result

    @staticmethod
    def calculate_quality_of_earnings(ticker: str, financials: dict) -> dict:
        """Analyze earnings quality through cash flow comparison"""
        result = {
            'accrual_ratio': None,
            'cash_conversion': None,
            'quality_score': 50,
            'flags': []
        }

        try:
            income = financials.get('income_annual')
            cash_flow = financials.get('cash_flow_annual')

            if income is None or cash_flow is None or income.empty or cash_flow.empty:
                return result

            # Get net income and operating cash flow
            net_income = None
            op_cash_flow = None

            for name in ['Net Income', 'NetIncome', 'Net Income Common Stockholders']:
                if name in income.index:
                    net_income = income.loc[name].iloc[0]
                    break

            for name in ['Operating Cash Flow', 'Total Cash From Operating Activities', 'OperatingCashFlow']:
                if name in cash_flow.index:
                    op_cash_flow = cash_flow.loc[name].iloc[0]
                    break

            if net_income and op_cash_flow:
                # Cash conversion ratio (OCF / Net Income)
                if net_income > 0:
                    result['cash_conversion'] = (op_cash_flow / net_income) * 100

                    # Good quality: OCF >= Net Income
                    if result['cash_conversion'] >= 100:
                        result['quality_score'] = 80 + min(20, (result['cash_conversion'] - 100) / 2)
                    elif result['cash_conversion'] >= 80:
                        result['quality_score'] = 60 + (result['cash_conversion'] - 80)
                    else:
                        result['quality_score'] = max(0, result['cash_conversion'] * 0.75)
                        result['flags'].append('Low cash conversion - earnings quality concern')

            # Calculate accrual ratio
            balance = financials.get('balance_annual')
            if balance is not None and not balance.empty:
                total_assets = None
                for name in ['Total Assets', 'TotalAssets']:
                    if name in balance.index:
                        total_assets_series = balance.loc[name]
                        if len(total_assets_series) >= 2:
                            total_assets = (total_assets_series.iloc[0] + total_assets_series.iloc[1]) / 2
                        else:
                            total_assets = total_assets_series.iloc[0]
                        break

                if total_assets and total_assets > 0 and net_income and op_cash_flow:
                    accruals = net_income - op_cash_flow
                    result['accrual_ratio'] = (accruals / total_assets) * 100

                    # High accrual ratio is a red flag
                    if abs(result['accrual_ratio']) > 10:
                        result['flags'].append('High accrual ratio - potential earnings manipulation')
                        result['quality_score'] = max(0, result['quality_score'] - 20)

        except Exception as e:
            result['error'] = str(e)

        return result

# ============================================================================
# CLASS: RetailEdgeEngine - Retail investor advantage features
# ============================================================================
class RetailEdgeEngine:
    """Advanced features giving retail investors an edge"""

    @staticmethod
    def bagholder_detector(hist: pd.DataFrame) -> dict:
        """
        Volume Profile Analysis - Detect overhead supply zones
        Identifies price levels with heavy volume (potential resistance)
        """
        result = {
            'overhead_supply_zones': [],
            'support_zones': [],
            'current_risk': 'LOW',
            'risk_score': 0,
            'volume_profile': None
        }

        try:
            if hist.empty or len(hist) < 20:
                return result

            current_price = hist['Close'].iloc[-1]

            # Create volume profile (price-volume distribution)
            price_min = hist['Low'].min()
            price_max = hist['High'].max()
            n_bins = 20

            price_bins = np.linspace(price_min, price_max, n_bins + 1)
            volume_profile = []

            for i in range(n_bins):
                bin_low = price_bins[i]
                bin_high = price_bins[i + 1]
                bin_mid = (bin_low + bin_high) / 2

                # Volume in this price range
                mask = (hist['Close'] >= bin_low) & (hist['Close'] < bin_high)
                vol = hist.loc[mask, 'Volume'].sum()

                volume_profile.append({
                    'price_low': bin_low,
                    'price_high': bin_high,
                    'price_mid': bin_mid,
                    'volume': vol
                })

            result['volume_profile'] = volume_profile

            # Calculate average volume per bin
            total_vol = sum(v['volume'] for v in volume_profile)
            avg_vol = total_vol / n_bins if n_bins > 0 else 0

            # Identify high volume zones (overhead supply = resistance)
            for vp in volume_profile:
                if vp['volume'] > avg_vol * 1.5:  # 50% above average
                    zone = {
                        'price_low': vp['price_low'],
                        'price_high': vp['price_high'],
                        'volume': vp['volume'],
                        'strength': vp['volume'] / avg_vol if avg_vol > 0 else 0
                    }

                    if vp['price_mid'] > current_price:
                        result['overhead_supply_zones'].append(zone)
                    else:
                        result['support_zones'].append(zone)

            # Calculate risk based on proximity to overhead supply
            if result['overhead_supply_zones']:
                nearest_supply = min(z['price_low'] for z in result['overhead_supply_zones'])
                distance_pct = ((nearest_supply - current_price) / current_price) * 100

                if distance_pct < 3:
                    result['current_risk'] = 'CRITICAL'
                    result['risk_score'] = 90
                elif distance_pct < 5:
                    result['current_risk'] = 'HIGH'
                    result['risk_score'] = 70
                elif distance_pct < 10:
                    result['current_risk'] = 'MODERATE'
                    result['risk_score'] = 50
                else:
                    result['current_risk'] = 'LOW'
                    result['risk_score'] = 20

        except Exception as e:
            result['error'] = str(e)

        return result

    @staticmethod
    def whale_watcher(ticker: str, info: dict, inst_holders: pd.DataFrame, insider_tx: pd.DataFrame) -> dict:
        """
        Institutional and Insider Sentiment Analysis
        Tracks smart money movements
        """
        result = {
            'institutional_signal': 'NEUTRAL',
            'insider_signal': 'NEUTRAL',
            'combined_signal': 'NEUTRAL',
            'whale_score': 50,
            'recent_institutional_change': None,
            'recent_insider_buys': 0,
            'recent_insider_sells': 0,
            'notable_transactions': []
        }

        try:
            # Institutional ownership analysis
            inst_ownership = info.get('heldPercentInstitutions', 0)
            if inst_ownership:
                inst_pct = inst_ownership * 100
                if inst_pct > 70:
                    result['institutional_signal'] = 'HEAVY INSTITUTIONAL'
                elif inst_pct > 40:
                    result['institutional_signal'] = 'MODERATE INSTITUTIONAL'
                else:
                    result['institutional_signal'] = 'LOW INSTITUTIONAL'

            # Analyze insider transactions
            if not insider_tx.empty:
                # Filter recent transactions (last 90 days)
                insider_tx = insider_tx.copy()

                # Count buys vs sells
                buys = insider_tx[insider_tx['Text'].str.contains('Purchase|Buy|Acquisition', case=False, na=False)]
                sells = insider_tx[insider_tx['Text'].str.contains('Sale|Sell|Disposition', case=False, na=False)]

                result['recent_insider_buys'] = len(buys)
                result['recent_insider_sells'] = len(sells)

                # Calculate insider sentiment
                total_tx = len(buys) + len(sells)
                if total_tx > 0:
                    buy_ratio = len(buys) / total_tx
                    if buy_ratio > 0.7:
                        result['insider_signal'] = 'STRONG BUY'
                        result['whale_score'] = 80
                    elif buy_ratio > 0.5:
                        result['insider_signal'] = 'MODERATE BUY'
                        result['whale_score'] = 65
                    elif buy_ratio < 0.3:
                        result['insider_signal'] = 'HEAVY SELLING'
                        result['whale_score'] = 25
                    else:
                        result['insider_signal'] = 'MIXED'
                        result['whale_score'] = 50

                # Get notable transactions
                for _, tx in insider_tx.head(5).iterrows():
                    result['notable_transactions'].append({
                        'insider': tx.get('Insider', 'Unknown'),
                        'action': tx.get('Text', 'Unknown'),
                        'shares': tx.get('Shares', 0),
                        'value': tx.get('Value', 0)
                    })

            # Combined signal
            if result['insider_signal'] in ['STRONG BUY', 'MODERATE BUY'] and inst_ownership and inst_ownership > 0.5:
                result['combined_signal'] = 'WHALE ACCUMULATION'
            elif result['insider_signal'] == 'HEAVY SELLING':
                result['combined_signal'] = 'WHALE DISTRIBUTION'

        except Exception as e:
            result['error'] = str(e)

        return result

    @staticmethod
    def gamma_squeeze_radar(options_data: dict, current_price: float) -> dict:
        """
        Options Flow Analysis for Gamma Squeeze Potential
        Identifies strikes with unusual OI relative to volume
        """
        result = {
            'squeeze_potential': 'LOW',
            'squeeze_score': 0,
            'hot_strikes': [],
            'call_put_ratio': None,
            'max_pain': None,
            'gamma_exposure': []
        }

        try:
            calls = options_data.get('calls', pd.DataFrame())
            puts = options_data.get('puts', pd.DataFrame())

            if calls.empty and puts.empty:
                return result

            # Calculate call/put ratio based on open interest
            total_call_oi = calls['openInterest'].sum() if not calls.empty and 'openInterest' in calls.columns else 0
            total_put_oi = puts['openInterest'].sum() if not puts.empty and 'openInterest' in puts.columns else 0

            if total_put_oi > 0:
                result['call_put_ratio'] = total_call_oi / total_put_oi

            # Find strikes with high OI relative to volume (potential gamma walls)
            if not calls.empty and 'openInterest' in calls.columns and 'volume' in calls.columns:
                calls = calls.copy()
                calls['oi_vol_ratio'] = calls['openInterest'] / (calls['volume'].replace(0, 1))

                # Hot strikes: high OI, near the money
                near_money = calls[
                    (calls['strike'] >= current_price * 0.9) &
                    (calls['strike'] <= current_price * 1.15)
                ].copy()

                if not near_money.empty:
                    # Sort by open interest
                    hot = near_money.nlargest(5, 'openInterest')

                    for _, row in hot.iterrows():
                        result['hot_strikes'].append({
                            'strike': row['strike'],
                            'type': 'CALL',
                            'open_interest': row['openInterest'],
                            'volume': row.get('volume', 0),
                            'implied_vol': row.get('impliedVolatility', 0)
                        })

                    # Check for gamma squeeze setup
                    # High call OI concentrated near current price
                    concentrated_oi = near_money[
                        (near_money['strike'] >= current_price) &
                        (near_money['strike'] <= current_price * 1.1)
                    ]['openInterest'].sum()

                    oi_concentration = concentrated_oi / total_call_oi if total_call_oi > 0 else 0

                    if oi_concentration > 0.3 and result['call_put_ratio'] and result['call_put_ratio'] > 1.5:
                        result['squeeze_potential'] = 'HIGH'
                        result['squeeze_score'] = 80
                    elif oi_concentration > 0.2 or (result['call_put_ratio'] and result['call_put_ratio'] > 1.2):
                        result['squeeze_potential'] = 'MODERATE'
                        result['squeeze_score'] = 50
                    else:
                        result['squeeze_potential'] = 'LOW'
                        result['squeeze_score'] = 20

            # Calculate max pain (strike where most options expire worthless)
            if not calls.empty and not puts.empty:
                all_strikes = sorted(set(calls['strike'].tolist() + puts['strike'].tolist()))
                max_pain_strike = None
                min_total_value = float('inf')

                for strike in all_strikes:
                    # Calculate intrinsic value at this strike
                    call_value = calls[calls['strike'] < strike]['openInterest'].sum() * (strike - calls[calls['strike'] < strike]['strike'].mean()) if len(calls[calls['strike'] < strike]) > 0 else 0
                    put_value = puts[puts['strike'] > strike]['openInterest'].sum() * (puts[puts['strike'] > strike]['strike'].mean() - strike) if len(puts[puts['strike'] > strike]) > 0 else 0

                    total_value = call_value + put_value
                    if total_value < min_total_value:
                        min_total_value = total_value
                        max_pain_strike = strike

                result['max_pain'] = max_pain_strike

        except Exception as e:
            result['error'] = str(e)

        return result

    @staticmethod
    @st.cache_data(ttl=300)
    def reality_check(ticker: str, period: str = '1y') -> dict:
        """
        Correlation Analysis vs SPY and BTC
        Check for idiosyncratic alpha
        """
        result = {
            'spy_correlation': None,
            'btc_correlation': None,
            'alpha_potential': 'UNKNOWN',
            'beta': None,
            'idiosyncratic_score': 50
        }

        try:
            # Fetch data
            tickers = [ticker, 'SPY', 'BTC-USD']
            data = yf.download(tickers, period=period, progress=False)['Close']

            if data.empty or ticker not in data.columns:
                return result

            # Calculate returns
            returns = data.pct_change().dropna()

            if len(returns) < 20:
                return result

            # Correlations
            if 'SPY' in returns.columns:
                result['spy_correlation'] = returns[ticker].corr(returns['SPY'])

                # Calculate beta
                cov = returns[ticker].cov(returns['SPY'])
                var = returns['SPY'].var()
                result['beta'] = cov / var if var > 0 else 1

            if 'BTC-USD' in returns.columns:
                result['btc_correlation'] = returns[ticker].corr(returns['BTC-USD'])

            # Idiosyncratic alpha assessment
            spy_corr = abs(result['spy_correlation']) if result['spy_correlation'] else 1
            btc_corr = abs(result['btc_correlation']) if result['btc_correlation'] else 0

            # Lower correlation = more idiosyncratic
            avg_corr = (spy_corr + btc_corr) / 2
            result['idiosyncratic_score'] = (1 - avg_corr) * 100

            if result['idiosyncratic_score'] > 70:
                result['alpha_potential'] = 'HIGH'
            elif result['idiosyncratic_score'] > 40:
                result['alpha_potential'] = 'MODERATE'
            else:
                result['alpha_potential'] = 'LOW (MARKET FOLLOWER)'

        except Exception as e:
            result['error'] = str(e)

        return result

# ============================================================================
# CLASS: PortfolioManager - Portfolio tracking and analysis
# ============================================================================
class PortfolioManager:
    """Portfolio management and truth tracking"""

    @staticmethod
    def analyze_portfolio(holdings: list) -> dict:
        """
        Analyze entire portfolio with forensic analysis on each position
        holdings: list of {'ticker': str, 'shares': float, 'cost': float}
        """
        result = {
            'positions': [],
            'total_value': 0,
            'total_cost': 0,
            'total_pnl': 0,
            'total_pnl_pct': 0,
            'portfolio_distortion_score': 0,
            'distorted_positions': 0,
            'real_vs_fake_growth': 'UNKNOWN'
        }

        distortion_scores = []

        for holding in holdings:
            ticker = holding.get('ticker', '').upper()
            shares = holding.get('shares', 0)
            cost = holding.get('cost', 0)

            if not ticker or shares <= 0:
                continue

            position = {
                'ticker': ticker,
                'shares': shares,
                'cost_basis': cost,
                'current_price': 0,
                'current_value': 0,
                'pnl': 0,
                'pnl_pct': 0,
                'distortion_analysis': None,
                'smart_score': None
            }

            try:
                info = DataEngine.get_info(ticker)
                financials = DataEngine.get_financials(ticker)

                if info:
                    current_price = info.get('currentPrice', info.get('regularMarketPrice', 0))
                    position['current_price'] = current_price
                    position['current_value'] = current_price * shares
                    position['cost_basis_total'] = cost * shares
                    position['pnl'] = position['current_value'] - position['cost_basis_total']
                    position['pnl_pct'] = (position['pnl'] / position['cost_basis_total'] * 100) if position['cost_basis_total'] > 0 else 0

                    result['total_value'] += position['current_value']
                    result['total_cost'] += position['cost_basis_total']

                    # Run forensic analysis
                    if financials:
                        distortion = ForensicLab.analyze_distortion(ticker, info, financials)
                        position['distortion_analysis'] = distortion

                        if distortion.get('distortion_score', 0) > 0:
                            distortion_scores.append(distortion['distortion_score'])

                        if distortion.get('has_distortion'):
                            result['distorted_positions'] += 1

            except Exception as e:
                position['error'] = str(e)

            result['positions'].append(position)

        # Calculate totals
        result['total_pnl'] = result['total_value'] - result['total_cost']
        result['total_pnl_pct'] = (result['total_pnl'] / result['total_cost'] * 100) if result['total_cost'] > 0 else 0

        # Portfolio-level distortion score
        if distortion_scores:
            result['portfolio_distortion_score'] = np.mean(distortion_scores)

        # Determine real vs fake growth
        if result['distorted_positions'] > len(holdings) * 0.5:
            result['real_vs_fake_growth'] = 'MOSTLY DISTORTED VALUE'
        elif result['distorted_positions'] > 0:
            result['real_vs_fake_growth'] = 'MIXED'
        else:
            result['real_vs_fake_growth'] = 'FUNDAMENTAL GROWTH'

        return result

# ============================================================================
# HELPER FUNCTIONS - Technical Analysis & Scoring
# ============================================================================

def calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
    """Calculate RSI indicator"""
    delta = prices.diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))


def calculate_macd(prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> dict:
    """Calculate MACD indicator"""
    ema_fast = prices.ewm(span=fast, adjust=False).mean()
    ema_slow = prices.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return {'macd': macd_line, 'signal': signal_line, 'histogram': histogram}


def calculate_bollinger_bands(prices: pd.Series, period: int = 20, std_dev: float = 2.0) -> dict:
    """Calculate Bollinger Bands"""
    sma = prices.rolling(window=period).mean()
    std = prices.rolling(window=period).std()
    upper = sma + (std * std_dev)
    lower = sma - (std * std_dev)
    return {'middle': sma, 'upper': upper, 'lower': lower}


def calculate_atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    """Calculate Average True Range"""
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return tr.rolling(window=period).mean()


def get_fundamental_metrics(info: dict) -> dict:
    """Extract fundamental metrics from stock info"""
    return {
        'revenue_growth': (info.get('revenueGrowth', 0) or 0) * 100,
        'earnings_growth': (info.get('earningsGrowth', 0) or 0) * 100,
        'profit_margin': (info.get('profitMargins', 0) or 0) * 100,
        'operating_margin': (info.get('operatingMargins', 0) or 0) * 100,
        'gross_margin': (info.get('grossMargins', 0) or 0) * 100,
        'roe': (info.get('returnOnEquity', 0) or 0) * 100,
        'roa': (info.get('returnOnAssets', 0) or 0) * 100,
        'debt_to_equity': (info.get('debtToEquity', 0) or 0) / 100,
        'current_ratio': info.get('currentRatio', 0) or 0,
        'quick_ratio': info.get('quickRatio', 0) or 0,
        'free_cash_flow': info.get('freeCashflow', 0) or 0,
        'operating_cash_flow': info.get('operatingCashflow', 0) or 0,
        'revenue': info.get('totalRevenue', 0) or 0,
        'ebitda': info.get('ebitda', 0) or 0,
        'market_cap': info.get('marketCap', 0) or 0,
        'pe_ratio': info.get('trailingPE', 0) or 0,
        'forward_pe': info.get('forwardPE', 0) or 0,
        'peg_ratio': info.get('pegRatio', 0) or 0,
        'price_to_book': info.get('priceToBook', 0) or 0,
        'price_to_sales': info.get('priceToSalesTrailing12Months', 0) or 0,
        'dividend_yield': (info.get('dividendYield', 0) or 0) * 100,
        'beta': info.get('beta', 1) or 1,
        'short_percent': (info.get('shortPercentOfFloat', 0) or 0) * 100,
        '52w_high': info.get('fiftyTwoWeekHigh', 0) or 0,
        '52w_low': info.get('fiftyTwoWeekLow', 0) or 0,
    }


def calculate_smart_score(info: dict, hist: pd.DataFrame, fundamentals: dict, weights: dict) -> tuple:
    """
    Calculate comprehensive investment score using professional-grade metrics.
    Each category scored 0-100, then weighted for final score.
    More realistic scoring with proper benchmarks and nuanced analysis.
    """
    scores = {}
    metrics = {}
    details = {}  # Store detailed breakdown

    # =========================================================================
    # VALUATION SCORE (0-100)
    # Benchmark: S&P 500 averages - P/E ~20-22, P/B ~4, EV/EBITDA ~14
    # =========================================================================
    val_score = 50  # Start neutral

    # P/E Analysis (weight: 25 points)
    pe = info.get('trailingPE') or info.get('forwardPE')
    forward_pe = info.get('forwardPE')
    metrics['pe'] = pe
    metrics['forward_pe'] = forward_pe

    if pe and pe > 0:
        if pe < 10: val_score += 20  # Deep value
        elif pe < 15: val_score += 15  # Value
        elif pe < 20: val_score += 10  # Fair
        elif pe < 25: val_score += 5   # Slightly expensive
        elif pe < 35: val_score -= 5   # Expensive
        elif pe < 50: val_score -= 10  # Very expensive
        else: val_score -= 15          # Extremely expensive

        # Forward P/E improvement bonus
        if forward_pe and pe and forward_pe < pe * 0.85:
            val_score += 8  # Earnings expected to grow significantly

    # PEG Ratio (weight: 20 points) - Gold standard for GARP
    peg = info.get('pegRatio')
    metrics['peg'] = peg
    if peg and peg > 0:
        if peg < 0.75: val_score += 15    # Undervalued growth
        elif peg < 1.0: val_score += 10   # Fair growth value
        elif peg < 1.5: val_score += 5    # Acceptable
        elif peg < 2.0: val_score += 0    # Fairly priced
        elif peg < 3.0: val_score -= 5    # Expensive for growth
        else: val_score -= 10             # Very expensive

    # FCF Yield (weight: 20 points) - Real cash generation
    mkt_cap = info.get('marketCap', 1) or 1
    fcf = info.get('freeCashflow', 0) or 0
    fcf_yield = (fcf / mkt_cap) * 100 if mkt_cap > 0 else 0
    metrics['fcf_yield'] = fcf_yield

    if fcf_yield > 10: val_score += 15    # Exceptional
    elif fcf_yield > 7: val_score += 12   # Excellent
    elif fcf_yield > 5: val_score += 8    # Good
    elif fcf_yield > 3: val_score += 4    # Acceptable
    elif fcf_yield > 0: val_score += 0    # Neutral
    else: val_score -= 10                  # Negative FCF concerning

    # EV/EBITDA (weight: 15 points)
    ev_ebitda = info.get('enterpriseToEbitda')
    if ev_ebitda and ev_ebitda > 0:
        if ev_ebitda < 8: val_score += 10
        elif ev_ebitda < 12: val_score += 6
        elif ev_ebitda < 16: val_score += 2
        elif ev_ebitda < 20: val_score -= 3
        else: val_score -= 8

    scores['valuation'] = max(0, min(100, val_score))

    # =========================================================================
    # QUALITY SCORE (0-100)
    # Measures business quality, competitive moat, financial strength
    # =========================================================================
    qual_score = 50

    # Profitability (weight: 35 points)
    profit_margin = fundamentals.get('profit_margin', 0)
    gross_margin = fundamentals.get('gross_margin', 0)
    operating_margin = fundamentals.get('operating_margin', 0)

    # Net profit margin
    if profit_margin > 30: qual_score += 15
    elif profit_margin > 20: qual_score += 10
    elif profit_margin > 10: qual_score += 5
    elif profit_margin > 5: qual_score += 2
    elif profit_margin < 0: qual_score -= 10

    # Gross margin (indicator of pricing power)
    if gross_margin > 60: qual_score += 10
    elif gross_margin > 40: qual_score += 6
    elif gross_margin > 25: qual_score += 2
    elif gross_margin < 15: qual_score -= 5

    # Return Metrics (weight: 30 points)
    roe = fundamentals.get('roe', 0)
    roa = fundamentals.get('roa', 0)

    if roe > 25: qual_score += 12
    elif roe > 18: qual_score += 8
    elif roe > 12: qual_score += 4
    elif roe > 8: qual_score += 1
    elif roe < 0: qual_score -= 8

    if roa > 15: qual_score += 8
    elif roa > 10: qual_score += 5
    elif roa > 5: qual_score += 2
    elif roa < 0: qual_score -= 5

    # Financial Strength (weight: 25 points)
    current_ratio = fundamentals.get('current_ratio', 0)
    debt_to_equity = fundamentals.get('debt_to_equity', 0)

    if current_ratio > 2.5: qual_score += 8
    elif current_ratio > 1.5: qual_score += 5
    elif current_ratio > 1.0: qual_score += 2
    elif current_ratio < 0.8: qual_score -= 8

    if debt_to_equity < 0.3: qual_score += 10
    elif debt_to_equity < 0.6: qual_score += 6
    elif debt_to_equity < 1.0: qual_score += 2
    elif debt_to_equity < 1.5: qual_score -= 3
    elif debt_to_equity < 2.5: qual_score -= 8
    else: qual_score -= 12

    scores['quality'] = max(0, min(100, qual_score))

    # =========================================================================
    # GROWTH SCORE (0-100)
    # Evaluates growth trajectory and sustainability
    # =========================================================================
    growth_score = 50

    # Revenue Growth (weight: 35 points)
    rev_growth = fundamentals.get('revenue_growth', 0)
    metrics['rev_growth'] = rev_growth

    if rev_growth > 50: growth_score += 18
    elif rev_growth > 30: growth_score += 14
    elif rev_growth > 20: growth_score += 10
    elif rev_growth > 10: growth_score += 6
    elif rev_growth > 5: growth_score += 2
    elif rev_growth > 0: growth_score += 0
    elif rev_growth > -5: growth_score -= 5
    else: growth_score -= 12

    # Earnings Growth (weight: 35 points)
    earnings_growth = fundamentals.get('earnings_growth', 0)
    metrics['earnings_growth'] = earnings_growth

    if earnings_growth > 50: growth_score += 18
    elif earnings_growth > 30: growth_score += 14
    elif earnings_growth > 20: growth_score += 10
    elif earnings_growth > 10: growth_score += 6
    elif earnings_growth > 0: growth_score += 2
    elif earnings_growth > -10: growth_score -= 5
    else: growth_score -= 12

    # Growth Consistency Bonus (weight: 15 points)
    if rev_growth > 10 and earnings_growth > 10:
        growth_score += 8  # Both growing nicely
    if rev_growth > 0 and earnings_growth > rev_growth:
        growth_score += 5  # Margin expansion

    # Penalize if growth is slowing significantly
    if rev_growth > 0 and earnings_growth < rev_growth * 0.5:
        growth_score -= 5  # Margin compression

    scores['growth'] = max(0, min(100, growth_score))

    # =========================================================================
    # MOMENTUM SCORE (0-100)
    # Technical strength and trend analysis
    # =========================================================================
    mom_score = 50

    if len(hist) > 0:
        current_price = hist['Close'].iloc[-1]

        # RSI Analysis (weight: 25 points)
        rsi_val = 50
        if len(hist) > 14:
            rsi_series = calculate_rsi(hist['Close'])
            rsi_val = rsi_series.iloc[-1] if not pd.isna(rsi_series.iloc[-1]) else 50
        metrics['rsi'] = rsi_val

        # Optimal RSI zone
        if 45 <= rsi_val <= 55: mom_score += 10    # Balanced
        elif 40 <= rsi_val <= 60: mom_score += 8   # Healthy
        elif 55 < rsi_val <= 65: mom_score += 5    # Bullish but not overheated
        elif 35 <= rsi_val < 40: mom_score += 6    # Potential reversal up
        elif rsi_val > 75: mom_score -= 8          # Overbought risk
        elif rsi_val < 25: mom_score -= 5          # Oversold (could be opportunity or trouble)

        # Moving Average Analysis (weight: 35 points)
        if len(hist) >= 50:
            ma50 = hist['Close'].rolling(50).mean().iloc[-1]
            metrics['ma50'] = ma50
            pct_from_ma50 = ((current_price - ma50) / ma50) * 100

            if current_price > ma50:
                if pct_from_ma50 < 5: mom_score += 10    # Just above - healthy
                elif pct_from_ma50 < 10: mom_score += 8  # Trending up
                elif pct_from_ma50 < 20: mom_score += 4  # Extended
                else: mom_score -= 2                      # Very extended
            else:
                if pct_from_ma50 > -5: mom_score += 2    # Just below
                elif pct_from_ma50 > -10: mom_score -= 3
                else: mom_score -= 8                      # Significantly below

        if len(hist) >= 200:
            ma200 = hist['Close'].rolling(200).mean().iloc[-1]
            ma50 = hist['Close'].rolling(50).mean().iloc[-1]
            metrics['ma200'] = ma200

            if ma50 > ma200: mom_score += 10   # Bullish trend (golden cross territory)
            else: mom_score -= 5               # Bearish trend

            if current_price > ma200: mom_score += 5
            else: mom_score -= 5

        # Price Performance (weight: 20 points)
        if len(hist) >= 63:  # ~3 months
            price_3m_ago = hist['Close'].iloc[-63]
            return_3m = ((current_price - price_3m_ago) / price_3m_ago) * 100
            metrics['return_3m'] = return_3m

            if return_3m > 20: mom_score += 8
            elif return_3m > 10: mom_score += 5
            elif return_3m > 0: mom_score += 2
            elif return_3m > -10: mom_score -= 3
            else: mom_score -= 8

        # 52-week position (weight: 15 points)
        high_52w = info.get('fiftyTwoWeekHigh', current_price)
        low_52w = info.get('fiftyTwoWeekLow', current_price)
        if high_52w > low_52w:
            range_position = (current_price - low_52w) / (high_52w - low_52w)
            metrics['52w_position'] = range_position * 100

            if 0.7 <= range_position <= 0.9: mom_score += 8    # Near highs but not at peak
            elif 0.5 <= range_position < 0.7: mom_score += 5   # Middle of range
            elif 0.3 <= range_position < 0.5: mom_score += 2   # Lower half
            elif range_position < 0.2: mom_score -= 5          # Near lows
            elif range_position > 0.95: mom_score -= 2         # At highs (risky)

    scores['momentum'] = max(0, min(100, mom_score))

    # =========================================================================
    # RISK SCORE (0-100) - Higher = LESS risky
    # =========================================================================
    risk_score = 70  # Start optimistic

    # Short Interest Risk (weight: 20 points)
    short_float = info.get('shortPercentOfFloat', 0) or 0
    metrics['short_float'] = short_float * 100

    if short_float > 0.30: risk_score -= 20      # Very high short interest
    elif short_float > 0.20: risk_score -= 15
    elif short_float > 0.10: risk_score -= 8
    elif short_float > 0.05: risk_score -= 3
    elif short_float < 0.02: risk_score += 5     # Low short interest is good

    # Beta / Volatility Risk (weight: 25 points)
    beta = info.get('beta', 1.0) or 1.0
    metrics['beta'] = beta

    if beta > 2.5: risk_score -= 20
    elif beta > 2.0: risk_score -= 15
    elif beta > 1.5: risk_score -= 8
    elif beta > 1.2: risk_score -= 3
    elif 0.8 <= beta <= 1.2: risk_score += 5    # Market-like volatility
    elif 0.5 <= beta < 0.8: risk_score += 3     # Lower volatility
    elif beta < 0.5: risk_score += 0            # Very low (might be stagnant)

    # Financial Risk (weight: 25 points)
    if debt_to_equity > 3: risk_score -= 15
    elif debt_to_equity > 2: risk_score -= 10
    elif debt_to_equity > 1.5: risk_score -= 5
    elif debt_to_equity < 0.5: risk_score += 8

    if current_ratio < 0.5: risk_score -= 12
    elif current_ratio < 1.0: risk_score -= 5
    elif current_ratio > 2.0: risk_score += 5

    # Profitability Risk (weight: 15 points)
    if profit_margin < 0: risk_score -= 15        # Unprofitable
    elif profit_margin < 5: risk_score -= 5
    elif profit_margin > 15: risk_score += 5

    # FCF Risk (weight: 15 points)
    if fcf < 0: risk_score -= 10
    elif fcf_yield > 5: risk_score += 5

    scores['risk'] = max(0, min(100, risk_score))

    # =========================================================================
    # CALCULATE WEIGHTED TOTAL SCORE
    # =========================================================================
    total_score = (
        scores['valuation'] * weights.get('valuation', 0.20) +
        scores['quality'] * weights.get('quality', 0.25) +
        scores['growth'] * weights.get('growth', 0.20) +
        scores['momentum'] * weights.get('momentum', 0.15) +
        scores['risk'] * weights.get('risk', 0.20)
    )

    return scores, total_score, metrics


def get_rating(score: float) -> tuple:
    """Convert score to rating and color - more nuanced ratings"""
    if score >= 80: return "STRONG BUY", '#22c55e'
    elif score >= 68: return "BUY", '#3b82f6'
    elif score >= 55: return "ACCUMULATE", '#06b6d4'
    elif score >= 45: return "HOLD", '#eab308'
    elif score >= 35: return "REDUCE", '#f97316'
    else: return "SELL", '#ef4444'


def format_large_number(num: float) -> str:
    """Format large numbers with K, M, B suffixes"""
    if num is None or pd.isna(num): return "N/A"
    if abs(num) >= 1e12: return f"${num/1e12:.2f}T"
    elif abs(num) >= 1e9: return f"${num/1e9:.2f}B"
    elif abs(num) >= 1e6: return f"${num/1e6:.2f}M"
    elif abs(num) >= 1e3: return f"${num/1e3:.2f}K"
    else: return f"${num:.2f}"


def time_ago(timestamp: int) -> str:
    """Convert timestamp to human-readable time ago"""
    now = datetime.now()
    dt = datetime.fromtimestamp(timestamp)
    diff = now - dt
    if diff.days > 0: return f"{diff.days}d ago"
    elif diff.seconds > 3600: return f"{diff.seconds // 3600}h ago"
    elif diff.seconds > 60: return f"{diff.seconds // 60}m ago"
    else: return "Just now"


def estimate_news_sentiment(title: str) -> str:
    """Simple sentiment estimation from news title"""
    title_lower = title.lower()
    bullish_words = ['surge', 'soar', 'jump', 'rally', 'gain', 'rise', 'beat', 'growth', 'profit', 'upgrade', 'buy', 'record', 'strong']
    bearish_words = ['fall', 'drop', 'plunge', 'crash', 'decline', 'loss', 'miss', 'weak', 'downgrade', 'sell', 'warning', 'concern']
    bullish_count = sum(1 for w in bullish_words if w in title_lower)
    bearish_count = sum(1 for w in bearish_words if w in title_lower)
    if bullish_count > bearish_count: return 'bullish'
    elif bearish_count > bullish_count: return 'bearish'
    return 'neutral'


def calculate_fear_greed() -> dict:
    """
    Comprehensive Fear & Greed Index using 10 market indicators.
    Each indicator scored 0-100, then averaged for final score.

    Indicators:
    1. VIX Level - Market volatility
    2. VIX Trend - 14-day VIX change
    3. Market Momentum - S&P 500 vs 125-day MA
    4. Stock Price Strength - Distance from 52-week high
    5. Market Breadth - Advance/Decline via RSP vs SPY
    6. Put/Call Proxy - VIX term structure
    7. Junk Bond Demand - HYG performance
    8. Safe Haven Demand - TLT vs SPY ratio
    9. Sector Rotation - XLY (cyclical) vs XLP (defensive)
    10. Credit Stress - HYG vs LQD spread
    """
    indicators = {}
    scores = []

    try:
        # Fetch all data upfront
        tickers_needed = ['^VIX', 'SPY', 'RSP', 'HYG', 'LQD', 'TLT', 'XLY', 'XLP', '^VIX3M']
        data = {}

        for t in tickers_needed:
            try:
                hist = yf.Ticker(t).history(period="6mo")
                if len(hist) > 0:
                    data[t] = hist['Close']
            except:
                pass

        vix_current = data.get('^VIX', pd.Series([20])).iloc[-1]
        indicators['vix'] = vix_current

        # =====================================================================
        # 1. VIX LEVEL (0-100, higher score = more greed/less fear)
        # =====================================================================
        vix_score = 50
        if vix_current < 12: vix_score = 95       # Extreme complacency
        elif vix_current < 15: vix_score = 80     # Low fear
        elif vix_current < 18: vix_score = 65     # Comfortable
        elif vix_current < 22: vix_score = 50     # Neutral
        elif vix_current < 28: vix_score = 35     # Elevated fear
        elif vix_current < 35: vix_score = 20     # High fear
        else: vix_score = 5                        # Extreme fear

        indicators['vix_level'] = {'value': vix_current, 'score': vix_score, 'label': 'VIX Level'}
        scores.append(vix_score)

        # =====================================================================
        # 2. VIX TREND (14-day change)
        # =====================================================================
        if '^VIX' in data and len(data['^VIX']) >= 14:
            vix_14d_ago = data['^VIX'].iloc[-14]
            vix_change = ((vix_current - vix_14d_ago) / vix_14d_ago) * 100

            if vix_change < -20: vix_trend_score = 90      # VIX dropping fast = greed
            elif vix_change < -10: vix_trend_score = 75
            elif vix_change < -5: vix_trend_score = 60
            elif vix_change < 5: vix_trend_score = 50      # Stable
            elif vix_change < 15: vix_trend_score = 35
            elif vix_change < 30: vix_trend_score = 20
            else: vix_trend_score = 5                       # VIX spiking = fear

            indicators['vix_trend'] = {'value': vix_change, 'score': vix_trend_score, 'label': 'VIX 14D Change'}
            scores.append(vix_trend_score)

        # =====================================================================
        # 3. MARKET MOMENTUM (SPY vs 125-day MA)
        # =====================================================================
        if 'SPY' in data and len(data['SPY']) >= 125:
            spy = data['SPY']
            spy_ma125 = spy.rolling(125).mean().iloc[-1]
            spy_current = spy.iloc[-1]
            mom_pct = ((spy_current - spy_ma125) / spy_ma125) * 100

            if mom_pct > 10: mom_score = 95
            elif mom_pct > 6: mom_score = 80
            elif mom_pct > 3: mom_score = 65
            elif mom_pct > 0: mom_score = 55
            elif mom_pct > -3: mom_score = 40
            elif mom_pct > -6: mom_score = 25
            else: mom_score = 10

            indicators['momentum'] = {'value': mom_pct, 'score': mom_score, 'label': 'Market Momentum'}
            scores.append(mom_score)

        # =====================================================================
        # 4. STOCK PRICE STRENGTH (SPY distance from 52-week high)
        # =====================================================================
        if 'SPY' in data and len(data['SPY']) >= 252:
            spy = data['SPY']
            high_52w = spy.tail(252).max()
            current = spy.iloc[-1]
            pct_from_high = ((current - high_52w) / high_52w) * 100

            if pct_from_high > -2: strength_score = 90     # Near highs
            elif pct_from_high > -5: strength_score = 75
            elif pct_from_high > -10: strength_score = 55
            elif pct_from_high > -15: strength_score = 40
            elif pct_from_high > -20: strength_score = 25
            else: strength_score = 10                       # Bear market territory

            indicators['price_strength'] = {'value': pct_from_high, 'score': strength_score, 'label': '52W High Distance'}
            scores.append(strength_score)

        # =====================================================================
        # 5. MARKET BREADTH (RSP equal weight vs SPY cap weight)
        # =====================================================================
        if 'RSP' in data and 'SPY' in data and len(data['RSP']) >= 20:
            rsp_ret = (data['RSP'].iloc[-1] / data['RSP'].iloc[-20] - 1) * 100
            spy_ret = (data['SPY'].iloc[-1] / data['SPY'].iloc[-20] - 1) * 100
            breadth_diff = rsp_ret - spy_ret  # Positive = broad participation

            if breadth_diff > 3: breadth_score = 85        # Broad rally
            elif breadth_diff > 1: breadth_score = 70
            elif breadth_diff > -1: breadth_score = 50     # Neutral
            elif breadth_diff > -3: breadth_score = 35
            else: breadth_score = 20                        # Narrow/concentrated

            indicators['breadth'] = {'value': breadth_diff, 'score': breadth_score, 'label': 'Market Breadth'}
            scores.append(breadth_score)

        # =====================================================================
        # 6. PUT/CALL PROXY - VIX Term Structure (VIX vs VIX3M)
        # =====================================================================
        if '^VIX' in data and '^VIX3M' in data:
            vix3m = data['^VIX3M'].iloc[-1]
            term_structure = (vix_current / vix3m - 1) * 100  # Negative = contango (normal)

            if term_structure < -15: pc_score = 85         # Deep contango = complacent
            elif term_structure < -8: pc_score = 70
            elif term_structure < -2: pc_score = 55
            elif term_structure < 5: pc_score = 40
            elif term_structure < 15: pc_score = 25        # Backwardation = fear
            else: pc_score = 10                             # Extreme backwardation

            indicators['put_call'] = {'value': term_structure, 'score': pc_score, 'label': 'VIX Term Structure'}
            scores.append(pc_score)

        # =====================================================================
        # 7. JUNK BOND DEMAND (HYG 20-day performance)
        # =====================================================================
        if 'HYG' in data and len(data['HYG']) >= 20:
            hyg_ret = (data['HYG'].iloc[-1] / data['HYG'].iloc[-20] - 1) * 100

            if hyg_ret > 2: junk_score = 85                # Risk-on
            elif hyg_ret > 1: junk_score = 70
            elif hyg_ret > 0: junk_score = 55
            elif hyg_ret > -1: junk_score = 40
            elif hyg_ret > -2: junk_score = 25
            else: junk_score = 10                           # Risk-off

            indicators['junk_bond'] = {'value': hyg_ret, 'score': junk_score, 'label': 'Junk Bond Demand'}
            scores.append(junk_score)

        # =====================================================================
        # 8. SAFE HAVEN DEMAND (TLT vs SPY 20-day relative performance)
        # =====================================================================
        if 'TLT' in data and 'SPY' in data and len(data['TLT']) >= 20:
            tlt_ret = (data['TLT'].iloc[-1] / data['TLT'].iloc[-20] - 1) * 100
            spy_ret = (data['SPY'].iloc[-1] / data['SPY'].iloc[-20] - 1) * 100
            safe_haven_diff = tlt_ret - spy_ret  # Positive = flight to safety

            if safe_haven_diff < -5: sh_score = 85         # Equities crushing bonds = greed
            elif safe_haven_diff < -2: sh_score = 70
            elif safe_haven_diff < 1: sh_score = 55
            elif safe_haven_diff < 3: sh_score = 40
            elif safe_haven_diff < 6: sh_score = 25
            else: sh_score = 10                             # Flight to safety = fear

            indicators['safe_haven'] = {'value': safe_haven_diff, 'score': sh_score, 'label': 'Safe Haven Demand'}
            scores.append(sh_score)

        # =====================================================================
        # 9. SECTOR ROTATION (XLY cyclical vs XLP defensive)
        # =====================================================================
        if 'XLY' in data and 'XLP' in data and len(data['XLY']) >= 20:
            xly_ret = (data['XLY'].iloc[-1] / data['XLY'].iloc[-20] - 1) * 100
            xlp_ret = (data['XLP'].iloc[-1] / data['XLP'].iloc[-20] - 1) * 100
            rotation_diff = xly_ret - xlp_ret  # Positive = risk-on rotation

            if rotation_diff > 5: rotation_score = 90      # Strong risk-on
            elif rotation_diff > 2: rotation_score = 75
            elif rotation_diff > 0: rotation_score = 55
            elif rotation_diff > -2: rotation_score = 40
            elif rotation_diff > -5: rotation_score = 25
            else: rotation_score = 10                       # Defensive rotation

            indicators['rotation'] = {'value': rotation_diff, 'score': rotation_score, 'label': 'Sector Rotation'}
            scores.append(rotation_score)

        # =====================================================================
        # 10. CREDIT STRESS (HYG vs LQD spread proxy)
        # =====================================================================
        if 'HYG' in data and 'LQD' in data and len(data['HYG']) >= 20:
            hyg_ret = (data['HYG'].iloc[-1] / data['HYG'].iloc[-20] - 1) * 100
            lqd_ret = (data['LQD'].iloc[-1] / data['LQD'].iloc[-20] - 1) * 100
            credit_diff = hyg_ret - lqd_ret  # Positive = credit tightening (good)

            if credit_diff > 1.5: credit_score = 85
            elif credit_diff > 0.5: credit_score = 70
            elif credit_diff > -0.5: credit_score = 50
            elif credit_diff > -1.5: credit_score = 35
            else: credit_score = 15                         # Credit widening = stress

            indicators['credit'] = {'value': credit_diff, 'score': credit_score, 'label': 'Credit Spreads'}
            scores.append(credit_score)

        # =====================================================================
        # FINAL SCORE CALCULATION
        # =====================================================================
        if scores:
            final_score = sum(scores) / len(scores)
        else:
            final_score = 50

        final_score = max(0, min(100, final_score))

        # Determine label
        if final_score >= 80: label = "Extreme Greed"
        elif final_score >= 65: label = "Greed"
        elif final_score >= 55: label = "Mild Greed"
        elif final_score >= 45: label = "Neutral"
        elif final_score >= 35: label = "Mild Fear"
        elif final_score >= 20: label = "Fear"
        else: label = "Extreme Fear"

        return {
            'score': final_score,
            'label': label,
            'vix': vix_current,
            'indicators': indicators,
            'num_indicators': len(scores)
        }

    except Exception as e:
        return {
            'score': 50,
            'label': "Neutral",
            'vix': 20,
            'indicators': {},
            'num_indicators': 0,
            'error': str(e)
        }


def generate_dcf_excel(ticker: str, info: dict, fundamentals: dict, dcf_params: dict) -> BytesIO:
    """Generate DCF model Excel file"""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        overview = {'Metric': ['Company', 'Ticker', 'Sector', 'Market Cap', 'Price', 'Date'],
                    'Value': [info.get('longName', ticker), ticker, info.get('sector', 'N/A'),
                             format_large_number(info.get('marketCap', 0)), f"${info.get('currentPrice', 0):.2f}",
                             datetime.now().strftime('%Y-%m-%d')]}
        pd.DataFrame(overview).to_excel(writer, sheet_name='Overview', index=False)

        current_revenue = info.get('totalRevenue', 1e9)
        years = list(range(1, 11))
        projected_revenue = [current_revenue * ((1 + dcf_params['revenue_growth']) ** y) if y <= 5
                            else current_revenue * ((1 + dcf_params['revenue_growth']) ** 5) * ((1 + dcf_params['terminal_growth']) ** (y-5))
                            for y in years]
        fcf_margin = max((fundamentals['profit_margin'] / 100) * 0.8, 0.05)
        projected_fcf = [rev * fcf_margin for rev in projected_revenue]
        pv_fcf = [fcf / ((1 + dcf_params['wacc']) ** y) for y, fcf in zip(years, projected_fcf)]

        projections = pd.DataFrame({'Year': years, 'Revenue': projected_revenue, 'FCF': projected_fcf, 'PV of FCF': pv_fcf})
        projections.to_excel(writer, sheet_name='Projections', index=False)

        terminal_fcf = projected_fcf[-1] * (1 + dcf_params['terminal_growth'])
        terminal_value = terminal_fcf / (dcf_params['wacc'] - dcf_params['terminal_growth'])
        pv_terminal = terminal_value / ((1 + dcf_params['wacc']) ** 10)
        enterprise_value = sum(pv_fcf) + pv_terminal
        net_debt = info.get('totalDebt', 0) - info.get('totalCash', 0)
        equity_value = enterprise_value - net_debt
        shares = info.get('sharesOutstanding', 1e9)
        fair_value = equity_value / shares if shares > 0 else 0

        valuation = {'Item': ['Enterprise Value', 'Equity Value', 'Fair Value', 'Current Price'],
                     'Value': [format_large_number(enterprise_value), format_large_number(equity_value),
                              f"${fair_value:.2f}", f"${info.get('currentPrice', 0):.2f}"]}
        pd.DataFrame(valuation).to_excel(writer, sheet_name='Valuation', index=False)
    output.seek(0)
    return output

# ============================================================================
# STOCK SIMULATOR GAME CLASS
# ============================================================================
class StockSimulator:
    """Historical stock trading simulator game"""

    @staticmethod
    @st.cache_data(ttl=3600)
    def get_historical_data(ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Fetch historical data for simulation"""
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(start=start_date, end=end_date)
            return hist if len(hist) > 0 else pd.DataFrame()
        except:
            return pd.DataFrame()

    @staticmethod
    def calculate_portfolio_value(holdings: dict, prices: dict) -> float:
        """Calculate total portfolio value"""
        total = 0
        for ticker, shares in holdings.items():
            if ticker == 'CASH':
                total += shares
            elif ticker in prices:
                total += shares * prices[ticker]
        return total

    @staticmethod
    def get_price_at_date(hist: pd.DataFrame, date: datetime) -> float:
        """Get closing price at or before a specific date"""
        if hist.empty:
            return 0
        hist_before = hist[hist.index <= date]
        if len(hist_before) > 0:
            return hist_before['Close'].iloc[-1]
        return hist['Close'].iloc[0]


@st.cache_data(ttl=300)
@st.cache_data(ttl=120)
def get_market_movers() -> dict:
    """Fetch top gainers, losers, and most active stocks - batch download for speed"""
    movers = {'gainers': [], 'losers': [], 'active': []}

    # Popular stocks to check
    watchlist = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'AMD', 'NFLX', 'CRM',
                 'JPM', 'V', 'MA', 'BAC', 'WMT', 'JNJ', 'PG', 'UNH', 'HD', 'DIS',
                 'PYPL', 'ADBE', 'INTC', 'CSCO', 'PEP', 'KO', 'MRK', 'ABT', 'TMO', 'COST']

    stock_data = []

    try:
        # Batch download - much faster than individual calls
        data = yf.download(watchlist, period='2d', progress=False, threads=True)
        if not data.empty:
            for ticker in watchlist:
                try:
                    if ticker in data['Close'].columns:
                        closes = data['Close'][ticker].dropna()
                        volumes = data['Volume'][ticker].dropna()
                        if len(closes) >= 2:
                            current = closes.iloc[-1]
                            prev = closes.iloc[-2]
                            change_pct = ((current - prev) / prev) * 100
                            volume = volumes.iloc[-1] if len(volumes) > 0 else 0

                            stock_data.append({
                                'ticker': ticker,
                                'name': ticker,
                                'price': current,
                                'change': change_pct,
                                'volume': volume
                            })
                except:
                    continue
    except:
        pass

    if stock_data:
        # Sort for gainers and losers
        sorted_by_change = sorted(stock_data, key=lambda x: x['change'], reverse=True)
        movers['gainers'] = sorted_by_change[:5]
        movers['losers'] = sorted_by_change[-5:][::-1]

        # Sort for most active
        sorted_by_volume = sorted(stock_data, key=lambda x: x['volume'], reverse=True)
        movers['active'] = sorted_by_volume[:5]

    return movers


# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================
if 'current_ticker' not in st.session_state:
    st.session_state['current_ticker'] = None
if 'analysis_data' not in st.session_state:
    st.session_state['analysis_data'] = None
if 'dcf_file' not in st.session_state:
    st.session_state['dcf_file'] = None
if 'fg_data' not in st.session_state:
    st.session_state['fg_data'] = calculate_fear_greed()
if 'chart_timeframe' not in st.session_state:
    st.session_state['chart_timeframe'] = '1Y'

# Portfolio state
if 'portfolio_holdings' not in st.session_state:
    st.session_state['portfolio_holdings'] = []

# Simulator game state
if 'sim_cash' not in st.session_state:
    st.session_state['sim_cash'] = 100000.0
if 'sim_holdings' not in st.session_state:
    st.session_state['sim_holdings'] = {}
if 'sim_history' not in st.session_state:
    st.session_state['sim_history'] = []
if 'sim_start_date' not in st.session_state:
    st.session_state['sim_start_date'] = datetime(2020, 1, 1)
if 'sim_current_date' not in st.session_state:
    st.session_state['sim_current_date'] = datetime(2020, 1, 1)
if 'sim_started' not in st.session_state:
    st.session_state['sim_started'] = False

# ============================================================================
# SIDEBAR - Global Controls & Portfolio Input
# ============================================================================
with st.sidebar:
    st.markdown(f"""
    <div style='text-align: center; padding: 20px 0;'>
        <div style='font-size: 24px; font-weight: 800; background: linear-gradient(135deg, {THEME["accent_primary"]}, {THEME["opportunity"]}); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>
            MISPRICED
        </div>
        <div style='font-size: 10px; color: {THEME["text_muted"]}; letter-spacing: 0.2em;'>FORENSIC INTELLIGENCE</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Market Sentiment Widget
    fg = st.session_state.get('fg_data', {'score': 50, 'label': 'Neutral', 'vix': 20})
    fg_score = fg.get('score', 50)
    fg_label = fg.get('label', 'Neutral')
    fg_vix = fg.get('vix', 20)

    # Professional color gradient
    if fg_score >= 65: fg_color = '#22c55e'
    elif fg_score >= 55: fg_color = '#84cc16'
    elif fg_score >= 45: fg_color = '#eab308'
    elif fg_score >= 35: fg_color = '#f97316'
    else: fg_color = '#ef4444'

    st.markdown(f"""
    <div style='background: {THEME["bg_card"]}; border: 1px solid {fg_color}; border-radius: 8px; padding: 16px; text-align: center;'>
        <div style='font-size: 10px; color: {THEME["text_muted"]}; text-transform: uppercase; letter-spacing: 0.1em;'>Fear & Greed</div>
        <div style='font-size: 32px; font-weight: 800; color: {fg_color}; margin: 8px 0;'>{fg_score:.0f}</div>
        <div style='font-size: 12px; color: {fg_color}; font-weight: 600;'>{fg_label}</div>
        <div style='font-size: 10px; color: {THEME["text_muted"]}; margin-top: 8px;'>VIX: {fg_vix:.1f}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Strategy Selection
    st.markdown(f"<div style='font-size: 11px; font-weight: 600; color: {THEME['text_secondary']}; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 8px;'>Investment Strategy</div>", unsafe_allow_html=True)
    strategy = st.selectbox(
        "Strategy",
        ["Balanced", "Value Focused", "Growth Focused", "Income Focused", "Aggressive"],
        label_visibility="collapsed"
    )

    st.markdown("---")

    # Quick Portfolio Entry
    st.markdown(f"<div style='font-size: 11px; font-weight: 600; color: {THEME['text_secondary']}; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 8px;'>Quick Add to Portfolio</div>", unsafe_allow_html=True)

    with st.form("quick_add_form"):
        qa_ticker = st.text_input("Ticker", placeholder="AAPL", label_visibility="collapsed")
        qa_cols = st.columns(2)
        qa_shares = qa_cols[0].number_input("Shares", min_value=0.0, value=0.0, label_visibility="collapsed", placeholder="Shares")
        qa_cost = qa_cols[1].number_input("Cost", min_value=0.0, value=0.0, label_visibility="collapsed", placeholder="Cost")
        if st.form_submit_button("➕ Add", use_container_width=True):
            if qa_ticker and qa_shares > 0:
                st.session_state['portfolio_holdings'].append({
                    'ticker': qa_ticker.upper(),
                    'shares': qa_shares,
                    'cost': qa_cost
                })
                st.success(f"Added {qa_ticker.upper()}")

    # Show current portfolio
    if st.session_state['portfolio_holdings']:
        st.markdown(f"<div style='font-size: 10px; color: {THEME['text_muted']}; margin-top: 12px;'>Current Holdings: {len(st.session_state['portfolio_holdings'])}</div>", unsafe_allow_html=True)

    st.markdown("---")

    # Data refresh
    if st.button("🔄 Refresh Market Data", use_container_width=True):
        st.session_state['fg_data'] = calculate_fear_greed()
        st.cache_data.clear()
        st.rerun()

# ============================================================================
# MAIN HEADER
# ============================================================================
st.markdown("<div class='main-header'>MISPRICED MARKET</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Forensic Investment Intelligence • Distortion Detection • Retail Edge</div>", unsafe_allow_html=True)

# ============================================================================
# LIVE TICKER TAPE
# ============================================================================
@st.cache_data(ttl=120)
def get_ticker_tape_data():
    """Get live ticker data for the tape - batch download for speed"""
    tickers = ['SPY', 'QQQ', 'DIA', 'IWM', 'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA', 'META', 'BTC-USD', 'GC=F', 'CL=F']
    tape_data = []
    try:
        # Batch download - much faster than individual calls
        data = yf.download(tickers, period='2d', progress=False, threads=True)
        if not data.empty:
            for t in tickers:
                try:
                    if t in data['Close'].columns:
                        closes = data['Close'][t].dropna()
                        if len(closes) >= 2:
                            current = closes.iloc[-1]
                            prev = closes.iloc[-2]
                            change = ((current - prev) / prev) * 100
                            tape_data.append({'ticker': t, 'price': current, 'change': change})
                except:
                    pass
    except:
        pass
    return tape_data

ticker_tape = get_ticker_tape_data()
if ticker_tape:
    tape_html = "<div style='background: linear-gradient(90deg, #0a0e17 0%, #131a2b 50%, #0a0e17 100%); padding: 10px 0; overflow: hidden; border-top: 1px solid #1e293b; border-bottom: 1px solid #1e293b; margin-bottom: 20px;'>"
    tape_html += "<div style='display: flex; gap: 40px; animation: scroll 30s linear infinite; white-space: nowrap;'>"
    for item in ticker_tape * 3:  # Repeat for seamless scroll
        color = '#22c55e' if item['change'] >= 0 else '#ef4444'
        arrow = '▲' if item['change'] >= 0 else '▼'
        ticker_name = item['ticker'].replace('-USD', '').replace('=F', '')
        tape_html += f"<span style='color: #94a3b8; font-size: 13px; font-weight: 500;'>{ticker_name}</span>"
        tape_html += f"<span style='color: #e2e8f0; font-size: 13px; margin-left: 8px;'>${item['price']:.2f}</span>"
        tape_html += f"<span style='color: {color}; font-size: 12px; margin-left: 6px;'>{arrow} {abs(item['change']):.2f}%</span>"
        tape_html += "<span style='margin-right: 40px;'></span>"
    tape_html += "</div></div>"
    tape_html += """<style>@keyframes scroll { 0% { transform: translateX(0); } 100% { transform: translateX(-33.33%); } }</style>"""
    st.markdown(tape_html, unsafe_allow_html=True)

# ============================================================================
# MAIN NAVIGATION TABS
# ============================================================================
main_tabs = st.tabs(["🏠 MARKET OVERVIEW", "🎯 SINGLE ASSET", "🔬 FORENSIC LAB", "⚡ RETAIL EDGE", "📊 MULTI-ASSET", "🌍 MACRO", "🎮 SIMULATOR"])

@st.cache_data(ttl=120)
def get_indices_data():
    """Batch fetch indices data for speed"""
    indices_tickers = ['SPY', 'QQQ', 'DIA', 'IWM']
    indices_data = {}
    try:
        data = yf.download(indices_tickers, period='5d', progress=False, threads=True)
        if not data.empty:
            for ticker in indices_tickers:
                try:
                    if ticker in data['Close'].columns:
                        closes = data['Close'][ticker].dropna()
                        if len(closes) >= 2:
                            indices_data[ticker] = {
                                'current': closes.iloc[-1],
                                'prev': closes.iloc[-2],
                                'change': ((closes.iloc[-1] - closes.iloc[-2]) / closes.iloc[-2]) * 100
                            }
                except:
                    pass
    except:
        pass
    return indices_data

# ============================================================================
# TAB 0: MARKET OVERVIEW (HOME)
# ============================================================================
with main_tabs[0]:
    st.markdown(f"<h2 style='color: {THEME['text_primary']}; margin-bottom: 20px;'>📈 Today's Market Pulse</h2>", unsafe_allow_html=True)

    # Get market movers and indices (cached)
    movers = get_market_movers()
    indices_data = get_indices_data()

    # Top row - Major indices
    idx_cols = st.columns(4)
    indices = [('SPY', 'S&P 500'), ('QQQ', 'NASDAQ'), ('DIA', 'DOW'), ('IWM', 'Russell 2000')]
    for i, (ticker, name) in enumerate(indices):
        with idx_cols[i]:
            if ticker in indices_data:
                idx = indices_data[ticker]
                color = THEME['positive'] if idx['change'] >= 0 else THEME['negative']
                arrow = '▲' if idx['change'] >= 0 else '▼'
                st.markdown(f"""
                    <div style='background: {THEME['card_bg']}; padding: 15px; border-radius: 8px; border: 1px solid {THEME['border']};'>
                        <div style='color: {THEME['text_muted']}; font-size: 11px; text-transform: uppercase;'>{name}</div>
                        <div style='color: {THEME['text_primary']}; font-size: 24px; font-weight: 700;'>${idx['current']:.2f}</div>
                        <div style='color: {color}; font-size: 14px;'>{arrow} {idx['change']:+.2f}%</div>
                    </div>
                """, unsafe_allow_html=True)

    st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)

    # Top Gainers and Losers Section
    mover_cols = st.columns(2)

    with mover_cols[0]:
        st.markdown(f"<h3 style='color: {THEME['green']}; margin-bottom: 15px;'>🚀 Top Gainers</h3>", unsafe_allow_html=True)
        if movers['gainers']:
            for stock in movers['gainers'][:5]:
                st.markdown(f"""
                    <div style='background: {THEME['card_bg']}; padding: 12px; border-radius: 6px; margin-bottom: 8px; border-left: 3px solid {THEME['green']}; display: flex; justify-content: space-between; align-items: center;'>
                        <div>
                            <span style='color: {THEME['green']}; font-weight: 700;'>{stock['ticker']}</span>
                            <span style='color: {THEME['text_muted']}; font-size: 12px; margin-left: 10px;'>${stock['price']:.2f}</span>
                        </div>
                        <span style='color: {THEME['green']}; font-weight: 700;'>+{stock['change']:.2f}%</span>
                    </div>
                """, unsafe_allow_html=True)

            # Chart for top gainer
            if movers['gainers']:
                top_gainer = movers['gainers'][0]['ticker']
                try:
                    gainer_hist = yf.Ticker(top_gainer).history(period='5d', interval='15m')
                    if not gainer_hist.empty:
                        fig_gainer = go.Figure()
                        fig_gainer.add_trace(go.Scatter(
                            x=gainer_hist.index, y=gainer_hist['Close'],
                            mode='lines', fill='tozeroy',
                            line=dict(color=THEME['positive'], width=2),
                            fillcolor='rgba(34, 197, 94, 0.1)'
                        ))
                        fig_gainer.update_layout(
                            height=200, margin=dict(l=0, r=0, t=30, b=0),
                            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                            title=dict(text=f'{top_gainer} - 5 Day', font=dict(size=12, color=THEME['text_muted'])),
                            xaxis=dict(showgrid=False, showticklabels=False),
                            yaxis=dict(showgrid=True, gridcolor=THEME['grid'], showticklabels=True, tickfont=dict(color=THEME['text_muted'], size=10))
                        )
                        st.plotly_chart(fig_gainer, use_container_width=True)
                except:
                    pass

    with mover_cols[1]:
        st.markdown(f"<h3 style='color: {THEME['red']}; margin-bottom: 15px;'>📉 Top Losers</h3>", unsafe_allow_html=True)
        if movers['losers']:
            for stock in movers['losers'][:5]:
                st.markdown(f"""
                    <div style='background: {THEME['card_bg']}; padding: 12px; border-radius: 6px; margin-bottom: 8px; border-left: 3px solid {THEME['red']}; display: flex; justify-content: space-between; align-items: center;'>
                        <div>
                            <span style='color: {THEME['red']}; font-weight: 700;'>{stock['ticker']}</span>
                            <span style='color: {THEME['text_muted']}; font-size: 12px; margin-left: 10px;'>${stock['price']:.2f}</span>
                        </div>
                        <span style='color: {THEME['red']}; font-weight: 700;'>{stock['change']:.2f}%</span>
                    </div>
                """, unsafe_allow_html=True)

            # Chart for top loser
            if movers['losers']:
                top_loser = movers['losers'][0]['ticker']
                try:
                    loser_hist = yf.Ticker(top_loser).history(period='5d', interval='15m')
                    if not loser_hist.empty:
                        fig_loser = go.Figure()
                        fig_loser.add_trace(go.Scatter(
                            x=loser_hist.index, y=loser_hist['Close'],
                            mode='lines', fill='tozeroy',
                            line=dict(color=THEME['negative'], width=2),
                            fillcolor='rgba(239, 68, 68, 0.1)'
                        ))
                        fig_loser.update_layout(
                            height=200, margin=dict(l=0, r=0, t=30, b=0),
                            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                            title=dict(text=f'{top_loser} - 5 Day', font=dict(size=12, color=THEME['text_muted'])),
                            xaxis=dict(showgrid=False, showticklabels=False),
                            yaxis=dict(showgrid=True, gridcolor=THEME['grid'], showticklabels=True, tickfont=dict(color=THEME['text_muted'], size=10))
                        )
                        st.plotly_chart(fig_loser, use_container_width=True)
                except:
                    pass

    st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)

    # Most Active
    st.markdown(f"<h3 style='color: {THEME['text_primary']}; margin-bottom: 15px;'>🔥 Most Active</h3>", unsafe_allow_html=True)
    if movers['active']:
        active_cols = st.columns(5)
        for i, stock in enumerate(movers['active'][:5]):
            with active_cols[i]:
                color = THEME['green'] if stock['change'] >= 0 else THEME['red']
                st.markdown(f"""
                    <div style='background: {THEME['card_bg']}; padding: 15px; border-radius: 8px; text-align: center; border: 1px solid {THEME['border']};'>
                        <div style='color: {color}; font-weight: 700; font-size: 18px;'>{stock['ticker']}</div>
                        <div style='color: {THEME['text_muted']}; font-size: 13px;'>${stock['price']:.2f}</div>
                        <div style='color: {color}; font-size: 14px; font-weight: 700;'>{stock['change']:+.2f}%</div>
                        <div style='color: {THEME['text_muted']}; font-size: 10px; margin-top: 5px;'>Vol: {stock['volume']/1e6:.1f}M</div>
                    </div>
                """, unsafe_allow_html=True)

    # Fear & Greed Mini Display
    st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
    fg = st.session_state.get('fg_data', calculate_fear_greed())
    fg_score = fg.get('score', 50)
    if fg_score >= 75:
        fg_label, fg_color = "EXTREME GREED", "#22c55e"
    elif fg_score >= 55:
        fg_label, fg_color = "GREED", "#84cc16"
    elif fg_score >= 45:
        fg_label, fg_color = "NEUTRAL", "#eab308"
    elif fg_score >= 25:
        fg_label, fg_color = "FEAR", "#f97316"
    else:
        fg_label, fg_color = "EXTREME FEAR", "#ef4444"

    st.markdown(f"""
        <div style='background: linear-gradient(135deg, {THEME['card_bg']} 0%, #1a1f2e 100%); padding: 25px; border-radius: 12px; text-align: center; border: 1px solid {THEME['border']};'>
            <div style='color: {THEME['text_muted']}; font-size: 12px; text-transform: uppercase; letter-spacing: 0.1em;'>Market Sentiment</div>
            <div style='color: {fg_color}; font-size: 48px; font-weight: 800; margin: 10px 0;'>{fg_score:.0f}</div>
            <div style='color: {fg_color}; font-size: 18px; font-weight: 600;'>{fg_label}</div>
        </div>
    """, unsafe_allow_html=True)

# ============================================================================
# TAB 1: SINGLE ASSET ANALYSIS
# ============================================================================
with main_tabs[1]:
    # Search bar
    search_cols = st.columns([3, 1])
    with search_cols[0]:
        ticker_input = st.text_input(
            "Search",
            placeholder="Enter ticker symbol (AAPL, NVDA, TSLA...)",
            label_visibility="collapsed"
        ).upper()
    with search_cols[1]:
        analyze_btn = st.button("⚡ ANALYZE", use_container_width=True, type="primary")

    if analyze_btn and ticker_input:
        st.session_state['current_ticker'] = ticker_input
        st.session_state['analysis_data'] = None

    # Main analysis
    if st.session_state['current_ticker']:
        ticker = st.session_state['current_ticker']

        # Set weights based on strategy
        if strategy == "Value Focused":
            weights = {'valuation': 0.40, 'quality': 0.25, 'growth': 0.10, 'momentum': 0.10, 'risk': 0.15}
        elif strategy == "Growth Focused":
            weights = {'valuation': 0.15, 'quality': 0.20, 'growth': 0.40, 'momentum': 0.15, 'risk': 0.10}
        elif strategy == "Income Focused":
            weights = {'valuation': 0.25, 'quality': 0.35, 'growth': 0.10, 'momentum': 0.10, 'risk': 0.20}
        elif strategy == "Aggressive":
            weights = {'valuation': 0.10, 'quality': 0.15, 'growth': 0.35, 'momentum': 0.30, 'risk': 0.10}
        else:
            weights = {'valuation': 0.25, 'quality': 0.25, 'growth': 0.20, 'momentum': 0.15, 'risk': 0.15}

        # Load data if needed (silent loading - no visible spinner)
        if not st.session_state['analysis_data'] or st.session_state['analysis_data'].get('ticker') != ticker:
            try:
                info = DataEngine.get_info(ticker)
                if not info or 'currentPrice' not in info:
                    st.error(f"Could not find data for {ticker}")
                    st.stop()

                hist = DataEngine.get_history(ticker, period='2y')
                if hist.empty:
                    st.error("No historical data available")
                    st.stop()

                fundamentals = get_fundamental_metrics(info)
                news = DataEngine.get_news(ticker)
                financials = DataEngine.get_financials(ticker)
                scores, total_score, metrics = calculate_smart_score(info, hist, fundamentals, weights)

                # Forensic analysis
                distortion = ForensicLab.analyze_distortion(ticker, info, financials)
                quality = ForensicLab.calculate_quality_of_earnings(ticker, financials)

                # Retail edge data
                inst_holders = DataEngine.get_institutional_holders(ticker)
                insider_tx = DataEngine.get_insider_transactions(ticker)
                options_data = DataEngine.get_options_chain(ticker)

                st.session_state['analysis_data'] = {
                    'ticker': ticker,
                    'info': info,
                    'hist': hist,
                    'fundamentals': fundamentals,
                    'news': news,
                    'financials': financials,
                    'scores': scores,
                    'total_score': total_score,
                    'metrics': metrics,
                    'distortion': distortion,
                    'quality': quality,
                    'inst_holders': inst_holders,
                    'insider_tx': insider_tx,
                    'options_data': options_data
                }
            except Exception as e:
                st.error(f"Error loading data: {str(e)}")
                st.stop()

        data = st.session_state['analysis_data']
        info = data['info']

        st.markdown("---")

        # Company Header
        header_cols = st.columns([3, 1])
        with header_cols[0]:
            st.markdown(f"""
            <div style='font-size: 28px; font-weight: 800; color: {THEME["text_primary"]};'>{info.get('longName', ticker)}</div>
            <div style='display: flex; gap: 12px; align-items: center; margin-top: 8px;'>
                <span class='badge badge-neutral'>{ticker}</span>
                <span style='color: {THEME["text_secondary"]}; font-size: 13px;'>{info.get('sector', 'N/A')} • {info.get('industry', 'N/A')}</span>
            </div>
            """, unsafe_allow_html=True)

            price = info.get('currentPrice', 0)
            change_pct = info.get('regularMarketChangePercent', 0)
            price_color = THEME['bullish'] if change_pct >= 0 else THEME['bearish']
            st.markdown(f"""
            <div style='font-size: 42px; font-weight: 900; color: {price_color}; margin-top: 12px;'>
                ${price:.2f}
                <span style='font-size: 18px; margin-left: 8px;'>{change_pct:+.2f}%</span>
            </div>
            """, unsafe_allow_html=True)

        with header_cols[1]:
            rating, rating_color = get_rating(data['total_score'])
            st.markdown(f"""
            <div style='background: {THEME["bg_card"]}; border: 2px solid {rating_color}; border-radius: 12px; padding: 20px; text-align: center;'>
                <div style='font-size: 10px; color: {THEME["text_muted"]}; text-transform: uppercase; letter-spacing: 0.1em;'>Smart Score</div>
                <div style='font-size: 48px; font-weight: 900; color: {rating_color}; margin: 8px 0;'>{data['total_score']:.0f}</div>
                <div style='font-size: 13px; font-weight: 700; color: {rating_color};'>{rating}</div>
            </div>
            """, unsafe_allow_html=True)

        # Score breakdown
        st.markdown("<div class='section-header'>Score Breakdown</div>", unsafe_allow_html=True)
        score_cols = st.columns(5)
        score_items = [
            ('Valuation', data['scores']['valuation'], '💎'),
            ('Quality', data['scores']['quality'], '⭐'),
            ('Growth', data['scores']['growth'], '🚀'),
            ('Momentum', data['scores']['momentum'], '📈'),
            ('Risk', data['scores']['risk'], '🛡️')
        ]
        for col, (label, score, emoji) in zip(score_cols, score_items):
            s_color = THEME['bullish'] if score >= 70 else THEME['warning'] if score >= 40 else THEME['bearish']
            col.markdown(f"""
            <div class='metric-card' style='text-align: center;'>
                <div style='font-size: 24px;'>{emoji}</div>
                <div style='font-size: 28px; font-weight: 800; color: {s_color};'>{score:.0f}</div>
                <div style='font-size: 10px; color: {THEME["text_muted"]}; text-transform: uppercase;'>{label}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # Analysis Sub-tabs
        analysis_tabs = st.tabs(["📈 CHART", "📰 NEWS", "📊 FINANCIALS", "💎 FUNDAMENTALS", "💰 VALUATION", "🔬 FORENSIC"])

        # CHART TAB
        with analysis_tabs[0]:
            # Timeframe selector
            tf_cols = st.columns(8)
            timeframes = ['1W', '1M', '3M', 'YTD', '1Y', '3Y', '5Y', 'MAX']
            selected_tf = st.session_state.get('chart_timeframe', '1Y')

            for i, tf in enumerate(timeframes):
                if tf_cols[i].button(tf, key=f"tf_{tf}", use_container_width=True,
                                     type="primary" if tf == selected_tf else "secondary"):
                    st.session_state['chart_timeframe'] = tf
                    selected_tf = tf

            # Get data for selected timeframe
            tf_config = TIMEFRAMES.get(selected_tf, TIMEFRAMES['1Y'])
            chart_hist = DataEngine.get_history(ticker, period=tf_config['period'], interval=tf_config['interval'])

            if not chart_hist.empty:
                # Technical indicators
                with st.expander("📊 Technical Indicators", expanded=False):
                    ind_cols = st.columns(4)
                    show_ma50 = ind_cols[0].checkbox("MA 50", value=True)
                    show_ma200 = ind_cols[1].checkbox("MA 200", value=True)
                    show_bb = ind_cols[2].checkbox("Bollinger Bands", value=False)
                    show_volume = ind_cols[3].checkbox("Volume", value=True)

                # Create professional chart
                fig = make_subplots(
                    rows=2 if show_volume else 1, cols=1, shared_xaxes=True,
                    row_heights=[0.75, 0.25] if show_volume else [1],
                    vertical_spacing=0.03
                )

                # Candlestick with improved styling
                fig.add_trace(go.Candlestick(
                    x=chart_hist.index,
                    open=chart_hist['Open'], high=chart_hist['High'],
                    low=chart_hist['Low'], close=chart_hist['Close'],
                    name='Price',
                    increasing=dict(line=dict(color='#22c55e', width=1), fillcolor='#22c55e'),
                    decreasing=dict(line=dict(color='#ef4444', width=1), fillcolor='#ef4444'),
                    hoverinfo='x+y',
                ), row=1, col=1)

                # Moving averages with better visibility
                if show_ma50 and len(chart_hist) >= 50:
                    ma50 = chart_hist['Close'].rolling(50).mean()
                    fig.add_trace(go.Scatter(
                        x=chart_hist.index, y=ma50, mode='lines', name='50 MA',
                        line=dict(color='#f59e0b', width=1.5),
                        hovertemplate='50 MA: $%{y:.2f}<extra></extra>'
                    ), row=1, col=1)

                if show_ma200 and len(chart_hist) >= 200:
                    ma200 = chart_hist['Close'].rolling(200).mean()
                    fig.add_trace(go.Scatter(
                        x=chart_hist.index, y=ma200, mode='lines', name='200 MA',
                        line=dict(color='#ec4899', width=1.5),
                        hovertemplate='200 MA: $%{y:.2f}<extra></extra>'
                    ), row=1, col=1)

                # Bollinger Bands with fill
                if show_bb:
                    bb = calculate_bollinger_bands(chart_hist['Close'])
                    fig.add_trace(go.Scatter(
                        x=chart_hist.index, y=bb['upper'], mode='lines', name='BB Upper',
                        line=dict(color='rgba(139, 92, 246, 0.5)', width=1),
                        hoverinfo='skip'
                    ), row=1, col=1)
                    fig.add_trace(go.Scatter(
                        x=chart_hist.index, y=bb['lower'], mode='lines', name='BB Lower',
                        line=dict(color='rgba(139, 92, 246, 0.5)', width=1),
                        fill='tonexty', fillcolor='rgba(139, 92, 246, 0.08)',
                        hoverinfo='skip'
                    ), row=1, col=1)

                # Volume bars
                if show_volume:
                    vol_colors = ['#22c55e' if chart_hist['Close'].iloc[i] >= chart_hist['Open'].iloc[i]
                                  else '#ef4444' for i in range(len(chart_hist))]
                    fig.add_trace(go.Bar(
                        x=chart_hist.index, y=chart_hist['Volume'], name='Volume',
                        marker_color=vol_colors, opacity=0.6,
                        hovertemplate='Vol: %{y:,.0f}<extra></extra>'
                    ), row=2, col=1)

                # Professional layout
                fig.update_layout(
                    height=580,
                    xaxis_rangeslider_visible=False,
                    showlegend=True,
                    plot_bgcolor='#0a0e17',
                    paper_bgcolor='#0a0e17',
                    font=dict(color='#9ca3af', family='Inter, sans-serif', size=11),
                    legend=dict(
                        orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5,
                        bgcolor='rgba(0,0,0,0)', font=dict(size=10)
                    ),
                    margin=dict(l=60, r=20, t=30, b=20),
                    hovermode='x unified',
                )

                # Axis styling
                fig.update_xaxes(
                    showgrid=True, gridcolor='#1f2937', gridwidth=1,
                    showline=True, linecolor='#374151',
                    tickfont=dict(size=10), dtick='M1' if selected_tf in ['1Y', '3Y', '5Y', 'MAX'] else None
                )
                fig.update_yaxes(
                    showgrid=True, gridcolor='#1f2937', gridwidth=1,
                    showline=True, linecolor='#374151',
                    tickfont=dict(size=10), tickprefix='$', row=1, col=1
                )
                if show_volume:
                    fig.update_yaxes(showgrid=False, tickfont=dict(size=9), row=2, col=1)

                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

                # Key stats
                stat_cols = st.columns(6)
                stat_cols[0].metric("52W High", f"${info.get('fiftyTwoWeekHigh', 0):.2f}")
                stat_cols[1].metric("52W Low", f"${info.get('fiftyTwoWeekLow', 0):.2f}")
                stat_cols[2].metric("Avg Volume", f"{info.get('averageVolume', 0)/1e6:.2f}M")
                stat_cols[3].metric("Beta", f"{info.get('beta', 0):.2f}")
                stat_cols[4].metric("RSI (14)", f"{data['metrics'].get('rsi', 50):.0f}")
                stat_cols[5].metric("Market Cap", format_large_number(info.get('marketCap', 0)))

        # NEWS TAB
        with analysis_tabs[1]:
            st.markdown("<div class='section-header'>Market Intelligence Feed</div>", unsafe_allow_html=True)

            # Live news link
            st.markdown(f"""
            <a href='https://finance.yahoo.com/quote/{ticker}/news' target='_blank' style='display: block; background: linear-gradient(135deg, {THEME["accent_primary"]}, {THEME["opportunity"]}); padding: 16px; border-radius: 8px; text-align: center; color: white; font-weight: 700; text-decoration: none; margin-bottom: 20px;'>
                📡 VIEW LIVE NEWS STREAM →
            </a>
            """, unsafe_allow_html=True)

            if data['news']:
                for article in data['news'][:15]:
                    sentiment = estimate_news_sentiment(article['title'])
                    sentiment_class = f"sentiment-{sentiment}"
                    sentiment_label = sentiment.upper()

                    thumbnail_html = f"<img src='{article['thumbnail']}' class='news-image'>" if article.get('thumbnail') else "<div class='news-image-placeholder'>📰</div>"

                    st.markdown(f"""
                    <a href='{article['link']}' target='_blank' style='text-decoration: none;'>
                        <div class='news-card'>
                            {thumbnail_html}
                            <div class='news-content'>
                                <div>
                                    <div class='news-title'>{article['title']}</div>
                                    <div class='news-meta'>
                                        <span class='news-publisher'>{article['publisher']}</span>
                                        <span class='news-time'>{time_ago(article['published'])}</span>
                                        <span class='news-sentiment {sentiment_class}'>{sentiment_label}</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </a>
                    """, unsafe_allow_html=True)
            else:
                st.info("No recent news available")

        # FINANCIALS TAB
        with analysis_tabs[2]:
            st.markdown("<div class='section-header'>Company Financials</div>", unsafe_allow_html=True)

            # Get company info for links
            company_name = info.get('longName', ticker)

            # Financial Links Section
            st.markdown(f"""
            <div style='margin-bottom: 24px;'>
                <div style='color: {THEME["text_muted"]}; font-size: 12px; margin-bottom: 16px; text-transform: uppercase; letter-spacing: 0.1em;'>
                    Detailed Financial Statements & SEC Filings
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Create link cards
            fin_col1, fin_col2 = st.columns(2)

            with fin_col1:
                # SEC Filings
                st.markdown(f"""
                <a href='https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={ticker}&type=10&dateb=&owner=include&count=40' target='_blank' style='text-decoration: none;'>
                    <div style='background: {THEME["card_bg"]}; border: 1px solid {THEME["border"]}; border-radius: 12px; padding: 20px; margin-bottom: 16px; transition: all 0.3s ease;' onmouseover="this.style.borderColor='{THEME["accent_primary"]}'" onmouseout="this.style.borderColor='{THEME["border"]}'">
                        <div style='display: flex; align-items: center; gap: 12px;'>
                            <div style='font-size: 28px;'>📋</div>
                            <div>
                                <div style='color: {THEME["text_primary"]}; font-weight: 700; font-size: 15px;'>SEC EDGAR Filings</div>
                                <div style='color: {THEME["text_muted"]}; font-size: 12px;'>10-K, 10-Q, 8-K Reports</div>
                            </div>
                        </div>
                    </div>
                </a>
                """, unsafe_allow_html=True)

                # Yahoo Finance Financials
                st.markdown(f"""
                <a href='https://finance.yahoo.com/quote/{ticker}/financials/' target='_blank' style='text-decoration: none;'>
                    <div style='background: {THEME["card_bg"]}; border: 1px solid {THEME["border"]}; border-radius: 12px; padding: 20px; margin-bottom: 16px; transition: all 0.3s ease;' onmouseover="this.style.borderColor='{THEME["accent_primary"]}'" onmouseout="this.style.borderColor='{THEME["border"]}'">
                        <div style='display: flex; align-items: center; gap: 12px;'>
                            <div style='font-size: 28px;'>💰</div>
                            <div>
                                <div style='color: {THEME["text_primary"]}; font-weight: 700; font-size: 15px;'>Income Statement</div>
                                <div style='color: {THEME["text_muted"]}; font-size: 12px;'>Revenue, Earnings, Margins</div>
                            </div>
                        </div>
                    </div>
                </a>
                """, unsafe_allow_html=True)

                # Balance Sheet
                st.markdown(f"""
                <a href='https://finance.yahoo.com/quote/{ticker}/balance-sheet/' target='_blank' style='text-decoration: none;'>
                    <div style='background: {THEME["card_bg"]}; border: 1px solid {THEME["border"]}; border-radius: 12px; padding: 20px; margin-bottom: 16px; transition: all 0.3s ease;' onmouseover="this.style.borderColor='{THEME["accent_primary"]}'" onmouseout="this.style.borderColor='{THEME["border"]}'">
                        <div style='display: flex; align-items: center; gap: 12px;'>
                            <div style='font-size: 28px;'>📊</div>
                            <div>
                                <div style='color: {THEME["text_primary"]}; font-weight: 700; font-size: 15px;'>Balance Sheet</div>
                                <div style='color: {THEME["text_muted"]}; font-size: 12px;'>Assets, Liabilities, Equity</div>
                            </div>
                        </div>
                    </div>
                </a>
                """, unsafe_allow_html=True)

            with fin_col2:
                # Cash Flow
                st.markdown(f"""
                <a href='https://finance.yahoo.com/quote/{ticker}/cash-flow/' target='_blank' style='text-decoration: none;'>
                    <div style='background: {THEME["card_bg"]}; border: 1px solid {THEME["border"]}; border-radius: 12px; padding: 20px; margin-bottom: 16px; transition: all 0.3s ease;' onmouseover="this.style.borderColor='{THEME["accent_primary"]}'" onmouseout="this.style.borderColor='{THEME["border"]}'">
                        <div style='display: flex; align-items: center; gap: 12px;'>
                            <div style='font-size: 28px;'>💵</div>
                            <div>
                                <div style='color: {THEME["text_primary"]}; font-weight: 700; font-size: 15px;'>Cash Flow Statement</div>
                                <div style='color: {THEME["text_muted"]}; font-size: 12px;'>Operating, Investing, Financing</div>
                            </div>
                        </div>
                    </div>
                </a>
                """, unsafe_allow_html=True)

                # Analyst Estimates
                st.markdown(f"""
                <a href='https://finance.yahoo.com/quote/{ticker}/analysis/' target='_blank' style='text-decoration: none;'>
                    <div style='background: {THEME["card_bg"]}; border: 1px solid {THEME["border"]}; border-radius: 12px; padding: 20px; margin-bottom: 16px; transition: all 0.3s ease;' onmouseover="this.style.borderColor='{THEME["accent_primary"]}'" onmouseout="this.style.borderColor='{THEME["border"]}'">
                        <div style='display: flex; align-items: center; gap: 12px;'>
                            <div style='font-size: 28px;'>📈</div>
                            <div>
                                <div style='color: {THEME["text_primary"]}; font-weight: 700; font-size: 15px;'>Analyst Estimates</div>
                                <div style='color: {THEME["text_muted"]}; font-size: 12px;'>EPS & Revenue Forecasts</div>
                            </div>
                        </div>
                    </div>
                </a>
                """, unsafe_allow_html=True)

                # Stock Analysis
                st.markdown(f"""
                <a href='https://stockanalysis.com/stocks/{ticker.lower()}/financials/' target='_blank' style='text-decoration: none;'>
                    <div style='background: {THEME["card_bg"]}; border: 1px solid {THEME["border"]}; border-radius: 12px; padding: 20px; margin-bottom: 16px; transition: all 0.3s ease;' onmouseover="this.style.borderColor='{THEME["accent_primary"]}'" onmouseout="this.style.borderColor='{THEME["border"]}'">
                        <div style='display: flex; align-items: center; gap: 12px;'>
                            <div style='font-size: 28px;'>🔍</div>
                            <div>
                                <div style='color: {THEME["text_primary"]}; font-weight: 700; font-size: 15px;'>Stock Analysis</div>
                                <div style='color: {THEME["text_muted"]}; font-size: 12px;'>Detailed Financial Data</div>
                            </div>
                        </div>
                    </div>
                </a>
                """, unsafe_allow_html=True)

            # Quick Financial Summary from loaded data
            st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
            st.markdown("<div class='subsection-header'>Quick Financial Summary</div>", unsafe_allow_html=True)

            fund = data['fundamentals']
            sum_col1, sum_col2, sum_col3, sum_col4 = st.columns(4)

            with sum_col1:
                st.markdown(f"""
                <div style='background: {THEME["card_bg"]}; border: 1px solid {THEME["border"]}; border-radius: 8px; padding: 16px; text-align: center;'>
                    <div style='color: {THEME["text_muted"]}; font-size: 10px; text-transform: uppercase;'>Revenue</div>
                    <div style='color: {THEME["text_primary"]}; font-size: 18px; font-weight: 700;'>{format_large_number(fund['revenue'])}</div>
                </div>
                """, unsafe_allow_html=True)

            with sum_col2:
                margin_color = THEME['green'] if fund['profit_margin'] > 10 else THEME['text_primary']
                st.markdown(f"""
                <div style='background: {THEME["card_bg"]}; border: 1px solid {THEME["border"]}; border-radius: 8px; padding: 16px; text-align: center;'>
                    <div style='color: {THEME["text_muted"]}; font-size: 10px; text-transform: uppercase;'>Profit Margin</div>
                    <div style='color: {margin_color}; font-size: 18px; font-weight: 700;'>{fund['profit_margin']:.1f}%</div>
                </div>
                """, unsafe_allow_html=True)

            with sum_col3:
                st.markdown(f"""
                <div style='background: {THEME["card_bg"]}; border: 1px solid {THEME["border"]}; border-radius: 8px; padding: 16px; text-align: center;'>
                    <div style='color: {THEME["text_muted"]}; font-size: 10px; text-transform: uppercase;'>Free Cash Flow</div>
                    <div style='color: {THEME["text_primary"]}; font-size: 18px; font-weight: 700;'>{format_large_number(fund['free_cash_flow'])}</div>
                </div>
                """, unsafe_allow_html=True)

            with sum_col4:
                de_color = THEME['green'] if fund['debt_to_equity'] < 0.5 else THEME['red'] if fund['debt_to_equity'] > 1.5 else THEME['text_primary']
                st.markdown(f"""
                <div style='background: {THEME["card_bg"]}; border: 1px solid {THEME["border"]}; border-radius: 8px; padding: 16px; text-align: center;'>
                    <div style='color: {THEME["text_muted"]}; font-size: 10px; text-transform: uppercase;'>Debt/Equity</div>
                    <div style='color: {de_color}; font-size: 18px; font-weight: 700;'>{fund['debt_to_equity']:.2f}x</div>
                </div>
                """, unsafe_allow_html=True)

        # FUNDAMENTALS TAB
        with analysis_tabs[3]:
            st.markdown("<div class='section-header'>Financial DNA</div>", unsafe_allow_html=True)

            fund = data['fundamentals']
            fund_col1, fund_col2, fund_col3 = st.columns(3)

            with fund_col1:
                st.markdown("<div class='subsection-header'>💰 Profitability</div>", unsafe_allow_html=True)
                st.metric("Revenue", format_large_number(fund['revenue']))
                st.metric("Revenue Growth", f"{fund['revenue_growth']:.1f}%",
                         delta="Good" if fund['revenue_growth'] > 10 else None)
                st.metric("Profit Margin", f"{fund['profit_margin']:.1f}%")
                st.metric("Operating Margin", f"{fund['operating_margin']:.1f}%")
                st.metric("Gross Margin", f"{fund['gross_margin']:.1f}%")

            with fund_col2:
                st.markdown("<div class='subsection-header'>📊 Returns</div>", unsafe_allow_html=True)
                st.metric("ROE", f"{fund['roe']:.1f}%", delta="Strong" if fund['roe'] > 15 else None)
                st.metric("ROA", f"{fund['roa']:.1f}%")
                st.metric("EBITDA", format_large_number(fund['ebitda']))
                st.metric("Free Cash Flow", format_large_number(fund['free_cash_flow']))
                st.metric("Operating Cash Flow", format_large_number(fund['operating_cash_flow']))

            with fund_col3:
                st.markdown("<div class='subsection-header'>🛡️ Financial Health</div>", unsafe_allow_html=True)
                st.metric("Current Ratio", f"{fund['current_ratio']:.2f}x")
                st.metric("Quick Ratio", f"{fund.get('quick_ratio', 0):.2f}x")
                st.metric("Debt/Equity", f"{fund['debt_to_equity']:.2f}x",
                         delta="Low" if fund['debt_to_equity'] < 0.5 else "High" if fund['debt_to_equity'] > 1 else None,
                         delta_color="normal" if fund['debt_to_equity'] < 0.5 else "inverse")
                st.metric("Beta", f"{fund['beta']:.2f}")
                st.metric("Short Interest", f"{fund['short_percent']:.1f}%")

        # VALUATION TAB
        with analysis_tabs[4]:
            st.markdown("<div class='section-header'>Valuation Analysis</div>", unsafe_allow_html=True)

            val_col1, val_col2 = st.columns(2)

            with val_col1:
                st.markdown("<div class='subsection-header'>📊 Market Multiples</div>", unsafe_allow_html=True)

                multiples = [
                    ('P/E Ratio', info.get('trailingPE', 0)),
                    ('Forward P/E', info.get('forwardPE', 0)),
                    ('PEG Ratio', info.get('pegRatio', 0)),
                    ('P/S Ratio', info.get('priceToSalesTrailing12Months', 0)),
                    ('P/B Ratio', info.get('priceToBook', 0)),
                    ('EV/Revenue', info.get('enterpriseToRevenue', 0)),
                    ('EV/EBITDA', info.get('enterpriseToEbitda', 0)),
                ]

                for name, value in multiples:
                    if value and value > 0:
                        st.markdown(f"""
                        <div class='metric-card' style='display: flex; justify-content: space-between; padding: 12px;'>
                            <span style='color: {THEME["text_secondary"]};'>{name}</span>
                            <span style='font-weight: 700; color: {THEME["accent_primary"]};'>{value:.2f}x</span>
                        </div>
                        """, unsafe_allow_html=True)

            with val_col2:
                st.markdown("<div class='subsection-header'>⚡ Quick DCF</div>", unsafe_allow_html=True)

                growth = st.slider("Growth Rate (%)", 0, 40, 15, key="qd_growth") / 100
                discount = st.slider("Discount Rate (%)", 5, 20, 10, key="qd_disc") / 100

                fcf = info.get('freeCashflow', 0)
                if fcf and fcf > 0:
                    projected = [fcf * ((1 + growth) ** i) for i in range(1, 6)]
                    pv = [cf / ((1 + discount) ** i) for i, cf in enumerate(projected, 1)]
                    terminal = projected[-1] * 1.03 / (discount - 0.03)
                    pv_terminal = terminal / ((1 + discount) ** 5)
                    ev = sum(pv) + pv_terminal
                    net_debt = info.get('totalDebt', 0) - info.get('totalCash', 0)
                    equity = ev - net_debt
                    shares = info.get('sharesOutstanding', 1)
                    fair = equity / shares if shares > 0 else 0
                    upside = ((fair - price) / price * 100) if price > 0 else 0

                    up_color = THEME['bullish'] if upside > 15 else THEME['warning'] if upside > 0 else THEME['bearish']
                    st.markdown(f"""
                    <div class='opportunity-card' style='text-align: center;'>
                        <div style='font-size: 11px; color: {THEME["text_muted"]};'>FAIR VALUE ESTIMATE</div>
                        <div style='font-size: 42px; font-weight: 900; color: {up_color};'>${fair:.2f}</div>
                        <div style='font-size: 18px; color: {up_color};'>{upside:+.1f}% Upside</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.info("FCF data not available")

                # DCF Model Generator
                st.markdown("---")
                st.markdown("<div class='subsection-header'>📥 Full DCF Model</div>", unsafe_allow_html=True)
                dcf_cols = st.columns(2)
                rg = dcf_cols[0].number_input("Revenue Growth %", 0.0, 50.0, 15.0, key="dcf_rg") / 100
                tg = dcf_cols[0].number_input("Terminal Growth %", 0.0, 5.0, 2.5, key="dcf_tg") / 100
                wa = dcf_cols[1].number_input("WACC %", 5.0, 20.0, 10.0, key="dcf_wa") / 100
                tr = dcf_cols[1].number_input("Tax Rate %", 0.0, 40.0, 21.0, key="dcf_tr") / 100

                if st.button("🚀 Generate DCF Model", use_container_width=True):
                    dcf_params = {'revenue_growth': rg, 'terminal_growth': tg, 'wacc': wa, 'tax_rate': tr}
                    st.session_state['dcf_file'] = generate_dcf_excel(ticker, info, data['fundamentals'], dcf_params)
                    st.success("Model generated!")

                if st.session_state.get('dcf_file'):
                    st.download_button("📥 Download Excel Model", st.session_state['dcf_file'],
                                      f"{ticker}_DCF_{datetime.now().strftime('%Y%m%d')}.xlsx",
                                      "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                      use_container_width=True)

        # FORENSIC TAB
        with analysis_tabs[5]:
            st.markdown("<div class='section-header'>Forensic Analysis</div>", unsafe_allow_html=True)

            distortion = data['distortion']
            quality = data['quality']

            if distortion.get('has_distortion'):
                st.markdown(f"""
                <div class='forensic-alert'>
                    <div style='font-size: 16px; font-weight: 700; color: {THEME["opportunity"]};'>🎯 DISTORTED VALUE DETECTED</div>
                    <div style='color: {THEME["text_secondary"]}; margin-top: 8px;'>
                        This stock shows significant earnings distortion from one-time items.
                        The real forward P/E is <strong>{distortion['pe_gap']:.1f}%</strong> lower than the reported GAAP P/E.
                    </div>
                </div>
                """, unsafe_allow_html=True)

            dist_cols = st.columns(3)
            with dist_cols[0]:
                gaap_pe = distortion.get('gaap_pe', 0) or 0
                st.metric("GAAP P/E", f"{gaap_pe:.1f}x" if gaap_pe > 0 else "N/A")
            with dist_cols[1]:
                real_pe = distortion.get('real_pe', 0) or 0
                st.metric("Real Forward P/E", f"{real_pe:.1f}x" if real_pe > 0 else "N/A",
                         delta=f"{distortion.get('pe_gap', 0):.1f}% gap" if distortion.get('pe_gap') else None)
            with dist_cols[2]:
                st.metric("Distortion Score", f"{distortion.get('distortion_score', 0):.0f}/100")

            st.markdown("---")
            st.markdown("<div class='subsection-header'>Earnings Quality</div>", unsafe_allow_html=True)

            qual_cols = st.columns(3)
            with qual_cols[0]:
                st.metric("Quality Score", f"{quality.get('quality_score', 50):.0f}/100")
            with qual_cols[1]:
                cash_conv = quality.get('cash_conversion')
                st.metric("Cash Conversion", f"{cash_conv:.1f}%" if cash_conv else "N/A")
            with qual_cols[2]:
                accrual = quality.get('accrual_ratio')
                st.metric("Accrual Ratio", f"{accrual:.1f}%" if accrual else "N/A")

            if quality.get('flags'):
                for flag in quality['flags']:
                    st.warning(f"⚠️ {flag}")

# ============================================================================
# TAB 2: FORENSIC LAB - Deep Distortion Analysis
# ============================================================================
with main_tabs[2]:
    st.markdown("<div class='section-header'>🔬 Forensic Laboratory</div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style='background: {THEME["bg_card"]}; border: 1px solid {THEME["border"]}; border-radius: 8px; padding: 16px; margin-bottom: 20px;'>
        <div style='font-size: 14px; color: {THEME["text_primary"]}; font-weight: 600;'>The Distortion Thesis</div>
        <div style='font-size: 13px; color: {THEME["text_secondary"]}; margin-top: 8px;'>
            Identify stocks where GAAP earnings are distorted by one-time items (restructuring, write-offs, litigation).
            When Real P/E is significantly lower than GAAP P/E, you may have found hidden value.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Forensic scanner
    forensic_ticker = st.text_input("Enter ticker for deep forensic scan", placeholder="AAPL", key="forensic_ticker").upper()

    if st.button("🔬 RUN FORENSIC SCAN", use_container_width=True) and forensic_ticker:
        f_info = DataEngine.get_info(forensic_ticker)
        f_financials = DataEngine.get_financials(forensic_ticker)
        f_hist = DataEngine.get_history(forensic_ticker, period='2y')

        if f_info and f_financials:
            # Distortion analysis
            f_distortion = ForensicLab.analyze_distortion(forensic_ticker, f_info, f_financials)
            f_quality = ForensicLab.calculate_quality_of_earnings(forensic_ticker, f_financials)

            # Display results
            st.markdown("---")
            st.markdown(f"<div style='font-size: 24px; font-weight: 800; color: {THEME['text_primary']};'>{f_info.get('longName', forensic_ticker)}</div>", unsafe_allow_html=True)

            # Distortion verdict
            if f_distortion.get('has_distortion'):
                st.markdown(f"""
                <div class='opportunity-card'>
                    <div style='font-size: 18px; font-weight: 700; color: {THEME["opportunity"]};'>🎯 DISTORTED VALUE OPPORTUNITY</div>
                    <div style='font-size: 14px; color: {THEME["text_secondary"]}; margin-top: 12px;'>
                        Real earnings power is {f_distortion.get('pe_gap', 0):.1f}% higher than GAAP suggests.
                        This stock may be undervalued due to accounting noise.
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class='metric-card'>
                    <div style='font-size: 16px; font-weight: 600; color: {THEME["text_primary"]};'>📊 No Significant Distortion Detected</div>
                    <div style='font-size: 13px; color: {THEME["text_secondary"]}; margin-top: 8px;'>
                        GAAP earnings appear to reflect true earnings power.
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # Metrics
            f_cols = st.columns(4)
            f_cols[0].metric("GAAP P/E", f"{f_distortion.get('gaap_pe', 0):.1f}x" if f_distortion.get('gaap_pe') else "N/A")
            f_cols[1].metric("Real P/E", f"{f_distortion.get('real_pe', 0):.1f}x" if f_distortion.get('real_pe') else "N/A")
            f_cols[2].metric("P/E Gap", f"{f_distortion.get('pe_gap', 0):.1f}%")
            f_cols[3].metric("Distortion Score", f"{f_distortion.get('distortion_score', 0):.0f}")

            # Adjustments breakdown
            if f_distortion.get('adjustments'):
                st.markdown("<div class='subsection-header'>One-Time Items Detected</div>", unsafe_allow_html=True)
                for adj_type, adj_value in f_distortion['adjustments']:
                    st.markdown(f"""
                    <div class='metric-card' style='display: flex; justify-content: space-between; padding: 12px;'>
                        <span style='color: {THEME["text_secondary"]};'>{adj_type}</span>
                        <span style='font-weight: 700; color: {THEME["opportunity"]};'>{format_large_number(adj_value)}</span>
                    </div>
                    """, unsafe_allow_html=True)

            # Quality analysis
            st.markdown("---")
            st.markdown("<div class='subsection-header'>Earnings Quality Analysis</div>", unsafe_allow_html=True)

            q_cols = st.columns(3)
            q_cols[0].metric("Quality Score", f"{f_quality.get('quality_score', 50):.0f}/100")
            cash_conv = f_quality.get('cash_conversion')
            q_cols[1].metric("Cash Conversion", f"{cash_conv:.1f}%" if cash_conv else "N/A",
                            delta="Strong" if cash_conv and cash_conv > 100 else "Weak" if cash_conv and cash_conv < 80 else None)
            accrual = f_quality.get('accrual_ratio')
            q_cols[2].metric("Accrual Ratio", f"{accrual:.1f}%" if accrual else "N/A")

            if f_quality.get('flags'):
                st.markdown("<div class='danger-alert'>", unsafe_allow_html=True)
                for flag in f_quality['flags']:
                    st.markdown(f"⚠️ {flag}")
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.error(f"Could not find data for {forensic_ticker}")

# ============================================================================
# TAB 3: RETAIL EDGE ENGINES
# ============================================================================
with main_tabs[3]:
    st.markdown("<div class='section-header'>⚡ Retail Edge Engines</div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(255, 109, 0, 0.1)); border: 1px solid {THEME["border"]}; border-radius: 8px; padding: 16px; margin-bottom: 20px;'>
        <div style='font-size: 14px; color: {THEME["text_primary"]}; font-weight: 600;'>Unfair Advantages for Retail Investors</div>
        <div style='font-size: 13px; color: {THEME["text_secondary"]}; margin-top: 8px;'>
            Volume profile analysis, whale tracking, gamma squeeze detection, and correlation analysis.
        </div>
    </div>
    """, unsafe_allow_html=True)

    edge_ticker = st.text_input("Enter ticker for edge analysis", placeholder="GME", key="edge_ticker").upper()

    if st.button("⚡ RUN EDGE ANALYSIS", use_container_width=True) and edge_ticker:
        e_info = DataEngine.get_info(edge_ticker)
        e_hist = DataEngine.get_history(edge_ticker, period='1y')
        e_inst = DataEngine.get_institutional_holders(edge_ticker)
        e_insider = DataEngine.get_insider_transactions(edge_ticker)
        e_options = DataEngine.get_options_chain(edge_ticker)

        if e_info and not e_hist.empty:
            current_price = e_info.get('currentPrice', e_hist['Close'].iloc[-1])

            st.markdown(f"<div style='font-size: 24px; font-weight: 800; margin: 20px 0;'>{e_info.get('longName', edge_ticker)} - ${current_price:.2f}</div>", unsafe_allow_html=True)

            # Create subtabs for each engine
            edge_tabs = st.tabs(["🎒 BAGHOLDER DETECTOR", "🐋 WHALE WATCHER", "🚀 GAMMA RADAR", "📊 REALITY CHECK"])

            # BAGHOLDER DETECTOR
            with edge_tabs[0]:
                st.markdown("<div class='subsection-header'>Volume Profile Analysis</div>", unsafe_allow_html=True)

                bagholder = RetailEdgeEngine.bagholder_detector(e_hist)

                risk_color = THEME['bearish'] if bagholder['current_risk'] in ['CRITICAL', 'HIGH'] else THEME['warning'] if bagholder['current_risk'] == 'MODERATE' else THEME['bullish']

                st.markdown(f"""
                <div class='metric-card' style='text-align: center; padding: 24px;'>
                    <div style='font-size: 12px; color: {THEME["text_muted"]}; text-transform: uppercase;'>Overhead Supply Risk</div>
                    <div style='font-size: 36px; font-weight: 800; color: {risk_color}; margin: 12px 0;'>{bagholder['current_risk']}</div>
                    <div style='font-size: 14px; color: {THEME["text_secondary"]};'>Risk Score: {bagholder['risk_score']}/100</div>
                </div>
                """, unsafe_allow_html=True)

                if bagholder['overhead_supply_zones']:
                    st.markdown("<div class='danger-alert'>", unsafe_allow_html=True)
                    st.markdown(f"**{len(bagholder['overhead_supply_zones'])} overhead supply zones detected!**")
                    st.markdown("Heavy volume was traded at these price levels - expect resistance:")
                    for zone in bagholder['overhead_supply_zones'][:3]:
                        st.markdown(f"${zone['price_low']:.2f} - ${zone['price_high']:.2f} (strength: {zone['strength']:.1f}x)")
                    st.markdown("</div>", unsafe_allow_html=True)

                if bagholder['support_zones']:
                    st.markdown("<div class='whale-alert'>", unsafe_allow_html=True)
                    st.markdown(f"**{len(bagholder['support_zones'])} support zones detected:**")
                    for zone in bagholder['support_zones'][:3]:
                        st.markdown(f"${zone['price_low']:.2f} - ${zone['price_high']:.2f}")
                    st.markdown("</div>", unsafe_allow_html=True)

            # WHALE WATCHER
            with edge_tabs[1]:
                st.markdown("<div class='subsection-header'>Institutional & Insider Activity</div>", unsafe_allow_html=True)

                whale = RetailEdgeEngine.whale_watcher(edge_ticker, e_info, e_inst, e_insider)

                whale_cols = st.columns(3)
                whale_cols[0].metric("Whale Score", f"{whale['whale_score']}/100")
                whale_cols[1].metric("Insider Signal", whale['insider_signal'])
                whale_cols[2].metric("Combined Signal", whale['combined_signal'])

                if whale['combined_signal'] == 'WHALE ACCUMULATION':
                    st.markdown(f"""
                    <div class='opportunity-card'>
                        <div style='font-size: 16px; font-weight: 700; color: {THEME["opportunity"]};'>WHALE ACCUMULATION DETECTED</div>
                        <div style='color: {THEME["text_secondary"]}; margin-top: 8px;'>
                            Smart money is buying. Insider buys: {whale['recent_insider_buys']}, Sells: {whale['recent_insider_sells']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                elif whale['combined_signal'] == 'WHALE DISTRIBUTION':
                    st.markdown(f"""
                    <div class='danger-alert'>
                        <div style='font-size: 16px; font-weight: 700; color: {THEME["bearish"]};'>WHALE DISTRIBUTION DETECTED</div>
                        <div style='color: {THEME["text_secondary"]}; margin-top: 8px;'>
                            Insiders are selling. Be cautious.
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                # Notable transactions
                if whale['notable_transactions']:
                    st.markdown("<div class='subsection-header'>Recent Insider Activity</div>", unsafe_allow_html=True)
                    for tx in whale['notable_transactions']:
                        st.markdown(f"""
                        <div class='metric-card' style='padding: 12px; margin: 4px 0;'>
                            <div style='font-weight: 600;'>{tx.get('insider', 'Unknown')}</div>
                            <div style='font-size: 12px; color: {THEME["text_secondary"]};'>{tx.get('action', 'Unknown')}</div>
                        </div>
                        """, unsafe_allow_html=True)

            # GAMMA SQUEEZE RADAR
            with edge_tabs[2]:
                st.markdown("<div class='subsection-header'>Options Flow Analysis</div>", unsafe_allow_html=True)

                gamma = RetailEdgeEngine.gamma_squeeze_radar(e_options, current_price)

                squeeze_color = THEME['opportunity'] if gamma['squeeze_potential'] == 'HIGH' else THEME['warning'] if gamma['squeeze_potential'] == 'MODERATE' else THEME['text_secondary']

                st.markdown(f"""
                <div class='metric-card' style='text-align: center; padding: 24px;'>
                    <div style='font-size: 12px; color: {THEME["text_muted"]}; text-transform: uppercase;'>Gamma Squeeze Potential</div>
                    <div style='font-size: 36px; font-weight: 800; color: {squeeze_color}; margin: 12px 0;'>{gamma['squeeze_potential']}</div>
                    <div style='font-size: 14px; color: {THEME["text_secondary"]};'>Score: {gamma['squeeze_score']}/100</div>
                </div>
                """, unsafe_allow_html=True)

                g_cols = st.columns(3)
                g_cols[0].metric("Call/Put Ratio", f"{gamma['call_put_ratio']:.2f}" if gamma['call_put_ratio'] else "N/A")
                g_cols[1].metric("Max Pain", f"${gamma['max_pain']:.2f}" if gamma['max_pain'] else "N/A")
                g_cols[2].metric("Current Price", f"${current_price:.2f}")

                if gamma['hot_strikes']:
                    st.markdown("<div class='subsection-header'>Hot Strikes (High OI Near Money)</div>", unsafe_allow_html=True)
                    for strike in gamma['hot_strikes']:
                        iv_pct = strike.get('implied_vol', 0) * 100
                        st.markdown(f"""
                        <div class='metric-card' style='display: flex; justify-content: space-between; padding: 10px; margin: 4px 0;'>
                            <span style='font-weight: 700;'>${strike['strike']:.0f} {strike['type']}</span>
                            <span style='color: {THEME["text_secondary"]};'>OI: {strike['open_interest']:,.0f} | IV: {iv_pct:.0f}%</span>
                        </div>
                        """, unsafe_allow_html=True)

            # REALITY CHECK
            with edge_tabs[3]:
                st.markdown("<div class='subsection-header'>Correlation Analysis</div>", unsafe_allow_html=True)

                reality = RetailEdgeEngine.reality_check(edge_ticker)

                alpha_color = THEME['bullish'] if reality['alpha_potential'] == 'HIGH' else THEME['warning'] if reality['alpha_potential'] == 'MODERATE' else THEME['text_secondary']

                st.markdown(f"""
                <div class='metric-card' style='text-align: center; padding: 24px;'>
                    <div style='font-size: 12px; color: {THEME["text_muted"]}; text-transform: uppercase;'>Alpha Potential</div>
                    <div style='font-size: 28px; font-weight: 800; color: {alpha_color}; margin: 12px 0;'>{reality['alpha_potential']}</div>
                    <div style='font-size: 14px; color: {THEME["text_secondary"]};'>Idiosyncratic Score: {reality['idiosyncratic_score']:.0f}/100</div>
                </div>
                """, unsafe_allow_html=True)

                r_cols = st.columns(3)
                r_cols[0].metric("SPY Correlation", f"{reality['spy_correlation']:.2f}" if reality['spy_correlation'] else "N/A")
                r_cols[1].metric("BTC Correlation", f"{reality['btc_correlation']:.2f}" if reality['btc_correlation'] else "N/A")
                r_cols[2].metric("Beta", f"{reality['beta']:.2f}" if reality['beta'] else "N/A")

                if reality['spy_correlation'] and abs(reality['spy_correlation']) < 0.5:
                    st.markdown(f"""
                    <div class='opportunity-card'>
                        <div style='font-weight: 700; color: {THEME["opportunity"]};'>LOW MARKET CORRELATION</div>
                        <div style='color: {THEME["text_secondary"]}; margin-top: 8px;'>
                            This stock moves independently from the market - potential alpha generator.
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.error(f"Could not load data for {edge_ticker}")

# ============================================================================
# TAB 5: MULTI-ASSET COMPARISON
# ============================================================================
with main_tabs[4]:
    st.markdown("<div class='section-header'>📊 Multi-Asset Comparison</div>", unsafe_allow_html=True)

    ma_cols = st.columns([3, 1])
    with ma_cols[0]:
        multi_tickers = st.text_input("Enter tickers (comma-separated)", "SPY, QQQ, AAPL, NVDA, BTC-USD", key="multi_tickers")
    with ma_cols[1]:
        multi_period = st.selectbox("Period", ['1M', '3M', '6M', '1Y', '2Y', '5Y'], index=3, key="multi_period")

    if st.button("📊 COMPARE", use_container_width=True):
        tickers = [t.strip().upper() for t in multi_tickers.split(",") if t.strip()]
        period_map = {'1M': '1mo', '3M': '3mo', '6M': '6mo', '1Y': '1y', '2Y': '2y', '5Y': '5y'}
        try:
            data_df = yf.download(tickers, period=period_map[multi_period], progress=False)['Close']
            if isinstance(data_df, pd.Series):
                data_df = data_df.to_frame(name=tickers[0])

            # Drop columns with all NaN and forward fill missing values
            data_df = data_df.dropna(axis=1, how='all')
            data_df = data_df.ffill().bfill()

            if data_df.empty:
                st.error("No data available for the selected tickers")
            else:
                # Normalize to base 100
                first_valid = data_df.iloc[0]
                normalized = (data_df / first_valid) * 100

                # Chart with professional colors
                fig = go.Figure()
                chart_colors = ['#3b82f6', '#22c55e', '#f59e0b', '#ec4899', '#8b5cf6', '#06b6d4', '#ef4444', '#84cc16']

                for idx, col in enumerate(normalized.columns):
                    color = chart_colors[idx % len(chart_colors)]
                    fig.add_trace(go.Scatter(
                        x=normalized.index,
                        y=normalized[col],
                        mode='lines',
                        name=str(col),
                        line=dict(color=color, width=2.5),
                        hovertemplate=f'<b>{col}</b><br>%{{x|%b %d, %Y}}<br>Return: %{{y:.1f}}%<extra></extra>'
                    ))

                fig.update_layout(
                    height=500,
                    plot_bgcolor=THEME['bg_primary'],
                    paper_bgcolor=THEME['bg_primary'],
                    font=dict(color=THEME['text_primary'], family='Inter'),
                    hovermode='x unified',
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
                    margin=dict(l=60, r=20, t=40, b=40),
                    yaxis_title='Normalized Performance (Base = 100)',
                )
                fig.update_xaxes(showgrid=True, gridcolor=THEME['chart_grid'], gridwidth=1)
                fig.update_yaxes(showgrid=True, gridcolor=THEME['chart_grid'], gridwidth=1)

                # Add 100 baseline
                fig.add_hline(y=100, line_dash="dash", line_color=THEME['text_muted'], opacity=0.5)

                st.plotly_chart(fig, use_container_width=True)

                # Performance table with proper NaN handling
                perf_data = []
                for col in data_df.columns:
                    first_price = data_df[col].iloc[0]
                    last_price = data_df[col].iloc[-1]

                    if pd.notna(first_price) and pd.notna(last_price) and first_price > 0:
                        total_ret = ((last_price / first_price) - 1) * 100
                        ret_str = f"{total_ret:+.2f}%"
                        curr_str = f"${last_price:,.2f}"
                    else:
                        ret_str = "N/A"
                        curr_str = "N/A"

                    perf_data.append({
                        'Asset': str(col),
                        'Current Price': curr_str,
                        'Period Return': ret_str
                    })

                # Sort by return
                perf_df = pd.DataFrame(perf_data)
                st.dataframe(perf_df, use_container_width=True, hide_index=True)

        except Exception as e:
            st.error(f"Error loading data: {str(e)}")

# ============================================================================
# TAB 6: MACRO DASHBOARD
# ============================================================================
with main_tabs[5]:
    st.markdown("<div class='section-header'>🌍 Global Macro Dashboard</div>", unsafe_allow_html=True)

    # Market indicators
    st.markdown("<div class='subsection-header'>Key Market Indicators</div>", unsafe_allow_html=True)

    if st.button("🔄 REFRESH MACRO DATA", use_container_width=True):
        st.session_state['fg_data'] = calculate_fear_greed()
        st.cache_data.clear()

    macro_indicators = {
        'VIX': '^VIX',
        '10Y Yield': '^TNX',
        'US Dollar': 'DX-Y.NYB',
        'Gold': 'GC=F',
        'Oil (WTI)': 'CL=F',
        'Bitcoin': 'BTC-USD'
    }

    macro_cols = st.columns(3)
    for i, (name, symbol) in enumerate(macro_indicators.items()):
        with macro_cols[i % 3]:
            try:
                m_data = yf.Ticker(symbol).history(period="5d")
                if len(m_data) > 0:
                    curr = m_data['Close'].iloc[-1]
                    prev = m_data['Close'].iloc[0]
                    chg = ((curr / prev) - 1) * 100
                    chg_color = '#22c55e' if chg >= 0 else '#ef4444'

                    st.markdown(f"""
                    <div class='metric-card' style='text-align: center; margin: 8px 0;'>
                        <div style='font-size: 11px; color: {THEME["text_muted"]}; text-transform: uppercase;'>{name}</div>
                        <div style='font-size: 24px; font-weight: 700; color: {THEME["text_primary"]}; margin: 8px 0;'>{curr:,.2f}</div>
                        <div style='font-size: 13px; font-weight: 600; color: {chg_color};'>{chg:+.2f}%</div>
                    </div>
                    """, unsafe_allow_html=True)
            except:
                st.markdown(f"""
                <div class='metric-card' style='text-align: center; margin: 8px 0;'>
                    <div style='font-size: 11px; color: {THEME["text_muted"]};'>{name}</div>
                    <div style='font-size: 18px; color: {THEME["text_muted"]}; margin: 8px 0;'>--</div>
                </div>
                """, unsafe_allow_html=True)

    # Fear & Greed Index - Comprehensive Display
    st.markdown("---")
    st.markdown("<div class='section-header'>📊 Fear & Greed Index (10 Indicators)</div>", unsafe_allow_html=True)

    fg = st.session_state['fg_data']
    fg_score = fg.get('score', 50)

    # Color based on score
    if fg_score >= 65: fg_color = '#22c55e'
    elif fg_score >= 55: fg_color = '#84cc16'
    elif fg_score >= 45: fg_color = '#eab308'
    elif fg_score >= 35: fg_color = '#f97316'
    else: fg_color = '#ef4444'

    # Main score display
    col_score, col_gauge = st.columns([1, 2])

    with col_score:
        st.markdown(f"""
        <div style='background: {THEME["bg_card"]}; border: 2px solid {fg_color}; border-radius: 12px; padding: 28px; text-align: center;'>
            <div style='font-size: 11px; color: {THEME["text_muted"]}; text-transform: uppercase; letter-spacing: 0.15em;'>Overall Sentiment</div>
            <div style='font-size: 56px; font-weight: 900; color: {fg_color}; margin: 12px 0;'>{fg_score:.0f}</div>
            <div style='font-size: 18px; font-weight: 700; color: {fg_color};'>{fg.get('label', 'Neutral')}</div>
            <div style='font-size: 11px; color: {THEME["text_muted"]}; margin-top: 12px;'>
                Based on {fg.get('num_indicators', 0)} indicators
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_gauge:
        # Create gauge chart
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=fg_score,
            domain={'x': [0, 1], 'y': [0, 1]},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': THEME['text_muted']},
                'bar': {'color': fg_color},
                'bgcolor': THEME['bg_card'],
                'borderwidth': 0,
                'steps': [
                    {'range': [0, 20], 'color': 'rgba(239, 68, 68, 0.3)'},
                    {'range': [20, 40], 'color': 'rgba(249, 115, 22, 0.3)'},
                    {'range': [40, 60], 'color': 'rgba(234, 179, 8, 0.3)'},
                    {'range': [60, 80], 'color': 'rgba(132, 204, 22, 0.3)'},
                    {'range': [80, 100], 'color': 'rgba(34, 197, 94, 0.3)'},
                ],
                'threshold': {
                    'line': {'color': fg_color, 'width': 4},
                    'thickness': 0.75,
                    'value': fg_score
                }
            },
            number={'font': {'size': 40, 'color': fg_color}}
        ))
        fig_gauge.update_layout(
            height=200,
            margin=dict(l=20, r=20, t=30, b=10),
            paper_bgcolor=THEME['bg_primary'],
            font=dict(color=THEME['text_primary'])
        )
        st.plotly_chart(fig_gauge, use_container_width=True, config={'displayModeBar': False})

    # Individual indicators breakdown
    fg_indicators = fg.get('indicators', {})

    if fg_indicators:
        st.markdown("<div class='subsection-header'>Indicator Breakdown</div>", unsafe_allow_html=True)

        # Create 2 rows of 5 indicators
        indicator_keys = list(fg_indicators.keys())
        rows = [indicator_keys[i:i+5] for i in range(0, len(indicator_keys), 5)]

        for row_keys in rows:
            cols = st.columns(len(row_keys))
            for col, key in zip(cols, row_keys):
                ind = fg_indicators.get(key, {})
                # Handle case where ind might not be a dict
                if not isinstance(ind, dict):
                    ind = {'score': 50, 'value': 0, 'label': key}
                ind_score = ind.get('score', 50)
                ind_value = ind.get('value', 0)
                ind_label = ind.get('label', key)

                # Color based on score
                if ind_score >= 65: ind_color = '#22c55e'
                elif ind_score >= 45: ind_color = '#eab308'
                else: ind_color = '#ef4444'

                # Determine if value should show % or not
                value_str = f"{ind_value:+.1f}%" if abs(ind_value) < 100 else f"{ind_value:.1f}"

                col.markdown(f"""
                <div class='metric-card' style='text-align: center; padding: 12px;'>
                    <div style='font-size: 10px; color: {THEME["text_muted"]}; text-transform: uppercase; margin-bottom: 6px;'>{ind_label}</div>
                    <div style='font-size: 24px; font-weight: 800; color: {ind_color};'>{ind_score:.0f}</div>
                    <div style='font-size: 11px; color: {THEME["text_secondary"]}; margin-top: 4px;'>{value_str}</div>
                </div>
                """, unsafe_allow_html=True)

        # Legend
        st.markdown(f"""
        <div style='display: flex; justify-content: center; gap: 20px; margin-top: 16px; flex-wrap: wrap;'>
            <span style='font-size: 11px;'><span style='color: #ef4444;'>●</span> Extreme Fear (0-20)</span>
            <span style='font-size: 11px;'><span style='color: #f97316;'>●</span> Fear (20-40)</span>
            <span style='font-size: 11px;'><span style='color: #eab308;'>●</span> Neutral (40-60)</span>
            <span style='font-size: 11px;'><span style='color: #84cc16;'>●</span> Greed (60-80)</span>
            <span style='font-size: 11px;'><span style='color: #22c55e;'>●</span> Extreme Greed (80-100)</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Click 'Refresh Macro Data' to load Fear & Greed indicators")

# ============================================================================
# TAB 6: STOCK SIMULATOR GAME
# ============================================================================
# TAB 6: STOCK SIMULATOR
# ============================================================================
with main_tabs[6]:
    st.markdown(f"""
    <div style='text-align: center; padding: 20px 0; border-bottom: 1px solid {THEME["border"]}; margin-bottom: 30px;'>
        <div style='font-size: 32px; font-weight: 800; color: {THEME["text_primary"]}; letter-spacing: -0.02em;'>TIME MACHINE</div>
        <div style='font-size: 12px; color: {THEME["text_muted"]}; letter-spacing: 0.15em; margin-top: 5px;'>HISTORICAL STOCK TRADING SIMULATOR</div>
    </div>
    """, unsafe_allow_html=True)

    # Initialize sim state if needed
    if 'sim_started' not in st.session_state:
        st.session_state['sim_started'] = False
    if 'sim_cash' not in st.session_state:
        st.session_state['sim_cash'] = 100000.0
    if 'sim_holdings' not in st.session_state:
        st.session_state['sim_holdings'] = {}
    if 'sim_trades' not in st.session_state:
        st.session_state['sim_trades'] = []

    # Helper function to get price (cached for speed)
    @st.cache_data(ttl=600, show_spinner=False)
    def get_sim_price(ticker: str, date_str: str):
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d')
            start = (date - timedelta(days=10)).strftime('%Y-%m-%d')
            end = (date + timedelta(days=1)).strftime('%Y-%m-%d')
            data = yf.Ticker(ticker).history(start=start, end=end)
            if not data.empty:
                return float(data['Close'].iloc[-1])
        except:
            pass
        return None

    if not st.session_state.get('sim_started'):
        # START SCREEN
        st.markdown(f"<div style='color: {THEME['text_secondary']}; font-size: 14px; margin-bottom: 20px;'>Pick a date, get $100K, and see if you can beat the market.</div>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Travel to", value=datetime(2020, 3, 23), min_value=datetime(2010, 1, 1), max_value=datetime.now() - timedelta(days=30))
        with col2:
            start_capital = st.selectbox("Starting cash", [50000, 100000, 250000, 500000], index=1, format_func=lambda x: f"${x:,}")

        if st.button("START SIMULATION", use_container_width=True, type="primary"):
            st.session_state['sim_started'] = True
            st.session_state['sim_date'] = datetime.combine(start_date, datetime.min.time())
            st.session_state['sim_start_date'] = datetime.combine(start_date, datetime.min.time())
            st.session_state['sim_cash'] = float(start_capital)
            st.session_state['sim_initial'] = float(start_capital)
            st.session_state['sim_holdings'] = {}
            st.session_state['sim_trades'] = []
            st.rerun()

        # Quick start suggestions
        st.markdown(f"<div style='margin-top: 30px; padding-top: 20px; border-top: 1px solid {THEME['border']};'></div>", unsafe_allow_html=True)
        st.markdown(f"<div style='color: {THEME['text_muted']}; font-size: 11px; margin-bottom: 10px;'>NOTABLE DATES</div>", unsafe_allow_html=True)
        dates_col = st.columns(4)
        notable = [("Mar 2020", "COVID bottom"), ("Jan 2023", "AI boom"), ("Mar 2009", "GFC bottom"), ("Jan 2015", "Pre-Tesla run")]
        for i, (d, desc) in enumerate(notable):
            with dates_col[i]:
                st.markdown(f"<div style='background: {THEME['card_bg']}; padding: 10px; border-radius: 4px; border: 1px solid {THEME['border']};'><div style='color: {THEME['text_primary']}; font-weight: 600;'>{d}</div><div style='color: {THEME['text_muted']}; font-size: 10px;'>{desc}</div></div>", unsafe_allow_html=True)

    else:
        # ACTIVE GAME
        current_date = st.session_state.get('sim_date', datetime.now())
        cash = st.session_state.get('sim_cash', 100000)
        holdings = st.session_state.get('sim_holdings', {})
        initial = st.session_state.get('sim_initial', 100000)

        # Calculate total value
        total_value = cash
        prices = {}
        date_str = current_date.strftime('%Y-%m-%d')
        for ticker, shares in holdings.items():
            p = get_sim_price(ticker, date_str)
            if p:
                prices[ticker] = p
                total_value += shares * p

        pnl = total_value - initial
        pnl_pct = (pnl / initial) * 100 if initial > 0 else 0

        # STATUS BAR
        st.markdown(f"""
        <div style='display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 25px;'>
            <div style='background: {THEME["card_bg"]}; padding: 15px; border-radius: 4px; border: 1px solid {THEME["border"]};'>
                <div style='color: {THEME["text_muted"]}; font-size: 10px; text-transform: uppercase;'>Date</div>
                <div style='color: {THEME["text_primary"]}; font-size: 18px; font-weight: 700;'>{current_date.strftime('%b %d, %Y')}</div>
            </div>
            <div style='background: {THEME["card_bg"]}; padding: 15px; border-radius: 4px; border: 1px solid {THEME["border"]};'>
                <div style='color: {THEME["text_muted"]}; font-size: 10px; text-transform: uppercase;'>Cash</div>
                <div style='color: {THEME["text_primary"]}; font-size: 18px; font-weight: 700;'>${cash:,.0f}</div>
            </div>
            <div style='background: {THEME["card_bg"]}; padding: 15px; border-radius: 4px; border: 1px solid {THEME["border"]};'>
                <div style='color: {THEME["text_muted"]}; font-size: 10px; text-transform: uppercase;'>Portfolio</div>
                <div style='color: {THEME["text_primary"]}; font-size: 18px; font-weight: 700;'>${total_value:,.0f}</div>
            </div>
            <div style='background: {THEME["card_bg"]}; padding: 15px; border-radius: 4px; border: 1px solid {THEME["border"]};'>
                <div style='color: {THEME["text_muted"]}; font-size: 10px; text-transform: uppercase;'>Return</div>
                <div style='color: {"#fff" if pnl_pct >= 0 else "#888"}; font-size: 18px; font-weight: 700;'>{pnl_pct:+.1f}%</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # TIME CONTROLS
        st.markdown(f"<div style='color: {THEME['text_muted']}; font-size: 10px; margin-bottom: 8px;'>FAST FORWARD</div>", unsafe_allow_html=True)
        tcol = st.columns(6)
        with tcol[0]:
            if st.button("+1 DAY", use_container_width=True):
                st.session_state['sim_date'] += timedelta(days=1)
                st.rerun()
        with tcol[1]:
            if st.button("+1 WEEK", use_container_width=True):
                st.session_state['sim_date'] += timedelta(weeks=1)
                st.rerun()
        with tcol[2]:
            if st.button("+1 MONTH", use_container_width=True):
                st.session_state['sim_date'] += timedelta(days=30)
                st.rerun()
        with tcol[3]:
            if st.button("+6 MONTHS", use_container_width=True):
                st.session_state['sim_date'] += timedelta(days=180)
                st.rerun()
        with tcol[4]:
            if st.button("+1 YEAR", use_container_width=True):
                st.session_state['sim_date'] += timedelta(days=365)
                st.rerun()
        with tcol[5]:
            if st.button("TODAY", use_container_width=True):
                st.session_state['sim_date'] = datetime.now() - timedelta(days=1)
                st.rerun()

        st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)

        # TRADING + HOLDINGS
        left, right = st.columns([3, 2])

        with left:
            st.markdown(f"<div style='color: {THEME['text_muted']}; font-size: 10px; margin-bottom: 10px;'>TRADE</div>", unsafe_allow_html=True)

            # Stock lookup
            lookup_ticker = st.text_input("Ticker", placeholder="AAPL, NVDA, TSLA...", label_visibility="collapsed").upper().strip()

            if lookup_ticker:
                price = get_sim_price(lookup_ticker, date_str)
                if price:
                    owned = holdings.get(lookup_ticker, 0)
                    max_buy = int(cash / price) if price > 0 else 0

                    st.markdown(f"""
                    <div style='background: {THEME["card_bg"]}; padding: 15px; border-radius: 4px; border: 1px solid {THEME["border"]}; margin: 10px 0;'>
                        <div style='display: flex; justify-content: space-between; align-items: center;'>
                            <div>
                                <span style='color: {THEME["text_primary"]}; font-size: 20px; font-weight: 700;'>{lookup_ticker}</span>
                                <span style='color: {THEME["text_muted"]}; font-size: 12px; margin-left: 10px;'>{current_date.strftime('%b %d, %Y')}</span>
                            </div>
                            <div style='color: {THEME["text_primary"]}; font-size: 24px; font-weight: 700;'>${price:.2f}</div>
                        </div>
                        <div style='color: {THEME["text_muted"]}; font-size: 11px; margin-top: 8px;'>You own: {owned} shares | Can buy: {max_buy} shares</div>
                    </div>
                    """, unsafe_allow_html=True)

                    # Chart
                    try:
                        chart_start = (current_date - timedelta(days=90)).strftime('%Y-%m-%d')
                        chart_end = (current_date + timedelta(days=1)).strftime('%Y-%m-%d')
                        chart_data = yf.Ticker(lookup_ticker).history(start=chart_start, end=chart_end)
                        if not chart_data.empty:
                            fig = go.Figure()
                            fig.add_trace(go.Scatter(x=chart_data.index, y=chart_data['Close'], mode='lines', line=dict(color='#ffffff', width=1.5), fill='tozeroy', fillcolor='rgba(255,255,255,0.05)'))
                            fig.update_layout(height=180, margin=dict(l=0,r=0,t=10,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(showgrid=False, showticklabels=False), yaxis=dict(showgrid=False, showticklabels=False), hovermode='x')
                            st.plotly_chart(fig, use_container_width=True)
                    except:
                        pass

                    # Buy/Sell
                    bcol, scol = st.columns(2)
                    with bcol:
                        buy_qty = st.number_input("Buy qty", min_value=0, max_value=max_buy, value=min(10, max_buy), label_visibility="collapsed", key="buy_qty")
                        if st.button(f"BUY {buy_qty}", use_container_width=True, type="primary", disabled=buy_qty == 0):
                            cost = buy_qty * price
                            st.session_state['sim_cash'] -= cost
                            st.session_state['sim_holdings'][lookup_ticker] = holdings.get(lookup_ticker, 0) + buy_qty
                            st.session_state['sim_trades'].append({'date': current_date.strftime('%Y-%m-%d'), 'action': 'BUY', 'ticker': lookup_ticker, 'qty': buy_qty, 'price': price})
                            st.rerun()

                    with scol:
                        sell_qty = st.number_input("Sell qty", min_value=0, max_value=owned, value=min(10, owned) if owned > 0 else 0, label_visibility="collapsed", key="sell_qty")
                        if st.button(f"SELL {sell_qty}", use_container_width=True, disabled=sell_qty == 0 or owned == 0):
                            proceeds = sell_qty * price
                            st.session_state['sim_cash'] += proceeds
                            st.session_state['sim_holdings'][lookup_ticker] -= sell_qty
                            if st.session_state['sim_holdings'][lookup_ticker] <= 0:
                                del st.session_state['sim_holdings'][lookup_ticker]
                            st.session_state['sim_trades'].append({'date': current_date.strftime('%Y-%m-%d'), 'action': 'SELL', 'ticker': lookup_ticker, 'qty': sell_qty, 'price': price})
                            st.rerun()
                else:
                    st.warning(f"No data for {lookup_ticker} on this date")

        with right:
            st.markdown(f"<div style='color: {THEME['text_muted']}; font-size: 10px; margin-bottom: 10px;'>HOLDINGS (click to expand)</div>", unsafe_allow_html=True)

            if holdings:
                for ticker, shares in holdings.items():
                    p = prices.get(ticker, 0)
                    val = shares * p
                    cost_basis = 0
                    shares_bought = 0
                    for t in st.session_state.get('sim_trades', []):
                        if t['ticker'] == ticker and t['action'] == 'BUY':
                            cost_basis += t['qty'] * t['price']
                            shares_bought += t['qty']
                    avg_cost = cost_basis / shares_bought if shares_bought > 0 else p
                    gain_loss = (p - avg_cost) * shares
                    gain_pct = ((p - avg_cost) / avg_cost * 100) if avg_cost > 0 else 0
                    gl_color = THEME['green'] if gain_loss >= 0 else THEME['red']

                    with st.expander(f"{ticker} — {shares} shares — ${val:,.0f}"):
                        st.markdown(f"""
                        <div style='padding: 5px 0;'>
                            <div style='display: flex; justify-content: space-between; margin-bottom: 8px;'>
                                <span style='color: {THEME["text_muted"]};'>Current Price</span>
                                <span style='color: {THEME["text_primary"]}; font-weight: 600;'>${p:.2f}</span>
                            </div>
                            <div style='display: flex; justify-content: space-between; margin-bottom: 8px;'>
                                <span style='color: {THEME["text_muted"]};'>Avg Cost</span>
                                <span style='color: {THEME["text_primary"]};'>${avg_cost:.2f}</span>
                            </div>
                            <div style='display: flex; justify-content: space-between; margin-bottom: 8px;'>
                                <span style='color: {THEME["text_muted"]};'>Shares</span>
                                <span style='color: {THEME["text_primary"]};'>{shares}</span>
                            </div>
                            <div style='display: flex; justify-content: space-between; margin-bottom: 8px;'>
                                <span style='color: {THEME["text_muted"]};'>Market Value</span>
                                <span style='color: {THEME["text_primary"]}; font-weight: 600;'>${val:,.2f}</span>
                            </div>
                            <div style='display: flex; justify-content: space-between; padding-top: 8px; border-top: 1px solid {THEME["border"]};'>
                                <span style='color: {THEME["text_muted"]};'>Gain/Loss</span>
                                <span style='color: {gl_color}; font-weight: 700;'>{gain_pct:+.1f}% (${gain_loss:+,.0f})</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        if st.button(f"SELL ALL {ticker}", key=f"sell_all_{ticker}", use_container_width=True):
                            st.session_state['sim_cash'] += val
                            st.session_state['sim_trades'].append({'date': current_date.strftime('%Y-%m-%d'), 'action': 'SELL', 'ticker': ticker, 'qty': shares, 'price': p})
                            del st.session_state['sim_holdings'][ticker]
                            st.rerun()
            else:
                st.markdown(f"<div style='color: {THEME['text_muted']}; font-style: italic; padding: 20px 0;'>No positions yet</div>", unsafe_allow_html=True)

            # Trade log
            if st.session_state.get('sim_trades'):
                st.markdown(f"<div style='color: {THEME['text_muted']}; font-size: 10px; margin: 20px 0 10px 0;'>RECENT TRADES</div>", unsafe_allow_html=True)
                for t in reversed(st.session_state['sim_trades'][-5:]):
                    st.markdown(f"<div style='color: {THEME['text_muted']}; font-size: 11px; padding: 3px 0;'>{t['date']} {t['action']} {t['qty']} {t['ticker']} @ ${t['price']:.2f}</div>", unsafe_allow_html=True)

        # END GAME
        st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
        ecol1, ecol2, ecol3 = st.columns([1, 1, 2])
        with ecol1:
            if st.button("RESET", use_container_width=True):
                for key in ['sim_started', 'sim_date', 'sim_cash', 'sim_holdings', 'sim_trades', 'sim_initial', 'sim_start_date']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()
        with ecol2:
            if st.button("END GAME", use_container_width=True, type="primary"):
                days = (current_date - st.session_state.get('sim_start_date', current_date)).days
                years = max(days / 365, 0.01)
                annual = (((total_value / initial) ** (1/years)) - 1) * 100 if initial > 0 else 0
                st.balloons()
                st.markdown(f"""
                <div style='background: {THEME["card_bg"]}; padding: 30px; border-radius: 8px; text-align: center; border: 2px solid {THEME["border"]}; margin-top: 20px;'>
                    <div style='color: {THEME["text_muted"]}; font-size: 11px; text-transform: uppercase;'>Final Return</div>
                    <div style='color: {THEME["text_primary"]}; font-size: 48px; font-weight: 800; margin: 10px 0;'>{pnl_pct:+.1f}%</div>
                    <div style='color: {THEME["text_secondary"]}; font-size: 14px;'>${initial:,.0f} → ${total_value:,.0f}</div>
                    <div style='color: {THEME["text_muted"]}; font-size: 12px; margin-top: 10px;'>{days} days | {annual:+.1f}% annualized</div>
                </div>
                """, unsafe_allow_html=True)

# ============================================================================
# FOOTER
# ============================================================================
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; padding: 32px 0;'>
    <div style='font-size: 24px; font-weight: 800; background: linear-gradient(135deg, {THEME["accent_primary"]}, {THEME["opportunity"]}); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>
        MISPRICED MARKET
    </div>
    <div style='font-size: 11px; color: {THEME["text_muted"]}; letter-spacing: 0.15em; margin-top: 8px;'>
        FORENSIC INVESTMENT INTELLIGENCE
    </div>
    <div style='font-size: 10px; color: {THEME["text_muted"]}; margin-top: 16px;'>
        Data via yfinance | For research purposes only | Not financial advice
    </div>
</div>
""", unsafe_allow_html=True)

