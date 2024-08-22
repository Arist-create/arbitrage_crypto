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
        if i['state'] == '1'
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
                        await redis.set(
                            f'{data["s"]}@MEXC',
                                json.dumps(data["d"])
                            )

                    except Exception as e:
                        print(e)
        except Exception as e:
            print(e)

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
