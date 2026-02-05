import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests

app = Flask(__name__)
# Replace with your actual IFrame host URL once deployed
CORS(app) 

RCAC_API_KEY = os.environ.get('RCAC_API_KEY')
RCAC_URL = "https://genai.rcac.purdue.edu/api/chat/completions"

@app.route('/')
def index():
    # This looks inside the /templates folder
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    student_email = data.get('student_email', 'Unknown')
    essay_content = data.get('message')

    # RESEARCH LOGGING: Captured by Render Logs
    print(f"--- RESEARCH LOG ENTRY ---")
    print(f"STUDENT: {student_email}")
    print(f"ESSAY: {essay_content}")
    print(f"--------------------------")

    headers = {
        "Authorization": f"Bearer {RCAC_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "llama4:latest",
        "messages": [{"role": "user", "content": essay_content}]
    }

    try:
        response = requests.post(RCAC_URL, headers=headers, json=payload, timeout=30)
        ai_reply = response.json()['choices'][0]['message']['content']
        
        print(f"AI_RESPONSE: {ai_reply}")
        return jsonify({"reply": ai_reply})
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return jsonify({"reply": "The Quiz Assistant is currently unavailable. Please try again later."}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))