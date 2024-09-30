from mongo import goplus_db, list_of_pairs_mexc_db, tokens_mexc_by_chains_db
from redis import trades_redis
import requests
import json
import time
import hmac
import hashlib
import httpx
import asyncio

async def get_decimals_mexc():
    resp = requests.get(
        f"https://www.mexc.com/open/api/v2/market/coin/list",
        headers={
            'Accept': 'application/json', 
            'Content-Type': 'application/json', 
            'X-MEXC-APIKEY': 'mx0vglNJacXHNmGojb'
        }
    )
    resp = resp.json()['data']
    dictionary = {i["currency"]: i for i in resp}


    with open('decimals_mexc.json', 'w') as f:
        json.dump(dictionary, f, indent=4)

async def signature(timestamp):
    secret = b"e4089671cab54eaab97caddadf3cabdc"
    return hmac.new(secret, f"timestamp={timestamp}".encode("utf-8"), hashlib.sha256).hexdigest()

async def get_tokens_mexc_by_chains():
    timestamp = int(time.time() * 1000)
    sign = await signature(timestamp) 
    resp = requests.get(
        f'https://api.mexc.com/api/v3/capital/config/getall?timestamp={timestamp}&signature={sign}',
        headers={ 
            'X-MEXC-APIKEY': 'mx0vglNJacXHNmGojb',
        }
    )
    tokens_by_chains = resp.json()

    dictionary = {i["coin"]: i for i in tokens_by_chains}
    
    with open('decimals_mexc.json') as f:
        tokens_with_decimals = json.load(f)
    
    for k, v in dictionary.items():
        info = tokens_with_decimals.get(k)
        if not info:
            continue
        info = info.get("coins")
        if not info:
            continue
        for i in v["networkList"]:
            for j in info:
                if i["network"] == j["chain"]:
                    i["decimals"] = j["precision"]
                    break
        await tokens_mexc_by_chains_db.update("coin", v["coin"], v, True)
    

async def get_pairs(): #переписать на получение из файла а обновление сделать на актуализаторе
    resp = requests.get(
        'https://api.mexc.com/api/v3/exchangeInfo',
        headers={
            'Accept': 'application/json', 
            'Content-Type': 'application/json', 
            'X-MEXC-APIKEY': 'mx0vglNJacXHNmGojb',
        }
    )
    resp = resp.json()["symbols"]
    arr = [
        i
        for i in resp
        if i['status'] == '1'
        and i.get("quoteAsset") == 'USDT'
    ]
    print(len(arr))
    arr = [list_of_pairs_mexc_db.update("symbol", i["symbol"], i, True) for i in arr]
    for i in range(0, len(arr), 20):
        await asyncio.gather(*arr[i:i+20])

async def get_tokens_by_goplus_for_trades():
    with open('chains_by_number_only_for_mexc.json') as f: 
        chains = json.load(f)
    tokens = await tokens_mexc_by_chains_db.get_all()
    trades = await trades_redis.get_all()
    trades = {i["symbol"] for i in trades} if trades else set()
    
    tokens = [i for i in tokens if f'{i["coin"]}USDT' in trades]
    flag = 1
    
    for v in tokens:
        networkList = v.get("networkList")
        if not networkList:
            continue
        
        for i in networkList:

            chain_number = chains.get(i["network"])
            if not chain_number:
                continue

            contract_address = i.get("contract")
            if not contract_address:
                continue

            while True:
                count = await goplus_db.count("contract_address", contract_address.lower())
                if count > 1:
                    await goplus_db.delete("contract_address", contract_address.lower())
                    continue
                break
                

            if flag==1:
                proxies="socks5://proxy_user:wcPYZj5Zlj@62.133.62.154:41257"
                flag = 2
            elif flag==2:
                proxies=None
                flag = 3
            else:
                proxies="socks5://FH6kGDAALu:q8iRUSt1lz@185.200.188.109:54604"
                flag = 1
            try:
                async with httpx.AsyncClient(mounts={"https://": httpx.AsyncHTTPTransport(proxy=proxies, verify=False)}) as client:
                    resp = await client.get(f'https://api.gopluslabs.io/api/v1/token_security/{chain_number}?contract_addresses={contract_address}')
                    resp = resp.json()["result"][f"{contract_address.lower()}"]
                dictionary = {
                    "contract_address": contract_address.lower()
                }
                dictionary.update(resp)
                await goplus_db.update("contract_address", contract_address.lower(), dictionary, True)
            except Exception as e:
                print(e)

    

async def get_tokens_by_goplus():
    with open('chains_by_number_only_for_mexc.json') as f: 
        chains = json.load(f)
    tokens = await tokens_mexc_by_chains_db.get_all()
    flag = 1
    
    for v in tokens:
        networkList = v.get("networkList")
        if not networkList:
            continue
        
        for i in networkList:

            chain_number = chains.get(i["network"])
            if not chain_number:
                continue

            contract_address = i.get("contract")
            if not contract_address:
                continue

            while True:
                count = await goplus_db.count("contract_address", contract_address.lower())
                if count > 1:
                    await goplus_db.delete("contract_address", contract_address.lower())
                    continue
                break
                

            if flag==1:
                proxies="socks5://proxy_user:wcPYZj5Zlj@62.133.62.154:41257"
                flag = 2
            elif flag==2:
                proxies=None
                flag = 3
            else:
                proxies="socks5://FH6kGDAALu:q8iRUSt1lz@185.200.188.109:54604"
                flag = 1
            try:
                async with httpx.AsyncClient(mounts={"https://": httpx.AsyncHTTPTransport(proxy=proxies, verify=False)}) as client:
                    resp = await client.get(f'https://api.gopluslabs.io/api/v1/token_security/{chain_number}?contract_addresses={contract_address}')
                    resp = resp.json()["result"][f"{contract_address.lower()}"]
                dictionary = {
                    "contract_address": contract_address.lower()
                }
                dictionary.update(resp)
                await goplus_db.update("contract_address", contract_address.lower(), dictionary, True)
            except Exception as e:
                print(e)




async def actualize():
    await get_pairs()
    await get_decimals_mexc()
    await get_tokens_mexc_by_chains()
    await get_tokens_by_goplus_for_trades()
