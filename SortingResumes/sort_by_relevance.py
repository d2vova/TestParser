def calculate_relevance_score(resume, keywords=None, max_salary=None):
    score = 0
    # Увеличиваем балл за наличие заголовка, деталей, зарплаты и местоположения
    if resume.get("title"):
        score += 10
    if resume.get("details"):
        score += 10
    if resume.get("estimated_salary", 'No salary') != 'No salary':
        score += 10
    if resume.get("location"):
        score += 5

    # Проверка на совпадение ключевых слов
    if keywords:
        for keyword in keywords:
            if keyword.lower() in resume.get("details", "").lower() or keyword.lower() in resume.get("title", "").lower():
                score += 15

    # Проверка на соответствие зарплате (учитывая гривны и возможные $)
    if max_salary and resume.get("estimated_salary", 'No salary') != 'No salary':
        try:
            salary = int(resume["estimated_salary"].replace(' ', '').replace('грн', '').replace('$', ''))
            if salary <= max_salary:
                score += 20
        except ValueError:
            pass

    # Проверка на указание опыта работы
    if "років" in resume.get("details", "") or "рік" in resume.get("details", ""):
        score += 10
    return score


def sort_candidates_by_relevance(resumes, keywords=None, max_salary=None):
    # Присваиваем каждому резюме балл релевантности
    for resume in resumes:
        resume["relevance_score"] = calculate_relevance_score(resume, keywords, max_salary)

    # Сортируем резюме по баллу релевантности в порядке убывания
    sorted_resumes = sorted(resumes, key=lambda x: x["relevance_score"], reverse=True)
    return sorted_resumes
