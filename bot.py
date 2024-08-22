
import time
from aiogram import types, executor
from aiogram import Bot, Dispatcher
from redis import redis
from mexc import get_tokens
import json
from web3 import Web3
from swap import get_eth_price
import datetime
import httpx
from mongo import trades_db, settings_db
API_TOKEN = '7473932480:AAHvJvYndS0-blMx8U-w57BBjMuUTl01E7E' #прод
# API_TOKEN = '6769001742:AAGW0d_60IymQPl8ef4U7Pvun3aIYf0aBPc'

bot = Bot(token=API_TOKEN)


dp = Dispatcher(bot)

async def calc_vol_in_usdt(arr):
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
    return total_cost, k

async def calc_vol_to_sell_on_mexc_in_usdt(arr, target_value):
    total_cost = 0.0
    total_volume = 0.0
    k = 0
    for i in arr:
        k += 1
        price = float(i['p'])
        volume = float(i['v'])
        value = price * volume
        if total_volume + volume >= target_value:
            volume_needed = target_value - total_volume
            remaining_value = volume_needed * price
            total_cost += remaining_value
            total_volume += volume_needed
            break
        else:
            total_cost += value
            total_volume += volume
    return total_cost, k

async def buy_on_mexc(mexc, one_inch, info, go_plus):
    if info["is_withdraw_enabled"] == False:
        return None, None
    mexc_vol, orders = await calc_vol_in_usdt(mexc['asks'])
    if mexc_vol < 3000:
        return None, None
    one_inch_vol = one_inch[0]['sell']
    one_inch_vol = one_inch_vol - (one_inch_vol * float(go_plus["sell_tax"]))
    gas = one_inch[0]['gas']
    profit = (one_inch_vol - mexc_vol) - gas
    return profit, orders
 
async def buy_on_one_inch(mexc, one_inch, info, gas_for_withdraw, go_plus):
    if info["is_deposit_enabled"] == False:
        return None, None
    one_inch_vol = one_inch[1]['buy']
    one_inch_vol = one_inch_vol - (one_inch_vol * float(go_plus["buy_tax"]))
    gas = one_inch[1]['gas']
    mexc_vol, orders = await calc_vol_to_sell_on_mexc_in_usdt(mexc['bids'], one_inch_vol)
    profit = (mexc_vol - 3000) - gas - gas_for_withdraw
    return profit, orders

@dp.message_handler(commands=['start'])
async def message_id(message: types.Message):
    await bot.send_message(message.chat.id, f"Message ID: {message.message_id}. Chat ID: {message.chat.id}.")

@dp.message_handler(commands=['show'])
async def message_id(message: types.Message):
    trades = trades_db.get_all()
    string = ""
    for trade in trades:
        string += f'{trade["symbol"]}: {trade["message"]}\n'

    await bot.send_message(message.chat.id, string)

@dp.message_handler(commands=['settings'])
async def message_id(message: types.Message):
    settings = settings_db.get("number", 1)
    if not settings:
        return
    string = ""
    for k, v in settings.items():
        string += f'{k}: {v}\n'

    await bot.send_message(message.chat.id, string)

@dp.message_handler(commands=['not'])
async def message_id(message: types.Message):
    while True:
        try:
            life_time_target = settings_db.get("number", 1)
            if not life_time_target:
                life_time_target = 0
            else:
                life_time_target = float(life_time_target["life_time_target"])
            arr = trades_db.get_all()
            if not arr:
                continue
            for trade in arr:
                if trade["notify"]:
                    continue
                life_time = datetime.datetime.now() - datetime.datetime.strptime(trade["start_time"], "%Y-%m-%d %H:%M:%S")
                if life_time.total_seconds() < life_time_target:
                    continue
                trades_db.update("symbol", trade["symbol"], {"notify": True})
                await bot.send_message(message.chat.id, f'{trade["symbol"]}: {trade["message"]}')
        except Exception as e:
            print(e)


