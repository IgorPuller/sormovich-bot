from dotenv import load_dotenv
import os
import openai
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, MessageHandler, CommandHandler,
    ContextTypes, filters
)

# get tokens and settings
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=OPENAI_API_KEY)

openai.api_key = OPENAI_API_KEY

# examples of text style
your_messages_sample = [
    "Ну выпьем — и посмотрим, кто тут зет, а кто просто за IPA.",
    "Павел, с тебя крафт, с меня моральная поддержка.",
    "Да, чарочка не помешает, но не в рабочее же время.",
    "Нижний, как всегда, встретил туманом и похмельем.",
    "Не пиши в вайбер — это чат для отчаявшихся.",
]

# flag of silence
is_silent = False  

# promt for openAI
async def reply_in_your_style(user_message: str) -> str:
    prompt = f"""
Ты — умный, ироничный, местами саркастичный человек.
Говоришь по-русски, в живом, разговорном стиле. Можешь вставлять лёгкий мат, бытовые фразы, отсылки к пиву, друзьям, новостям.
Вот примеры твоей речи:

{chr(10).join(f"- {msg}" for msg in your_messages_sample)}

Ответь на сообщение: "{user_message}"
"""
    #client = openai.OpenAI()

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.9,
        max_tokens=150
    )

    return response.choices[0].message.content


# message processing
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global is_silent

    message = update.message
    if not message or not message.text or message.from_user.is_bot:
        return

    if is_silent:
        return  # Молчим

    user_text = message.text
    reply = await reply_in_your_style(user_text)
    await message.reply_text(reply)

# silent
async def command_tiho(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global is_silent
    is_silent = True
    await update.message.reply_text("🤫 Молчу, как партизан.")

# talk
async def command_govori(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global is_silent
    is_silent = False
    await update.message.reply_text("🗣️ Я снова в деле!")

# launch bot
def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CommandHandler("silent", command_tiho))
    app.add_handler(CommandHandler("talk", command_govori))

    print("🤖 Бот запущен. Отвечает на всё, пока не скажешь /тихо...")
    app.run_polling()

if __name__ == "__main__":
    main()

