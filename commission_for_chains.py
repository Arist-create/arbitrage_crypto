from web3 import Web3
import json
from redis import redis

async def get_gas_price(rpc_url):
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    return w3.eth.gas_price

async def get_commission_token_price(pair):
    orders = await redis.get(pair)
    if not orders:
        return 0
    orders = json.loads(orders)
    price = float(orders["bids"][0]["p"])
    return price

    
async def get_gas_price_in_usdt():
    with open("chains_by_rpc_url.json") as f:
        urls = json.load(f)
    with open("chains_by_token_for_commission.json") as f:
        tokens = json.load(f)
    dictionary = {}
    for chain_name, url in urls.items():
        gas_price = await get_gas_price(url)
        gas_price = gas_price/10**18
        token = tokens.get(chain_name)
        pair = token+"USDT@MEXC"
        token_price = await get_commission_token_price(pair)
        commission = gas_price*token_price
        dictionary[chain_name] = commission
    with open("chains_by_gas_price.json", "w") as f:
        json.dump(dictionary, f, indent=4)
        

# async def get_commission_for_withdraw(chain_name):
#     with open("chains_by_rpc_url.json") as f:
#         urls = json.load(f)
#     url = urls.get(chain_name)
#     if not url:
#         return 0
#     gas_price = await get_gas_price(url)
#     gas_price = gas_price*21000/10**18
#     with open("chains_by_token_for_commission.json") as f:
#         tokens = json.load(f)
#     token = tokens.get(chain_name)
#     if not token:
#         return 0
#     pair = token+"USDT@MEXC"
#     token_price = await get_commission_token_price(pair)
#     return gas_price * token_price
    


    