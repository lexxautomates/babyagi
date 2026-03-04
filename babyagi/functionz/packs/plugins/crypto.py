"""
Crypto Plugin for BabyAGI
Provides cryptocurrency tools for price checking, market data, and analysis.
Each function is completely self-contained with ALL imports inside.
"""

from babyagi.functionz.core.framework import func
from typing import Optional, Dict, Any, List


@func.register_function(
    metadata={
        "description": "Get current price of a cryptocurrency in USD. Supports bitcoin, ethereum, and other major coins."
    }
)
def get_crypto_price(coin_id: str = "bitcoin") -> Dict[str, Any]:
    """Get current cryptocurrency price from CoinGecko API."""
    import json
    import urllib.request
    import urllib.error
    
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd&include_24hr_change=true&include_market_cap=true"
    
    try:
        req = urllib.request.Request(url, headers={})
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode())
    except Exception as e:
        return {"error": f"Failed to fetch price: {str(e)}"}
    
    if coin_id in result:
        data = result[coin_id]
        return {
            "coin": coin_id,
            "price_usd": data.get("usd", "N/A"),
            "market_cap_usd": data.get("usd_market_cap", "N/A"),
            "24h_change_percent": data.get("usd_24h_change", "N/A")
        }
    
    return {"error": f"Coin '{coin_id}' not found. Try 'bitcoin', 'ethereum', 'solana', etc."}


@func.register_function(
    metadata={
        "description": "Get detailed market data for top cryptocurrencies by market cap."
    }
)
def get_top_cryptos(limit: int = 10) -> List[Dict[str, Any]]:
    """Get top cryptocurrencies by market capitalization."""
    import json
    import urllib.request
    
    limit = min(limit, 50)
    url = f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page={limit}&page=1&sparkline=false&price_change_percentage=24h"
    
    try:
        req = urllib.request.Request(url, headers={})
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode())
    except Exception as e:
        return [{"error": f"Failed to fetch market data: {str(e)}"}]
    
    coins = []
    for coin in result:
        coins.append({
            "rank": coin.get("market_cap_rank"),
            "name": coin.get("name"),
            "symbol": coin.get("symbol", "").upper(),
            "price_usd": coin.get("current_price"),
            "market_cap_usd": coin.get("market_cap"),
            "24h_change_percent": coin.get("price_change_percentage_24h"),
            "volume_24h_usd": coin.get("total_volume")
        })
    
    return coins


@func.register_function(
    metadata={
        "description": "Get trending cryptocurrencies on CoinGecko."
    }
)
def get_trending_cryptos() -> Dict[str, Any]:
    """Get trending cryptocurrencies from CoinGecko."""
    import json
    import urllib.request
    
    url = "https://api.coingecko.com/api/v3/search/trending"
    
    try:
        req = urllib.request.Request(url, headers={})
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode())
    except Exception as e:
        return {"error": f"Failed to fetch trending: {str(e)}"}
    
    trending = []
    for item in result.get("coins", [])[:7]:
        coin = item.get("item", {})
        trending.append({
            "name": coin.get("name"),
            "symbol": coin.get("symbol", "").upper(),
            "market_cap_rank": coin.get("market_cap_rank"),
            "price_btc": coin.get("price_btc")
        })
    
    return {"trending": trending}


@func.register_function(
    metadata={
        "description": "Convert an amount from one cryptocurrency to another or to USD."
    }
)
def convert_crypto(amount: float, from_coin: str, to_coin: str = "usd") -> Dict[str, Any]:
    """Convert cryptocurrency amounts."""
    import json
    import urllib.request
    
    try:
        if to_coin.lower() == "usd":
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={from_coin}&vs_currencies=usd"
            req = urllib.request.Request(url, headers={})
            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode())
            
            if from_coin in result:
                rate = result[from_coin].get("usd", 0)
                converted = amount * rate
                return {
                    "from": from_coin,
                    "to": "USD",
                    "amount": amount,
                    "converted": converted,
                    "rate": rate
                }
        else:
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={from_coin},{to_coin}&vs_currencies=usd"
            req = urllib.request.Request(url, headers={})
            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode())
            
            if from_coin in result and to_coin in result:
                from_rate = result[from_coin].get("usd", 0)
                to_rate = result[to_coin].get("usd", 0)
                
                if to_rate > 0:
                    usd_value = amount * from_rate
                    converted = usd_value / to_rate
                    return {
                        "from": from_coin,
                        "to": to_coin,
                        "amount": amount,
                        "converted": converted,
                        "rate": from_rate / to_rate
                    }
        
        return {"error": f"Could not convert from {from_coin} to {to_coin}"}
    except Exception as e:
        return {"error": f"Failed to convert: {str(e)}"}


