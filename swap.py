
import json
import asyncio
import httpx
from redis import redis
from mongo import goplus_db, list_of_pairs_mexc_db
import datetime
from commission_for_chains import get_gas_price_in_usdt

proxy_mounts={"https://": httpx.AsyncHTTPTransport(proxy="socks5://proxy_user:wcPYZj5Zlj@62.133.62.154:41257")}

async def fetch(client, chain_number, sell_token, buy_token, amount):
    resp = await client.get(f'https://api-defillama.1inch.io/v5.2/{chain_number}/quote?src={sell_token}&dst={buy_token}&amount={amount}&includeGas=true')
    return resp.json()


async def get_eth_price(client):
    resp = await client.get('https://api-defillama.1inch.io/v5.2/1/quote?src=0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE&dst=0xdac17f958d2ee523a2206206994597c13d831ec7&amount=3000000000000000000&includeGas=true')
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

async def fetch_volume(coin, withdraw_fee):
    vol = await redis.get(f'{coin}USDT@MEXC')
    if not vol:
        return None
    vol, _ = await calculate_vol(json.loads(vol)['asks'])
    vol -= float(withdraw_fee)
    return vol


async def main():
    with open('chains_by_number_only_for_mexc.json') as f:
        chains = json.load(f)
    while True:
        await get_gas_price_in_usdt()
        pairs = await list_of_pairs_mexc_db.get_all()
        with open('tokens_mexc_by_chains.json') as f:
            tokens_with_and_dep = json.load(f)
        usdt_token = tokens_with_and_dep['USDT']
        with open('chains_by_gas_price.json') as f:
            gas_price = json.load(f)
        
        tasks = []
        for pair in pairs:
            main_token = tokens_with_and_dep[pair["symbol"][:-4]]
            tasks.append(check_prices(
                main_token,
                usdt_token,
                chains,
                gas_price
            ))
            if len(tasks) > 50:
                await asyncio.gather(*tasks)
                tasks = []
                
        if tasks:
            await asyncio.gather(*tasks)



async def check_prices(main_token, usdt_token, chains, gas_price):
    try:
        max_tokens = 0
        max_usdt = 0
        dictionary = {}
        for i in main_token['networkList']:
            chain_number = chains.get(i['network'])
            if not chain_number:
                continue

            contract_address = i.get('contract')
            if not contract_address:
                continue

            if i.get("withdrawTips") or i.get("depositTips"):
                continue

            goplus = await goplus_db.get("contract_address", contract_address.lower())
            if not goplus:
                continue
            if (goplus.get("is_anti_whale", 0) == 1) or (goplus.get("is_honeypot", 0) == 1) or (goplus.get("cannot_buy", 0) == 1) or (goplus.get("cannot_sell_all", 0) == 1):
                continue


            decimals = i.get('decimals')
            if not decimals:
                continue

            usdt_token_detect = [j for j in usdt_token['networkList'] if j['network'] == i['network']][0]


            amount = await fetch_volume(i["coin"], i["withdrawFee"])
            if amount is None:
                continue
            amount = format(amount*10**decimals, '.0f')
            print(amount)
            async with httpx.AsyncClient(
                # mounts=proxy_mounts
                verify=False
            ) as client:
                resp = await fetch(client, chain_number, contract_address, usdt_token_detect["contract"], amount)
                if not resp.get("toAmount"):
                    continue
                check = float(resp['toAmount'])/10**usdt_token_detect["decimals"] - float(resp["gas"])*gas_price[i["network"]]
                if check > max_usdt:
                    max_usdt = check
                    dictionary["gas_sell"] = float(resp['gas'])
                    dictionary["sell"] = float(resp['toAmount'])/10**usdt_token_detect["decimals"]
                    dictionary["chain_sell"] = i["network"]
                amount_usdt = 3000*10**usdt_token_detect["decimals"]
                resp = await fetch(client, chain_number, usdt_token_detect["contract"], contract_address, amount_usdt)
                if not resp.get("toAmount"):
                    continue
                check = float(resp['toAmount'])/10**decimals - float(resp["gas"])*gas_price[i["network"]]
                if check > max_tokens:
                    max_tokens = check
                    dictionary["gas_buy"] = float(resp['gas'])
                    dictionary["buy"] = float(resp['toAmount'])/10**decimals
                    dictionary["chain_buy"] = i["network"]

        if not dictionary.get("sell") or not dictionary.get("buy"):
            return
        
        await redis.set(
                    f'{i["coin"]}USDT@1INCH',
                    json.dumps(
                        [
                            {'sell': int(dictionary["sell"]), "gas": dictionary["gas_sell"], "chain": dictionary["chain_sell"]},
                            {'buy': int(dictionary["buy"]), "gas": dictionary["gas_buy"], "chain": dictionary["chain_buy"]},
                            datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        ]
                    )
                )
    except Exception as e:
        print(e)

        
if __name__ == '__main__':
    asyncio.run(main())
    
    
