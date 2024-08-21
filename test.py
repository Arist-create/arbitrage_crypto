# import requests
# import json

# url = "https://api.coingecko.com/api/v3/coins/list?include_platform=true&status=active"

# headers = {
#     "accept": "application/json",
#     "x-cg-pro-api-key": "CG-DPuxKumEeJL3Lt2FxW77CqqF"
# }

# response = requests.get(url, headers=headers)
# response = response.json()

# with open('list_of_tokens_cg.json', 'w') as f:
#     json.dump(response, f, indent=4)
# print(len(response))

# from moralis import evm_api
# import json

# with open('list_of_tokens_cg.json', 'r') as f:
#     response = json.load(f)
# array = [i["platforms"]["ethereum"] for i in response if i["platforms"].get("ethereum")]
# print(len(array))
# arr_finish = []
# api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJub25jZSI6IjY4YWQyY2I0LWFiOGYtNGQzNi04MzhiLTQ5NzE3MjU4ZDVjMiIsIm9yZ0lkIjoiMzgyNjg1IiwidXNlcklkIjoiMzkzMjEyIiwidHlwZUlkIjoiZjc5ZDIzNGYtMzA1Mi00NTdmLWFmMTEtM2M3OTY2ZjRmMjdlIiwidHlwZSI6IlBST0pFQ1QiLCJpYXQiOjE3MTAzNzEyNDYsImV4cCI6NDg2NjEzMTI0Nn0.QTF_4SqSYdPjS0UtzKKvYH5n3EMy97IZwa6t1yg0mws"
# for i in range(0, len(array), 10):
#     print(i)
#     params = {
#         "addresses": array[i:i+10],
#         "chain": "eth"
#     }

#     result = evm_api.token.get_token_metadata(
#         api_key=api_key,
#         params=params,
#     )

#     arr_finish.append(result)
# with open('list_of_tokens_moralis.json', 'w') as f:
#     json.dump(arr_finish, f, indent=4)
# print(len(result))

# import json

# with open('list_of_tokens_moralis.json', 'r') as f:
#     response = json.load(f)
# arr = []
# for i in response:
#     arr.extend(i)
# with open('list_of_tokens_moralis_new.json', 'w') as f:
#     json.dump(arr, f, indent=4)

# q = 238874646354674635
# print(int(q)/10**18)
# from web3 import Web3


# rpc_url = "https://rpc.ankr.com/eth" 
# web_3 = Web3(Web3.HTTPProvider(rpc_url))
# one_eth = 3276464013
# web_3 = Web3(Web3.HTTPProvider(rpc_url))
# gas = web_3.eth.gas_price/10**18
# mn = gas*one_eth

# print(mn)


# proxies = {
#     'https': 'socks5://199.187.210.54:4145',

# }

# import httpx
# import asyncio
# import json

# async def make_req(client):
#     url = 'https://api.cow.fi/mainnet/api/v1/quote'
#     data = {"sellToken": "0xdac17f958d2ee523a2206206994597c13d831ec7",
#                       "appData": "0xf249b3db926aa5b5a1b18f3fec86b9cc99b9a8a99ad7e8034242d2838ae97422",
#                       "buyToken": "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
#                       "buyTokenBalance": "erc20",
#                       "from": "0x2f30Fc17AE05Ad5Aa17949C3C3E22C9d98C7930e",
#                       "kind": "sell",
#                       "onchainOrder": False,
#                       "partiallyFillable": False,
#                       "receiver": "0x2f30Fc17AE05Ad5Aa17949C3C3E22C9d98C7930e",
#                       "sellAmountBeforeFee": "1000000000",
#                       "sellToken": "0xdac17f958d2ee523a2206206994597c13d831ec7",
#                       "sellTokenBalance": "erc20",
#                       "signingScheme": "eip712"
#                       }
#     resp = await client.post(url, data=json.dumps(data))
#     print(resp.text)

