from bot import bot, create_keyboard_for_notify
import time
import asyncio
import json
from mongo import list_of_pairs_mexc_db, tokens_mexc_by_chains_db, goplus_db, users_settings_db
from redis_facade import redis, trades_redis
import datetime
import traceback


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
        total_cost += value
        total_volume += volume

    return total_cost, k


async def buy_on_mexc(mexc, one_inch, info, goplus, chains_by_gas_price):
    if info["withdrawEnable"] == False:
        return None, None, None, None
    
    mexc_vol, orders = await calc_vol_in_usdt(mexc['asks'])
    if mexc_vol < 3000:
        return None, None, None, None
    
    one_inch_vol = one_inch[0]['sell'] 
    tax = goplus["sell_tax"]
    if tax == '':
        tax = 0

    one_inch_vol -= one_inch_vol * float(tax)

    gas_price = chains_by_gas_price[info["network"]]
    gas = one_inch[0]['gas']
    commission = gas_price * gas
    gas_for_withdraw = gas_price * 21000

    profit = one_inch_vol - mexc_vol - commission - gas_for_withdraw

    return profit, orders, commission, gas_for_withdraw

async def buy_on_one_inch(mexc, one_inch, info, goplus, chains_by_gas_price):
    if info["depositEnable"] == False:
        return None, None, None, None
    
    one_inch_vol = one_inch[1]['buy']
    tax = goplus["buy_tax"]
    if tax == '':
        tax = 0
    one_inch_vol -= one_inch_vol * float(tax)

    mexc_vol, orders = await calc_vol_to_sell_on_mexc_in_usdt(mexc['bids'], one_inch_vol)

    gas_price = chains_by_gas_price[info["network"]]
    gas = one_inch[1]['gas']
    commission = gas_price * gas
    gas_for_withdraw = gas_price * 21000
    
    profit = mexc_vol - 3000 - commission - gas_for_withdraw

    return profit, orders, commission, gas_for_withdraw

async def notify():
    while True:
        settings = await users_settings_db.get_all() 
        arr = await trades_redis.get_all()
        if len(arr) == 0:
            continue
        for user_settings in settings:
            notify_is_on = user_settings["notify_is_on"]
            if not notify_is_on:
                continue
            chat_id = user_settings["chat_id"]
            life_time_target = float(user_settings["life_time_target"])
            target_profit = float(user_settings["target_profit"])
            for i in arr:
                life_time = i["lifetime"]
                if chat_id in i["notify"]:
                    continue
                if life_time < life_time_target:
                    continue
                if i["profit"] < target_profit:
                    continue
                try:
                    keyboard = await create_keyboard_for_notify(i["symbol"])
                    await bot.send_message(chat_id, i["message"], parse_mode='Markdown', reply_markup=keyboard)
                    i["notify"] = i["notify"] + [chat_id]
                    await trades_redis.set(i["symbol"], json.dumps(i))
                except Exception as e:
                    print(e)
                await asyncio.sleep(3)

async def scan():
    await bot.send_message(1317668838, "Hello")
    with open('chains_by_number_only_for_mexc.json') as f:
        chains_by_number = json.load(f)
    with open('chains_for_defilama.json') as f:
        chains_for_defilama = json.load(f)
    while True:
        pairs = await list_of_pairs_mexc_db.get_all()
        target_profit = 0
        tokens_info = await tokens_mexc_by_chains_db.get_all()
        usdt_addresses = [i for i in tokens_info if i["coin"] == "USDT"][0]["networkList"]
        
        goplus = await goplus_db.get_all()
        trades = await trades_redis.get_all()

        chains_by_gas_price = await redis.get("chains_by_gas_price")
        if not chains_by_gas_price:
            continue
        chains_by_gas_price = json.loads(chains_by_gas_price)
        arr = set()
        tasks = []
        for pair in pairs:
            symbol = pair["symbol"]
            if symbol in ["SEILORUSDT"]:
                continue
            trade = next((i for i in trades if i["symbol"] == symbol), None)
            tasks.append(get_profit(symbol, tokens_info, target_profit, chains_by_gas_price, goplus, trade, chains_by_number, usdt_addresses, chains_for_defilama))
            if len(tasks) > 10:
                results = await asyncio.gather(*tasks)
                for result in results:
                    if not result:
                        continue
                    arr.add(result)
                tasks = []

        if tasks:
            results = await asyncio.gather(*tasks)
            for result in results:
                if not result:
                    continue
                arr.add(result)

        current_trades = await trades_redis.get_all()
        for i in current_trades:
            if i["symbol"] in arr:
                continue
            await trades_redis.delete(i["symbol"])



