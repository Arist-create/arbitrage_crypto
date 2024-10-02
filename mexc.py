import time
import websockets
import json
import asyncio 
from redis_facade import redis
from mongo import list_of_pairs_mexc_db

stop_event = asyncio.Event()

async def get_quote(subscribe_list):
    while not stop_event.is_set(): 
        try:
            async with websockets.connect('wss://wbs.mexc.com/ws', ping_interval=10, ping_timeout=None) as websocket:
                await websocket.send(
                    json.dumps({
                        "method": "SUBSCRIPTION",
                        "params": subscribe_list
                    })
                )
                dict = {}
                while not stop_event.is_set():
                    data = await websocket.recv()
                    data = json.loads(data)
                    pair = data.get("s")
                    if not pair: 
                        continue
                    await asyncio.sleep(0.01)
                    dict[f'{pair}@MEXC'] = json.dumps(data["d"])
                    if len(dict) == 10:
                        await redis.mset(dict)
                        dict = {}
                await websocket.close()
        except:
            await asyncio.sleep(30)

async def stop():
    await asyncio.sleep(3)
    stop_event.set()

async def main():
    while True:
        print("start")
        pairs = await list_of_pairs_mexc_db.get_all()
        subscribe_list = [f'spot@public.limit.depth.v3.api@{pair["symbol"]}@20' for pair in pairs]
        
        tasks = []
        for i in range(0, len(subscribe_list), 20):
            chunk = subscribe_list[i:i + 20]
            tasks.append(get_quote(chunk))
            if len(tasks) >= 30:
                tasks.append(stop())
                await asyncio.gather(*tasks)
                stop_event.clear() 
                tasks = []
        if tasks:
            tasks.append(stop())
            await asyncio.gather(*tasks)
            stop_event.clear() 

        # await asyncio.gather(*tasks)
        # stop_event.clear() 


if __name__ == '__main__':
    while True:
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            loop.run_until_complete(main())
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(30)
