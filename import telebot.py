from telegram import Update, ReplyKeyboardMarkup, Bot, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from fpdf import FPDF
import logging
from datetime import datetime, timedelta

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Этапы диалога
CHOOSING_SPECIALIST, CHOOSING_DATE, CHOOSING_TIME = range(3)

# Хранение списка врачей
doctors = ["Стоматолог", "Терапевт", "Психиатр", "Эндокринолог"]

# Функция для создания PDF-файла
def create_pdf(doctor, date):
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font('TimesNewRomanPSMT', '', 'E:\\Создание чатбота\\timesnewromanpsmt.ttf', uni=True)  # Добавляем шрифт с поддержкой UTF-8
    pdf.set_font("TimesNewRomanPSMT", size=12)  # Используем этот шрифт
    
    pdf.cell(200, 10, txt="Запись на прием", ln=True, align='C')
    pdf.cell(200, 10, txt=f"Врач: {doctor}", ln=True, align='L')
    pdf.cell(200, 10, txt=f"Дата: {date}", ln=True, align='L')
    pdf.output("appointment_ticket.pdf")

# Функция для создания клавиатуры с врачами
def create_doctor_keyboard():
    keyboard = [[KeyboardButton(doctor)] for doctor in doctors]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# Функция для создания клавиатуры с датами
def create_date_keyboard():
    keyboard = [[KeyboardButton((datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d"))] for i in range(7)]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# Старт диалога и начало выбора врача
async def handle_appointment_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Выберите специалиста:", reply_markup=create_doctor_keyboard())
    return CHOOSING_SPECIALIST

# Выбор врача и переход к выбору даты
async def choose_specialist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['doctor'] = update.message.text
    await update.message.reply_text("Выберите дату приема:", reply_markup=create_date_keyboard())
    return CHOOSING_DATE

# Выбор даты и переход к подтверждению
async def choose_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['date'] = update.message.text
    create_pdf(context.user_data['doctor'], context.user_data['date'])
    await update.message.reply_text(f"Вы записаны на прием к {context.user_data['doctor']} на {context.user_data['date']}. Талон сохранен в PDF формате.", reply_markup=create_keyboard())
    return ConversationHandler.END

# Функция для создания основной клавиатуры
def create_keyboard():
    keyboard = [
        [KeyboardButton("Записаться на прием")],
        [KeyboardButton("🏠 Главное меню")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# Функция для старта бота
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Добро пожаловать! Нажмите 'Записаться на прием', чтобы начать.", reply_markup=create_keyboard())

# Основная функция для запуска бота
def main() -> None:
    bot_token = "7322321899:AAHA2t4_iqyhwSzT185KtvsB8NLKJ3x-oi4"  # Замените на свой токен
    bot = Bot(token=bot_token)
    application = ApplicationBuilder().token(bot_token).build()

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('Записаться на прием'), handle_appointment_button)],
        states={
            CHOOSING_SPECIALIST: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_specialist)],
            CHOOSING_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_date)],
        },
        fallbacks=[],
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("start", start))

    application.run_polling()

if __name__ == '__main__':
    main()
