# -*- coding: utf-8 -*-
import sqlite3
from datetime import datetime

from aiogram import Bot, Dispatcher, executor
from aiogram import types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

db = sqlite3.connect("files/database1.db")
cur = db.cursor()

WORKING = False
API_TOKEN = "6379303105:AAGUNqdnvs4a8Km24pY4mz_qcgS6ir5D6lg"
ADMIN = -1001874740927
MAIN_KEY = 4892

bot = Bot(token=API_TOKEN, parse_mode="Markdown")
dp = Dispatcher(bot, storage=MemoryStorage())

edutaiment_dict = {}
module_dict = {}


class form_edutaiment(StatesGroup):
    comment_1 = State()
    comment_2 = State()
    comment_3 = State()
    comment_4 = State()
    comment_5 = State()


class form_modules(StatesGroup):
    comment = State()

class form_key(StatesGroup):
    key = State()

def is_registered(tID):
    cur.execute(f"SELECT * from users where tID = {tID}")
    data = cur.fetchall()
    if len(data) == 0:
        return False
    return True

@dp.callback_query_handler()
async def check_callback(callback: types.CallbackQuery, state: FSMContext):
    await bot.edit_message_reply_markup(chat_id=callback.message.chat.id,
                                        message_id=callback.message.message_id,
                                        reply_markup=None)

    data = callback.data.split("_")
    print(data)
    if data[0] == "start":
        if data[1] == "feedback":
            await bot.edit_message_text(chat_id=callback.message.chat.id,
                                        message_id=callback.message.message_id,
                                        text=f"Выбрано: *обратная связь 📝*"
                                             f"\n\n_Для изменения выбора нажми /start_")
            module_dict[callback.message.chat.id] = {}
            row = []
            for a in range(1, 6):
                row.append(types.InlineKeyboardButton(text=f"{a}", callback_data=f"group_{a}"))
            kb_answer = types.InlineKeyboardMarkup(inline_keyboard=[row])
            await callback.message.answer(text=f"*Какой у тебя квартал?*", reply_markup=kb_answer)


        elif data[1] == "edutaiment":
            await bot.edit_message_text(chat_id=callback.message.chat.id,
                                        message_id=callback.message.message_id,
                                        text=f"Выбрано: *игротехника 🎮*"
                                             f"\n\n_Для изменения выбора нажми /start_")
            edutaiment_dict[callback.message.chat.id] = {}
            row = []
            for a in range(1, 6):
                row.append(types.InlineKeyboardButton(text=f"{a}", callback_data=f"edu_{a}"))
            kb_answer = types.InlineKeyboardMarkup(inline_keyboard=[row])
            await callback.message.answer(text=f"*Выберите квартал*", reply_markup=kb_answer)

    elif data[0] == "group":
        group = int(data[1])
        module_dict[callback.message.chat.id]['group'] = group
        cur.execute(f"SELECT * FROM list")
        modules = cur.fetchall()
        print(modules)
        kb_answer = types.InlineKeyboardMarkup(row_width=1)
        for a in modules:
            btn = types.InlineKeyboardButton(text=a[0], callback_data=f"module_{a[1]}")
            kb_answer.add(btn)
        await callback.message.answer(text="*Выбери свой модуль*", reply_markup=kb_answer)

    elif data[0] == "module":
        module_dict[callback.message.chat.id]['module'] = data[1]
        await callback.message.answer(text="*Как тебе занятие? Напиши, что понравилось и не понравилось*")
        await form_modules.comment.set()

    elif data[0] == "pdf":
        module = data[1]
        day = str(datetime.now().strftime("%d-%m-%Y"))
        feedback = cur.execute(
            f"SELECT groupe, comment FROM modules WHERE post_date = \"{day}\" AND module = \"{module}\"").fetchall()
        module_name = cur.execute(f"SELECT name FROM list WHERE id = \"{module}\"").fetchall()[0]
        text_to_send = f"*{module_name[0]}* за _{datetime.now().strftime('%d.%m.%Y')}_\n\n"
        for a in feedback:
            text_to_send += f"{a[1]} ({a[0]} квартал)\n\n"
        await callback.message.answer(text=text_to_send)

    elif data[0] == "edu":
        edutaiment_dict[callback.message.chat.id]['group'] = int(data[1])
        await callback.message.answer(
            text="*1. Есть ли понимание детей об организации органов управления в Центрополисе?*")
        await form_edutaiment.comment_1.set()

