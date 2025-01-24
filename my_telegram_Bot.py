import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackContext, MessageHandler, filters, CallbackQueryHandler

# توکن API که از BotFather دریافت کرده‌اید
TOKEN =  "7563490359:AAH3p2f9JcP4Bii0HnOUGb2fZnatEHWw6r8"

# تنظیمات لاگ برای نمایش خطاها
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# تابع برای دستور start
async def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user

    # چاپ خوش آمدگویی در کنسول
    print(f"User {user.first_name} has started the bot!")

    # تعریف دکمه‌های اصلی منو
    keyboard = [
        [KeyboardButton("پکیج‌های آموزشی پایتون")],
        [KeyboardButton("پشتیبانی و سوالات متداول")],
        [KeyboardButton("دریافت نمونه رایگان")]
    ]

    # ایجاد صفحه کلید پاسخ
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

    # ارسال پیام خوش آمدگویی و منو
    await update.message.reply_text(
        f"سلام {user.first_name} عزیز! خوش آمدید.\nبرای شروع از گزینه‌های منو استفاده کنید.",
        reply_markup=reply_markup
    )

# تابع برای مدیریت انتخاب‌ها
async def handle_response(update: Update, context: CallbackContext) -> None:
    text = update.message.text

    # چاپ انتخاب‌های کاربر در کنسول
    print(f"User selected: {text}")

    if text == "پکیج‌های آموزشی پایتون":
        keyboard = [
            [
                InlineKeyboardButton("پکیج پایتون - پایه هفتم", callback_data='seventh'),
                InlineKeyboardButton("پکیج پایتون - پایه هشتم", callback_data='eighth'),
            ],
            [InlineKeyboardButton("پکیج پایتون - پایه نهم", callback_data='ninth')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("پکیج‌های آموزشی پایتون را انتخاب کنید:\nلطفاً یک پایه را انتخاب کنید:", reply_markup=reply_markup)

    elif text == "پشتیبانی و سوالات متداول":
        await update.message.reply_text("شما به بخش پشتیبانی و سوالات متداول منتقل شدید. در اینجا می‌توانید سوالات خود را بپرسید.")

    elif text == "دریافت نمونه رایگان":
        await update.message.reply_text("شما به بخش دریافت نمونه رایگان منتقل شدید. فایل نمونه رایگان در اختیار شما قرار گرفت.")

# تابع برای پاسخ به انتخاب‌های داخل منو
async def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    # چاپ اطلاعات دکمه‌های فشرده شده در کنسول
    print(f"Button pressed: {query.data}")

    if query.data == 'seventh':
        await query.edit_message_text(text="پکیج‌های آموزشی پایتون برای پایه هفتم:\nبرای خرید این پکیج، لطفاً با ما تماس بگیرید.")
        
    elif query.data == 'eighth':
        await query.edit_message_text(text="پکیج‌های آموزشی پایتون برای پایه هشتم:\nبرای خرید این پکیج، لطفاً با ما تماس بگیرید.")
        
    elif query.data == 'ninth':
        await query.edit_message_text(text="پکیج‌های آموزشی پایتون برای پایه نهم:\nبرای خرید این پکیج، لطفاً با ما تماس بگیرید.")

# تابع اصلی برای راه‌اندازی ربات
def main() -> None:
    # ساخت یک Application با استفاده از توکن API
    application = Application.builder().token(TOKEN).build()

    # ثبت دستور start
    application.add_handler(CommandHandler("start", start))

    # ثبت handler برای انتخاب‌های منو
    application.add_handler(MessageHandler(filters.TEXT, handle_response))

    # ثبت handler برای callback های دکمه‌های منو
    application.add_handler(CallbackQueryHandler(button))

    # شروع ربات
    print("Bot is running...")
    application.run_polling()

if __name__ == '__main__':
    main()
