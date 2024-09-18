from bot import bot
import time
import asyncio
import json
from mongo import list_of_pairs_mexc_db, trades_db, tokens_mexc_by_chains_db, goplus_db, settings_db
from redis import redis
import datetime

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
        life_time_target = await settings_db.get("number", 1)
        if not life_time_target:
            life_time_target = 0
        else:
            life_time_target = float(life_time_target["life_time_target"])
        arr = await trades_db.get_all()
        if not arr:
            continue
        for trade in arr:
            life_time = datetime.datetime.now() - datetime.datetime.strptime(trade["start_time"], "%Y-%m-%d %H:%M:%S")

            if trade["notify"]:
                continue
            if life_time.total_seconds() < life_time_target:
                continue
            await trades_db.update("symbol", trade["symbol"], {"notify": True})
            await bot.send_message(1317668838, f'{trade["symbol"]}: {trade["message"]}')
        await asyncio.sleep(5)

async def scan():
    await bot.send_message(1317668838, "Hello")
    while True:
        pairs = await list_of_pairs_mexc_db.get_all()
        target_profit = await settings_db.get("number", 1)
        target_profit = float(target_profit["target_profit"]) if target_profit else 0.0
        tokens_info = await tokens_mexc_by_chains_db.get_all()
        goplus = await goplus_db.get_all()
        trades = await trades_db.get_all()

        chains_by_gas_price = await redis.get("chains_by_gas_price")
        if not chains_by_gas_price:
            continue
        chains_by_gas_price = json.loads(chains_by_gas_price)
        arr = set()
        tasks = []
        for pair in pairs:
            tasks.append(get_profit(pair, tokens_info, target_profit, chains_by_gas_price, goplus, trades))
            if len(tasks) > 30:
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

        current_trades = await trades_db.get_all()
        for i in current_trades:
            if i["symbol"] in arr:
                continue
            await trades_db.delete("symbol", i["symbol"])


async def get_profit(pair, tokens_info, target_profit, chains_by_gas_price, goplus, trades):
    start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    one_inch = await redis.get(f'{pair["symbol"]}@1INCH')
    if not one_inch:
        return None
    one_inch = json.loads(one_inch)
    mexc = await redis.get(f'{pair["symbol"]}@MEXC')
    mexc = json.loads(mexc)
    tokens_info = [i for i in tokens_info if i["coin"] == pair["symbol"][:-4]][0]
    info = tokens_info["networkList"]

    chain_buy = one_inch[0]["chain"]
    chain_sell = one_inch[1]["chain"]
    info_buy = next((i for i in info if i["network"] == chain_buy), None)
    info_sell = next((i for i in info if i["network"] == chain_sell), None)
    if not info_buy or not info_sell:
        return None
    
    goplus_buy = next((i for i in goplus if i["contract_address"] == info_buy["contract"].lower()), None)
    goplus_sell = next((i for i in goplus if i["contract_address"] == info_sell["contract"].lower()), None)
    if not goplus_buy or not goplus_sell:
        return None

    profit_mexc, orders_to_buy, gas_buy, gas_for_withdraw_buy = await buy_on_mexc(mexc, one_inch, info_buy, goplus_buy, chains_by_gas_price) 
    profit_one_inch, orders_to_sell, gas_sell, gas_for_withdraw_sell = await buy_on_one_inch(mexc, one_inch, info_sell, goplus_sell, chains_by_gas_price)
    
    if not profit_mexc or not profit_one_inch:
        return None
    if profit_mexc < target_profit and profit_one_inch < target_profit:
        return None
    if info_buy.get("withdrawTips") or info_sell.get("withdrawTips") or info_buy.get("depositTips") or info_sell.get("depositTips"):
        return None
    message = f'\n mexc: {float(profit_mexc):.2f} \
        \n orders_to_buy: {orders_to_buy} \
        \n gas_buy: {gas_buy} \
        \n gas_for_withdraw_buy: {gas_for_withdraw_buy} \
        \n chain_buy: {chain_buy} \n \
        \n one_inch: {float(profit_one_inch):.2f} \
        \n orders_to_sell: {orders_to_sell} \
        \n gas_sell: {gas_sell} \
        \n gas_for_withdraw_sell: {gas_for_withdraw_sell} \
        \n chain_sell: {chain_sell} \n '
    item = {"symbol": pair["symbol"], 
            "message": message,
            "start_time": start_time,
            "notify": False}
    check = next((i for i in trades if i["symbol"] == pair["symbol"]), None)
    if check:
        await trades_db.update("symbol", pair["symbol"], {"message": message})
    else:
        await trades_db.add(item)
    return item["symbol"]

async def main():
    task1 = asyncio.create_task(scan())
    task2 = asyncio.create_task(notify())
    await asyncio.gather(task1, task2)  


if __name__ == "__main__":
    while True:
        try:
            asyncio.run(main())
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)