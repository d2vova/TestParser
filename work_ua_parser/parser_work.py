import requests
from bs4 import BeautifulSoup
import json
import time
import random
from tqdm import tqdm


def fetch_resumes(job_title=None, experience=None, skill=None, location=None, salary=None, pages=1):
    job_title_formatted = job_title.lower().replace(" ", "+") if job_title else ""
    base_url = f"https://www.work.ua/resumes-{job_title_formatted}/"
    resume_list = []

    for page in tqdm(range(1, pages + 1), desc="Обработка страниц"):
        url = f"{base_url}?page={page}"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Отладочный вывод для проверки URL
        print(f"Парсинг страницы: {url}")

        # Ищем блоки резюме на странице
        resumes = soup.find_all('div', class_='card card-hover card-search resume-link card-visited wordwrap')
        print(f"Найдено резюме на странице: {len(resumes)}")  # Отладочный вывод

        for resume in resumes:
            title = resume.find('h2').text.strip() if resume.find('h2') else 'No title'
            link = f"https://www.work.ua{resume.find('a')['href']}" if resume.find('a') else 'No link'

            # Извлечение имени и локации
            personal_info = resume.find('p', class_='mt-xs mb-0')
            name = personal_info.find('span', class_='strong-600').text.strip() \
                if personal_info and personal_info.find('span', class_='strong-600') else 'No name'
            location_data = personal_info.find_all('span')[2].text.strip() \
                if personal_info and len(personal_info.find_all('span')) > 2 else 'No location'

            # Извлечение зарплаты
            salary_element = resume.find('p', class_='h5 strong-600 mt-xs mb-0 nowrap')
            salary_data = salary_element.text.strip().replace('\u00a0', '').replace('грн', '').strip() \
                if salary_element else 'No salary'

            details = resume.find('p', class_='overflow').text.strip() \
                if resume.find('p', class_='overflow') else 'No details'
            # Извлечение даты публикации
            date_published_element = resume.find('time')
            date_published = date_published_element['datetime'] if date_published_element else 'No date'

            resume_data = {
                "title": title,
                "link": link,
                "name": name,
                "location": location_data,
                "salary": salary_data,
                "details": details,
                "date_published": date_published
            }

            # Применение фильтров после парсинга
            if experience and experience.lower() not in details.lower():
                continue
            if skill and skill.lower() not in details.lower():
                continue
            if location and location.lower() not in location_data.lower():
                continue
            if salary:
                try:
                    # Извлекаем числовое значение зарплаты для сравнения
                    salary_value = int(salary_data.replace(' ', ''))
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

    resumes = fetch_resumes(job_title=job_title, experience=experience, skill=skill,
                            location=location, salary=salary, pages=pages)
    save_to_json(resumes, 'resumes_work_ua.json')
