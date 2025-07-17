import re
from fuzzywuzzy import fuzz

# Define skill set
TECHNICAL_SKILL_SET = [
    "C++", "C", "Python", "Java", "JavaScript", "SQL", "R", "Machine Learning", "Deep Learning",
    "TensorFlow", "PyTorch", "NLP", "Data Science", "Power BI", "Tableau", "Excel",
    "Git", "Docker", "Kubernetes", "AWS", "Azure", "GCP", "Flask", "Django", "FastAPI",
    "HTML", "CSS", "React", "Node.js", "Angular", "SEO", "Oracle", "Hadoop", "Big Data",
    "ETL", "Pandas", "NumPy", "JIRA", "Agile"
]

def extract_skills(text, threshold=90):
    """
    Extracts technical skills from the given text using fuzzy matching.
    Returns a sorted list of matched skills or ['No skills found'].
    """
    words = re.findall(r'\b\w+\b', text)
    found_skills = set()

    # Prioritize longer skills (like C++ over C)
    for skill in sorted(TECHNICAL_SKILL_SET, key=len, reverse=True):
        if skill == "AWS":
            if re.search(r'\bAWS\b', text, re.IGNORECASE):
                found_skills.add("AWS")
        else:
            if any(fuzz.token_sort_ratio(skill.lower(), word.lower()) >= threshold for word in words):
                found_skills.add(skill)

    # Avoid double count of "C" if "C++" is present
    if "C++" in found_skills and "C" in found_skills:
        found_skills.remove("C")

    # Bonus detection: If Excel found, suggest related skills
    if "Excel" in found_skills:
        for related_skill in ["Power BI", "Tableau", "Pandas"]:
            if fuzz.partial_ratio(related_skill.lower(), text.lower()) >= threshold - 5:
                found_skills.add(related_skill)

    return sorted(found_skills) if found_skills else ["No skills found"]
