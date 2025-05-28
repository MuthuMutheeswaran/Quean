from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_from_directory
import os
import uuid
from openpyxl import Workbook
import google.generativeai as genai

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# In-memory user storage
users = {}  # Format: {username: password}

# Gemini API setup
genai.configure(api_key="AIzaSyB4428jdHMpEAjssd6mOJ1dhgDGf5qnjOs")
model = genai.GenerativeModel("gemini-1.5-flash")

# Download directory
DOWNLOAD_FOLDER = os.path.join(app.root_path, "downloads")
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route("/")
def index():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template("index.html", username=session['user'])

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        pwd = request.form['password']
        if user in users and users[user] == pwd:
            session['user'] = user
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        flash('Invalid credentials!', 'danger')
    return render_template('login.html')

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        user = request.form['username']
        pwd = request.form['password']
        if user in users:
            flash('Username already exists!', 'danger')
        else:
            users[user] = pwd
            flash('Signup successful! Please login.', 'success')
            return redirect(url_for('login'))
    return render_template('signup.html')

@app.route("/logout")
def logout():
    session.pop('user', None)
    flash('Logged out successfully.', 'info')
    return redirect(url_for('login'))

@app.route("/generate", methods=["POST"])
def generate():
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.json
    topic = data.get("topic", "")
    question_count = int(data.get("questions", 5))
    option_count = int(data.get("options", 4))
    difficulty = data.get("difficulty", "Medium")

    if not topic.strip():
        return jsonify({"error": "Topic is required."}), 400

    prompt = f"""
    Generate {question_count} multiple-choice questions on the topic '{topic}'.
    Each question should have {option_count} options.
    Difficulty: {difficulty}.
    
    Format:
    1. <Question>
    A) Option A
    B) Option B
    C) Option C
    D) Option D
    Answer: <Correct Option Letter>
    """

    try:
        response = model.generate_content(prompt)
        question_text = response.text.strip()
        filename = f"{uuid.uuid4().hex}.xlsx"
        filepath = os.path.join(DOWNLOAD_FOLDER, filename)
        save_to_excel(question_text, filepath)
        return jsonify({"questions": question_text, "file": filename})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/download/<filename>")
def download(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)

def save_to_excel(text, filepath):
    wb = Workbook()
    ws = wb.active
    ws.title = "Questions"

    lines = text.split("\n")
    q_no, row = 0, []

    for line in lines:
        line = line.strip()
        if line == "":
            continue
        if line[0].isdigit() and '.' in line:
            if row:
                ws.append(row)
                row = []
            q_no += 1
            row.append(line)
        else:
            row.append(line)

    if row:
        ws.append(row)

    wb.save(filepath)

if __name__ == "__main__":
    app.run(debug=True)
