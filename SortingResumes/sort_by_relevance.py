def calculate_relevance_score(resume, keywords=None, max_salary=None):
    score = 0
    if resume.get("title"):
        score += 10
    if resume.get("details"):
        score += 10
    if resume.get("salary", 'No salary') != 'No salary':
        score += 10
    if resume.get("location"):
        score += 5

    if keywords:
        for keyword in keywords:
            if keyword.lower() in resume.get("details", "").lower() or keyword.lower() in resume.get("title", "").lower():
                score += 15

    if max_salary and resume.get("salary", 'No salary') != 'No salary':
        try:
            salary = int(resume["salary"].replace(' ', '').replace('грн', '').replace('$', ''))
            if salary <= max_salary:
                score += 20
        except ValueError:
            pass

    if "років" in resume.get("details", "") or "рік" in resume.get("details", ""):
        score += 10
    return score


def sort_candidates_by_relevance(resumes, keywords=None, max_salary=None):
    for resume in resumes:
        resume["relevance_score"] = calculate_relevance_score(resume, keywords, max_salary)

    sorted_resumes = sorted(resumes, key=lambda x: x["relevance_score"], reverse=True)
    return sorted_resumes
