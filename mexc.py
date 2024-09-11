
import websockets
import json
import asyncio 
from redis import redis


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
                        await asyncio.sleep(10)
        except Exception as e:
            print(e)
            await asyncio.sleep(10)

async def main():
    with open('list_of_pairs_mexc.json') as f:
        pairs = json.load(f)
    subscribe_list = [f'spot@public.limit.depth.v3.api@{pair["symbol"]}@20' for pair in pairs]
    
    tasks = []
    for i in range(0, len(subscribe_list), 20):
        chunk = subscribe_list[i:i + 20]
        tasks.append(get_quote(chunk))

    await asyncio.gather(*tasks)



if __name__ == '__main__':
    asyncio.run(main())
