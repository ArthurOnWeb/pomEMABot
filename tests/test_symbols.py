import ccxt
exchange = ccxt.binance({'enableRateLimit': True})
markets = exchange.load_markets()
print('ETHUSD' in markets)
print('ETH/USDT' in markets)
print('ETHUSDT' in markets)
if 'ETH/USDT' in markets:
    print(markets['ETH/USDT'])
