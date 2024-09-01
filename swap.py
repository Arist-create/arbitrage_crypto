
import json
import asyncio
import httpx
from redis import redis
from web3 import Web3
import datetime


proxy_mounts={"https://": httpx.AsyncHTTPTransport(proxy="socks5://proxy_user:wcPYZj5Zlj@62.133.62.154:41257")}

async def get_token_address():
    with open('list_of_pairs_mexc.json') as f1, open('tokens_mexc_by_chains.json') as f2:
        arr = json.load(f1)
        arr_address = json.load(f2)
    symbol_to_address = {}
    for j in arr_address.values():
        for i in j["networkList"]:
            if i["network"] == "Ethereum(ERC20)":
                if not i.get("decimals"):
                    continue
                symbol_to_address[i["coin"]] = (i["contract"], int(i["decimals"]))

    for i in arr:
        if i['symbol'][:-4] in symbol_to_address:
            i['contract'], i['decimals'] = symbol_to_address[i['symbol'][:-4]]
    return arr

async def set_results(results, mn, redis_client):

    dict_f = {arr[1]: arr for arr in results}
    for arr in results:
        token = arr[1]
        if token.endswith('_F'):
            continue
        i = dict_f[f'{token}_F']
        try:
            await redis_client.set(
                    f'{token}@1INCH',
                    json.dumps(
                        [
                            {'sell': int(arr[0]['toAmount'])/(10**i[2]), "gas": mn*arr[0]["gas"]},
                            {'buy': int(i[0]['toAmount'])/(10**arr[2]), "gas": mn*i[0]["gas"]},
                            datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        ]
                    )
                )
        except Exception as e:
            print(e)

async def fetch(client, token, token_2, amount, name, decimals):
    resp = await client.get(f'https://api-defillama.1inch.io/v5.2/1/quote?src={token}&dst={token_2}&amount={amount}&includeGas=true')
    return [resp.json(), name, decimals]
async def make_request(client, sell_token, buy_token, amount, amount_2, token, token_2, decimals, decimals_2, mn):
    try:
        tasks = []
        tasks.extend([fetch(client, sell_token, buy_token, amount, token, decimals), fetch(client, buy_token, sell_token, amount_2, token_2, decimals_2)])
        print(token)
        print(token_2)
        results = await asyncio.gather(*tasks)
        await set_results(results, mn, redis)
    except Exception as e:
        print(e)


async def get_eth_price(client):
    resp = await client.get('https://api-defillama.1inch.io/v5.2/1/quote?src=0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE&dst=0xdac17f958d2ee523a2206206994597c13d831ec7&amount=1000000000000000000&includeGas=true')
    return resp.json()
    

async def calculate_vol(arr):
    total_cost = 0.0
    target_value = 3000.0
    total_volume = 0.0
    k = 0
    for i in arr:
        k += 1
        price = float(i['p'])
        volume = float(i['v'])
        value = price * volume

        if total_cost + value >= target_value:
            remaining_value = target_value - total_cost
            volume_needed = remaining_value / price
            total_cost += remaining_value
            total_volume += volume_needed
            break
        else:
            total_cost += value
            total_volume += volume

    return total_volume, k

async def fetch_volume(redis, token, dict_of_inf):
    vol = await redis.get(f'{token["symbol"]}@MEXC')
    if vol:
        vol, _ = await calculate_vol(json.loads(vol)['asks'])
        vol -= float(dict_of_inf['withdrawFee'])
        return vol * (10 ** token['decimals'])
    return None


async def main():
    rpc_url = "https://rpc.ankr.com/eth"
    tokens = await get_token_address()
    while True:
        try:
            async with httpx.AsyncClient(
                    limits=httpx.Limits(max_keepalive_connections=3000, max_connections=3000),
                    timeout=60,
                    # mounts=proxy_mounts
                    verify=False
                ) as client:
                one_eth = await get_eth_price(client)
                one_eth = int(one_eth['toAmount'])/(10**6) 
                web_3 = Web3(Web3.HTTPProvider(rpc_url))
                gas = web_3.eth.gas_price/10**18
                mn = gas*one_eth

                with open('tokens_mexc_by_chains.json') as f:
                    tokens_with_and_dep = json.load(f)
                dict_of_inf = {}
                for v in tokens_with_and_dep.values():
                    for i in v["networkList"]:
                        if i["network"] == "Ethereum(ERC20)":
                            dict_of_inf[i["coin"]] = i

                tasks = []
                for token in tokens:
                    try:
                        _ = token['contract']
                    except:
                        continue
                    vol = await fetch_volume(redis, token, dict_of_inf[token["symbol"][:-4]])
                    if not vol:
                        continue
                    tasks.append(make_request( 
                            client,
                            token['contract'], 
                            '0xdac17f958d2ee523a2206206994597c13d831ec7', 
                            format(vol, '.0f'),
                            3000000000,
                            token["symbol"],
                            f'{token["symbol"]}_F', 
                            token['decimals'],
                            6,
                            mn
                        ))
                    if len(tasks) >= 10:
                        await asyncio.gather(*tasks)
                        tasks = []
                if tasks:
                    await asyncio.gather(*tasks)

        except Exception as e:
            print(e)


        
if __name__ == '__main__':
    while True:
        try:
            asyncio.run(main())
        except Exception as e:
            print(e)
    
