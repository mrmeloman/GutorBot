import asyncio
import datetime
import csv
import os
import random

import statistics

import PIL.Image
import telebot.types
from telebot.async_telebot import AsyncTeleBot, State, StateMemoryStorage
from telebot import asyncio_filters
from telebot.asyncio_handler_backends import StatesGroup
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from generator.generator_main import generate_postcard

# def log_exception(exctype, value, tb):
#     error_log = f"ERROR:\n" \
#                 f"Type: {exctype}\n" \
#                 f"Value: {value}\n" \
#                 f"Traceback: {tb}\n\n"
#
#     print(error_log)
#
#     # Open a file with access mode 'a'
#     log_file = open('log.txt', 'a')
#
#     # Append log string at the end of file
#     log_file.write(error_log)
#
#     # Close the file
#     log_file.close()
#
#
# sys.excepthook = log_exception

# === TG Setup ===
with open('data/token.txt') as f:
    TOKEN = f.read()

state_storage = StateMemoryStorage()
tg_bot = AsyncTeleBot(TOKEN, state_storage=state_storage)


class MyStates(StatesGroup):
    regular = State()
    new_year = State()
    wolves = State()


# === Main keyboard ===
regen_button = InlineKeyboardButton("♻️ Бабуль, а можешь переделать?",
                                    callback_data='regenerate')
forward_button = InlineKeyboardButton("✉️ Отправить создателю бота",
                                      callback_data='forward_to_me')
change_style_button = InlineKeyboardButton("🎨 Сменить стиль",
                                           callback_data="change_style")

main_keyboard = InlineKeyboardMarkup()
main_keyboard.add(regen_button)
main_keyboard.add(forward_button)
main_keyboard.add(change_style_button)

# === Admin keyboard ===
publish_button = InlineKeyboardButton("➡️ В канал",
                                      callback_data="to_channel")

admin_keyboard = InlineKeyboardMarkup()
admin_keyboard.add(publish_button)

# === Styles keyboard ===
regular_style_button = InlineKeyboardButton("👵 Открытки из ватсапа",
                                            callback_data="style_regular")
new_year_style_button = InlineKeyboardButton("🎅 Новогодние открытки",
                                             callback_data="style_new_year")
wolves_style_button = InlineKeyboardButton("🐺 Волчьи цитаты",
                                           callback_data="style_wolves")

styles_keyboard = InlineKeyboardMarkup()
styles_keyboard.add(regular_style_button)
styles_keyboard.add(new_year_style_button)
#styles_keyboard.add(wolves_style_button)

my_id = 268173857
nande_id = 368232202
channel_id = -1001961432265
csv_data_file_path = "data/data_file.csv"


@tg_bot.message_handler(commands=['help', 'start'])
async def send_welcome(message):
    await tg_bot.set_state(message.from_user.id, MyStates.regular, message.chat.id)

    with open('greeting.txt', encoding='utf-8') as greeting_file:
        greeting = greeting_file.read()

    await tg_bot.reply_to(message, greeting)


@tg_bot.message_handler(commands=['data'])
async def send_data(message: telebot.types.Message):
    if message.from_user.id != my_id:
        return

    data_list_of_dicts = await statistics.get_data()

    if len(data_list_of_dicts) == 0:
        await tg_bot.reply_to(message=message, text="Прости, внучок, что-то я датасет не чувствую")
        return

    data_file = open(csv_data_file_path, 'w', encoding='UTF-8')
    writer = csv.writer(data_file)

    for dictionary in data_list_of_dicts:
        writer.writerow(dictionary.values())

    data_file.close()

    response = "Держи данные, золотой мой"

    if os.path.getsize(csv_data_file_path) > 1610612736:
        response = "Что-то данные тяжёленькие последнее время, мне бы тележку..."

    with open(csv_data_file_path, "rb") as dfile:
        data_file = dfile.read()

    await tg_bot.send_document(chat_id=message.chat.id,
                               document=data_file,
                               visible_file_name='data_file.csv',
                               caption=response)

    os.remove(csv_data_file_path)


