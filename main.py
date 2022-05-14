import ichi_api
from asyncio import get_event_loop
from filters import FILTERS, filters_from_args
from contextlib import suppress


async def scan(fils: dict):
    coins = dict()

    print("\n- Getting all Binance coins...")
    coins['BINANCE'] = await ichi_api.all_binance_coins(quote=['USDT', 'BTC'])
    print(f"- {len(coins['BINANCE'])} coins found.")
    print("- Getting all Kucoin coins...")
    coins['KUCOIN'] = await ichi_api.all_kucoin_coins(quote=['USDT', 'BTC'])
    print(f"- {len(coins['KUCOIN'])} coins found.")

    for tf in fils:
        candles = dict()
        print(f"\nCandlestick analysis for tf={tf}")
        print("- Getting Binance coins candles...")
        candles['BINANCE'] = await ichi_api.get_binance_candles(coins['BINANCE'], tf)
        print(f"- Candles of {len(coins['BINANCE'])} coins extracted.")
        print("- Getting Kucoin coins candles...")
        candles['KUCOIN'] = await ichi_api.get_kucoin_candles(coins['KUCOIN'], tf)
        print(f"- Candles of {len(coins['KUCOIN'])} coins extracted.")
        print("- Calculating ichimoku...")
        for exchange_candles in candles.values():
            for coin in exchange_candles:
                ichi_api.compute_ichimoku(exchange_candles[coin])
        print("- Ichimoku indicators cauculeted.")
        print(f"- Applying {tf} filters...")
        for exchange in coins:
            for coin in coins[exchange][:]:
                with suppress(KeyError, IndexError):
                    for f in fils[tf]:
                        fil_fun = FILTERS[f]
                        if not fil_fun.analyze(df=candles[exchange][coin], parameter=fils[tf][f]):
                            coins[exchange].remove(coin)
                            break
        print(f"- {sum([len(x) for x in coins.values()])} coins remaining.")

    print(f"\n- All filters applied.")
    result = []
    for exc in coins:
        for coin in coins[exc]:
            result.append(f"{exc}:{coin.replace('-', '')}")
    with open("result.txt", "w") as file:
        file.write("\n".join(result))
    print(f"- Output written in result.txt.")


print("----------| ICHIMOKU SCAN |----------")
loop = get_event_loop()
_filters = filters_from_args()
for t in _filters:
    print(f"Filters {t}: {'  '.join(f'-{k} {_filters[t][k]}' for k in _filters[t])}")
loop.run_until_complete(scan(_filters))

