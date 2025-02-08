import os
import requests
import logging
from telegram import Update, InputFile
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Konfigurasi
BOT_TOKEN = "7577324092:AAFMm1zWb9D5p4f0xUkbEScks7QyQ3zVaaY"
API_URL = "http://147.139.167.176:8000/check-emails/"  # Ganti dengan URL API Anda

# Setup logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

def start(update: Update, context: CallbackContext):
    update.message.reply_text("📩 Kirimkan file .txt yang berisi email untuk dicek!")

def handle_file(update: Update, context: CallbackContext):
    file = update.message.document

    if not file.file_name.endswith(".txt"):
        update.message.reply_text("⚠️ Hanya file .txt yang diperbolehkan!")
        return

    file_path = f"downloads/{file.file_name}"
    os.makedirs("downloads", exist_ok=True)

    # Download file dari Telegram
    file_obj = context.bot.get_file(file.file_id)
    file_obj.download(file_path)

    update.message.reply_text("⏳ Sedang memproses file...")

    # Kirim file ke API
    with open(file_path, "rb") as f:
        response = requests.post(API_URL, files={"file": f})

    if response.status_code != 200:
        update.message.reply_text("❌ Terjadi kesalahan saat memeriksa email.")
        return

    result = response.json()
    
    # Buat hasil dalam bentuk teks
    result_text = f"📊 Hasil Pengecekan ({result['total_checked']} email dicek):\n"
    result_txt_content = ""
    
    for res in result["results"]:
        status = "✅ Valid" if res["exists"] else "❌ Tidak Valid"
        result_text += f"- {res['email']} → {status}\n"
        result_txt_content += f"{res['email']} → {status}\n"

    update.message.reply_text(result_text)

    # Simpan hasil ke file
    result_file_path = "downloads/result.txt"
    with open(result_file_path, "w") as result_file:
        result_file.write(result_txt_content)

    # Kirim file hasil ke pengguna
    with open(result_file_path, "rb") as result_file:
        update.message.reply_document(document=InputFile(result_file, filename="result.txt"))

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.document.mime_type("text/plain"), handle_file))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
