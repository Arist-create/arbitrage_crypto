from web3 import Web3
import json
from redis import redis

async def get_gas_price(rpc_url):
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    gas = w3.eth.gas_price
    return gas

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
    await redis.set("chains_by_gas_price", json.dumps(dictionary))
        


    