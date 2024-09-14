import time
from aiogram import types, executor
from aiogram import Bot, Dispatcher 
from redis import redis
import json
from commission_for_chains import get_gas_price_in_usdt
import datetime
import asyncio
from mongo import trades_db, settings_db, goplus_db
API_TOKEN = '7473932480:AAHvJvYndS0-blMx8U-w57BBjMuUTl01E7E' #прод
# API_TOKEN = '6769001742:AAGW0d_60IymQPl8ef4U7Pvun3aIYf0aBPc'

bot = Bot(token=API_TOKEN)


dp = Dispatcher(bot)

async def calc_vol_in_usdt(arr):
    total_cost = 0.0
    target_value = 1000.0
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


async def buy_on_mexc(mexc, one_inch, info, goplus):
    if (goplus.get("is_anti_whale", 0) == 1) or (goplus.get("is_honeypot", 0) == 1) or (goplus.get("cannot_buy", 0) == 1) or (goplus.get("cannot_sell_all", 0) == 1):
        return None, None, None
    if info["withdrawEnable"] == False:
        return None, None, None
    mexc_vol, orders = await calc_vol_in_usdt(mexc['asks'])
    if mexc_vol < 1000:
        return None, None, None
    one_inch_vol = one_inch[0]['sell']

    with open('chains_by_gas_price.json') as f:
        chains_by_gas_price = json.load(f)
    gas_price = chains_by_gas_price[info["network"]]
    gas = one_inch[0]['gas']
    commission = gas_price * gas

    tax = goplus["sell_tax"]
    if tax == '':
        tax = 0
    one_inch_vol = one_inch_vol - (one_inch_vol * float(tax))

    profit = (one_inch_vol - mexc_vol) - commission

    return profit, orders, commission
 
async def buy_on_one_inch(mexc, one_inch, info, goplus):
    if (goplus.get("is_anti_whale", 0) == 1) or (goplus.get("is_honeypot", 0) == 1) or (goplus.get("cannot_buy", 0) == 1) or (goplus.get("cannot_sell_all", 0) == 1):
        return None, None, None, None
    if info["depositEnable"] == False:
        return None, None, None, None
    one_inch_vol = one_inch[1]['buy']

    tax = goplus["buy_tax"]
    if tax == '':
        tax = 0
    one_inch_vol = one_inch_vol - (one_inch_vol * float(tax))
    mexc_vol, orders = await calc_vol_to_sell_on_mexc_in_usdt(mexc['bids'], one_inch_vol)
    with open('chains_by_gas_price.json') as f:
        chains_by_gas_price = json.load(f)
    gas_price = chains_by_gas_price[info["network"]]
    gas = one_inch[1]['gas']
    commission = gas_price * gas
    gas_for_withdraw = gas_price * 21000
    profit = (mexc_vol - 1000) - commission - gas_for_withdraw

    return profit, orders, commission, gas_for_withdraw

@dp.message_handler(commands=['start'])
async def message_id(message: types.Message):
    await bot.send_message(message.chat.id, f"Message ID: {message.message_id}. Chat ID: {message.chat.id}.")

@dp.message_handler(commands=['show'])
async def message_id(message: types.Message):
    trades = await trades_db.get_all()
    string = ""
    for trade in trades:
        string += f'{trade["symbol"]}: {trade["message"]}\n'

    await bot.send_message(message.chat.id, string)

@dp.message_handler(commands=['settings'])
async def message_id(message: types.Message):
    settings = await settings_db.get("number", 1)
    if not settings:
        return
    string = ""
    for k, v in settings.items():
        string += f'{k}: {v}\n'

    await bot.send_message(message.chat.id, string)

@dp.message_handler(commands=['not'])
async def message_id(message: types.Message):
    while True:
        life_time_target = await settings_db.get("number", 1)
        if not life_time_target:
            life_time_target = 0
        else:
            life_time_target = float(life_time_target["life_time_target"])
        arr = await trades_db.get_all()
        if not arr:
            continue
        for trade in arr:
            if trade["notify"]:
                continue
            life_time = datetime.datetime.now() - datetime.datetime.strptime(trade["start_time"], "%Y-%m-%d %H:%M:%S")
            if life_time.total_seconds() < life_time_target:
                continue
            await trades_db.update("symbol", trade["symbol"], {"notify": True})
            await bot.send_message(message.chat.id, f'{trade["symbol"]}: {trade["message"]}')
        await asyncio.sleep(5)


