import time
import websockets
import json
import asyncio 
from redis_facade import redis
from mongo import list_of_pairs_mexc_db

stop_event = asyncio.Event()
stop_event_main = asyncio.Event()

async def manage_message(websocket):
    dict = {}
    while not stop_event.is_set():
        data = await websocket.recv()
        data = json.loads(data)
        pair = data.get("s")
        if not pair: 
            continue
        await asyncio.sleep(0.01)
        dict[f'{pair}@MEXC'] = json.dumps(data["d"])
        if len(dict) == 15:
            await redis.mset(dict)
            dict = {}

async def get_quote(subscribe_list):
    while not stop_event_main.is_set():
        try:
            async with websockets.connect('wss://wbs.mexc.com/ws', ping_interval=10, ping_timeout=None) as websocket:
                while not stop_event_main.is_set():
                    print("start")
                    
                    tasks = []
                    for i in range(0, len(subscribe_list), 20):
                        chunk = subscribe_list[i:i + 20]
                        await websocket.send( 
                            json.dumps({
                                "method": "SUBSCRIPTION",
                                "params": chunk
                            })
                        )
                        tasks.append(stop())
                        tasks.append(manage_message(websocket))
                        await asyncio.gather(*tasks)
                        await websocket.send(
                            json.dumps({
                                "method": "UNSUBSCRIPTION",
                                "params": chunk
                            })
                        )
                        tasks = []
                        stop_event.clear()
                await websocket.close()
        except Exception as e:
            print(e)
            await asyncio.sleep(30)


async def main():
    while True:
        pairs = await list_of_pairs_mexc_db.get_all()
        subscribe_list = [f'spot@public.limit.depth.v3.api@{pair["symbol"]}@20' for pair in pairs]
        tasks = []
        for i in range(0, len(subscribe_list), 200):
            tasks.append(get_quote(subscribe_list[i:i+200]))
        tasks.append(stop_main())
        await asyncio.gather(*tasks)
        stop_event_main.clear()

async def stop():
    await asyncio.sleep(3)
    stop_event.set()

async def stop_main():
    await asyncio.sleep(3600)
    stop_event_main.set()


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