@tg_bot.message_handler(commands=['stats'])
async def send_stats(message: telebot.types.Message):
    if message.from_user.id != my_id and message.from_user.id != nande_id:
        return

    data_list_of_dicts = await statistics.get_data()

    request_amount = len(data_list_of_dicts)
    no_regen_amount = 0

    for d in data_list_of_dicts:
        if d['is_regeneration'] == 0:
            no_regen_amount += 1

    response = f"💌 Всего открыточек сделано: *{request_amount}*\n" \
               f"❄️ Не считая перегенераций: *{no_regen_amount}*"

    await tg_bot.reply_to(message=message,
                          text=response,
                          parse_mode='markdown')


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@tg_bot.message_handler(content_types=['text'])
async def process_text_message(message: telebot.types.Message):
    state: str = await tg_bot.get_state(message.from_user.id, message.chat.id)

    if state is None:
        state = "regular"  # Default style

    style = state.replace("MyStates:", "")

    wait_message = await tg_bot.reply_to(message=message,
                                         text="Умничка! Теперь подожди немного, бабуля посмотрит, "
                                              "что с этим можно сделать... "
                                              "Может занять немного времени, у бабули всего 2 гига, да 2 ядра")

    await _reply_with_postcard(message, style=style)
    await tg_bot.delete_message(chat_id=wait_message.chat.id, message_id=wait_message.id)


@tg_bot.message_handler(content_types=['photo'])
async def process_image_message(message):
    state: str = await tg_bot.get_state(message.from_user.id, message.chat.id)

    if state is None:
        state = "regular"  # Default style

    style = state.replace("MyStates:", "")

    await _forward_to_me(message, False)
    wait_message = await tg_bot.reply_to(message=message,
                                         text="Умничка! Теперь подожди немного, бабуля посмотрит, "
                                              "что с этим можно сделать... "
                                              "Может занять немного времени, у бабули всего 2 гига, да 2 ядра")

    await _reply_with_postcard(message, style=style)
    await tg_bot.delete_message(chat_id=wait_message.chat.id, message_id=wait_message.id)


@tg_bot.message_handler(content_types=['document'])
async def process_document(message: telebot.types.Message):
    print(f"Got message of type {message.content_type}")

    if message.document.file_name.endswith(".png"):
        state: str = await tg_bot.get_state(message.from_user.id, message.chat.id)

        if state is None:
            state = "regular"  # Default style

        style = state.replace("MyStates:", "")

        wait_message = await tg_bot.reply_to(message=message,
                                             text="Умничка! Теперь подожди немного, бабуля посмотрит, "
                                                  "что с этим можно сделать... "
                                                  "Может занять немного времени, у бабули всего 2 гига, да 2 ядра")

        await _reply_with_postcard(message, style=style)
        await tg_bot.delete_message(chat_id=wait_message.chat.id, message_id=wait_message.id)

    await _forward_to_me(message, respond=False)


@tg_bot.message_handler(content_types=['image', 'animation',
                                       'file', 'audio', 'sticker',
                                       'video', 'voice',
                                       'location', 'contact', 'video_note'])
async def process_other_messages(message: telebot.types.Message):
    print(f"Got message of type {message.content_type}")
    await _forward_to_me(message)


@tg_bot.callback_query_handler(func=lambda call: True)
async def callback(call: telebot.types.CallbackQuery):
    await tg_bot.answer_callback_query(callback_query_id=call.id)

    if call.data == "regenerate":
        state: str = await tg_bot.get_state(call.from_user.id, call.message.chat.id)

        if state is None:
            state = "regular"  # Default style

        style = state.replace("MyStates:", "")

        await _reply_with_postcard(call.message.reply_to_message, is_regen=True, style=style)

        # import cProfile
        #
        # with cProfile.Profile() as pr:
        #     await _reply_with_postcard(call.message.reply_to_message)
        #
        # stats = pstats.Stats(pr)
        # stats.sort_stats(pstats.SortKey.TIME)
        # stats.print_stats()

    elif call.data == "forward_to_me":
        await _forward_to_me(call.message)
    elif call.data == "to_channel":
        await _to_channel(call)
    elif call.data == "change_style":
        await _change_style(call.message)
    elif call.data == "style_regular":
        await tg_bot.set_state(call.from_user.id, MyStates.regular, call.message.chat.id)
        await tg_bot.send_message(chat_id=call.message.chat.id,
                                  text=f"Стиль изменён на открытки из ватсапа. Введи текст или пришли фото с "
                                       f"подписью.")
    elif call.data == "style_new_year":
        await tg_bot.set_state(call.from_user.id, MyStates.new_year, call.message.chat.id)
        await tg_bot.send_message(chat_id=call.message.chat.id,
                                  text=f"Стиль изменён на новогодний. Введи текст или пришли фото с "
                                       f"подписью.")
    elif call.data == "style_wolves":
        await tg_bot.set_state(call.from_user.id, MyStates.wolves, call.message.chat.id)
        await tg_bot.send_message(chat_id=call.message.chat.id,
                                  text=f"Стиль изменён на волчий, брат. Введи текст или пришли фото с "
                                       f"подписью.")


