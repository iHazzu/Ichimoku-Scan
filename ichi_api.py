from aiohttp import ClientSession, ServerDisconnectedError
from asyncio import gather, sleep
import pandas as pd
from datetime import datetime, timedelta


MAX_CANDLES = 110   # Needded candles to coumpute ichimoku

# Ichimoku parameters
W1 = 9
W2 = 26
W3 = 52
D = 27

with open("proxies.txt") as file:
    proxies = file.read().splitlines()
    proxies.insert(0, '')     # Localhost


async def all_binance_coins() -> list:
    async with ClientSession() as session:
        async with session.get("https://api.binance.com/api/v3/exchangeInfo") as resp:
            info = await resp.json()
    pairs = [c['symbol'] for c in info['symbols'] if c['quoteAsset'] in ['USDT', 'BTC']]
    return pairs


async def get_binance_candles(pairs: list, timeframe: str) -> list:
    async with ClientSession() as session:
        max_req, cooldown = 1200, 60   # Binance rate limit = 1200 requests / 60 s
        i = 0
        candles = []
        while i < len(pairs):
            for proxy in proxies:
                tasks = [binance_candle(p, timeframe, MAX_CANDLES, proxy, session) for p in pairs[i:i + max_req]]
                ret = await gather(*tasks, return_exceptions=True)
                for r in ret:
                    if not isinstance(r, Exception):
                        candles.append(r)
                i += max_req
                if i > len(pairs):
                    break
            else:
                await sleep(cooldown)
        return candles


async def binance_candle(symbol: str, timeframe: str, limit: int, proxy: str, session: ClientSession) -> dict:
    url = "https://api.binance.com/api/v3/klines"
    params = {
        'symbol': symbol,
        'interval': timeframe,
        'limit': limit
    }
    while True:
        try:
            async with session.get(url=url, params=params, proxy=proxy) as resp:
                data = await resp.json()
        except ServerDisconnectedError:
            continue
        else:
            break
    data = [d[:6] for d in data]
    df = pd.DataFrame(data, columns=["TIME", "OPEN", "HIGH", "LOW", "PRICE", "VOLUME"])
    df["PRICE"] = pd.to_numeric(df["PRICE"])
    df["HIGH"] = pd.to_numeric(df["HIGH"])
    df["LOW"] = pd.to_numeric(df["LOW"])
    return {'symbol': symbol, 'candles': df}


async def all_kucoin_coins() -> list:
    async with ClientSession() as session:
        async with session.get("https://openapi-v2.kucoin.com/api/v1/market/allTickers") as i:
            data = await i.json()
        info = data['data']['ticker']
        pairs = [c['symbol'] for c in info if c['symbol'].split("-")[1] in ['USDT', 'BTC']]
        return pairs


async def get_kucoin_candles(pairs: list, timeframe: str) -> list:
    async with ClientSession() as session:
        max_req, cooldown = 100, 10    # Kucoin rate limit = 100 requests / 10s
        start_time = datetime.utcnow() - MAX_CANDLES * timedelta(days=1)
        start_time = int(start_time.timestamp())
        i = 0
        candles = []
        while i < len(pairs):
            for proxy in proxies:
                tasks = [kucoin_candle(p, timeframe, start_time, proxy, session) for p in pairs[i:i + max_req]]
                ret = await gather(*tasks, return_exceptions=True)
                for r in ret:
                    if not isinstance(r, Exception):
                        candles.append(r)
                i += max_req
                if i > len(pairs):
                    break
            else:
                await sleep(cooldown)
        return candles


async def kucoin_candle(symbol: str, timeframe: str, start_at: int, proxy: str, session: ClientSession) -> dict:
    url = "https://openapi-v2.kucoin.com/api/v1/market/candles"
    params = {
        'symbol': symbol,
        'type': timeframe,
        'startAt': start_at
    }
    while True:
        async with session.get(url=url, params=params, proxy=proxy) as resp:
            data = await resp.json()
        if data['code'] != '429000':  # Not Rate limited
            break
    data = [d[:6] for d in reversed(data["data"])]
    df = pd.DataFrame(data, columns=["TIME", "OPEN", "PRICE", "HIGH", "LOW", "VOLUME"])
    df["PRICE"] = pd.to_numeric(df["PRICE"])
    df["HIGH"] = pd.to_numeric(df["HIGH"])
    df["LOW"] = pd.to_numeric(df["LOW"])
    return {'symbol': symbol, 'candles': df}


def compute_ichimoku(df: pd.DataFrame):
    df['TK'] = (df['HIGH'].rolling(W1, min_periods=0).max() + df['LOW'].rolling(W1, min_periods=0).min()) / 2
    df['KJ'] = (df['HIGH'].rolling(W2, min_periods=0).max() + df['LOW'].rolling(W2, min_periods=0).min()) / 2
    df['CK'] = df['PRICE'].shift(-D)
    df['SSAF'] = ((df['TK'] + df['KJ']) / 2)  # Future
    df['SSA'] = df['SSAF'].shift(W2)    # Present
    df['SSBF'] = ((df['HIGH'].rolling(W3).max() + df['LOW'].rolling(W3).min()) / 2)
    df['SSB'] = df['SSBF'].shift(W2)