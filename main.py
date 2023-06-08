
import os
import telebot
from telebot import custom_filters
import logging
import openai
import requests 

logging.basicConfig(level=logging.INFO, filename="bot.log",filemode="a", format='(%(asctime)s %(levelname)s) - %(message)s')

openai.api_key = os.environ.get('openaiToken')

tgToken = os.environ.get('telegramToken')
bot = telebot.TeleBot(tgToken)

userMessages = dict()

def count_tokens(messages):
    tokens = 0
    for message in messages:
        if message["role"] == "user":
            tokens += len(message["content"])
    return tokens

@bot.message_handler(text_startswith="!")
def start_filter(message):
    logging.info(f"{message.from_user.username}: {message.text}")
    try:
        count = count_tokens(userMessages[message.from_user.username])
    except:
        count = 0
    
    logging.info(f"{message.from_user.username} tokens: {count}")

    if message.text.startswith("!generate "):
        prompt = message.text[10:]
        try:
            a = openai.Image.create(
            prompt=prompt,
            n=1,
            size="1024x1024"
            )

            url = a['data'][0]['url']

            bot.send_photo(message.chat.id, url, reply_to_message_id=message.message_id)
        except:
            bot.reply_to(message, "Либо хуйню заказал чибо что-то еще, иди нахуй короче")

    else:
        try:
            if 1: #just for testing
                try:
                    messages = userMessages[message.from_user.username]
                except KeyError:
                    messages = []
                
                messages.append({"role": "user", "content": message.text[1:]})

                while count_tokens(messages) > 4000:
                    messages.pop(0)
                    messages.pop(0)
                
                completions = openai.ChatCompletion.create(
                model="gpt-3.5-turbo", 
                messages=messages
                )

                respond = completions.choices[0]["message"]["content"]
                bot.reply_to(message, respond)
                messages.append(completions.choices[0]["message"])
                userMessages[message.from_user.username] = messages

            else:

                respond = openai.Completion.create(
                model="text-davinci-003",
                prompt=message.text[1:],
                max_tokens=1024,
                temperature=0.5
                )['choices'][0]['text']
                bot.reply_to(message, respond)

        except Exception as e:
            logging.error(e)
            bot.reply_to(message, "Connection to OpenAI timed out :(")

bot.add_custom_filter(custom_filters.TextStartsFilter())

if __name__ == "__main__":
    bot.send_message(496270846, "bot deployed")
    import asyncio
    asyncio.run(bot.polling(skip_pending=True))
    # while True:
    #     try:
    #         asyncio.run(bot.polling(skip_pending=True))
    #     except Exception as e:
    #         logging.error(e)
    #         bot.send_message(496270846, "fuckin bitch crashed, trying to reboot")