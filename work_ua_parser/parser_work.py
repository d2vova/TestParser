import requests
from bs4 import BeautifulSoup
import json
import time
import random
from tqdm import tqdm


def fetch_resumes_work_ua(job_title=None, location=None, pages=1):
    job_title_formatted = job_title.lower().replace(" ", "+") if job_title else ""
    location_formatted = f"-{location.lower()}" if location else ""

    base_url = f"https://www.work.ua/resumes{location_formatted}-{job_title_formatted}/"

    resume_list = []

    for page in range(1, pages + 1):
        url = f"{base_url}?page={page}"
        print(f"Парсинг страницы: {url}")

        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        resumes = soup.find_all('div', class_='card card-hover card-search resume-link card-visited wordwrap')
        print(f"Найдено резюме на странице: {len(resumes)}")

        for resume in resumes:
            title = resume.find('h2').text.strip() if resume.find('h2') else 'No title'
            link = f"https://www.work.ua{resume.find('a')['href']}" if resume.find('a') else 'No link'
            details = resume.find('p', class_='overflow').text.strip() if resume.find(
                'p', 'overflow') else 'No details'
            posted_time = resume.find('div', class_='text-muted').text.strip() if resume.find(
                'div', 'text-muted') else 'No time'
            salary_data = resume.find('span', class_='text-muted').text.strip() if resume.find(
                'span', 'text-muted') else 'No salary'

            resume_data = {
                "title": title,
                "link": link,
                "details": details,
                "posted_time": posted_time,
                "salary": salary_data
            }

            resume_list.append(resume_data)

        time.sleep(random.randint(5, 10))

    return resume_list


def save_to_json(data, filename):
    """Сохранение списка данных о резюме в JSON файл."""
    with open(filename, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)
    print(f"Данные сохранены в {filename}")


if __name__ == "__main__":
    job_title = "Python-програміст"
    experience = ""
    skill = "Python"
    location = ""
    salary = ""
    pages = 3

    resumes = fetch_resumes_work_ua(job_title=job_title, experience=experience, skill=skill,
                            location=location, salary=salary, pages=pages)
    save_to_json(resumes, 'resumes_work_ua.json')
