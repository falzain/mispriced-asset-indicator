import yfinance as yf
from datetime import datetime

def get_stock_data(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info
    hist = stock.history(period="1y")
    
    return {
        'info': info,
        'price_history': hist,
        'ticker': ticker
    }

def get_fundamental_metrics(data):
    info = data['info']
    return {
        'revenue_growth': info.get('revenueGrowth', 0) * 100,
        'profit_margin': info.get('profitMargins', 0) * 100,
        'roe': info.get('returnOnEquity', 0) * 100,
        'debt_to_equity': info.get('debtToEquity', 0)
    }
def get_stock_data_with_interval(ticker, interval='1d', period='max'):
    """Get stock data with specific time intervals"""
    stock = yf.Ticker(ticker)
    hist = stock.history(period=period, interval=interval)
    return hist

def get_real_estate_data():
    """Placeholder for real estate data - we'll expand this"""
    # Will integrate Zillow API, Fred API for housing data
    return {
        'median_home_price': 0,
        'rental_yield': 0,
        'vacancy_rate': 0
    }

def get_alternative_assets():
    """Placeholder for alternative asset tracking"""
    # Will track: collectibles, NFTs, commodities, etc.
    return {
        'pokemon_cards': {},
        'collectibles': {},
        'commodities': {}
    }

def get_economic_indicators():
    """Economic statistics from FRED and other sources"""
    # Will pull: inflation, unemployment, GDP, interest rates
    return {
        'inflation_rate': 0,
        'unemployment': 0,
        'gdp_growth': 0
    }

def get_multi_asset_data(asset_types):
    """Fetch data for multiple asset classes"""
    data = {}
    
    # Stocks
    if 'stocks' in asset_types:
        data['stocks'] = {}
    
    # Real Estate
    if 'real_estate' in asset_types:
        data['real_estate'] = get_real_estate_data()
    
    # Alternatives
    if 'alternatives' in asset_types:
        data['alternatives'] = get_alternative_assets()
    
    # Economics
    if 'economics' in asset_types:
        data['economics'] = get_economic_indicators()
    
    return data
def get_historical_data_custom(ticker, period="max", interval="1d"):
    """Flexible historical data fetching with custom intervals"""
    stock = yf.Ticker(ticker)
    return stock.history(period=period, interval=interval)

def get_crypto_data(symbol):
    """Fetch crypto data (BTC-USD, ETH-USD, etc.)"""
    crypto = yf.Ticker(symbol)
    return {
        'info': crypto.info,
        'price_history': crypto.history(period="max"),
        'ticker': symbol
    }

def get_real_estate_etf_data():
    """Get real estate market proxy through REITs"""
    reit_etfs = ['VNQ', 'IYR', 'XLRE']
    data = {}
    for etf in reit_etfs:
        stock = yf.Ticker(etf)
        data[etf] = stock.history(period="max")
    return data

def get_commodity_data(commodity):
    """Fetch commodity prices (GC=F for gold, CL=F for oil, etc.)"""
    comm = yf.Ticker(commodity)
    return {
        'price_history': comm.history(period="max"),
        'ticker': commodity
    }

def get_multi_asset_data(tickers_dict):
    """
    Fetch multiple asset classes at once
    tickers_dict format: {'Equities': ['AAPL', 'MSFT'], 'Crypto': ['BTC-USD'], 'Commodities': ['GC=F']}
    """
    all_data = {}
    for asset_class, tickers in tickers_dict.items():
        all_data[asset_class] = {}
        for ticker in tickers:
            try:
                stock = yf.Ticker(ticker)
                all_data[asset_class][ticker] = stock.history(period="max")
            except:
                print(f"Failed to fetch {ticker}")
    return all_data