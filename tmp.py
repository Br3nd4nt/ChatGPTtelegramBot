respond = openai.Completion.create(
                model="text-davinci-003",
                prompt=message.text[1:],
                max_tokens=1024,
                temperature=0.5
                )['choices'][0]['text']
                bot.reply_to(message, respond)