import streamlit as st
import os
import tempfile
import zipfile
import pandas as pd
import json
from collections import Counter
import time

# Your extract functions
from resume_parser.extract_name import extract_name as extract_names
from resume_parser.extract_contact import extract_phone
from resume_parser.extract_email import extract_email
from resume_parser.extract_education import extract_education
from resume_parser.extract_skills import extract_skills
from resume_parser.extract_experience import extract_experience
from resume_parser.extract_projects import extract_projects

# Helper to load external resource files only once
def load_data_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return set(line.strip().lower() for line in file if line.strip())

# Flatten helper for dashboard
def flatten_column(col):
    items = []
    for val in col.dropna():
        items.extend([v.strip() for v in val.split(',') if v.strip() and 'no ' not in v.lower()])
    return items

# Function to process a single resume file
def process_resume(file_path, text, jobs, companies, projects, original_filename=None):

    edu_data = extract_education(text)
    exp_data = extract_experience(text, jobs, companies)
    return {
        "File Name": original_filename if original_filename else os.path.basename(file_path),
        "Name": extract_names(original_filename if original_filename else file_path),
        "Email": extract_email(text),
        "Phone": extract_phone(text),
        "Education": ", ".join(edu_data.get("Education", [])),
        "Specialization": ", ".join(edu_data.get("Specialization", [])),
        "Graduation Years": ", ".join(edu_data.get("Year of Graduation", [])),
        "University": ", ".join(edu_data.get("Institution/University", [])),
        "Skills": ", ".join(extract_skills(text)),
        "Projects": ", ".join(extract_projects(text, projects)),
        "Experience Titles": ", ".join(exp_data.get("Job Titles", [])),
        "Experience Companies": ", ".join(exp_data.get("Companies", [])),
        "Experience Durations": ", ".join(exp_data.get("Durations", [])),
        "Experience Skills": ", ".join(exp_data.get("Key Skills", [])),
    }

# --- Streamlit App Start ---
st.set_page_config(page_title="ResumeXtract", layout="wide")

# Session state for navigation
if "section" not in st.session_state:
    st.session_state.section = "Dashboard"
if "show_sidebar" not in st.session_state:
    st.session_state.show_sidebar = False

# Hamburger button at top-left (Streamlit native, not HTML/JS)
col1, col2 = st.columns([0.08, 0.92])
with col1:
    # Hamburger toggles sidebar open/close
    if st.button("☰", key="menu_toggle", help="Toggle menu"):
        st.session_state.show_sidebar = not st.session_state.show_sidebar

# Sidebar logic: only show when triggered
if st.session_state.show_sidebar:
    with st.sidebar:
        st.markdown("### ☰ Menu")
        # Only change section, do NOT close sidebar on button click
        if st.button("Dashboard", use_container_width=True):
            st.session_state.section = "Dashboard"
        if st.button("Output", use_container_width=True):
            st.session_state.section = "Output"
        # Only hamburger button toggles sidebar

st.title("📄 ResumeXtract - Smart Resume Information Extractor")

section = st.session_state.section

