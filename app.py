from flask import Flask, request, jsonify, render_template_string
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import PyPDF2, io
from time import sleep

app = Flask(__name__)

# Custom CSS and HTML with animations
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ResumeMatch Pro</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        :root {
            --primary: #6c63ff;
            --secondary: #4d44db;
        }
        body {
            background: linear-gradient(135deg, #f5f7fa 0%, #e4e8f0 100%);
            min-height: 100vh;
        }
        .card {
            border: none;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
        }
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 35px rgba(0,0,0,0.15);
        }
        .btn-primary {
            background-color: var(--primary);
            border: none;
            padding: 12px 30px;
            border-radius: 50px;
            font-weight: 600;
        }
        .btn-primary:hover {
            background-color: var(--secondary);
        }
        .progress-bar {
            background-color: var(--primary);
            transition: width 2s ease-in-out;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .fade-in {
            animation: fadeIn 0.8s forwards;
        }
        .pulse {
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }
    </style>
</head>
<body class="py-5">
    <div class="container">
        <div class="row justify-content-center">
            <div class="col-md-8 col-lg-6 fade-in">
                <div class="card p-4 mb-4 text-center">
                    <h1 class="mb-4">🎯 ResumeMatch <span class="text-primary">Pro</span></h1>
                    <p class="text-muted mb-4">Upload your resume and job description to get instant compatibility score</p>
                    
                    <form id="matchForm" action="/match" method="post" enctype="multipart/form-data">
                        <div class="mb-4">
                            <label for="resume" class="form-label d-block text-start mb-2 fw-bold">Your Resume</label>
                            <input type="file" class="form-control" name="resume" accept=".pdf" required>
                        </div>
                        
                        <div class="mb-4">
                            <label for="jd" class="form-label d-block text-start mb-2 fw-bold">Job Description</label>
                            <input type="file" class="form-control" name="jd" accept=".pdf" required>
                        </div>
                        
                        <button type="submit" class="btn btn-primary btn-lg mt-3 pulse">
                            <span id="submitText">Calculate Match</span>
                            <span id="spinner" class="spinner-border spinner-border-sm d-none" role="status"></span>
                        </button>
                    </form>
                </div>
                
                <div id="resultCard" class="card p-4 text-center d-none">
                    <h2 class="mb-3">Your Match Score</h2>
                    <div class="progress mb-4 mx-auto" style="height: 25px; width: 80%">
                        <div id="scoreBar" class="progress-bar progress-bar-striped" role="progressbar" style="width: 0%"></div>
                    </div>
                    <h3 id="scoreText" class="display-4 mb-4"></h3>
                    <p id="feedback" class="lead"></p>
                    <a href="/" class="btn btn-outline-primary">Try Another</a>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        document.getElementById('matchForm').addEventListener('submit', function(e) {
            const btn = this.querySelector('button[type="submit"]');
            btn.disabled = true;
            document.getElementById('submitText').textContent = 'Analyzing...';
            document.getElementById('spinner').classList.remove('d-none');
        });
        
        // Animate progress bar if we're returning with a score
        const urlParams = new URLSearchParams(window.location.search);
        const score = urlParams.get('score');
        if (score) {
            document.getElementById('matchForm').classList.add('d-none');
            document.getElementById('resultCard').classList.remove('d-none');
            
            const scoreBar = document.getElementById('scoreBar');
            const scoreText = document.getElementById('scoreText');
            const feedback = document.getElementById('feedback');
            
            let width = 0;
            const interval = setInterval(() => {
                width += 2;
                scoreBar.style.width = width + '%';
                scoreText.textContent = width + '%';
                
                if (width >= score) {
                    clearInterval(interval);
                    scoreBar.style.width = score + '%';
                    scoreText.textContent = score + '%';
                    
                    // Dynamic feedback
                    if (score >= 80) {
                        feedback.textContent = "Excellent match! This position is perfect for you!";
                        feedback.className = "lead text-success";
                    } else if (score >= 50) {
                        feedback.textContent = "Good match! Consider tailoring your resume further.";
                        feedback.className = "lead text-primary";
                    } else {
                        feedback.textContent = "Keep looking! This position may not be the best fit.";
                        feedback.className = "lead text-danger";
                    }
                }
            }, 50);
        }
    </script>
</body>
</html>
"""

def pdf_to_text(file):
    pdf = PyPDF2.PdfReader(io.BytesIO(file.read()))
    return " ".join(page.extract_text() for page in pdf.pages)

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/match', methods=['POST'])
def match():
    resume_text = pdf_to_text(request.files['resume'])
    jd_text = pdf_to_text(request.files['jd'])
    
    vectors = TfidfVectorizer().fit_transform([jd_text, resume_text])
    score = round(cosine_similarity(vectors[0], vectors[1])[0][0] * 100, 2)
    
    # Return the HTML with score parameter
    return render_template_string(HTML_TEMPLATE + """
    <script>
        window.location.href = '/?score={}';
    </script>
    """.format(score))

if __name__ == '__main__':
    app.run(port=5000, debug=True)