@dp.message_handler(commands=['menu'])
async def command_start(message: types.Message):
    global WORKING
    tID = message.chat.id

    if tID != ADMIN and is_registered(tID):
        if WORKING:
            kb_answer = types.InlineKeyboardMarkup(row_width=1)
            btn_1 = types.InlineKeyboardButton(text="Обратная связь 📝", callback_data="start_feedback")
            btn_2 = types.InlineKeyboardButton(text="Игротехника 🎮", callback_data="start_edutaiment")
            kb_answer.add(btn_1, btn_2)
            await message.answer(text="*Выбери, что хочешь сделать*",
                                 reply_markup=kb_answer)
        else:
            await message.answer("*Сейчас бот не работает, возвращайся попозже*")

@dp.message_handler(commands=['start'])
async def command_start(message: types.Message):
    global WORKING
    tID = message.chat.id
    if tID == ADMIN:
        WORKING = True
        await message.answer(f"*Бот запущен!*"
                             f"\n\n_Для остановки отправьте /stop_")
        # РАССЫЛКА ВСЕМ О НАЧАЛЕ

    else:
        print(is_registered(tID))
        if is_registered(tID) == False:
            await message.answer("Приветствуем тебя на смене «Центрополис: курс на приключения»!\nЧтобы продолжить, введи код, который тебе скажут твои квартальные")
            await form_key.key.set()
        else:
            await message.answer("*Ты уже ввёл код подтверждения. Чтобы открыть меню, нажми /menu*")

@dp.message_handler(commands=['stop'])
async def command_start(message: types.Message):
    global WORKING
    tID = message.chat.id
    if tID == ADMIN:
        WORKING = False
        await message.answer(f"*Бот остановлен!*"
                             f"\n\n_Для запуска отправьте /start_")

@dp.message_handler(commands=['all'])
async def command_pdf(message: types.Message):
    cur.execute(f"SELECT * FROM list")
    modules = cur.fetchall()
    print(modules)
    kb_answer = types.InlineKeyboardMarkup(row_width=1)
    for a in modules:
        btn = types.InlineKeyboardButton(text=a[0], callback_data=f"pdf_{a[1]}")
        kb_answer.add(btn)
    await message.answer(text="*Выберите модуль для отчёта*", reply_markup=kb_answer)

@dp.message_handler(state=form_key.key)
async def process_rename(message: types.Message, state: FSMContext):
    await state.finish()
    key = int(message.text)
    if key == MAIN_KEY:
        cur.execute(f"INSERT INTO users (tID) VALUES ({message.chat.id})")
        await message.answer("*Отлично, код верный! Теперь ты можешь использовать команду /menu\n\nХорошего тебе дня!*")
    else:
        await message.answer("Упс, неверный код. Попробуй снова, нажми на /start и введи код")

@dp.message_handler(state=form_edutaiment.comment_1)
async def process_rename(message: types.Message, state: FSMContext):
    if message.text != "/start":
        await state.finish()
        edutaiment_dict[message.chat.id]["comment_1"] = message.text
        await message.answer("*2. Как кварталятам первый день стажировки? Что понравилось ? Что не понравилось?*")
        await form_edutaiment.comment_2.set()

    else:
        await state.finish()
        del edutaiment_dict[message.chat.id]
        await command_start(message)


@dp.message_handler(state=form_edutaiment.comment_2)
async def process_rename(message: types.Message, state: FSMContext):
    if message.text != "/start":
        await state.finish()
        edutaiment_dict[message.chat.id]["comment_2"] = message.text
        await message.answer("*3. Понимают ли кварталята ценность трудового удостоверения?*")
        await form_edutaiment.comment_3.set()

    else:
        await state.finish()
        del edutaiment_dict[message.chat.id]
        await command_start(message)

@dp.message_handler(state=form_edutaiment.comment_4)
async def process_rename(message: types.Message, state: FSMContext):
    if message.text != "/start":
        await state.finish()
        edutaiment_dict[message.chat.id]["comment_4"] = message.text
        await message.answer("*5. Донесли ли главы суть работы профсоюза?*")
        await form_edutaiment.comment_5.set()

    else:
        await state.finish()
        del edutaiment_dict[message.chat.id]
        await command_start(message)

