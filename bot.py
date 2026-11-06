import os, asyncio, tempfile, requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from replicate import Replicate
from pydub import AudioSegment

TOKEN = os.environ.get("TELEGRAM_TOKEN")
REPLICATE_TOKEN = os.environ.get("REPLICATE_API_TOKEN")
replicate = Replicate(REPLICATE_TOKEN)

# Модель для генерации музыки
MUSIC_MODEL = "meta/musicgen:4c978ba047c04d7f99f8c47d8f0d2d6c4d8d0f4e6b2a1c3d5e7f8a9b0c1d2e3f"

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text("Генерирую музыку... 🎵")

    text = update.message.text
    try:
        # Генерация
        output = replicate.run(MUSIC_MODEL, input={"prompt": text, "duration": 10})
        url = output[0] if isinstance(output, list) else output

        # Скачать
        r = requests.get(url)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
            f.write(r.content)
            mp3_path = f.name

        # Добавить текст сверху
        audio = AudioSegment.from_mp3(mp3_path)
        # Просто отправляем
        with open(mp3_path, 'rb') as f:
            await update.message.reply_audio(f, title=text[:50], performer="AI Bot")

    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
print("Bot with music + top text started")
app.run_polling()
