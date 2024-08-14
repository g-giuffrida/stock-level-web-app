import yfinance as yf
import pandas as pd
import sys
import json

def fetch_stock_data(symbol):
    stock = yf.Ticker(symbol)
    info = stock.info
    balance_sheet = stock.balance_sheet
    financials = stock.financials

    def get_value(metric):
        value = info.get(metric, 'N/A')
        return 0 if pd.isna(value) or value == 'N/A' else value

    total_assets = balance_sheet.iloc[balance_sheet.index.get_loc('Total Assets'), 0] if 'Total Assets' in balance_sheet.index else 0
    total_revenue = financials.iloc[financials.index.get_loc('Total Revenue'), 0] if 'Total Revenue' in financials.index else 0
    cash = balance_sheet.iloc[balance_sheet.index.get_loc('Cash And Cash Equivalents'), 0] if 'Cash And Cash Equivalents' in balance_sheet.index else 0
    shares_outstanding = get_value('sharesOutstanding')
    stock_price = get_value('currentPrice')
    cash_per_share = cash / shares_outstanding if cash != 0 and shares_outstanding != 0 else 0
    cash_yield = (cash_per_share / stock_price) if cash_per_share != 0 and stock_price != 0 else 0

    asset_turnover_ratio = total_revenue / total_assets if total_assets != 0 and total_revenue != 0 else 0
    debt_ratio = balance_sheet.iloc[balance_sheet.index.get_loc('Total Debt'), 0] / total_assets if 'Total Debt' in balance_sheet.index and total_assets != 0 else 0

    return {
        'Symbol': symbol,
        'ROE (%)': get_value('returnOnEquity'),
        'Operating Profit Margin (%)': get_value('operatingMargins'),
        'Net Profit Margin (%)': get_value('profitMargins'),
        'Asset Turnover Ratio (%)': asset_turnover_ratio,
        'Debt to Equity Ratio (%)': get_value('debtToEquity') / 100,
        'Debt Ratio (%)': debt_ratio,
        'Cash per Share': cash_per_share,
        'Cash per share (%)': cash_yield,
        'PE': get_value('trailingPE'),
        'PEG': get_value('pegRatio'),
        'EV/Sales': get_value('enterpriseToRevenue'),
        'Stock Price': stock_price
    }

if __name__ == "__main__":
    symbol = sys.argv[1]
    try:
        data = fetch_stock_data(symbol)
        print(json.dumps(data))
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

