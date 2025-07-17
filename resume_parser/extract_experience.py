import re
import os

# Local paths (can be customized later)
import os

MODULE_DIR = os.path.dirname(__file__)  # This is resume_parser/
TEXT_FILE_DIR = os.path.join(MODULE_DIR, "..", "Text Files")
TEXT_FILE_DIR = os.path.abspath(TEXT_FILE_DIR)  # (optional, for absolute path)

job_titles_filepath = os.path.join(TEXT_FILE_DIR, "Jobs.txt")
company_names_filepath = os.path.join(TEXT_FILE_DIR, "Companies.txt")


def load_data_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return set(line.strip().lower() for line in file if line.strip())


# Load once for reuse
job_titles_set = load_data_from_file(job_titles_filepath)
company_names_set = load_data_from_file(company_names_filepath)


def extract_experience(text, job_titles_set=None, company_names_set=None):
    """Extract job titles, companies, durations, and key skills from a resume text."""

    # Match job titles by simple string containment
    job_titles = [title for title in job_titles_set if title.lower() in text.lower()] if job_titles_set else []

    # Match company names
    companies = [company for company in company_names_set if company in text.lower()] if company_names_set else []
    clean_companies = list(set(companies))

    # Duration pattern like Jan 2020 - Present, 2019–2021, etc.
    duration_pattern = r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)?\s?\d{4}(?:\s?[-to–]\s?(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)?\s?\d{4}| Present)?\b"
    durations = re.findall(duration_pattern, text)
    durations = [d for d in durations if re.search(r"\d{4}", d) and int(re.search(r"\d{4}", d).group()) >= 2000]
    durations = sorted(set(d.strip() for d in durations))

    # Extract key technical/business skills mentioned
    skills_pattern = r"\b(?:Linux|Oracle|Shell Scripting|ITIL|Python|Java|C\+\+|C#|ASP\.NET|JavaScript|HTML5|CSS|Bootstrap|Google Analytics|SEO|Tally|Adobe Photoshop|Illustrator|Visual Studio|Risk Calculation|Fraud Reporting|Financial Data Analysis)\b"
    skills = list(set(re.findall(skills_pattern, text, re.IGNORECASE)))
    skills = [skill.lower() for skill in skills]

    return {
        "Job Titles": sorted(set(job_titles)) or ["No job titles found"],
        "Companies": sorted(clean_companies) or ["No companies found"],
        "Durations": durations or ["No durations found"],
        "Key Skills": sorted(skills) or ["No key skills found"]
    }
