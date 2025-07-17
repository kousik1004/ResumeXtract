import re

# Mapping for standardizing degrees
DEGREE_MAPPING = {
    "btech": "B.Tech", "be": "B.E", "me": "M.E", "master": "Master's",
    "bachelor": "Bachelor's", "mtech": "M.Tech", "mba": "MBA", "phd": "Ph.D"
}

# Regular Expressions
DEGREE_REGEX = r"(?i)(B\.?Tech|M\.?Tech|B\.?E|M\.?E|MBA|Ph\.?D|Diploma|Bachelor|Master)[^,.\n]*"
SPECIALIZATION_REGEX = r"(?i)(ECE|CSE|IT|Mechanical|Electrical|Electronics|Civil|Biotech|AI|Data Science|Finance|Management|Marketing|Physics|Chemistry)"
YEAR_REGEX = r"\b(19\d{2}|20\d{2})\b"
UNIVERSITY_REGEX = r"(?i)(?:from|at|in)\s+([A-Za-z\s&,.]+(?:University|Institute|College))"


def clean_degrees(degrees):
    cleaned = {DEGREE_MAPPING.get(deg.lower(), deg) for deg in degrees}
    return sorted(cleaned) if cleaned else ["No degree found"]


def clean_specializations(specializations):
    cleaned = {spec.lower().capitalize() for spec in specializations}
    return sorted(cleaned) if cleaned else ["No specialization found"]


def extract_education(text):
    degrees = re.findall(DEGREE_REGEX, text)
    specializations = re.findall(SPECIALIZATION_REGEX, text)
    years = re.findall(YEAR_REGEX, text)
    universities = re.findall(UNIVERSITY_REGEX, text)

    return {
        "Education": clean_degrees(degrees),
        "Specialization": clean_specializations(specializations),
        "Year of Graduation": sorted(set(years)) if years else ["No years found"],
        "Institution/University": sorted(set(universities)) if universities else ["No university found"]
    }
