import time
from aiogram import types, executor
from aiogram import Bot, Dispatcher 
from mongo import trades_db, settings_db

API_TOKEN = '7473932480:AAHvJvYndS0-blMx8U-w57BBjMuUTl01E7E' #прод
# API_TOKEN = '6769001742:AAGW0d_60IymQPl8ef4U7Pvun3aIYf0aBPc'

bot = Bot(token=API_TOKEN)


dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def message_id(message: types.Message):
    await bot.send_message(message.chat.id, f"Message ID: {message.message_id}. Chat ID: {message.chat.id}.")

@dp.message_handler(commands=['show'])
async def message_id(message: types.Message):
    trades = await trades_db.get_all()
    string = ""
    for trade in trades:
        string += f'{trade["symbol"]}: {trade["message"]}\n'
    try:
        await bot.send_message(message.chat.id, string)
    except Exception as e:
        await bot.send_message(message.chat.id, e)

@dp.message_handler(commands=['settings'])
async def message_id(message: types.Message):
    settings = await settings_db.get("number", 1)
    if not settings:
        return
    string = ""
    for k, v in settings.items():
        string += f'{k}: {v}\n'

    await bot.send_message(message.chat.id, string)


@dp.message_handler(lambda message: message.text and ':' in message.text.lower())
async def message_id(message: types.Message):
    life_time_target = float(message.text[1:])
    await settings_db.update("number", 1, {"life_time_target": life_time_target}, True)
    await bot.send_message(message.chat.id, "Done")

@dp.message_handler(lambda message: message.text and '.' in message.text.lower())
async def message_id(message: types.Message):
    target_profit = float(message.text[1:])
    await settings_db.update("number", 1, {"target_profit": target_profit}, True)
    await bot.send_message(message.chat.id, "Done")


if __name__ == '__main__':
    while True:
        try:
            executor.start_polling(dp, skip_updates=True)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)