@dp.message_handler(lambda message: message.text and ':' in message.text.lower())
async def message_id(message: types.Message):
    life_time_target = float(message.text[1:])
    check = settings_db.get("number", 1)
    if not check:
        settings_db.add({"life_time_target": 0.0, "number": 1})
    else:
        settings_db.update("number", 1, {"life_time_target": life_time_target})
    await bot.send_message(message.chat.id, "Done")

@dp.message_handler(lambda message: message.text and '.' in message.text.lower())
async def message_id(message: types.Message):
    target_profit = float(message.text[1:])
    check = settings_db.get("number", 1)
    if not check:
        settings_db.add({"target_profit": 0.0, "number": 1})
    else:
        settings_db.update("number", 1, {"target_profit": target_profit})
    await bot.send_message(message.chat.id, "Done")


@dp.message_handler(commands=['scan'])
async def message_id(message: types.Message):
    await bot.send_message(message.chat.id, "Scanning...")
    tokens = await get_tokens()
    while True:
        try:
            target_profit = settings_db.get("number", 1)
            if not target_profit:
                target_profit = 0
            else:
                target_profit = float(target_profit["target_profit"])
             
            rpc_url = "https://rpc.ankr.com/eth"
            async with httpx.AsyncClient(
                            limits=httpx.Limits(max_keepalive_connections=3000, max_connections=3000),
                            timeout=60,
                            verify=False,
                            mounts={"https://": httpx.AsyncHTTPTransport(proxy="socks5://proxy_user:wcPYZj5Zlj@62.133.62.154:41257", verify=False)}
                        ) as client:
                one_eth = await get_eth_price(client)
            web_3 = Web3(Web3.HTTPProvider(rpc_url))
            gas = web_3.eth.gas_price/10**18
            gas_for_withdraw = gas*int(one_eth["toAmount"])
            with open('list_of_tokens_with_and_dep_mexc_plus.json') as f:
                tokens_with_and_dep = json.load(f)
            dict_of_inf = {}
            for j in tokens_with_and_dep:
                for i in j["coins"]:
                    if i["chain"] == "Ethereum(ERC20)":
                        dict_of_inf[j["currency"]] = i
            with open("list_of_tokens_goplus.json") as f:
                go_plus = json.load(f)
            arr = set()
            start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            for token in tokens:
                try:
                    info = dict_of_inf[token['symbol'][:-4]]
                    one_inch = await redis.get(f'{token["symbol"]}@1INCH')
                    if not one_inch:
                        continue
                    one_inch = json.loads(one_inch)
                    mexc = await redis.get(f'{token["symbol"]}@MEXC')
                    mexc = json.loads(mexc)
                    for i in go_plus:
                        try:
                            go = i[info["address"].lower()] 
                            break
                        except:
                            continue
                    profit_mexc, orders_to_buy = await buy_on_mexc(mexc, one_inch, info, go)
            
                    profit_one_inch, orders_to_sell = await buy_on_one_inch(mexc, one_inch, info, gas_for_withdraw, go)
                    if profit_mexc and profit_one_inch:
                        if profit_mexc > target_profit or profit_one_inch > target_profit:
                            message = f'\n mexc: {float(profit_mexc):.2f} \n orders_to_buy: {orders_to_buy} \n one_inch: {float(profit_one_inch):.2f} \n orders_to_sell: {orders_to_sell}'
                            line = {"symbol": token["symbol"], 
                                    "message": message,
                                    "start_time": start_time,
                                    "notify": False}
                            check = trades_db.get("symbol", token["symbol"])
                            if not check:
                                trades_db.add(line)
                            trades_db.update("symbol", token["symbol"], {"message": message})
                            arr.add(line["symbol"])

                            # сделать удаление неактуальных арбитражей(если в списке нет этой пары то удалить её из монги)
                    else:
                        continue
                except Exception as e:
                    pass
            current_trades = trades_db.get_all()
            for i in current_trades:
                if i["symbol"] not in arr:
                    trades_db.delete("symbol", i["symbol"])
            

        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)
        
        


if __name__ == '__main__':
    # создать папку если её нет 
    while True:
        try:
            executor.start_polling(dp, skip_updates=True)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)