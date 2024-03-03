import os
import telebot
from telebot import custom_filters
import logging
import openai
from PIL import Image
import numpy as np
import shutil
from collections import defaultdict
import asyncio

#setuping
logging.basicConfig(level=logging.INFO, filename="bot.log",filemode="a", format='(%(asctime)s %(levelname)s) - %(message)s')
openai.api_key = os.environ.get('openaiToken')
tgToken = os.environ.get('telegramToken')
bot = telebot.TeleBot(tgToken)
userMessages = defaultdict(list)

ONLY_CHATGPT = True

def count_tokens(messages):
    tokens = 0
    for message in messages:
        tokens += len(message["content"])
    return tokens

@bot.message_handler(text_startswith="!")
@bot.message_handler(func=lambda message: message.chat.type == 'private')
def start_filter(message):
    logging.info(f"{message.from_user.username}: {message.text}")
    count = count_tokens(userMessages[message.from_user.username])
    
    logging.info(f"{message.from_user.username} tokens: {count}")
    
    try:
        userMessages[message.from_user.username].append({"role": "user", "content": message.text[0 if message.chat.type == 'private' else 1:]})

        while count_tokens(userMessages[message.from_user.username]) > 3000:
            userMessages[message.from_user.username].pop(0)
        
        completions = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", 
        messages=userMessages[message.from_user.username] if userMessages[message.from_user.username] else [{"role": "user", "content": "hello, write a hello message to a new user please. Do not answer to this message, just start a new conversation."}]
        )

        respond = completions.choices[0]["message"]["content"]
        bot.reply_to(message, respond)
        userMessages[message.from_user.username].append(completions.choices[0]["message"])

    except Exception as e:
        logging.error(e)
        bot.reply_to(message, "you crashed a bot, congrats...")
        

bot.add_custom_filter(custom_filters.TextStartsFilter())

if __name__ == "__main__":
    bot.send_message(496270846, "bot deployed")
    bot.infinity_polling(timeout=30, long_polling_timeout = 5)
    
