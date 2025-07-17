import os
import pandas as pd

from resume_parser.extract_name import extract_name as extract_names
from resume_parser.extract_contact import extract_phone
from resume_parser.extract_email import extract_email
from resume_parser.extract_education import extract_education
from resume_parser.extract_skills import extract_skills
from resume_parser.extract_experience import extract_experience
from resume_parser.extract_projects import extract_projects


def test_runner(root_folder, output_name="final_resume_output.csv"):
    """Scans all .txt files in all subfolders under root_folder, or at root, processes them, and exports results."""
    extracted_data = []

    # Recursively walk through all files and folders
    for dirpath, dirnames, filenames in os.walk(root_folder):
        for file in filenames:
            if file.endswith(".txt"):
                file_path = os.path.join(dirpath, file)
                # Batch is the immediate parent folder, or 'root' if at the top level
                parent = os.path.basename(os.path.dirname(file_path))
                batch_folder = parent if dirpath != root_folder else 'root'
                with open(file_path, "r", encoding="utf-8") as f:
                    text = f.read()

                edu_data = extract_education(text)
                exp_data = extract_experience(text)

                extracted_data.append({
                    "File Name": file,
                    "Batch": batch_folder,
                    "Extracted Name": extract_names(file_path),
                    "Email": extract_email(text),
                    "Phone": extract_phone(text),
                    "Education": ", ".join(edu_data.get("Education", [])),
                    "Specialization": ", ".join(edu_data.get("Specialization", [])),
                    "Graduation Years": ", ".join(edu_data.get("Year of Graduation", [])),
                    "University": ", ".join(edu_data.get("Institution/University", [])),
                    "Skills": ", ".join(extract_skills(text)),
                    "Experience Titles": ", ".join(exp_data.get("Job Titles", [])),
                    "Experience Companies": ", ".join(exp_data.get("Companies", [])),
                    "Experience Durations": ", ".join(exp_data.get("Durations", [])),
                    "Experience Skills": ", ".join(exp_data.get("Key Skills", [])),
                    "Projects": ", ".join(extract_projects(text)),
                })

    df = pd.DataFrame(extracted_data)
    os.makedirs("output", exist_ok=True)
    output_path = os.path.join("output", output_name)
    df.to_csv(output_path, index=False)

    print(f"✅ Extraction completed. Output saved to:\n{output_path}")
    print("\n🔍 Sample Preview:")
    print(df.head())

    return df
