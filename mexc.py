import requests
import websockets
import json
import asyncio 
from redis import redis




async def get_tokens(): #переписать на получение из файла а обновление сделать на актуализаторе
    with open('list_of_deposit_and_withdraw_tokens_mexc.json', 'r') as f:
        arr = json.load(f)
    arr_new = set()
    for i in arr:
        for j in i["coins"]:
            if j["chain"] == "Ethereum(ERC20)":
                arr_new.add(i["currency"])
    resp = requests.get(
        'https://www.mexc.com/open/api/v2/market/symbols',
        headers={
            'Accept': 'application/json', 
            'Content-Type': 'application/json', 
            'X-MEXC-APIKEY': 'mx0vglNJacXHNmGojb',
        }
    )
    resp = resp.json()["data"]

    arr = [
        i
        for i in resp
        if i['state'] == 'ENABLED'
        and i.get('symbol')[-4:] == 'USDT'
        and i.get('symbol')[:-5] in arr_new
    ]
    print(len(arr))
    for i in arr:
        i["symbol"] = i["symbol"].replace('_USDT', 'USDT')
    # сохранить список в json файл
    with open('list_of_tokens_mexc.json', 'w') as f:
        json.dump(arr, f, indent=4)
    return arr

# async def calculate_avg_price(arr):
#     total_cost = 0.0
#     target_value = 1000.0
#     total_volume = 0.0
#     k = 0
#     for i in arr:
#         k += 1
#         price = float(i['p'])
#         volume = float(i['v'])
#         value = price * volume

#         if total_cost + value >= target_value:
#             remaining_value = target_value - total_cost
#             volume_needed = remaining_value / price
#             total_cost += remaining_value
#             total_volume += volume_needed
#             break
#         else:
#             total_cost += value
#             total_volume += volume

#     avg_price = total_cost / total_volume
#     return avg_price, k, total_cost, total_volume

async def get_quote(subscribe_list):
    while True: 
        try:
            async with websockets.connect('wss://wbs.mexc.com/ws', ping_interval=5, ping_timeout=30) as websocket:
                await websocket.send(
                    json.dumps({
                        "method": "SUBSCRIPTION",
                        "params": subscribe_list
                    })
                )
                while True:
                    data = await websocket.recv()
                    data = json.loads(data)
                    try:
                        # avg_price_bid, orders_bid, vol_bid_in_usdt, vol_bid = await calculate_avg_price(data['d']['bids'])
                        # avg_price_ask, orders_ask, vol_ask_in_usdt, vol_ask = await calculate_avg_price(data['d']['asks'])

                        await redis.set(
                            f'{data["s"]}@MEXC',
                                json.dumps(data["d"])
                            )

                    except Exception as e:
                        pass
        except Exception as e:
            pass

async def main():
    tokens = await get_tokens()
    subscribe_list = [f'spot@public.limit.depth.v3.api@{token["symbol"]}@20' for token in tokens]
    
    tasks = []
    for i in range(0, len(subscribe_list), 20):
        chunk = subscribe_list[i:i + 20]
        tasks.append(get_quote(chunk))

    await asyncio.gather(*tasks)
if __name__ == '__main__':
    asyncio.run(main())
