
import requests
import json

def check_price(symbol, url):
    try:
        response = requests.get(f"{url}/api/v3/ticker/price", params={"symbol": symbol}, timeout=5)
        data = response.json()
        print(f"{symbol} on {url}: {data}")
    except Exception as e:
        print(f"Error fetching {symbol} from {url}: {e}")

def check_futures_price(symbol):
    try:
        url = "https://fapi.binance.com/fapi/v1/ticker/price"
        response = requests.get(url, params={"symbol": symbol}, timeout=5)
        data = response.json()
        print(f"{symbol} Futures: {data}")
    except Exception as e:
        print(f"Error fetching {symbol} Futures: {e}")

print("Checking Prices...")
check_price("PAXGUSDT", "https://api.binance.com")
check_price("BTCUSDT", "https://api.binance.com")
check_price("PAXGUSDT", "https://testnet.binance.vision")
check_futures_price("XAUUSDT")