async def get_profit(symbol, tokens_info, target_profit, chains_by_gas_price, goplus, trade, chains_by_number, usdt_addresses, chains_for_defilama):
    start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    one_inch = await redis.get(f'{symbol}@1INCH')
    if not one_inch:
        return None
    one_inch = json.loads(one_inch)
    mexc = await redis.get(f'{symbol}@MEXC')
    mexc = json.loads(mexc)
    info = [i for i in tokens_info if i["coin"] == symbol[:-4]][0]["networkList"]

    chain_buy = one_inch[0]["chain"]
    chain_sell = one_inch[1]["chain"]
    usdt_address_buy = [i for i in usdt_addresses if i["network"] == chain_buy][0]["contract"]
    usdt_address_sell = [i for i in usdt_addresses if i["network"] == chain_sell][0]["contract"]
    info_buy = next((i for i in info if i["network"] == chain_buy), None)
    info_sell = next((i for i in info if i["network"] == chain_sell), None)
    if not info_buy or not info_sell:
        return None
    if info_buy.get("withdrawTips") or info_sell.get("withdrawTips") or info_buy.get("depositTips") or info_sell.get("depositTips"):
        return None
    
    goplus_buy = next((i for i in goplus if i["contract_address"] == info_buy["contract"].lower()), None)
    goplus_sell = next((i for i in goplus if i["contract_address"] == info_sell["contract"].lower()), None)
    if not goplus_buy or not goplus_sell:
        return None

    profit_mexc, orders_to_buy, gas_sell, gas_for_withdraw_sell = await buy_on_mexc(mexc, one_inch, info_buy, goplus_buy, chains_by_gas_price) 
    if not profit_mexc:
        return None
    profit_one_inch, orders_to_sell, gas_buy, gas_for_withdraw_buy = await buy_on_one_inch(mexc, one_inch, info_sell, goplus_sell, chains_by_gas_price)
    if not profit_one_inch:
        return None
    
    last_time = trade["start_time"] if trade else start_time
    life_time = datetime.datetime.now() - datetime.datetime.strptime(last_time, "%Y-%m-%d %H:%M:%S")
    total_seconds = int(life_time.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    # Форматируем строку
    formatted_time_difference = f"{hours:02}:{minutes:02}:{seconds:02}"
    
    if profit_one_inch >= target_profit:
        profit = profit_one_inch
        message = (f'*{symbol[:-4]}/USDT({chain_sell}): Swap -> Mexc*' + '\n' + 
            '\n' + f'_Contract:_ `{info_sell["contract"]}`' +
            '\n' + f'_Commission for buying:_ *{goplus_sell["buy_tax"]}%*' +
            '\n' + f'[GoPlus](https://gopluslabs.io/token-security/{chains_by_number[chain_sell]}/{info_sell["contract"]})' + '\n' +
            '\n' + f'📗 | [Swap](https://swap.defillama.com/?chain={chains_for_defilama[f"{chain_sell}"]}&from={usdt_address_sell}&tab=swap&to={info_sell["contract"]}) |' + '\n' +
            '\n' + f'📕 | [Mexc](https://www.mexc.com/ru-RU/exchange/{symbol[:-4]}_USDT) | [Deposit](https://www.mexc.com/ru-RU/assets/deposit/{symbol[:-4]})' +
            '\n' + f'Orders: *{orders_to_sell}*' + '\n' +
            '\n' + f'_Commision:_' +
            '\n' + f'Gas for swap: *{float(gas_buy):.2f}$*' +
            '\n' + f'Gas for withdraw: *{float(gas_for_withdraw_buy):.2f}$*' + '\n' +
            '\n' + f'_Profit(considering commissions):_ *{profit_one_inch:.2f}$*' + '\n' +
            '\n' + f'_Lifetime:_ *{formatted_time_difference}*')
        

    elif profit_mexc >= target_profit: 
        profit = profit_mexc
        message = (f'*{symbol[:-4]}/USDT({chain_buy}): Mexc -> Swap*' + '\n' +
            '\n' + f'_Contract_: `{info_buy["contract"]}`' +
            '\n' + f'_Commission for selling:_ {goplus_buy["sell_tax"]}%' +
            '\n' + f'[GoPlus](https://gopluslabs.io/token-security/{chains_by_number[chain_buy]}/{info_buy["contract"]})' + '\n' +
            '\n' + f'📗 | [Mexc](https://www.mexc.com/ru-RU/exchange/{symbol[:-4]}_USDT) | [Withdraw](https://www.mexc.com/ru-RU/assets/withdraw/{symbol[:-4]})' 
            '\n' + f'Orders: *{orders_to_buy}*' + '\n' +
            '\n' + f'📕 | [Swap](https://swap.defillama.com/?chain={chains_for_defilama[f"{chain_buy}"]}&from={info_buy["contract"]}&tab=swap&to={usdt_address_buy}) |' + '\n' + 
            '\n' + f'_Commision:_' +
            '\n' + f'Gas for swap: *{float(gas_sell):.2f}$*' +
            '\n' + f'Gas for withdraw: *{float(gas_for_withdraw_sell):.2f}$*' + '\n' +
            '\n' + f'_Profit(considering commissions):_ *{profit_mexc:.2f}$*' + '\n' +
            '\n' + f'_Lifetime:_ *{formatted_time_difference}*')
    else:
        return None
    item = {"symbol": symbol, 
            "profit": profit,
            "message": message,
            "start_time": start_time,
            "lifetime": total_seconds,
            "notify": []}
    if trade:
        trade["message"] = message
        trade["profit"] = profit
        trade["lifetime"] = total_seconds
        await trades_redis.set(symbol, json.dumps(trade))
    else:
        await trades_redis.set(symbol, json.dumps(item))    

    return item["symbol"]

async def main():
    task1 = asyncio.create_task(scan())
    task2 = asyncio.create_task(notify())
    await asyncio.gather(task1, task2)  


if __name__ == "__main__":
    while True: 
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            loop.run_until_complete(main())
        except Exception as e:
            print(traceback.format_exc())
            time.sleep(5)