# Ichimoku-Scan
 Scan all the coins on Binance and Kucoin /USDT + /BTC and output in a `.txt` a list of coins that match filters

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
- f11: The weekly Kijun is below/above the current candle
- f12 n: distance CK <-> candle = more than n% 
- f13: distance price <-> SSB = less than n%
- f14 n: max stochastic = n
- f15 n: number of days that prices have closed below the Kijun = n
- f16: there is a twist the cloud at x to y days from the chikou (-f15 3-5 c) or there is a twist the cloud at x to u days from the current candle (-f15 2-6 d)
- f17: distance TK <-> KJ = less than n%