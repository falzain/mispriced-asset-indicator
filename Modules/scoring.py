import numpy as np

def calculate_investment_score(info, fundamentals, hist, weights):
    scores = {}
    
    # VALUATION
    pe = info.get('trailingPE', 0)
    ps = info.get('priceToSalesTrailing12Months', 0)
    pb = info.get('priceToBook', 0)
    
    valuation_score = 0
    if pe > 0 and pe < 14:
        valuation_score += 40
    elif pe < 20:
        valuation_score += 25
    else:
        valuation_score += 10
    
    if ps < 3:
        valuation_score += 30
    elif ps < 5:
        valuation_score += 20
    
    if pb < 2:
        valuation_score += 30
    elif pb < 5:
        valuation_score += 15
    
    scores['valuation'] = min(valuation_score, 100)
    
    # QUALITY
    roe = fundamentals['roe']
    margin = fundamentals['profit_margin']
    debt_equity = fundamentals['debt_to_equity']
    
    quality_score = 0
    if roe > 20:
        quality_score += 40
    elif roe > 15:
        quality_score += 30
    elif roe > 10:
        quality_score += 20
    
    if margin > 20:
        quality_score += 35
    elif margin > 10:
        quality_score += 25
    
    if debt_equity < 0.5:
        quality_score += 25
    elif debt_equity < 1:
        quality_score += 15
    
    scores['quality'] = min(quality_score, 100)
    
    # GROWTH
    rev_growth = fundamentals['revenue_growth']
    
    if rev_growth > 30:
        growth_score = 100
    elif rev_growth > 20:
        growth_score = 80
    elif rev_growth > 10:
        growth_score = 60
    else:
        growth_score = 20
    
    scores['growth'] = growth_score
    
    # MOMENTUM
    current_price = hist['Close'].iloc[-1]
    ma50 = hist['Close'].rolling(50).mean().iloc[-1]
    ma200 = hist['Close'].rolling(200).mean().iloc[-1]
    
    momentum_score = 0
    if current_price > ma50:
        momentum_score += 30
    if current_price > ma200:
        momentum_score += 30
    if ma50 > ma200:
        momentum_score += 20
    
    scores['momentum'] = min(momentum_score, 100)
    
    # RISK
    beta = info.get('beta', 1)
    volatility = hist['Close'].pct_change().std() * np.sqrt(252) * 100
    
    risk_score = 0
    if beta < 0.8:
        risk_score += 50
    elif beta < 1.2:
        risk_score += 35
    
    if volatility < 20:
        risk_score += 50
    elif volatility < 30:
        risk_score += 35
    
    scores['risk'] = min(risk_score, 100)
    
    # TOTAL
    total_score = (
        scores['valuation'] * weights['valuation'] +
        scores['quality'] * weights['quality'] +
        scores['growth'] * weights['growth'] +
        scores['momentum'] * weights['momentum'] +
        scores['risk'] * weights['risk']
    ) / sum(weights.values())
    
    scores['total'] = total_score
    
    return scores

def get_rating(score):
    if score >= 80:
        return "STRONG BUY", "#1db954"
    elif score >= 65:
        return "BUY", "#1db954"
    elif score >= 50:
        return "HOLD", "#ffa927"
    elif score >= 35:
        return "SELL", "#f15e6c"
    else:
        return "STRONG SELL", "#f15e6c"