# async def get_quote():
#     tasks = []
#     async with httpx.AsyncClient(
#         limits=httpx.Limits(max_keepalive_connections=600, max_connections=600), timeout=40, mounts={"https://": httpx.AsyncHTTPTransport(proxy="socks5://bmWEur:eFWBjr@209.46.2.35:8000", verify=False)}, verify=False
#     ) as client:
#         for i in range(100):
#             tasks.append(make_req(client))
#         await asyncio.gather(*tasks)


# asyncio.run(get_quote())
# import requests
# import json

# resp = requests.get('https://www.mexc.com/open/api/v2/market/coin/list')
# with open('list_of_deposit_and_withdraw_tokens_mexc.json', 'w') as f:

# print(json.dumps(resp.json(), indent=4))


# import httpx
# import asyncio

# proxy_mounts={"https://": httpx.AsyncHTTPTransport(proxy="socks5://bmWEur:eFWBjr@209.46.2.35:8000", verify=False)}

# async def fetch(session, url):
#     try:
#         resp = await session.get(url)
#         return resp.json()
#     except Exception as e:
#         print(e)

# async def main(urls):
#     async with httpx.AsyncClient(limits=httpx.Limits(max_keepalive_connections=None, max_connections=None), timeout=60, mounts=proxy_mounts, verify=False) as session:
#         tasks = [fetch(session, url) for url in urls]
#         results = await asyncio.gather(*tasks)
#         print(results)




# urls = ["https://api-defillama.1inch.io/v5.2/1/quote?src=0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE&dst=0xdac17f958d2ee523a2206206994597c13d831ec7&amount=10000000000000000000&includeGas=true"] * 500
# asyncio.run(main(urls))

# Все результаты собраны в список results



# import json
# with open('list_of_deposit_and_withdraw_tokens_mexc.json') as f:
#     tokens = json.load(f)

# with open('list_of_tokens_cg.json') as f:
#     tokens_2 = json.load(f)


# arr = []
# for i in tokens:
#     for j in tokens_2:
#         try:
#             a = j["platforms"]["ethereum"]
#         except:
#             continue
#         if i["currency"] == j["symbol"].upper() and (i["full_name"] == j["name"] or i["full_name"] == j["name"].upper() or i["full_name"].upper() == j["name"]):
#                 for chain in i["coins"]:
#                     if chain["chain"] == "Ethereum(ERC20)":
#                         chain["address"] = j["platforms"]["ethereum"]
#                 arr.append(i)
# print(len(arr))

# with open('list_of_tokens_cg_and_mexc_plus.json', 'w') as f:
#     json.dump(arr, f, indent=4)



# import requests
# import json
# import httpx
# import asyncio

# async def fetch(session, url):
#     try:
#         resp = await session.get(url)
#         return resp.json()["result"]
#     except Exception as e:
#         print(e)
# async def main():
#     with open('list_of_tokens_with_and_dep_mexc_plus.json') as f:
#         tokens = json.load(f)
#     dictionary = {}
#     for j in tokens:
#             for i in j["coins"]:
#                 if i["chain"] == "Ethereum(ERC20)":
#                     dictionary[i["address"]] = j["currency"]
                    
#     arr = list(dictionary.keys())
#     dictionary_finish = []
#     async with httpx.AsyncClient(
#                         limits=httpx.Limits(max_keepalive_connections=3000, max_connections=3000),
#                         timeout=60,
#                         verify=False,
#                         mounts={"https://": httpx.AsyncHTTPTransport(proxy="socks5://bmWEur:eFWBjr@209.46.2.35:8000", verify=False)}
#                     ) as client:
#         tasks = []
#         results = []
#         for i in arr:
#             await asyncio.sleep(0.5)
#             tasks.append(fetch(client, f"https://api.gopluslabs.io/api/v1/token_security/1?contract_addresses={i}"))
#             if len(tasks) > 1:
#                 result = await asyncio.gather(*tasks)
#                 results.extend(result)
#                 tasks = []
#         if tasks:
#             result = await asyncio.gather(*tasks)
#             results.extend(result)


#     for j in results:
#         try:
#             dictionary_finish.append(j)
#         except Exception as e:
#             print(e)

