from pybit.unified_trading import HTTP


session = HTTP(
    testnet=True,
    api_key="x0eVUdWKCAnCUdEYw9",
    api_secret="6HbJhpTSN0uuynsKpTy2I9tdmokdZqSCxmlC",
    demo=True

)
print(session)
# Get the orderbook of the USDT Perpetual, BTCUSDT

a = session.get_orderbook(category="linear", symbol="BTCUSDT")
print(a)
# Get the orderbook of the USDT Perpetual, BTCUSDT
session.get_orderbook(category="linear", symbol="BTCUSDT")

# # Create five long USDC Options orders.
# # (Currently, only USDC Options support sending orders in bulk.)
# payload = {"category": "option"}
# orders = [{
#   "symbol": "BTC-30JUN23-20000-C",
#   "side": "Buy",
#   "orderType": "Limit",
#   "qty": "0.1",
#   "price": i,
# } for i in [15000, 15500, 16000, 16500, 16600]]
#
# payload["request"] = orders
# # Submit the orders in bulk.
# session.place_batch_order(payload)

print(session.place_order(
    category="spot",
    symbol="BTCUSDT",
    side="Buy",
    orderType="Market",
    qty=1000,
))

print(session.)