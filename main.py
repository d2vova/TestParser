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
    job_title = "data analyst"
    location = "kyiv"
    pages = 2

    print("Парсинг данных с work.ua...")
    work_ua_resumes = fetch_resumes_work_ua(job_title = job_title, location = location, pages = pages)
    print("Парсинг данных с rabota.ua...")
    driver = setup_selenium()
    url = "https://rabota.ua/candidates/python/ukraine"
    rabota_ua_resumes = fetch_resumes_rabota_ua(url, driver)

    driver.quit()
    all_resumes = work_ua_resumes + rabota_ua_resumes
    save_resumes(all_resumes, 'all_resumes.json')
    resumes = load_resumes('all_resumes.json')
    keywords = ["Python", "Дані", "Аналіз"]
    max_salary = 50000
    sorted_resumes = sort_candidates_by_relevance(resumes, keywords=keywords, max_salary=max_salary)

    for resume in sorted_resumes:
        title = resume.get("title", "No title")
        relevance_score = resume.get("relevance_score", 0)
        estimated_salary = resume.get("estimated_salary", "No salary")

        print(f"Заголовок: {title}, Балл релевантности: {relevance_score}, Зарплата: {estimated_salary}")
