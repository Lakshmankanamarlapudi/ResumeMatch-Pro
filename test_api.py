import requests

# STEP 1: Put your PDFs in the SAME FOLDER as these scripts
resume = 'my_resume.pdf'  # ← Replace with your filename
jd = 'job_description.pdf'  # ← Replace with your filename

# STEP 2: Run the test
response = requests.post(
    'http://localhost:5000/match',
    files={
        'resume': open(resume, 'rb'),
        'jd': open(jd, 'rb')
    }
)

print(f"Match Score: {response.json()['score']}%")