
import websockets
import json
import asyncio 
from redis import redis

stop_task = False

async def get_quote(subscribe_list):
    try:
        async with websockets.connect('wss://wbs.mexc.com/ws', ping_interval=5, ping_timeout=None) as websocket:
            await websocket.send(
                json.dumps({
                    "method": "SUBSCRIPTION",
                    "params": subscribe_list
                })
            )
            while True:
                if stop_task:
                    break
                data = await websocket.recv()
                data = json.loads(data)
                pair = data.get("s")
                if not pair: 
                    continue
                await redis.set(
                    f'{pair}@MEXC',
                        json.dumps(data["d"])
                )
            await websocket.close()
    except:
        pass
async def stop():
    await asyncio.sleep(3600)
    global stop_task
    stop_task = True

async def main():
    while True:
        print("start")
        with open('list_of_pairs_mexc.json') as f:
            pairs = json.load(f)
        subscribe_list = [f'spot@public.limit.depth.v3.api@{pair["symbol"]}@20' for pair in pairs]
        
        tasks = []
        for i in range(0, len(subscribe_list), 20):
            chunk = subscribe_list[i:i + 20]
            tasks.append(get_quote(chunk))
        tasks.append(stop())

        await asyncio.gather(*tasks)
        global stop_task
        stop_task = False





if __name__ == '__main__':
    asyncio.run(main())
