import anthropic
import json

def analyze_stock_with_ai(stock_data, fundamentals, api_key):
    """Deep AI analysis using Claude"""
    
    client = anthropic.Anthropic(api_key=api_key)
    
    info = stock_data['info']
    ticker = stock_data['ticker']
    news = stock_data.get('news', [])[:3]  # Latest 3 news items
    
    # Build comprehensive prompt
    news_summary = "\n".join([f"- {item.get('title', 'N/A')}" for item in news]) if news else "No recent news"
    
    prompt = f"""You are a professional equity analyst. Provide a comprehensive investment analysis for:

**Company:** {info.get('longName', ticker)} ({ticker})
**Sector:** {info.get('sector', 'N/A')} | **Industry:** {info.get('industry', 'N/A')}

**Current Metrics:**
- Price: ${info.get('currentPrice', 0):.2f}
- Market Cap: ${info.get('marketCap', 0)/1e9:.2f}B
- P/E: {info.get('trailingPE', 'N/A')} | Forward P/E: {info.get('forwardPE', 'N/A')}
- P/S: {info.get('priceToSalesTrailing12Months', 'N/A')}
- EV/EBITDA: {info.get('enterpriseToEbitda', 'N/A')}

**Growth & Profitability:**
- Revenue Growth: {fundamentals['revenue_growth']:.1f}%
- Earnings Growth: {fundamentals['earnings_growth']:.1f}%
- Profit Margin: {fundamentals['profit_margin']:.1f}%
- ROE: {fundamentals['roe']:.1f}%

**Financial Health:**
- Debt/Equity: {fundamentals['debt_to_equity']:.2f}
- Current Ratio: {fundamentals['current_ratio']:.2f}
- Free Cash Flow: ${fundamentals['free_cashflow']/1e9:.2f}B

**Recent News:**
{news_summary}

**Analyst Consensus:** {info.get('recommendationKey', 'N/A').upper()}
**Target Price:** ${info.get('targetMeanPrice', 0):.2f}

Provide:
1. **Business Quality** (3-4 sentences on competitive position, moat, industry dynamics)
2. **Financial Health** (2-3 sentences on balance sheet strength and cash generation)
3. **Growth Outlook** (3-4 sentences on growth drivers and sustainability)
4. **Valuation Assessment** (Is it cheap/fair/expensive relative to growth and quality?)
5. **Key Risks** (Top 3 specific risks)
6. **Investment Thesis** (2-3 sentences: why buy or avoid)
7. **Rating** (Strong Buy / Buy / Hold / Sell / Strong Sell with confidence level)

Be specific and quantitative where possible."""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return message.content[0].text

def get_comparative_analysis(tickers_data, api_key):
    """Compare multiple stocks using AI"""
    
    client = anthropic.Anthropic(api_key=api_key)
    
    comparison_text = ""
    for ticker, data in tickers_data.items():
        info = data['info']
        comparison_text += f"""
{ticker}: PE={info.get('trailingPE', 'N/A')}, Growth={info.get('revenueGrowth', 0)*100:.1f}%, 
Margin={info.get('profitMargins', 0)*100:.1f}%, ROE={info.get('returnOnEquity', 0)*100:.1f}%
"""
    
    prompt = f"""Compare these stocks and rank them for investment attractiveness:

{comparison_text}

Provide:
1. Ranking (best to worst with brief reasoning)
2. Which is best for growth investors?
3. Which is best for value investors?
4. Which has the best risk/reward?"""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return message.content[0].text

def get_risk_scores(stock_data, fundamentals, api_key):
    """AI-powered risk scoring"""
    
    client = anthropic.Anthropic(api_key=api_key)
    
    info = stock_data['info']
    
    prompt = f"""Rate these risk dimensions (1-10 scale, 10=highest risk) for {info.get('longName')}:

**Financial Data:**
- Beta: {info.get('beta', 'N/A')}
- Debt/Equity: {fundamentals['debt_to_equity']}
- Current Ratio: {fundamentals['current_ratio']}
- Profit Margin: {fundamentals['profit_margin']:.1f}%

**Risk Categories:**
1. Market Risk (volatility, beta)
2. Financial Risk (leverage, liquidity)
3. Business Model Risk (competitive moat, disruption risk)
4. Growth Risk (can it sustain growth?)
5. Valuation Risk (overpriced?)

Respond with ONLY valid JSON:
{{"market_risk": X, "financial_risk": X, "business_risk": X, "growth_risk": X, "valuation_risk": X}}"""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return message.content[0].text