@func.register_function(
    metadata={
        "description": "Get detailed information about a specific cryptocurrency."
    }
)
def get_crypto_info(coin_id: str = "bitcoin") -> Dict[str, Any]:
    """Get detailed information about a cryptocurrency."""
    import json
    import urllib.request
    
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}?localization=false&tickers=false&community_data=false&developer_data=false"
    
    try:
        req = urllib.request.Request(url, headers={})
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode())
    except Exception as e:
        return {"error": f"Failed to fetch info: {str(e)}"}
    
    if "id" not in result:
        return {"error": f"Coin '{coin_id}' not found"}
    
    return {
        "name": result.get("name"),
        "symbol": result.get("symbol", "").upper(),
        "rank": result.get("market_cap_rank"),
        "current_price_usd": result.get("market_data", {}).get("current_price", {}).get("usd"),
        "ath_usd": result.get("market_data", {}).get("ath", {}).get("usd"),
        "atl_usd": result.get("market_data", {}).get("atl", {}).get("usd"),
        "market_cap_usd": result.get("market_data", {}).get("market_cap", {}).get("usd"),
        "total_supply": result.get("market_data", {}).get("total_supply"),
        "circulating_supply": result.get("market_data", {}).get("circulating_supply"),
        "description": result.get("description", {}).get("en", "")[:500] + "..." if result.get("description", {}).get("en") else None
    }


@func.register_function(
    metadata={
        "description": "Get Bitcoin dominance and global market data."
    }
)
def get_global_market_data() -> Dict[str, Any]:
    """Get global cryptocurrency market data including Bitcoin dominance."""
    import json
    import urllib.request
    
    url = "https://api.coingecko.com/api/v3/global"
    
    try:
        req = urllib.request.Request(url, headers={})
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode())
    except Exception as e:
        return {"error": f"Failed to fetch global data: {str(e)}"}
    
    data = result.get("data", {})
    
    return {
        "total_market_cap_usd": data.get("total_market_cap", {}).get("usd"),
        "total_volume_24h_usd": data.get("total_volume", {}).get("usd"),
        "bitcoin_dominance_percent": data.get("market_cap_percentage", {}).get("btc"),
        "ethereum_dominance_percent": data.get("market_cap_percentage", {}).get("eth"),
        "active_cryptocurrencies": data.get("active_cryptocurrencies"),
        "markets": data.get("markets")
    }


@func.register_function(
    metadata={
        "description": "Search for cryptocurrencies by name or symbol."
    }
)
def search_crypto(query: str) -> List[Dict[str, Any]]:
    """Search for cryptocurrencies by name or symbol."""
    import json
    import urllib.request
    
    url = f"https://api.coingecko.com/api/v3/search?query={query}"
    
    try:
        req = urllib.request.Request(url, headers={})
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode())
    except Exception as e:
        return [{"error": f"Search failed: {str(e)}"}]
    
    coins = []
    for coin in result.get("coins", [])[:10]:
        coins.append({
            "id": coin.get("id"),
            "name": coin.get("name"),
            "symbol": coin.get("symbol", "").upper(),
            "market_cap_rank": coin.get("market_cap_rank")
        })
    
    return coins


