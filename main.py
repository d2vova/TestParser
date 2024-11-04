import json
import time
from rabota_ua_parser.rabota_ua_parser import fetch_resumes_rabota_ua, setup_selenium
from work_ua_parser.parser_work import fetch_resumes_work_ua
from SortingResumes.sort_by_relevance import sort_candidates_by_relevance

def load_resumes(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return json.load(file)

def save_resumes(data, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    # Запуск парсера work.ua
    print("Парсинг данных с work.ua...")
    work_ua_resumes = fetch_resumes_work_ua()  # функция парсинга work.ua

    # Запуск парсер rabota.ua
    print("Парсинг данных с rabota.ua...")
    driver = setup_selenium()  # инициализация драйвера для Selenium
    url = "https://rabota.ua/candidates/python/ukraine"  # URL для парсинга резюме на rabota.ua
    rabota_ua_resumes = fetch_resumes_rabota_ua(url, driver)  # функция парсинга rabota.ua

    driver.quit()

    # Объединяем все резюме
    all_resumes = work_ua_resumes + rabota_ua_resumes

    # Сохраняем объединенные данные в JSON-файл
    save_resumes(all_resumes, 'all_resumes.json')

    # Загрузка данных из файла
    resumes = load_resumes('all_resumes.json')

    # Определяем критерии сортировки
    keywords = ["Python", "Дані", "Аналіз"]  # Пример ключевых слов
    max_salary = 50000  # Максимальная зарплата в гривнах

    # Сортировка резюме по релевантности
    sorted_resumes = sort_candidates_by_relevance(resumes, keywords=keywords, max_salary=max_salary)

    # Вывод отсортированных резюме
    for resume in sorted_resumes:
        title = resume.get("title", "No title")
        relevance_score = resume.get("relevance_score", 0)
        estimated_salary = resume.get("estimated_salary", "No salary")

        print(f"Заголовок: {title}, Балл релевантности: {relevance_score}, Зарплата: {estimated_salary}")
