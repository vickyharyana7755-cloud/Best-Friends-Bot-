import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# Logging सेटअप
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# एक्टिव पार्टनर्स और वेटिंग लिस्ट
waiting_users = set()
active_pairs = {}  # {user_id: partner_id}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    welcome_text = (
        "👋 स्वागत है Anonymous Dating/Chat Bot में!\n\n"
        "कमांड्स:\n"
        "🔎 /find - किसी अजनबी से चैट शुरू करने के लिए\n"
        "🛑 /stop - मौजूदा चैट खत्म करने के लिए\n"
        "ℹ️ /help - मदद के लिए"
    )
    await update.message.reply_text(welcome_text)


async def find_partner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # अगर यूजर पहले से किसी से जुड़ा है
    if user_id in active_pairs:
        await update.message.reply_text(
            "⚠️ आप पहले से किसी से जुड़े हैं! नई चैट के लिए पहले /stop दबाएं।"
        )
        return

    # अगर यूजर पहले से वेटिंग लिस्ट में है
    if user_id in waiting_users:
        await update.message.reply_text(
            "⏳ हम आपके लिए पार्टनर ढूंढ रहे हैं... कृपया थोड़ा इंतजार करें।"
        )
        return

    # अगर कोई वेट कर रहा है, तो पेयर करें
    if waiting_users:
        partner_id = waiting_users.pop()

        # दोनों को कनेक्ट करें
        active_pairs[user_id] = partner_id
        active_pairs[partner_id] = user_id

        await context.bot.send_message(
            chat_id=user_id,
            text="🎉 पार्टनर मिल गया! अब आप अनाम (Anonymous) रूप से चैट कर सकते हैं। चैट रोकने के लिए /stop लिखें।",
        )
        await context.bot.send_message(
            chat_id=partner_id,
            text="🎉 पार्टनर मिल गया! अब आप अनाम (Anonymous) रूप से चैट कर सकते हैं। चैट रोकने के लिए /stop लिखें।",
        )
    else:
        # अगर कोई नहीं है तो यूजर को वेटिंग लिस्ट में डालें
        waiting_users.add(user_id)
        await update.message.reply_text(
            "🔍 पार्टनर ढूंढा जा रहा है... जैसे ही कोई जुड़ेगा, चैट शुरू हो जाएगी।"
        )


async def stop_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # अगर वेटिंग में है तो हटाएं
    if user_id in waiting_users:
        waiting_users.remove(user_id)
        await update.message.reply_text("❌ सर्च कैंसल कर दी गई है।")
        return

    # अगर एक्टिव चैट में है तो डिस्कनेक्ट करें
    if user_id in active_pairs:
        partner_id = active_pairs.pop(user_id)
        active_pairs.pop(partner_id, None)

        await update.message.reply_text(
            "🛑 आपने चैट खत्म कर दी है। नया पार्टनर ढूंढने के लिए /find दबाएं।"
        )
        await context.bot.send_message(
            chat_id=partner_id,
            text="🛑 आपके पार्टनर ने चैट छोड़ दी है। नया पार्टनर ढूंढने के लिए /find दबाएं।",
        )
    else:
        await update.message.reply_text(
            "⚠️ आप किसी भी एक्टिव चैट में नहीं हैं।"
        )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # चेक करें कि यूजर कनेक्टेड है या नहीं
    if user_id in active_pairs:
        partner_id = active_pairs[user_id]

        # टेक्स्ट और मीडिया दोनों फॉरवर्ड करना
        if update.message.text:
            await context.bot.send_message(
                chat_id=partner_id, text=update.message.text
            )
        elif update.message.photo:
            await context.bot.send_photo(
                chat_id=partner_id, photo=update.message.photo[-1].file_id
            )
        elif update.message.sticker:
            await context.bot.send_sticker(
                chat_id=partner_id, sticker=update.message.sticker.file_id
            )
        elif update.message.voice:
            await context.bot.send_voice(
                chat_id=partner_id, voice=update.message.voice.file_id
            )
    else:
        await update.message.reply_text(
            "⚠️ आपका कोई एक्टिव पार्टनर नहीं है। बात करने के लिए /find दबाएं।"
        )


if __name__ == "__main__":
    TOKEN = "8852018894:AAHmnRrh8pomKF-WAkzK5ehlFsX2oDY0f0A"  # अपना BotFather टोकन डालें

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("find", find_partner))
    app.add_handler(CommandHandler("stop", stop_chat))
    app.add_handler(
        MessageHandler(filters.ALL & ~filters.COMMAND, handle_message)
    )

    print("Bot is running...")
    app.run_polling()
  
