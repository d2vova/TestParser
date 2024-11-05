# run_all.py
import subprocess

print("Запуск парсингу та сортування...")
subprocess.run(["python", "main.py"])

print("Запуск Telegram-бота...")
subprocess.run(["python", "telegram_bot.py"])