#     print(len(dictionary_finish))
#     with open('list_of_tokens_goplus.json', 'w') as f:
#         json.dump(dictionary_finish, f, indent=4)


# asyncio.run(main())

# from goplus.token import Token
# import json
# with open('list_of_tokens_cg_and_mexc_plus.json') as f:
#     tokens = json.load(f)
# dictionary = {}
# for j in tokens:
#         for i in j["coins"]:
#             if i["chain"] == "Ethereum(ERC20)":
#                 dictionary[i["address"]] = j["currency"]
                
# arr = list(dictionary.keys())
# for i in range(0, len(arr), 10):
#     data = Token(access_token=None).token_security(
#         chain_id="1", addresses=arr[i:i+10]
#     )
#     print(len(data.result.keys()))
#     for k, v in data.result.items():
#         dictionary[k] = v.__dict__
#         print(v.__dict__)
   
# with open('list_of_tokens_goplus.json', 'w') as f:
#     json.dump(data.get("result"), f, indent=4)

# import json
# import requests
# import time

# with open ('list_of_tokens_mexc.json') as f:
#     tokens = json.load(f)

# resp = requests.get(
#         'https://www.mexc.com/open/api/v2/market/symbols',
#         headers={
#             'Accept': 'application/json', 
#             'Content-Type': 'application/json', 
#             'X-MEXC-APIKEY': 'mx0vglNJacXHNmGojb',
#         }
#     )
# resp = resp.json()["data"]

# tokens = [
#     i
#     for i in resp
#     if i['state'] == 'ENABLED'
#     and i.get('symbol')[-4:] == 'USDT'
# ]
# print(len(tokens))
# for i in tokens:
#     i["symbol"] = i["symbol"].replace('_USDT', 'USDT')
# # сохранить список в json файл
# # with open('list_of_tokens_mexc.json', 'w') as f:
# #     json.dump(arr, f, indent=4)
# # return arr

