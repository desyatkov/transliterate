from dotenv import load_dotenv
from flask import Flask, jsonify
import threading
import os
from transliterate.decorators import transliterate_function
import hashlib
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineQuery, InputTextMessageContent, InlineQueryResultArticle

load_dotenv()
TOKEN = os.environ['TOKEN']
environment = os.environ['ENV']
logging.basicConfig(level=logging.WARNING)
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

app = Flask(__name__)


@app.route("/")
def hello():
    return jsonify(
        status='ok',
        code=200
    )


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.reply("transliterate bot")


@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    await message.reply("write @swpa_bot in chat and message")


@dp.message_handler()
async def echo_message(msg: types.Message):
    await bot.send_message(msg.from_user.id, msg.text)


@transliterate_function(language_code='ru')
def decorator_test(text):
    print(text)
    return text.capitalize()


@dp.inline_handler()
async def inline_echo(inline_query: InlineQuery):
    text = decorator_test(inline_query.query) or 'echo'
    input_content = InputTextMessageContent(text)
    result_id: str = hashlib.md5(text.encode()).hexdigest()
    item = InlineQueryResultArticle(
        id=result_id,
        title=f'Result {text!r}',
        input_message_content=input_content,
    )

    cache = 1 if environment == 'dev' else 300
    await bot.answer_inline_query(inline_query.id, results=[item], cache_time=cache)


if __name__ == '__main__':
    threading.Thread(target=app.run, kwargs={'port': 8080}).start()
    executor.start_polling(dp, skip_updates=True)