@func.register_function(
    metadata={
        "description": "Get price history for a cryptocurrency over a number of days."
    }
)
def get_crypto_price_history(coin_id: str = "bitcoin", days: int = 7) -> Dict[str, Any]:
    """Get historical price data for a cryptocurrency."""
    import json
    import urllib.request
    
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=usd&days={days}"
    
    try:
        req = urllib.request.Request(url, headers={})
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode())
    except Exception as e:
        return {"error": f"Failed to fetch history: {str(e)}"}
    
    prices = result.get("prices", [])
    
    if not prices:
        return {"error": "No price data available"}
    
    price_values = [p[1] for p in prices]
    
    return {
        "coin": coin_id,
        "days": days,
        "current_price": price_values[-1] if price_values else None,
        "highest_price": max(price_values) if price_values else None,
        "lowest_price": min(price_values) if price_values else None,
        "price_change": price_values[-1] - price_values[0] if len(price_values) > 1 else 0,
        "percent_change": ((price_values[-1] - price_values[0]) / price_values[0] * 100) if len(price_values) > 1 and price_values[0] > 0 else 0
    }


@func.register_function(
    metadata={
        "description": "Get Ethereum gas prices in Gwei."
    }
)
def get_eth_gas_price() -> Dict[str, Any]:
    """Get current Ethereum gas prices."""
    import json
    import urllib.request
    
    url = "https://api.etherscan.io/api?module=gastracker&action=gasoracle"
    
    try:
        req = urllib.request.Request(url, headers={})
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode())
    except Exception as e:
        return {"error": f"Failed to fetch gas prices: {str(e)}"}
    
    if result.get("status") == "1":
        data = result.get("result", {})
        return {
            "safe_gas_price_gwei": data.get("SafeGasPrice"),
            "propose_gas_price_gwei": data.get("ProposeGasPrice"),
            "fast_gas_price_gwei": data.get("FastGasPrice"),
            "base_fee_gwei": data.get("suggestBaseFee")
        }
    
    return {"error": "Could not fetch gas prices. Try again later."}


@func.register_function(
    metadata={
        "description": "Get crypto market summary with key metrics."
    }
)
def get_crypto_market_summary() -> str:
    """Get a formatted summary of the crypto market."""
    import json
    import urllib.request
    
    # Get global data
    try:
        req = urllib.request.Request("https://api.coingecko.com/api/v3/global", headers={})
        with urllib.request.urlopen(req, timeout=10) as response:
            global_result = json.loads(response.read().decode())
    except Exception as e:
        return f"Error fetching market data: {str(e)}"
    
    data = global_result.get("data", {})
    market_cap = data.get("total_market_cap", {}).get("usd", 0)
    btc_dominance = data.get("market_cap_percentage", {}).get("btc", 0)
    eth_dominance = data.get("market_cap_percentage", {}).get("eth", 0)
    active_cryptos = data.get("active_cryptocurrencies", 0)
    
    # Get top 5 cryptos
    try:
        req = urllib.request.Request(
            "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=5&page=1&sparkline=false&price_change_percentage=24h",
            headers={}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            top_result = json.loads(response.read().decode())
    except Exception as e:
        return f"Error fetching top cryptos: {str(e)}"
    
    # Format market cap
    if market_cap:
        market_cap_str = f"${market_cap/1e12:.2f}T"
    else:
        market_cap_str = "N/A"
    
    # Build summary
    summary = f"""📊 **Crypto Market Summary**

🌍 **Global Market**
• Total Market Cap: {market_cap_str}
• BTC Dominance: {btc_dominance:.1f}%
• ETH Dominance: {eth_dominance:.1f}%
• Active Cryptos: {active_cryptos:,}

🏆 **Top 5 by Market Cap**
"""
    
    for coin in top_result:
        rank = coin.get("market_cap_rank")
        name = coin.get("name")
        symbol = coin.get("symbol", "").upper()
        price = coin.get("current_price", 0) or 0
        change = coin.get("price_change_percentage_24h", 0) or 0
        change_emoji = "🟢" if change >= 0 else "🔴"
        summary += f"• #{rank} {name} ({symbol}): ${price:,.2f} {change_emoji} {change:.2f}%\n"
    
    return summary