if section == "Dashboard":
    tabs = st.tabs(["🗂 Bulk Resume Upload", "📄 Single Resume Upload"])

    # Load external resources ONCE
    jobs_set = load_data_from_file("Text Files/Jobs.txt")
    companies_set = load_data_from_file("Text Files/Companies.txt")
    projects_set = load_data_from_file("Text Files/Project_names.txt")

    # Ensure output directories exist
    os.makedirs("output/csv files", exist_ok=True)
    os.makedirs("output/JSON files", exist_ok=True)

    # Initialize session state for results and last processed filenames
    if "bulk_result" not in st.session_state:
        st.session_state.bulk_result = None
    if "single_result" not in st.session_state:
        st.session_state.single_result = None
    if "last_bulk_filename" not in st.session_state:
        st.session_state.last_bulk_filename = None
    if "last_single_filename" not in st.session_state:
        st.session_state.last_single_filename = None

    # -------------------------- MODE 1: BULK --------------------------
    with tabs[0]:
        st.header("Upload a Zip File Containing Resumes (.txt files)")
        zip_file = st.file_uploader("\U0001F4C1 Upload ZIP File", type=["zip"], key="bulk_zip")

        # Only process if a new zip file is uploaded
        if zip_file is not None and (zip_file.name != st.session_state.last_bulk_filename):
            st.session_state.bulk_result = None
            st.session_state.last_bulk_filename = zip_file.name

            with tempfile.TemporaryDirectory() as tmpdir:
                zip_path = os.path.join(tmpdir, "resumes.zip")
                with open(zip_path, "wb") as f:
                    f.write(zip_file.read())

                with zipfile.ZipFile(zip_path, "r") as zip_ref:
                    zip_ref.extractall(tmpdir)

                st.success("✅ Resumes extracted successfully.")

                txt_files = []
                for root, _, files in os.walk(tmpdir):
                    for file in files:
                        if file.endswith(".txt"):
                            txt_files.append(os.path.join(root, file))

                extracted_data = []
                progress = st.progress(0)
                status = st.empty()

                for i, file_path in enumerate(txt_files):
                    with open(file_path, 'r', encoding='utf-8') as file:
                        text = file.read()

                    extracted_data.append(process_resume(file_path, text, jobs_set, companies_set, projects_set))
                    progress.progress((i + 1) / len(txt_files))
                    status.info(f"Processing {i + 1}/{len(txt_files)}: {os.path.basename(file_path)}")

                df = pd.DataFrame(extracted_data)
                st.session_state.bulk_result = df  # Store result in session state

        # Display results if available
        df = st.session_state.bulk_result
        if df is not None and not df.empty:
            st.subheader("\U0001F4CA Extracted Resume Data")
            st.dataframe(df, use_container_width=True)

            csv_data = df.to_csv(index=False).encode("utf-8")
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            csv_filename = f"extracted_resume_data_{timestamp}.csv"
            csv_output_path = os.path.join("output/csv files", csv_filename)

            # Save CSV to output/csv files when button is clicked AND show download link for local file
            if st.button("\u2B07\uFE0F Save Extracted CSV File to Output"):
                with open(csv_output_path, "wb") as f:
                    f.write(csv_data)
                st.success(f"File saved to: {csv_output_path}")

            # Provide browser download separately
            st.download_button("\u2B07\uFE0F Download Extracted CSV File", csv_data, csv_filename, "text/csv")

            # --- Dashboard Charts ---
            import plotly.express as px

            st.subheader("\U0001F4C8 Dashboard Insights")
            # Prepare skill data for filtering
            skill_items = flatten_column(df['Skills']) if 'Skills' in df.columns else []
            skill_counts = Counter(skill_items)
            skill_df = pd.DataFrame(skill_counts.items(), columns=['Skill', 'Count']).sort_values('Count', ascending=False)

            # Skills chart and filter
            st.markdown("#### Top Skills")
            st.plotly_chart(px.bar(skill_df.head(15), x='Skill', y='Count', title='Top Skills'), use_container_width=True)

            # Skill filter checkboxes
            selected_skills = st.multiselect(
                "Filter resumes by skills (select one or more):",
                options=skill_df['Skill'].tolist(),
                default=[]
            )

            if selected_skills:
                # Filter rows where ALL selected skills are present (cumulative AND logic)
                mask = df['Skills'].apply(
                    lambda x: all(skill in x for skill in selected_skills)
                )
                filtered_df = df[mask]
                st.markdown(f"**Filtered resumes with ALL selected skills ({len(filtered_df)})**")
                st.dataframe(filtered_df, use_container_width=True)

                # Download/save filtered CSV
                filtered_csv_data = filtered_df.to_csv(index=False).encode("utf-8")
                filtered_csv_filename = f"filtered_resume_data_{time.strftime('%Y%m%d-%H%M%S')}.csv"
                filtered_csv_output_path = os.path.join("output/csv files", filtered_csv_filename)

                if st.button("\u2B07\uFE0F Save Filtered CSV File to Output"):
                    with open(filtered_csv_output_path, "wb") as f:
                        f.write(filtered_csv_data)
                    st.success(f"Filtered file saved to: {filtered_csv_output_path}")

                st.download_button("\u2B07\uFE0F Download Filtered CSV File", filtered_csv_data, filtered_csv_filename, "text/csv")
            else:
                st.info("Select skills above to filter resumes.")

            # Other charts
            for column, title in [
                ('Education', 'Top Qualifications'),
                ('Specialization', 'Top Specializations')
            ]:
                items = flatten_column(df[column]) if column in df.columns else []
                if items:
                    counts = Counter(items)
                    data_df = pd.DataFrame(counts.items(), columns=[column, 'Count']).sort_values('Count', ascending=False)
                    chart = px.pie(data_df, names=column, values='Count', title=title)
                    st.plotly_chart(chart, use_container_width=True)
                else:
                    st.info(f"No {column} data to display.")
        elif df is not None:
            st.warning("No resumes found in the uploaded zip.")

    # -------------------------- MODE 2: SINGLE --------------------------
    with tabs[1]:
        st.header("Upload a Single Resume File (.txt)")
        txt_file = st.file_uploader("\U0001F4C4 Upload Resume (.txt)", type=["txt"], key="single_file")

        # Only process if a new txt file is uploaded
        if txt_file is not None and (txt_file.name != st.session_state.last_single_filename):
            st.session_state.single_result = None
            st.session_state.last_single_filename = txt_file.name

            with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp_file:
                tmp_file.write(txt_file.read())
                resume_path = tmp_file.name

            with open(resume_path, 'r', encoding='utf-8') as file:
                text = file.read()

            st.success(f"✅ Resume uploaded: {txt_file.name}")
            result = process_resume(
                file_path=resume_path,
                text=text,
                jobs=jobs_set,
                companies=companies_set,
                projects=projects_set,
                original_filename=txt_file.name  # this fixes name extraction
            )
            st.session_state.single_result = result  # Store result in session state

        # Display results if available
        result = st.session_state.single_result
        if result is not None:
            st.subheader("\U0001F4DD Extracted Details")
            for k, v in result.items():
                st.markdown(f"**{k}:** {v if v else 'Not Found'}")

            json_data = json.dumps(result, indent=2)
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            json_filename = f"resume_info_{timestamp}.json"
            json_output_path = os.path.join("output/JSON files", json_filename)

            # Save JSON to output/JSON files when button is clicked AND show download link for local file
            if st.button("\u2B07\uFE0F Save Extracted Info (JSON) to Output Folder"):
                with open(json_output_path, "w", encoding="utf-8") as f:
                    f.write(json_data)
                st.success(f"File saved to: {json_output_path}")

            # Provide browser download separately
            st.download_button("\u2B07\uFE0F Download Extracted Info (JSON)", json_data, json_filename, "application/json")

