import os
import logging
from telegram import Update, InputFile
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Konfigurasi
BOT_TOKEN = "7577324092:AAFMm1zWb9D5p4f0xUkbEScks7QyQ3zVaaY"

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

    # Baca isi file
    with open(file_path, "r") as f:
        emails = f.readlines()

    valid_emails = []
    invalid_emails = []

    # Cek apakah email memiliki ekstensi @unima.ac.id
    for email in emails:
        email = email.strip()
        if email.endswith("@unima.ac.id"):
            valid_emails.append(email)
        else:
            invalid_emails.append(email)

    # Buat hasil dalam bentuk teks
    result_text = f"📊 Hasil Pengecekan:\n✅ Valid: {len(valid_emails)}\n❌ Tidak Valid: {len(invalid_emails)}"
    update.message.reply_text(result_text)

    # Simpan hasil ke file
    result_file_path = "downloads/result.txt"
    with open(result_file_path, "w") as result_file:
        result_file.write("✅ Email Valid:\n" + "\n".join(valid_emails) + "\n\n")
        result_file.write("❌ Email Tidak Valid:\n" + "\n".join(invalid_emails) + "\n")

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
