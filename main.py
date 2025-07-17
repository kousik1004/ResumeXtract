from test.test_runner import test_runner
from test.single_resume_runner import run_single_resume

if __name__ == "__main__":
    # 🔄 Mode 1: Bulk resume folder (Creates CSV)
    sample_resumes_path = "sample_resumes"
    test_runner(sample_resumes_path)

    # 👤 Mode 2: Test a single resume file (Displays clean info)
    # single_resume_path = r"test_batch\953_Mohan_Kumar_Girirajan.txt"
    # run_single_resume(single_resume_path)
