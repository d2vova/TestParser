import argparse
import os
import json
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from tqdm import tqdm


# Константы для CSS-селекторов
CV_CARD_SELECTOR = 'section.cv-card'
TITLE_SELECTOR = 'p[data-id="cv-speciality"]'
LINK_SELECTOR = 'a.santa-no-underline'
NAME_SELECTOR = 'p.santa-typo-regular.santa-truncate'
DETAILS_SELECTOR = 'div.santa-flex.santa-items-center.santa-space-x-10.santa-pr-20.santa-whitespace-nowrap'
POSTED_TIME_SELECTOR = 'p.santa-typo-additional.santa-text-black-500'
SALARY_SELECTOR = ('div.santa-flex.santa-items-center.santa-space-x-10.santa-pr-20.santa-whitespace-nowrap '
                   'p.santa-typo-secondary')

def setup_selenium():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Работать в фоновом режиме
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver


def fetch_resumes_rabota_ua(url, driver):
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, CV_CARD_SELECTOR)))
    except TimeoutException:
        print("Превышено время ожидания загрузки страницы. Пропуск страницы.")
        return []

    resumes = driver.find_elements(By.CSS_SELECTOR, CV_CARD_SELECTOR)
    resume_list = []

    for resume in resumes:
        try:
            title = resume.find_element(By.CSS_SELECTOR, TITLE_SELECTOR).text.strip()
        except NoSuchElementException:
            title = 'No title'

        try:
            link = resume.find_element(By.CSS_SELECTOR, LINK_SELECTOR).get_attribute('href')
        except NoSuchElementException:
            link = 'No link'

        try:
            name = resume.find_element(By.CSS_SELECTOR, NAME_SELECTOR).text.strip()
        except NoSuchElementException:
            name = 'No name'

        try:
            details = resume.find_element(By.CSS_SELECTOR, DETAILS_SELECTOR).text.strip()
        except NoSuchElementException:
            details = 'No details'

        try:
            posted_time = resume.find_element(By.CSS_SELECTOR, POSTED_TIME_SELECTOR).text.strip()
        except NoSuchElementException:
            posted_time = 'No time'

        try:
            salary_elements = resume.find_elements(By.CSS_SELECTOR, SALARY_SELECTOR)
            salary = 'No salary'
            for element in salary_elements:
                text = element.text.strip()
                if "грн" in text or "$" in text:
                    salary = text
                    break
        except NoSuchElementException:
            salary = 'No salary'

        resume_data = {
            "title": title,
            "link": link,
            "name": name,
            "details": details,
            "posted_time": posted_time,
            "salary": salary
        }

        # Проверка на дублирование по уникальному 'link'
        if all(item.get('link') != link for item in resume_list):
            resume_list.append(resume_data)

    return resume_list


def save_to_json(data, filename):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as json_file:
            existing_data = json.load(json_file)
        # Фильтрация дубликатов перед добавлением
        unique_data = [item for item in data if all(item.get('link') != ex['link'] for ex in existing_data)]
        existing_data.extend(unique_data)
        with open(filename, 'w', encoding='utf-8') as json_file:
            json.dump(existing_data, json_file, ensure_ascii=False, indent=4)
    else:
        with open(filename, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)


def main(pages, skill=None):
    driver = setup_selenium()

    if skill:
        base_url = f"https://rabota.ua/candidates/{skill}/ukraine"
    else:
        base_url = "https://rabota.ua/candidates/all/ukraine"

    for page in tqdm(range(1, pages + 1), desc="Обработка страниц"):
        url = f"{base_url}?page={page}"
        print(f"\nОбрабатываю страницу {page}...")

        # Случайный таймслип от 3 до 10 секунд
        sleep_time = random.randint(3, 10)
        print(f"Ожидание {sleep_time} секунд...")
        time.sleep(sleep_time)

        resumes = fetch_resumes_rabota_ua(url, driver)
        print(f"Найдено {len(resumes)} резюме на странице {page}.")

        if not resumes:
            print(f"Нет резюме на странице {page}. Завершаю...")
            break

        save_to_json(resumes, 'resumes_rabota_ua.json')

    driver.quit()
    print("Данные успешно сохранены в resumes_rabota_ua.json")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Скрипт для парсинга резюме.")
    parser.add_argument(
        '--pages', type=int, default=2, help='Количество страниц для обхода (по умолчанию 2)')
    parser.add_argument(
        '--skill', type=str, default=None, help='Ключевое слово для поиска (например, "python")')
    args = parser.parse_args()
    main(args.pages, args.skill)
