import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackContext, MessageHandler, filters, CallbackQueryHandler
import requests
import os

# توکن API و مرچنت زرین‌پال
TOKEN = os.getenv("BOT_TOKEN")
MERCHANT_ID = os.getenv("MERCHANT_ID")
CALLBACK_URL = "https://your-replit-username.repl.co/verify"  # لینک بازگشت برای تأیید پرداخت

# مسیر فایل‌های PDF
FILE_PATH = "files/"

# لیست محصولات
products = {
    "seventh": {"name": "آموزش پایتون، ویژه هفتمی‌ها", "price": 200000, "file": FILE_PATH + "python7.pdf"},
    "eighth": {"name": "آموزش پایتون، ویژه هشتمی‌ها", "price": 200000, "file": FILE_PATH + "python8.pdf"},
    "ninth": {"name": "آموزش پایتون، ویژه نهمی‌ها", "price": 200000, "file": FILE_PATH + "python9.pdf"}
}

# ذخیره درخواست‌های پرداخت
pending_payments = {}

# تنظیمات لاگ
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# تابع شروع ربات
async def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    keyboard = [[KeyboardButton("📚 پکیج‌های آموزشی پایتون")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

    await update.message.reply_text(f"سلام {user.first_name} عزیز! 🎉\nلطفاً یک گزینه را انتخاب کنید:", reply_markup=reply_markup)

# نمایش لیست دوره‌های آموزشی
async def handle_response(update: Update, context: CallbackContext) -> None:
    text = update.message.text

    if text == "📚 پکیج‌های آموزشی پایتون":
        keyboard = [
            [
                InlineKeyboardButton(f"{products['seventh']['name']} - {products['seventh']['price']} ریال", callback_data='seventh'),
                InlineKeyboardButton(f"{products['eighth']['name']} - {products['eighth']['price']} ریال", callback_data='eighth')
            ],
            [InlineKeyboardButton(f"{products['ninth']['name']} - {products['ninth']['price']} ریال", callback_data='ninth')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("📌 لطفاً یکی از دوره‌های زیر را انتخاب کنید:", reply_markup=reply_markup)

# ایجاد لینک پرداخت در زرین‌پال
async def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    product_key = query.data
    if product_key in products:
        product_info = products[product_key]
        user_id = query.message.chat_id

        # درخواست پرداخت به زرین‌پال
        data = {
            "merchant_id": MERCHANT_ID,
            "amount": product_info["price"],
            "callback_url": CALLBACK_URL,
            "description": f"خرید {product_info['name']}"
        }
        response = requests.post("https://api.zarinpal.com/pg/v4/payment/request.json", json=data)
        result = response.json()

        if "data" in result and "authority" in result["data"]:
            authority = result["data"]["authority"]
            payment_url = f"https://www.zarinpal.com/pg/StartPay/{authority}"

            # ذخیره اطلاعات پرداخت
            pending_payments[authority] = {"user_id": user_id, "file": product_info["file"], "amount": product_info["price"]}

            await query.edit_message_text(f"💳 برای خرید {product_info['name']}، روی لینک زیر کلیک کنید:\n{payment_url}")
        else:
            await query.edit_message_text("❌ مشکلی در ایجاد لینک پرداخت به وجود آمد. لطفاً دوباره امتحان کنید.")

# تأیید پرداخت و ارسال فایل به کاربر
async def verify_payment(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    authority = query.data

    if authority in pending_payments:
        payment_info = pending_payments[authority]
        verification_data = {
            "merchant_id": MERCHANT_ID,
            "amount": payment_info["amount"],
            "authority": authority
        }
        response = requests.post("https://api.zarinpal.com/pg/v4/payment/verify.json", json=verification_data)
        result = response.json()

        if "data" in result and result["data"]["code"] == 100:
            # ارسال فایل بعد از پرداخت موفق
            await send_file_to_user(payment_info["user_id"], payment_info["file"], context)
            del pending_payments[authority]  # حذف پرداخت موفق از لیست
        else:
            await context.bot.send_message(chat_id=payment_info["user_id"], text="❌ پرداخت شما تأیید نشد. لطفاً مجدداً تلاش کنید.")

# ارسال فایل PDF به کاربر
async def send_file_to_user(chat_id, file_path, context):
    await context.bot.send_document(chat_id=chat_id, document=open(file_path, "rb"),
                                    caption="✅ با تشکر از خرید شما! فایل آموزشی برای شما ارسال شد.")

# تابع اصلی برای راه‌اندازی ربات
def main() -> None:
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT, handle_response))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(CallbackQueryHandler(verify_payment))

    print("🤖 Bot is running...")
    application.run_polling()

if __name__ == '__main__':
    main()