# arr = [i["symbol"][:-4] for i in tokens]
# print(len(arr))
# arr_fin = {}
# for i in arr:
#     try:
#         resp = requests.get(
#             f"https://www.mexc.com/api/platform/asset/api/asset/spot/currency/v3?currency={i}", headers={"Baggage": "sentry-environment=prd,sentry-release=production%20-%20v3.264.27%20-%20ad19e7f,sentry-public_key=5594a84400b54fcaa39ef63446eb004f,sentry-trace_id=9fbce1cf88174c07984a0ef6a23ed1e6,sentry-sample_rate=0.1,sentry-transaction=%2Fassets%2Fwithdraw%2F%5B%5B...token%5D%5D,sentry-sampled=true",
#                                                                                                         "Cookie": 'g_state={"i_p":1708557027484,"i_l":1}; _ga=GA1.1.1594787517.1708549852; mxc_reset_tradingview_key=false; NEXT_LOCALE=ru-RU; mxc_display_format=indented; mexc_fingerprint_visitorId=36d706161411334438476293a75d26cc; mexc_fingerprint_requestId=; _fbp=fb.1.1721518766371.536432910168625978; mexc_exchange_orderbook_col3=quan; x-mxc-fingerprint=8f3c0f7e45d4b93e6ef291afdcf4bfc6; uc_token=WEBb7bdf0f4c5192971d5107e7eaa0537fe9a04676725e01b61a763f08311a285cd; u_id=WEBb7bdf0f4c5192971d5107e7eaa0537fe9a04676725e01b61a763f08311a285cd; mxc_exchange_order_confirmation=[100,101]; mexc_invite_code=mexc-1nZC1; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%22c338470278154d4baccbaac43f5f4440%22%2C%22first_id%22%3A%2218dcd81c54c862-0a34f4b144c22-76325b51-1296000-18dcd81c54db2c%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_utm_source%22%3A%22mexc%22%2C%22%24latest_utm_medium%22%3A%22internalmsg%22%2C%22%24latest_utm_campaign%22%3A%22bonus_mday20240726%22%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMThkY2Q4MWM1NGM4NjItMGEzNGY0YjE0NGMyMi03NjMyNWI1MS0xMjk2MDAwLTE4ZGNkODFjNTRkYjJjIiwiJGlkZW50aXR5X2xvZ2luX2lkIjoiYzMzODQ3MDI3ODE1NGQ0YmFjY2JhYWM0M2Y1ZjQ0NDAifQ%3D%3D%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%24identity_login_id%22%2C%22value%22%3A%22c338470278154d4baccbaac43f5f4440%22%7D%2C%22%24device_id%22%3A%2218dcd81c54c862-0a34f4b144c22-76325b51-1296000-18dcd81c54db2c%22%7D; bm_sz=89EFD2264D6AB60042E0E167A68BDD48~YAAQr5oQAvd5v9qQAQAA22Dy+RjcQw3KqEkQf/N1aK0C6HINP2cRtdev24Zt3A7+lp2OBxHfDm7m/XbdCz2+zeEhzSVlfUi4tEFuIkeEcGTMPOFGmu1VUh19iQHt4jBDbqSsN8IGb310SOSovFey2bgktHdlQ1orMUVGR+c+4nD0tcmMRiG4ulRI6a1zDKx5KdvhjW5JAVnGkTZVDRZ0lyzn0SGdTZhn2/FYKJEfwhO96hn7WNK7l63bp0Cruzkw7YU8BWqU+lj88BdwcqpeIQz2YWCDdD2xjCa79WXfgsLurrINQENjUBWIQQe8P+QSWsyZYHWDcjlsXI/GzyclvW2/FPOmoFseeXZS6S5gy0I5q9UwHEy1sQBteBymqU6tUwzCWtYs4wn42oBAo39UUcF6NP8u73Zvf73jKLwWEkkaLifv2orNwmVNffRYB9bPwlHB1c+IVGjIHBDyx30jHYOQDynIpJ9tqdH2T+V1Gbk01Sj32Nlb6fTflHm7ridl2yaunt0ci1RJ2e+eTqTybv2Bo5VXe51VFyObXhPWK/c149bIvdTCyybyIc33qb3ulzbC36J7MWwF~3617603~3225136; bm_mi=A0FAF22C5C8637424528574FAA04E467~YAAQZ5oQAotXireQAQAAVZNY+hi4iPGsS76oLDdgYAM+IDzb0g7qQ83Yt629zhORjaSGfsh/4usA1nX8zL0fpBtlMfM4HtqMd7fDYrCC0PF7HVSUtfpVLa6pdaH3QWEgNjHj7JXXMl4TDbQjYb/QX9h79Arh8JQR7dXQ5A/YSbo78N4xs6yEJKZQQYigvZTSQymn93Z5IfKqU7HvgS6ZmhER2nadnYa1J9U023EbY+7aX6Sav6WkTZ4xDyLkA7w7U0NA4G6PEBsvLlQywm427/8t6veMG/qdNakVRwH2eAsRgnN9TgfyBt21TDVUerFOn935HfehaFSpDaRDfpOaEA==~1; _rdt_uuid=1708549852484.7620f9f3-be2f-4d0e-b063-cc404a69bd84; bm_sv=4281DBA41B9BD4F9EAC90D347A84DA9C~YAAQZ5oQAuxYireQAQAAMc5Y+hiTeenwYTfnh3PKYRMZA/7ngi66yqTJHtzpUyKKUjee9XtqVBAkULbSWXfXMsMCQSAazMHw8EyicCPTuoa43EmMTKA5wZ2hqBTrdA2ttyhKh6IbvHmgKZ3uLTad3q4T84uKRJPdlDIo3pZJ/rjH1Xoxu82hk2DYt+3NYbywk32NpQ7aP1o/JzdeJjsP+BquFklqSwnBQ0qxIa+EoGZBkKPUoPzCWw+t7tt73oLf~1; ak_bmsc=72A776521C1A3B25D54F86A8382F3241~000000000000000000000000000000~YAAQZ5oQAg1ZireQAQAAstNY+hiKZ/dXii534GEISmgQY6yzWeIUHFxY7kJ6JzJVjH5H9SidZnYjIZGwXe/SJ+bL+Qe427ZN8dMm6NKr4OgMfzZ1FxvxTXz+C6G6lDKu4w8BohIVowmvf1RH1qfZb9XgiAYMTvuJSRFaSidP3w4jutlps6oTd3t9Vmz4bB6RM2dE4rw1x03HDQEvqLvC8pcxZ4rVa1CG5OHWOLEIxaDdRSOOZ7C2k8fttl+LhQMDWbpm5yuSu5lzMhH+KKeOOb5hgoAVEhtT/aefsB4SKHMvJ1wrHkbZT5ZJJeYhlAEBSMMokk3NEtMKEVb7K5GJauMjMicwoiE1NUdHcTp8rOpua2AB9+iGSABa/wiTaw795X/ntY6IW8j3S21MezDsYvB6xnxi11gWM4wXXuwXELn/JgL1cGIOkzIV4ZxyxIvdLlUDZk4dJ8YxdP3C9HkmGuO9nQ70hRvMjMsHdVnY1Uj05NRpSW/KOycE6KvL+AQxz1yt/YvJ; _ga_L6XJCQTK75=GS1.1.1722187000.103.1.1722187073.60.0.0; _abck=3E77D4A76F3F4D27C5E64C854125B0F7~0~YAAQZ5oQAktaireQAQAAdk5Z+gxizJDqZfrh9qU9lSqYd084SGPP9iKdOZ5uka33Ruat1NvS5lktHw1rM7Tm+xn9bm/TNGog1uHSfLKzKpqy7ubAxARjtPQuQIz8+xngoxpGfIxR1H/OCTMmOLL3p22706ohVeFkRGlI+r4xFCZhIRT851QPylFNdwu6p5g3XohXErHnHQCx8vUYTxHP+8ROi1iOxcuGxGll6ZmhZj0XeFXnWxiD9eVgyB+YhN9IVzi6GorSo9NrkJQJFkOP2xJf12Y5Fn8Tk9T05R5Q98+3KCpQ7DAsg3abrMiNc0h8cB0L8d23273Pfy+emC29spW1HmUknUEKRohR71vyffk5OCfEfkKsyhCYWwEo6bm3aRDgdo3Bp9A8abw/hrDQTf9aifNxUDESFMAFK2GnX2XfmzVYU0+qyw==~-1~-1~-1; RT="z=1&dm=www.mexc.com&si=5730b7fb-7da2-4ff7-a1a2-f18de8776743&ss=lz5toghk&sl=2&tt=4ci&bcn=%2F%2F02179916.akstat.io%2F'}
#         )
#         arr_fin[i] = resp.json()["data"]
#         print(len(arr_fin.keys()))
#         time.sleep(0.5)
#     except:
#         pass

# with open ('list_of_tokens_mexc_with_addresses.json', 'w') as f:
#     json.dump(arr_fin, f, indent=4)

# import json 

# with open('list_of_tokens_mexc_with_addresses.json') as f:
#     tokens = json.load(f)
# arr = []
# for k, v in tokens.items():
#     for i in v["chains"]:
#         if i["chainName"] == "Ethereum(ERC20)":
#             arr.append(i)

# print(len(arr))
# import requests
# resp = requests.get('https://api.gopluslabs.io/api/v1/token_security/1?contract_addresses=0x043312456f73D8014D9b84f4337DE54995CD2A5B')
# # "https://api.gopluslabs.io/api/v1/token_security/1?contract_addresses=
# # 0x25bE643995fA9F077c7349FB78d13c5ee3fc11d6


# print(resp.json())
# import requests

# resp = requests.get(
#         'https://www.mexc.com/open/api/v2/market/symbols',
#         headers={
#             'Accept': 'application/json', 
#             'Content-Type': 'application/json', 
#             'X-MEXC-APIKEY': 'mx0vglNJacXHNmGojb',
#         }
#     )
# resp = resp.json()["data"]
# print(resp)

import certifi
print(certifi.where())