# Ichimoku-Scan
 Scan all the coins on Binance and Kucoin /USDT + /BTC and output in a `.txt` a list of coins that match filters.

- f1: current candle is below/above the TK (below = 0, above = 1)
- f2: current candle is below/above the KJ
- f3: current candle is below/above the SSA
- f4: current candle is below/above the SSB
- f5: TK is below/above the KJ
- f6: CK is below/above the TK
- f7: CK is below/above the KJ
- f8: CK is below/above the candle (= the candle right above the chikou)
- f9: CK is below/above the SSA
- f10: CK is below/above the SSB
- f11 n: distance CK <-> candle = more than n% 
- f12: distance price <-> SSB = less than n%
- f13 n: max stochastic = n
- f14 n: number of days that prices have closed below the Kijun = n
- f15: there is a twist the cloud at x to y days from the chikou (-f15 3-5 c) or there is a twist the cloud at x to u days from the current candle (-f15 2-6 d)
- f16: distance TK <-> KJ = more than n%.

### Timeframe
Inform the desired timeframe as the last filter parameter. If none is given, `1d` will be selected by default.
Examples:
- -f15 3-5 d 4h (timeframe will be `4 hours`);
- -f2 1 1w (timeframe will be `1 week`);
- -f1 0 (timeframe will be `1 day`).