@dp.message_handler(state=form_edutaiment.comment_5)
async def process_rename(message: types.Message, state: FSMContext):
    if message.text != "/start":
        await state.finish()
        edutaiment_dict[message.chat.id]["comment_5"] = message.text
        cur.execute(
            f"INSERT INTO edutaiment (telegram_id, post_date, comment_1, comment_2, comment_3) VALUES ({message.chat.id}, \"{datetime.now()}\", \"{edutaiment_dict[message.chat.id]['comment_1']}\", \"{edutaiment_dict[message.chat.id]['comment_2']}\", \"{edutaiment_dict[message.chat.id]['comment_3']}\")")
        db.commit()
        await bot.send_message(chat_id=ADMIN,
                               text="*Игротехника*"
                                    f"\n\n*Квартал:* {edutaiment_dict[message.chat.id]['group']}"
                                    f"\n*1.* {edutaiment_dict[message.chat.id]['comment_1']}"
                                    f"\n*2.* {edutaiment_dict[message.chat.id]['comment_2']}"
                                    f"\n*3.* {edutaiment_dict[message.chat.id]['comment_3']}"
                                    f"\n*4.* {edutaiment_dict[message.chat.id]['comment_4']}"
                                    f"\n*5.* {edutaiment_dict[message.chat.id]['comment_5']}")
        print(edutaiment_dict[message.chat.id])
        await message.answer("*Обратная связь принята, спасибо!*")
        edutaiment_dict[message.chat.id] = {}

    else:
        await state.finish()
        del edutaiment_dict[message.chat.id]
        await command_start(message)


@dp.message_handler(state=form_edutaiment.comment_3)
async def process_rename(message: types.Message, state: FSMContext):
    if message.text != "/start":
        await state.finish()
        edutaiment_dict[message.chat.id]["comment_3"] = message.text
        await message.answer("*4. Как дети воспринимают историю с центриками? Поняли ли они , что в этом есть соревновательный мотив?*")
        await form_edutaiment.comment_4.set()

    else:
        await state.finish()
        del edutaiment_dict[message.chat.id]
        await command_start(message)


@dp.message_handler(state=form_modules.comment)
async def process_rename(message: types.Message, state: FSMContext):
    if message.text != "/start":
        await state.finish()
        module_dict[message.chat.id]["comment"] = message.text
        module_name = \
            cur.execute(f"SELECT name FROM list WHERE id = \"{module_dict[message.chat.id]['module']}\"").fetchall()[0]

        print(
            f"INSERT INTO modules (telegram_id, post_date, module, groupe, comment) VALUES ({message.chat.id}, \"{datetime.now().strftime('%d-%m-%Y')}\", \"{module_dict[message.chat.id]['module']}\", {module_dict[message.chat.id]['group']}, \"{module_dict[message.chat.id]['comment']}\")")
        cur.execute(
            f"INSERT INTO modules (telegram_id, post_date, module, groupe, comment) VALUES ({message.chat.id}, \"{datetime.now().strftime('%d-%m-%Y')}\", \"{module_dict[message.chat.id]['module']}\", {module_dict[message.chat.id]['group']}, \"{module_dict[message.chat.id]['comment']}\")")
        db.commit()
        # print(cur.execute(f"INSERT INTO modules (telegram_id, post_date, module, group, comment) VALUES ({message.chat.id}, \"{datetime.now().strftime('%d-%m-%Y')}\", \"{module_dict[message.chat.id]['module']}\", {module_dict[message.chat.id]['group']}, \"{module_dict[message.chat.id]['comment']}\")"))

        await bot.send_message(chat_id=ADMIN,
                               text="*Обратная связь*"
                                    f"\n\nКвартал: *{module_dict[message.chat.id]['group']}*"
                                    f"\nМодуль: *{module_name[0]}*"
                                    f"\nКомментарий: *{module_dict[message.chat.id]['comment']}*")
        await message.answer("*Спасибо тебе большое! Хорошего дня!*")
        module_dict[message.chat.id] = {}

    else:
        await state.finish()
        del module_dict[message.chat.id]
        await command_start(message)


async def on_startup():
    await bot.send_message(chat_id=ADMIN, text="*Бот перезагружен автоматически. Статус: остановлен*"
                                               "\n\n_Для того, чтобы запустить бота, отправьте /start_")


if __name__ == "__main__":
    executor.start(dp, on_startup())
    executor.start_polling(dp, skip_updates=True)

