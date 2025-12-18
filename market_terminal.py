import time
import yfinance as yf
import requests
from rich.console import Console
from rich.table import Table
from rich.live import Live

console = Console()

# --- CONFIGURATION ---
# Crypto IDs for CoinGecko
CRYPTO_IDS = ["bitcoin", "ethereum"]
# Stock Tickers for Yahoo Finance 
# Note: For Indian stocks like Reliance, use '.NS' for NSE
STOCK_TICKERS = ["NVDA", "TSLA", "AMZN", "AAPL", "RELIANCE.NS"]

def fetch_market_data():
    results = []

    # 1. Fetch Crypto Data (CoinGecko)
    try:
        crypto_url = "https://api.coingecko.com/api/v3/simple/price"
        params = {"ids": ",".join(CRYPTO_IDS), "vs_currencies": "usd", "include_24hr_change": "true"}
        c_data = requests.get(crypto_url, params=params).json()
        for coin in CRYPTO_IDS:
            price = c_data[coin]['usd']
            change = c_data[coin]['usd_24h_change']
            results.append({"name": coin.upper(), "price": f"${price:,.2f}", "change": change})
    except:
        pass

    # 2. Fetch Stock Data (yfinance)
    try:
        for ticker in STOCK_TICKERS:
            stock = yf.Ticker(ticker)
            # Get the latest price and previous close to calculate change
            info = stock.fast_info
            current_price = info['last_price']
            # Calculate % change manually for speed
            prev_close = info['previous_close']
            change = ((current_price - prev_close) / prev_close) * 100
            
            symbol = ticker.replace(".NS", "") # Clean up Reliance name
            results.append({"name": symbol, "price": f"${current_price:,.2f}", "change": change})
    except:
        pass

    return results

def generate_table(data_list):
    table = Table(title="📊 GLOBAL MARKET TERMINAL", style="bold blue", header_style="bold cyan")
    table.add_column("Asset", style="white")
    table.add_column("Price", justify="right")
    table.add_column("24h Change", justify="right")
    table.add_column("Status", justify="center")

    for item in data_list:
        color = "green" if item['change'] > 0 else "red"
        icon = "▲" if item['change'] > 0 else "▼"
        
        table.add_row(
            item['name'], 
            item['price'], 
            f"[{color}]{item['change']:.2f}%[/{color}]",
            f"[{color}]{icon}[/{color}]"
        )
    return table

if __name__ == "__main__":
    console.print("[bold yellow]Syncing with Wall Street & Crypto Exchanges...[/bold yellow]")
    
    with Live(generate_table([]), refresh_per_second=1) as live:
        while True:
            data = fetch_market_data()
            live.update(generate_table(data))
            time.sleep(10) # Stocks update slower, 10s is plenty
