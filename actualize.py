
import requests
import json


async def check_deposit_and_withdraw_mexc():
    resp = requests.get(
        f"https://www.mexc.com/open/api/v2/market/coin/list",
        headers={
            'Accept': 'application/json', 
            'Content-Type': 'application/json', 
            'X-MEXC-APIKEY': 'mx0vglNJacXHNmGojb'
        }
    )
    resp = resp.json()['data']

    with open('list_of_deposit_and_withdraw_tokens_mexc.json', 'w') as f:
        json.dump(resp, f, indent=4)

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




async def actualize():
    await check_deposit_and_withdraw_mexc()
    with open('list_of_deposit_and_withdraw_tokens_mexc.json') as f:
        tokens = json.load(f)

    with open('list_of_tokens_mexc_with_addresses.json') as f:
        tokens_2 = json.load(f)
    arr = []


    for i in tokens:
        try:
            info = tokens_2[i["currency"]]
        except:
            continue
        for j in i["coins"]:
            if j["chain"] == "Ethereum(ERC20)":
                for chain in info["chains"]:
                    if chain["chainName"] == "Ethereum(ERC20)":
                        j["address"] = chain["contractAddress"]
                        arr.append(i)
                        break
                break

    with open('list_of_tokens_with_and_dep_mexc_plus.json', 'w') as f:
        json.dump(arr, f, indent=4)

async def get_token_address():
    await actualize()
    with open('list_of_tokens_mexc.json') as f1, open('list_of_tokens_with_and_dep_mexc_plus.json') as f2:
        arr = json.load(f1)
        arr_address = json.load(f2)
    symbol_to_address = {}
    for j in arr_address:
        for i in j["coins"]:
            if i["chain"] == "Ethereum(ERC20)":
                symbol_to_address[j["currency"]] = (i["address"], int(i["precision"]))

    
    for i in arr:
        if i['symbol'][:-4] in symbol_to_address:
            i['address'], i['decimals'] = symbol_to_address[i['symbol'][:-4]]
    return arr