@dp.message_handler(lambda message: message.text and ':' in message.text.lower())
async def message_id(message: types.Message):
    life_time_target = float(message.text[1:])
    check = await settings_db.get("number", 1)
    if not check:
        await settings_db.add({"life_time_target": 0.0, "number": 1})
    else:
        await settings_db.update("number", 1, {"life_time_target": life_time_target})
    await bot.send_message(message.chat.id, "Done")

@dp.message_handler(lambda message: message.text and '.' in message.text.lower())
async def message_id(message: types.Message):
    target_profit = float(message.text[1:])
    check = await settings_db.get("number", 1)
    if not check:
        await settings_db.add({"target_profit": 0.0, "number": 1})
    else:
        await settings_db.update("number", 1, {"target_profit": target_profit})
    await bot.send_message(message.chat.id, "Done")


@dp.message_handler(commands=['scan'])
async def message_id(message: types.Message):
    with open ('list_of_pairs_mexc.json') as f:
        pairs = json.load(f)
    await bot.send_message(message.chat.id, "Scanning...")
    while True:
        await get_gas_price_in_usdt()
        target_profit = await settings_db.get("number", 1)
        if not target_profit:
            target_profit = 0
        else:
            target_profit = float(target_profit["target_profit"])
        
        with open('tokens_mexc_by_chains.json') as f:
            tokens_with_and_dep = json.load(f)
        arr = set()
        start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for pair in pairs:
            one_inch = await redis.get(f'{pair["symbol"]}@1INCH')
            if not one_inch:
                continue
            one_inch = json.loads(one_inch)
            mexc = await redis.get(f'{pair["symbol"]}@MEXC')
            mexc = json.loads(mexc)
            info = tokens_with_and_dep[pair['symbol'][:-4]]["networkList"]
            if not one_inch[0].get("chain"):
                continue
            chain_buy = one_inch[0]["chain"]
            chain_sell = one_inch[1]["chain"]
            info_buy = [i for i in info if i["network"] == chain_buy][0]
            info_sell = [i for i in info if i["network"] == chain_sell][0]
            
            goplus_buy = await goplus_db.get("contract_address", info_buy["contract"].lower())
            goplus_sell = await goplus_db.get("contract_address", info_sell["contract"].lower())
            if not goplus_buy or not goplus_sell:
                continue

            profit_mexc, orders_to_buy, gas_buy = await buy_on_mexc(mexc, one_inch, info_buy, goplus_buy) 
            profit_one_inch, orders_to_sell, gas_sell, gas_for_withdraw = await buy_on_one_inch(mexc, one_inch, info_sell, goplus_sell)
            
            if not profit_mexc or not profit_one_inch:
                continue
            if profit_mexc < target_profit and profit_one_inch < target_profit:
                continue
            if info_buy.get("withdrawTips") or info_sell.get("withdrawTips") or info_buy.get("depositTips") or info_sell.get("depositTips"):
                continue
            message = f'\n mexc: {float(profit_mexc):.2f} \
                \n orders_to_buy: {orders_to_buy} \
                \n gas_buy: {gas_buy} \
                \n chain_buy: {chain_buy} \n \
                \n one_inch: {float(profit_one_inch):.2f} \
                \n orders_to_sell: {orders_to_sell} \
                \n gas_sell: {gas_sell} \
                \n gas_for_withdraw: {gas_for_withdraw} \
                \n chain_sell: {chain_sell} \n '
            line = {"symbol": pair["symbol"], 
                    "message": message,
                    "start_time": start_time,
                    "notify": False}
            check = await trades_db.get("symbol", pair["symbol"])
            if not check:
                await trades_db.add(line)
            await trades_db.update("symbol", pair["symbol"], {"message": message})
            arr.add(line["symbol"])

        current_trades = await trades_db.get_all()
        for i in current_trades:
            if i["symbol"] not in arr:
                await trades_db.delete("symbol", i["symbol"])

if __name__ == '__main__':
    while True:
        try:
            executor.start_polling(dp, skip_updates=True)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)