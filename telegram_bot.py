import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from SortingResumes.sort_by_relevance import sort_candidates_by_relevance
from work_ua_parser.parser_work import fetch_resumes_work_ua
from rabota_ua_parser.rabota_ua_parser import fetch_resumes_rabota_ua

TOKEN = '7822942364:AAGePPGtX-uqjHBBO5J7hx7IxKonwZyfz9w'
JOB_TITLE,  SKILL, SALARY, CONFIRMATION = range(4)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Привіт! Я бот для пошуку резюме. Використовуй команду /find, "
        "щоб знайти релевантні резюме за своїми критеріями."
    )

async def find(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Введіть посаду для пошуку (наприклад, 'Python Developer'):")
    return JOB_TITLE

async def job_title(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['job_title'] = update.message.text
    await update.message.reply_text("Введіть навички або ключові слова (наприклад, 'Python'):")
    return SKILL

# async def location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     context.user_data['location'] = update.message.text
#     await update.message.reply_text("Введіть навички або ключові слова (наприклад, 'Python'):")
#     return SKILL

async def skill(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['skill'] = update.message.text
    await update.message.reply_text(
        "Введіть очікувану зарплату (наприклад, '50000') або залиште порожнім для будь-якого рівня:")
    return SALARY

async def salary(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['salary'] = int(update.message.text) if update.message.text.isdigit() else None
    await update.message.reply_text("Запускаю пошук із заданими критеріями...")
    return CONFIRMATION

async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    job_title = context.user_data.get('job_title')
    # location = context.user_data.get('location')
    skill = context.user_data.get('skill')
    salary = context.user_data.get('salary')

    await update.message.reply_text("Запускаю парсинг данных с Work.ua и Rabota.ua...")

    work_ua_resumes = fetch_resumes_work_ua(
        job_title=job_title, skill=skill, salary=salary, pages=1)
    rabota_ua_resumes = fetch_resumes_rabota_ua(
        job_title=job_title, skill=skill, salary=salary, pages=1)

    all_resumes = work_ua_resumes + rabota_ua_resumes
    sorted_resumes = sort_candidates_by_relevance(
        all_resumes, keywords=[skill], max_salary=int(salary) if salary else None)

    top_resumes = sorted_resumes[:5]

    result_text = "Топ-5 релевантних резюме:\n\n"
    for resume in top_resumes:
        result_text += f"Заголовок: {resume['title']}\n"
        # result_text += f"Местоположение: {resume['location']}\n"
        result_text += f"Зарплата: {resume['estimated_salary']}\n"
        result_text += f"Ссылка: {resume['link']}\n\n"

    if not top_resumes:
        result_text = "Не найдено релевантных резюме по заданным критериям."

    await update.message.reply_text(result_text)

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Пошук скасовано. Використовуйте команду /find для нового пошуку.")
    return ConversationHandler.END

def main():
    application = ApplicationBuilder().token(TOKEN).build()

    # ConversationHandler для обработки поиска
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("find", find)],
        states={
            JOB_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, job_title)],
            # LOCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, location)],
            SKILL: [MessageHandler(filters.TEXT & ~filters.COMMAND, skill)],
            SALARY: [MessageHandler(filters.TEXT & ~filters.COMMAND, salary)],
            CONFIRMATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(conv_handler)

    application.run_polling()

if __name__ == '__main__':
    main()
