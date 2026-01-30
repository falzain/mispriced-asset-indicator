import numpy as np
import pandas as pd

def calculate_dcf(cash_flows, terminal_growth_rate, discount_rate, shares_outstanding):
    """
    DCF Valuation Model
    cash_flows: list of projected free cash flows for next 5-10 years
    terminal_growth_rate: perpetual growth rate (usually 2-3%)
    discount_rate: WACC (weighted average cost of capital)
    """
    
    # Present value of projected cash flows
    pv_cash_flows = []
    for year, cf in enumerate(cash_flows, 1):
        pv = cf / ((1 + discount_rate) ** year)
        pv_cash_flows.append(pv)
    
    # Terminal value (Gordon Growth Model)
    terminal_cf = cash_flows[-1] * (1 + terminal_growth_rate)
    terminal_value = terminal_cf / (discount_rate - terminal_growth_rate)
    pv_terminal = terminal_value / ((1 + discount_rate) ** len(cash_flows))
    
    # Enterprise value
    enterprise_value = sum(pv_cash_flows) + pv_terminal
    
    # Equity value per share
    price_per_share = enterprise_value / shares_outstanding
    
    return {
        'enterprise_value': enterprise_value,
        'price_per_share': price_per_share,
        'pv_cash_flows': pv_cash_flows,
        'terminal_value': pv_terminal
    }

def calculate_wacc(risk_free_rate, beta, market_return, debt_ratio, tax_rate, cost_of_debt):
    """Calculate Weighted Average Cost of Capital"""
    cost_of_equity = risk_free_rate + beta * (market_return - risk_free_rate)
    wacc = (1 - debt_ratio) * cost_of_equity + debt_ratio * cost_of_debt * (1 - tax_rate)
    return wacc

def calculate_multiples(data):
    """Calculate valuation multiples"""
    info = data['info']
    
    multiples = {
        'P/E': info.get('trailingPE', 0),
        'Forward P/E': info.get('forwardPE', 0),
        'P/S': info.get('priceToSalesTrailing12Months', 0),
        'P/B': info.get('priceToBook', 0),
        'EV/EBITDA': info.get('enterpriseToEbitda', 0)
    }
    
    return multiples