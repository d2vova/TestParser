import requests
from bs4 import BeautifulSoup
import json
import time
import random
from tqdm import tqdm


def fetch_resumes_work_ua(job_title=None, experience=None, skill=None, location=None, salary=None, pages=1):
    # Базовый URL для work.ua
    base_url = "https://www.work.ua/resumes"

    # Формируем URL на основе фильтров
    if job_title:
        base_url += f"{job_title.lower().replace(' ', '+')}/"
    if skill:
        base_url += f"{skill.lower().replace(' ', '+')}/"
    if location:
        base_url += f"{location.lower().replace(' ', '+')}/"

    resume_list = []

    for page in range(1, pages + 1):
        url = f"{base_url}?page={page}"
        print(f"Парсинг страницы: {url}")

        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        resumes = soup.find_all('div', class_='card card-hover card-search resume-link card-visited wordwrap')
        print(f"Найдено резюме на странице: {len(resumes)}")  # Отладочный вывод

        for resume in resumes:
            title = resume.find('h2').text.strip() if resume.find('h2') else 'No title'
            link = f"https://www.work.ua{resume.find('a')['href']}" if resume.find('a') else 'No link'
            name = resume.find('span', class_='resume-link__title').text.strip() if resume.find(
                'span', class_='resume-link__title') else 'No name'
            details = resume.find('p', class_='overflow').text.strip() if resume.find(
                'p', class_='overflow') else 'No details'
            posted_time = resume.find('div', class_='text-muted').text.strip() if resume.find(
                'div', class_='text-muted') else 'No time'
            salary_data = resume.find('span', class_='text-muted').text.strip() if resume.find(
                'span', class_='text-muted') else 'No salary'

            resume_data = {
                "title": title,
                "link": link,
                "name": name,
                "details": details,
                "posted_time": posted_time,
                "salary": salary_data
            }

            # Применение фильтров после парсинга
            if experience and experience.lower() not in details.lower():
                continue
            if skill and skill.lower() not in details.lower():
                continue
            if location and location.lower() not in details.lower():
                continue
            if salary:
                try:
                    # Извлекаем числовое значение зарплаты для сравнения
                    salary_value = int(salary_data.replace(' ', '').replace('грн', ''))
                    if salary_value < int(salary):
                        continue
                except ValueError:
                    continue  # Пропускаем, если зарплата указана некорректно

            # Добавляем резюме в список после успешного прохождения всех фильтров
            resume_list.append(resume_data)

        time.sleep(random.randint(5, 10))  # Умеренная задержка

    return resume_list


def save_to_json(data, filename):
    """Сохранение списка данных о резюме в JSON файл."""
    with open(filename, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)
    print(f"Данные сохранены в {filename}")


# Пример использования
if __name__ == "__main__":
    job_title = "Python-програміст"
    experience = ""
    skill = "Python"
    location = "Дистанційно"
    salary = ""
    pages = 3

    resumes = fetch_resumes_work_ua(job_title=job_title, experience=experience, skill=skill,
                            location=location, salary=salary, pages=pages)
    save_to_json(resumes, 'resumes_work_ua.json')
