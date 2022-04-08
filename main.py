import sys
import ichi_api
from asyncio import get_event_loop
from filters import FILTERS
from contextlib import suppress


async def scan(fils: dict):
    coins = dict()

    print("\n- Getting all Binance coins...")
    binance_symbols = await ichi_api.all_binance_coins()
    print(f"- {len(binance_symbols)} coins found.")
    print("- Getting Binance coins candles...")
    coins['BINANCE'] = await ichi_api.get_binance_candles(binance_symbols, '1d')
    print(f"- Candles of {len(coins['BINANCE'])} coins extracted.")

    print("\n- Getting all Kucoin coins...")
    kucoin_symbols = await ichi_api.all_kucoin_coins()
    print(f"- {len(kucoin_symbols)} coins found.")
    print("- Getting Kucoin coins candles...")
    coins['KUCOIN'] = await ichi_api.get_kucoin_candles(kucoin_symbols, '1day')
    print(f"- Candles of {len(coins['KUCOIN'])} coins extracted.")

    print("\n- Calculating ichimoku...")
    for list_coins in coins.values():
        for coin in list_coins:
            ichi_api.compute_ichimoku(coin['candles'])
    print("- Ichimoku indicators cauculeted.")

    print("\n- Applying filters...")
    f11_parameter = ''
    if 'F11' in fils:
        f11_parameter = fils['F11']
        fils.pop('F11')
    remaining = dict()
    for exchange in coins:
        remaining[exchange] = []
        for coin in coins[exchange]:
            with suppress(KeyError, IndexError):
                for f in fils:
                    fil_fun = FILTERS[f]
                    if not fil_fun.analyze(df=coin["candles"], parameter=fils[f]):
                        break
                else:
                    remaining[exchange].append(coin)
    if f11_parameter:
        print("- Getting weekly candles to apply F11...")
        binance_symbols = [c["symbol"] for c in remaining["BINANCE"]]
        coins['BINANCE'] = await ichi_api.get_binance_candles(binance_symbols, '1w')
        kucoin_symbols = [c["symbol"] for c in remaining["KUCOIN"]]
        coins['KUCOIN'] = await ichi_api.get_kucoin_candles(kucoin_symbols, '1week')
        for list_coins in coins.values():
            for coin in list_coins:
                ichi_api.compute_ichimoku(coin['candles'])
        remaining = dict()
        for exchange in coins:
            remaining[exchange] = []
            for coin in coins[exchange]:
                with suppress(KeyError, IndexError):
                    if FILTERS['F11'].analyze(df=coin["candles"], parameter=f11_parameter):
                        remaining[exchange].append(coin)

    coin_list = []
    for exchange in remaining:
        for coin in remaining[exchange]:
            coin_list.append(f"{exchange}:{coin['symbol'].replace('-', '')}")
    print(f"- All filters applied. {len(coin_list)} coins remaining.")
    with open("result.txt", "w") as file:
        file.write("\n".join(coin_list))
    print(f"- Output written in result.txt.")


def get_filters() -> dict:
    fil = dict()
    i = 1
    while i < len(sys.argv):
        j = i
        i += 1
        while i < len(sys.argv) and not sys.argv[i].upper().startswith("-F"):
            i += 1
        parameters = " ".join(sys.argv[j+1: i]).upper()
        fil[sys.argv[j].upper()[1:]] = parameters
    return fil


print("----------| ICHIMOKU SCAN |----------")
loop = get_event_loop()
_filters = get_filters()
print(" ".join(sys.argv[1:]).upper())
loop.run_until_complete(scan(_filters))

