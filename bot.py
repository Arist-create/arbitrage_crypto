import time
import json
from aiogram import types, executor
from aiogram import Bot, Dispatcher
from mongo import users_settings_db
from redis_facade import trades_redis
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

API_TOKEN = '7473932480:AAHvJvYndS0-blMx8U-w57BBjMuUTl01E7E'  # прод
# API_TOKEN = '6769001742:AAGW0d_60IymQPl8ef4U7Pvun3aIYf0aBPc'

bot = Bot(token=API_TOKEN)

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

async def create_keyboard(chat_id):
    # Создаем кнопки с состоянием
    user_settings = await users_settings_db.get("chat_id", chat_id)
    button1_text = "✅" if user_settings["notify_is_on"] else "❌"

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton(text=button1_text, callback_data="button1") 
    )
    return keyboard

async def create_keyboard_for_select_profit():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton(text='1️⃣', callback_data="10"),
        types.InlineKeyboardButton(text='5️⃣', callback_data="50"),
        types.InlineKeyboardButton(text='🔟', callback_data="100")
    ) 
    return keyboard


async def create_keyboard_for_update_notify(symbol):
    # Создаем кнопки с состоянием
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton(text='🔁', callback_data=symbol) 
    )
    return keyboard

async def set_commands(dp):
    commands = [
        types.BotCommand(command="/change_notify_settings", description="Изменить настройки уведомлений"),
        types.BotCommand(command="/notify_status", description="Статус уведомлений"),
        types.BotCommand(command="/show_arbs", description="Топ 5 арбитражных ситуаций"),
        types.BotCommand(command="/show_notify_settings", description="Просмотреть настройки уведомлений"),
    ]
    await bot.set_my_commands(commands)


class Form(StatesGroup):
    waiting_life_time_target = State()
    waiting_target_profit = State()
    waiting_notify_is_on = State()


@dp.message_handler(commands=['start'], state="*")
async def message_id(message: types.Message, state: FSMContext):
    await state.finish()

    await bot.send_message(message.chat.id, f"Hello, {message.from_user.first_name}, for beginning please set up notification settings, use /change_settings")


@dp.message_handler(commands=['change_notify_settings'], state="*")
async def message_id(message: types.Message, state: FSMContext):
    await state.finish()

    keyboard = await create_keyboard_for_select_profit()
    await bot.send_message(message.chat.id, "Select target profit", reply_markup=keyboard)
    await Form.waiting_target_profit.set()

@dp.message_handler(commands=["show_notify_settings"], state="*")
async def message_id(message: types.Message, state: FSMContext):
    await state.finish()
    settings = await users_settings_db.get("chat_id", message.chat.id)
    if not settings:
        await bot.send_message(message.chat.id, "Settings not found, use /change_notify_settings")
        return

    await bot.send_message(message.chat.id, f"Target profit: {settings['target_profit']}$")
    await bot.send_message(message.chat.id, f"Life time target: {settings['life_time_target']} seconds")

@dp.callback_query_handler(lambda c: c.data in ["10", "50", "100"], state=Form.waiting_target_profit)
async def message_id(callback_query: types.CallbackQuery, state: FSMContext):
    chat_id = callback_query.message.chat.id
    user_settings = {"target_profit": int(callback_query.data),
        "chat_id": chat_id,
        "notify_is_on": True}
    await users_settings_db.update("chat_id", chat_id, user_settings, True)
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(chat_id, "Enter life time target(seconds):")
    await Form.waiting_life_time_target.set()


@dp.message_handler(state=Form.waiting_life_time_target)
async def message_id(message: types.Message, state: FSMContext):
    try:
        life_time_target = float(message.text)
    except ValueError:
        await bot.send_message(message.chat.id, "Life time target must be a positive number")
        return
    if life_time_target < 0:
        await bot.send_message(message.chat.id, "Life time target must be a positive number")
        return
    await users_settings_db.update("chat_id", message.chat.id, {"life_time_target": life_time_target})
    await bot.send_message(message.chat.id, "Done")
    await state.finish()


@dp.message_handler(commands=['notify_status'], state="*")
async def message_id(message: types.Message, state: FSMContext):
    await state.finish()

    if not await users_settings_db.get("chat_id", message.chat.id):
        await bot.send_message(message.chat.id, "You have to set up notifications settings first, use /change_notify_settings")
        return
    keyboard = await create_keyboard(message.chat.id)
    await bot.send_message(message.chat.id, "Notifications", reply_markup=keyboard)
    await Form.waiting_notify_is_on.set()


@dp.callback_query_handler(lambda c: c.data in ["button1"], state=Form.waiting_notify_is_on)
async def message_id(callback_query: types.CallbackQuery, state: FSMContext):
    chat_id = callback_query.message.chat.id
    user_settings = await users_settings_db.get("chat_id", chat_id)
    await users_settings_db.update("chat_id", chat_id, {"notify_is_on": not user_settings["notify_is_on"]})
    keyboard = await create_keyboard(chat_id)
    
    # Обновляем сообщение с новой клавиатурой
    await bot.edit_message_reply_markup(chat_id, callback_query.message.message_id, reply_markup=keyboard)
    
    # Убираем индикатор загрузки на кнопке
    await bot.answer_callback_query(callback_query.id)
    await state.finish()

@dp.callback_query_handler(lambda c: c.data not in ["button1"])
async def message_id(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    symbol = callback_query.data
    
    trade = await trades_redis.get(symbol)

    text = json.loads(trade)["message"] if trade else "Not found" 
    if callback_query.message.text != text:
        chat_id = callback_query.message.chat.id
        keyboard = await create_keyboard_for_notify(symbol)
        # Обновляем сообщение с новой клавиатурой
        await bot.edit_message_text(text, chat_id=chat_id, message_id=callback_query.message.message_id, reply_markup=keyboard, parse_mode='Markdown')



@dp.message_handler(commands=['show_arbs'], state="*")
async def message_id(message: types.Message, state: FSMContext):
    await state.finish()
    trades = await trades_redis.get_all()
    if not trades:
        await bot.send_message(message.chat.id, "No trades")
        return
    string = ""
    k = 0
    trades = sorted(trades, key=lambda x: x["profit"], reverse=True)
    for trade in trades:
        if k >= 5:
            break
        string += f'{trade["message"]}\n\n' + \
            '------------------------------'+'\n\n'
        k += 1
    try:
        await bot.send_message(message.chat.id, string, parse_mode='Markdown')
    except Exception as e:
        await bot.send_message(message.chat.id, e)


if __name__ == '__main__':
    while True:
        try:
            executor.start_polling(dp, skip_updates=True, on_startup=set_commands)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)