elif section == "Output":
    st.header("📁 Output Files")

    # Tabs for CSV and JSON files
    output_tabs = st.tabs(["CSV Files", "JSON Files"])

    # --- CSV Files Tab ---
    with output_tabs[0]:
        st.markdown("### Saved CSV Files")
        csv_dir = "output/csv files"
        csv_files = [f for f in os.listdir(csv_dir) if f.endswith(".csv")]

        if csv_files:
            # Sort files by modified date (descending)
            csv_files_sorted = sorted(
                csv_files,
                key=lambda f: os.path.getmtime(os.path.join(csv_dir, f)),
                reverse=True
            )
            sort_option = st.selectbox(
                "Sort by:",
                ["Modified Date (Newest First)", "Modified Date (Oldest First)", "Name (A-Z)", "Name (Z-A)"],
                index=0
            )
            if sort_option == "Modified Date (Oldest First)":
                csv_files_sorted = sorted(
                    csv_files,
                    key=lambda f: os.path.getmtime(os.path.join(csv_dir, f)),
                    reverse=False
                )
            elif sort_option == "Name (A-Z)":
                csv_files_sorted = sorted(csv_files)
            elif sort_option == "Name (Z-A)":
                csv_files_sorted = sorted(csv_files, reverse=True)

            for file in csv_files_sorted:
                file_path = os.path.abspath(os.path.join(csv_dir, file))
                mod_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getmtime(file_path)))
                # Use download button for clickable link, no filepath shown
                with open(file_path, "rb") as f:
                    file_bytes = f.read()
                st.download_button(
                    label=f"{file} (Last Modified: {mod_time})",
                    data=file_bytes,
                    file_name=file,
                    mime="text/csv"
                )
        else:
            st.info("No CSV files found in output folder.")

    # --- JSON Files Tab ---
    with output_tabs[1]:
        st.markdown("### Saved JSON Files")
        json_dir = "output/JSON files"
        json_files = [f for f in os.listdir(json_dir) if f.endswith(".json")]

        if json_files:
            # Sort files by modified date (descending)
            json_files_sorted = sorted(
                json_files,
                key=lambda f: os.path.getmtime(os.path.join(json_dir, f)),
                reverse=True
            )
            sort_option_json = st.selectbox(
                "Sort by:",
                ["Modified Date (Newest First)", "Modified Date (Oldest First)", "Name (A-Z)", "Name (Z-A)"],
                index=0,
                key="json_sort"
            )
            if sort_option_json == "Modified Date (Oldest First)":
                json_files_sorted = sorted(
                    json_files,
                    key=lambda f: os.path.getmtime(os.path.join(json_dir, f)),
                    reverse=False
                )
            elif sort_option_json == "Name (A-Z)":
                json_files_sorted = sorted(json_files)
            elif sort_option_json == "Name (Z-A)":
                json_files_sorted = sorted(json_files, reverse=True)

            for file in json_files_sorted:
                file_path = os.path.abspath(os.path.join(json_dir, file))
                mod_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getmtime(file_path)))
                with open(file_path, "rb") as f:
                    file_bytes = f.read()
                st.download_button(
                    label=f"{file} (Last Modified: {mod_time})",
                    data=file_bytes,
                    file_name=file,
                    mime="application/json"
                )
        else:
            st.info("No JSON files found in output folder.")
