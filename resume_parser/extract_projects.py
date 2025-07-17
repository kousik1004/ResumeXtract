import os
import re

# Define project root and text file directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
TEXT_FILE_DIR = os.path.join(PROJECT_ROOT, "Text Files")

project_names_filepath = os.path.join(TEXT_FILE_DIR, "Project_names.txt")


def load_data_from_file(file_path):
    """Reads data from a file and returns it as a set."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return set(line.strip().lower() for line in file if line.strip())


# Load project names set (once per import)
project_names_set = load_data_from_file(project_names_filepath)


def extract_projects(text, project_names_set=None):
    """Extracts predefined project names from the resume text."""
    if not project_names_set:
        return ["No projects found"]
    
    text_lower = text.lower()
    matched_projects = sorted({project for project in project_names_set if project.lower() in text_lower})
    
    return matched_projects if matched_projects else ["No projects found"]
