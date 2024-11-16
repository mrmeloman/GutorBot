import asyncio
import datetime
import csv
import os
import random

# import statistics

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
regen_button = InlineKeyboardButton("♻️ Переделать",
                                    callback_data='regenerate')
forward_button = InlineKeyboardButton("✉️ Отправить создателю бота",
                                      callback_data='forward_to_me')
change_style_button = InlineKeyboardButton("🎨 Сменить стиль",
                                           callback_data="change_style")

main_keyboard = InlineKeyboardMarkup()
main_keyboard.add(regen_button)
# main_keyboard.add(forward_button)
# main_keyboard.add(change_style_button)

# === Admin keyboard ===
publish_button = InlineKeyboardButton("➡️ В канал",
                                      callback_data="to_channel")

admin_keyboard = InlineKeyboardMarkup()
admin_keyboard.add(publish_button)

# === Styles keyboard ===
regular_style_button = InlineKeyboardButton("👵 Открытки из ватсапа",
                                            callback_data="style_regular")
#new_year_style_button = InlineKeyboardButton("🎅 Новогодние открытки",
#                                             callback_data="style_new_year")
#wolves_style_button = InlineKeyboardButton("🐺 Волчьи цитаты",
#                                           callback_data="style_wolves")

styles_keyboard = InlineKeyboardMarkup()
styles_keyboard.add(regular_style_button)
#styles_keyboard.add(new_year_style_button)
#styles_keyboard.add(wolves_style_button)

my_id = 268173857
channel_id = -1001657092866
csv_data_file_path = "data/data_file.csv"
wait_message_text = "Генерация..."


@tg_bot.message_handler(commands=['help', 'start'])
async def send_welcome(message):
    with open('greeting.txt', encoding='utf-8') as greeting_file:
        greeting = greeting_file.read()

    member = await tg_bot.get_chat_member(chat_id=channel_id, user_id=message.from_user.id)

    await tg_bot.set_state(message.from_user.id, MyStates.regular, message.chat.id)

    await tg_bot.reply_to(message, greeting, parse_mode='MarkdownV2')


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@tg_bot.message_handler(content_types=['text'])
async def process_text_message(message: telebot.types.Message):
    member = await tg_bot.get_chat_member(chat_id=channel_id, user_id=message.from_user.id)
    if member.status not in ['member', 'creator', 'administrator']:
        await tg_bot.reply_to(message, "Подпишись на [Gutor Production](https://t.me/gutorpro) чтобы начать",
                              parse_mode='MarkdownV2')
        return

    state: str = await tg_bot.get_state(message.from_user.id, message.chat.id)

    if state is None:
        state = "regular"  # Default style

    style = state.replace("MyStates:", "")

    wait_message = await tg_bot.reply_to(message=message,
                                         text=wait_message_text)

    await _reply_with_postcard(message, style=style)
    await tg_bot.delete_message(chat_id=wait_message.chat.id, message_id=wait_message.id)


@tg_bot.message_handler(content_types=['photo'])
async def process_image_message(message):
    state: str = await tg_bot.get_state(message.from_user.id, message.chat.id)

    if state is None:
        state = "regular"  # Default style

    style = state.replace("MyStates:", "")
    wait_message = await tg_bot.reply_to(message=message,
                                         text=wait_message_text)

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
                                             text=wait_message_text)

        await _reply_with_postcard(message, style=style)
        await tg_bot.delete_message(chat_id=wait_message.chat.id, message_id=wait_message.id)


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
    elif call.data == "style_regular":
        await tg_bot.set_state(call.from_user.id, MyStates.regular, call.message.chat.id)
        await tg_bot.send_message(chat_id=call.message.chat.id,
                                  text=f"Стиль изменён на открытки из ватсапа. Введи текст или пришли фото с "
                                       f"подписью.")


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

    chat_id = message.chat.id
    image = await generate_postcard(query=query, usr_image=usr_img, style=style, is_png=is_png)
    await tg_bot.send_photo(chat_id=chat_id, photo=image, reply_to_message_id=message.id, reply_markup=main_keyboard)

    if random.uniform(0, 1) <= 0.2:
        await tg_bot.send_message(chat_id=chat_id,
                                  text="Классный канал: https://t.me/gutorpro")


async def main():
    tg_bot.add_custom_filter(asyncio_filters.StateFilter(tg_bot))
    await tg_bot.infinity_polling()


if __name__ == '__main__':
    asyncio.run(main())
