import os
from resume_parser.extract_name import extract_name as extract_names
from resume_parser.extract_contact import extract_phone
from resume_parser.extract_email import extract_email
from resume_parser.extract_education import extract_education
from resume_parser.extract_skills import extract_skills
from resume_parser.extract_experience import extract_experience
from resume_parser.extract_projects import extract_projects



def run_single_resume(file_path, original_filename=None):
    """Extracts and displays all info from a single resume file."""
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return

    with open(file_path, "r", encoding="utf-8") as file:
        text = file.read()

    edu_data = extract_education(text)
    exp_data = extract_experience(text)

    result = {
        "Extracted Name": extract_names(original_filename or file_path),
        "Email": extract_email(text),
        "Phone Number": extract_phone(text),
        "Education": ", ".join(edu_data.get("Education", [])),
        "Specialization": ", ".join(edu_data.get("Specialization", [])),
        "Graduation Year(s)": ", ".join(edu_data.get("Year of Graduation", [])),
        "University": ", ".join(edu_data.get("Institution/University", [])),
        "Skills": ", ".join(extract_skills(text)),
        "Experience Titles": ", ".join(exp_data.get("Job Titles", [])),
        "Experience Companies": ", ".join(exp_data.get("Companies", [])),
        "Experience Durations": ", ".join(exp_data.get("Durations", [])),
        "Experience Skills": ", ".join(exp_data.get("Key Skills", [])),
        "Projects": ", ".join(extract_projects(text))
    }

    print(f"\n📝 Extracted Details from: {os.path.basename(file_path)}")
    print("-------------------------------------------------------------")
    for key, value in result.items():
        print(f"{key:25}: {value}")