async def _change_style(message):
    await tg_bot.send_message(chat_id=message.chat.id,
                              text="Выбери стиль, который тебе больше нравится",
                              reply_to_message_id=message.id,
                              reply_markup=styles_keyboard)


async def _reply_with_postcard(message, is_regen=False, style="regular"):
    query = message.text
    usr_img = None
    is_png = False

    if message.content_type == 'photo':
        query = message.caption

        usr_img_id = message.photo[-1].file_id
        usr_img_info = await tg_bot.get_file(usr_img_id)
        downloaded_file = await tg_bot.download_file(usr_img_info.file_path)

        file_path = f"assets/{style}/temp/img_{message.from_user.id}_{message.id}.jpg"

        with open(f"{file_path}", 'wb') as new_file:
            new_file.write(downloaded_file)

        usr_img = PIL.Image.open(file_path).convert("RGBA")

        os.remove(file_path)
    elif message.content_type == 'document':
        query = message.caption

        usr_png_id = message.document.file_id
        usr_png_info = await tg_bot.get_file(usr_png_id)
        downloaded_file = await tg_bot.download_file(usr_png_info.file_path)

        file_path = f"assets/{style}/temp/img_{message.from_user.id}_{message.id}.png"

        with open(f"{file_path}", 'wb') as new_file:
            new_file.write(downloaded_file)

        usr_img = PIL.Image.open(file_path).convert("RGBA")
        is_png = True

        os.remove(file_path)

    if query is None:
        query = "---noquery---"

    now = datetime.datetime.now(tz=datetime.timezone.utc).strftime("%m/%d/%Y %H:%M:%S %Z")
    await statistics.add_entry(timestamp=now, query=query, is_regen=is_regen)

    chat_id = message.chat.id
    image = await generate_postcard(query=query, usr_image=usr_img, style=style, is_png=is_png)
    await tg_bot.send_photo(chat_id=chat_id, photo=image, reply_to_message_id=message.id, reply_markup=main_keyboard)

    if random.uniform(0, 1) <= 0.2:
        await tg_bot.send_message(chat_id=chat_id,
                                  text="Канал с лучшими (по мнению автора бота) открытками и новостями по боту тут: "
                                       "https://t.me/grannypraskovia")


async def _forward_to_me(message, respond=True):
    print("Forwarding the message")
    from_chat_id = message.chat.id
    to_chat_id = my_id

    try:
        last_name = message.reply_to_message.from_user.last_name
        if last_name is None:
            last_name = ""

        forward_text = f"Вот тебе гостинец от {message.reply_to_message.from_user.first_name} {last_name} (@{message.reply_to_message.from_user.username} id: {message.reply_to_message.from_user.id}), внучок"
        print("Name is readable")
    except:
        forward_text = f"Вот тебе гостинец, внучок"
        print("Name is unreadable")

    if respond:
        print("respond=true: responding")
        await tg_bot.reply_to(message=message, text="Ой, какая красота, налюбоваться не могу! "
                                                    "Переслала внуку, он вклеит в альбом!")

    if message.content_type == 'photo':
        await tg_bot.send_photo(chat_id=to_chat_id, photo=message.photo[-1].file_id,
                                caption=forward_text, reply_markup=admin_keyboard)
    else:
        await tg_bot.forward_message(chat_id=to_chat_id, from_chat_id=message.chat.id,
                                     message_id=message.id)


async def _to_channel(call: telebot.types.CallbackQuery):
    if call.from_user.id != my_id:
        return

    await tg_bot.send_photo(chat_id=channel_id, photo=call.message.photo[-1].file_id)

    await tg_bot.reply_to(message=call.message,
                          text="Переслала в канал!")


async def main():
    tg_bot.add_custom_filter(asyncio_filters.StateFilter(tg_bot))
    await tg_bot.infinity_polling()


if __name__ == '__main__':
    asyncio.run(main())
