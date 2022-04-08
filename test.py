import ichi_api
import asyncio
import aiohttp
from filters import StockFilter


async def test():
    async with aiohttp.ClientSession() as session:
        coin = await ichi_api.binance_candle('BTCUSDT', "1d", 110, '', session)
        candles = coin["1D"]
        ichi_api.compute_ichimoku(candles)
        f = StockFilter().analyze(candles, '100')
        print(f)

loop = asyncio.get_event_loop()
loop.run_until_complete(test())