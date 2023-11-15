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

if not ONLY_CHATGPT:
    try:
        os.mkdir("./image_frames/")
    except:
        pass

    try:
        os.mkdir("./user_images/")
    except:
        pass

    pixel_size = 25
    divider = 10

    def generate_frames(light):
        dark = [i * 0.8 for i in light]

        for i in range(1, 7):
            data = np.array(Image.open(f'./frames_templates/{i}.png').convert('RGB'))
            r, g, b = data.T
            
            light_area = (r == 0) & (g == 255) & (b == 0)
            dark_area = (r == 255) & (g == 0) & (b == 0)

            data[light_area.T] = light
            data[dark_area.T] = dark
            Image.fromarray(data).resize((pixel_size, pixel_size)).save(f'./image_frames/{light}_{i}.png')


    @bot.message_handler(content_types=['photo', 'text'])
    def handle_image(message):
        if not (message.text and message.text.startswith("!amogus") and message.photo):
            return

        file_path = f"./user_images/{message.from_user.username}.jpg"
        gif_path = f"./user_images/{message.from_user.username}.gif"

        photo = message.photo[-1]
        file_id = photo.file_id

        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        with open(file_path, 'wb') as new_file:
            new_file.write(downloaded_file)

        im = Image.open(file_path)
        im = im.resize((im.width // divider, im.height // divider))
        w, h = im.width, im.height
        data = np.array(im.convert("RGB"))
        
        colors = set()
        for i in range(h):
            for j in range(w):
                color = list(data[i, j])
                if str(color) not in colors:
                    generate_frames(color)
                    colors.add(str(color))
        bot.reply_to(message, "Colors generated, just wait")


        frames = [Image.new("RGB", (25 * w, 25 * h)) for _ in range(6)]

        for i in range(h):
                for j in range(w):
                    for _ in range(1, 7):
                        frames[_ - 1].paste(Image.open(f'./image_frames/{str(list(data[i, j]))}_{_}.png'), (j * 25, i * 25))

        frames[0].save(gif_path, save_all=True, append_images=frames[1:])
        with open(gif_path, 'rb') as gif:
            bot.send_document(message.chat.id, gif)

        #clearing
        folder = './image_frames'
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        # os.remove(file_path)
        # os.remove(gif_path)

def count_tokens(messages):
    tokens = 0
    for message in messages:
        tokens += len(message["content"])
    return tokens

@bot.message_handler(text_startswith="!")
def start_filter(message):
    logging.info(f"{message.from_user.username}: {message.text}")
    count = count_tokens(userMessages[message.from_user.username])
    
    logging.info(f"{message.from_user.username} tokens: {count}")

    if not ONLY_CHATGPT:
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
                return
            except:
                bot.reply_to(message, "not working")
                return

        elif message.text.startswith("!amogus "):
            return

    else:
        try:
            userMessages[message.from_user.username].append({"role": "user", "content": message.text[1:]})

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
    
