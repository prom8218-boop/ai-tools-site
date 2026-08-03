from flask import Flask, request, jsonify, render_template
import subprocess
import os
import base64
import requests
import uuid
import tempfile
import shutil
from code_analyzer import CodeAnalyzer
from session_manager import SessionManager
from rate_limiter import RateLimiter, SecurityManager, ErrorHandler
from learning_hub import LearningHub
from jarvis import get_brain

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-12345")

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

analyzer = CodeAnalyzer()
session_mgr = SessionManager()
rate_limiter = RateLimiter()
security_mgr = SecurityManager()
error_handler = ErrorHandler()
learning_hub = LearningHub()
jarvis = get_brain()

def add_cors(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

@app.after_request
def after_request(response):
    return add_cors(response)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/jarvis')
def jarvis_ui():
    return render_template('jarvis.html')

@app.route('/api/jarvis', methods=['POST', 'OPTIONS'])
def jarvis_command():
    if request.method == 'OPTIONS':
        return '', 200
    data = request.get_json(silent=True) or {}
    command = data.get('command', '')
    if not command or not command.strip():
        return jsonify({"text": "I didn't catch that, sir. Please say or type a command."})
    try:
        result = jarvis.process(command)
        return jsonify(result)
    except Exception as e:
        return jsonify({"text": f"I encountered an error processing that, sir: {str(e)}"})

@app.route('/api/ai', methods=['POST', 'OPTIONS'])
def ai_assistant():
    if request.method == 'OPTIONS':
        return '', 200
    data = request.get_json(silent=True) or {}
    user_id = data.get('user_id', 'anonymous')
    user_prompt = data.get('prompt', '')

    if not user_prompt:
        return jsonify({"result": "Please provide a prompt."})

    if not GEMINI_API_KEY:
        return jsonify({"result": "Error: GEMINI_API_KEY is not set on the server."})

    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        headers = {'Content-Type': 'application/json'}
        payload = {"contents": [{"parts": [{"text": user_prompt}]}]}
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        res_data = response.json()

        if 'candidates' not in res_data:
            return jsonify({"result": f"API Error: {res_data.get('error', {}).get('message', 'Unknown error')}"}), 500

        reply = res_data['candidates'][0]['content']['parts'][0]['text']
        session_mgr.save_chat_message(user_id, 'user', user_prompt)
        session_mgr.save_chat_message(user_id, 'ai', reply)
        return jsonify({"result": reply})
    except Exception as e:
        return jsonify({"result": f"Error: {str(e)}"}), 500

@app.route('/api/generate-image', methods=['POST', 'HEAD', 'OPTIONS'])
def generate_image():
    if request.method in ['HEAD', 'OPTIONS']:
        return '', 200
    data = request.get_json(silent=True) or {}
    prompt = data.get('prompt', '')

    if not prompt:
        return jsonify({"error": "Please provide a prompt"}), 400

    if not GEMINI_API_KEY:
        return jsonify({"error": "GEMINI_API_KEY not set"}), 500

    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-preview-image-generation:generateContent?key={GEMINI_API_KEY}"
        headers = {'Content-Type': 'application/json'}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseModalities": ["TEXT", "IMAGE"]}
        }
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        res_data = response.json()

        if 'candidates' not in res_data:
            return jsonify({"error": res_data.get('error', {}).get('message', 'Image generation failed')}), 500

        for part in res_data['candidates'][0]['content']['parts']:
            if 'inlineData' in part:
                image_data = part['inlineData']['data']
                mime_type = part['inlineData']['mimeType']
                return jsonify({"image": f"data:{mime_type};base64,{image_data}"})

        return jsonify({"error": "No image returned"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/algo', methods=['POST', 'OPTIONS'])
def generate_algo():
    if request.method == 'OPTIONS':
        return '', 200
    data = request.get_json(silent=True) or {}
    strategy = data.get('prompt', data.get('strategy', ''))

    if not strategy:
        return jsonify({"result": "Please describe your trading strategy."})

    if not GEMINI_API_KEY:
        return jsonify({"result": "Error: GEMINI_API_KEY is not set."})

    try:
        prompt = f"Write a complete Pine Script v5 trading strategy for TradingView based on this idea: {strategy}. Include entry/exit conditions, stop loss, take profit, and proper comments."
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        headers = {'Content-Type': 'application/json'}
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        res_data = response.json()

        if 'candidates' not in res_data:
            return jsonify({"result": f"API Error: {res_data.get('error', {}).get('message', 'Unknown')}"}), 500

        reply = res_data['candidates'][0]['content']['parts'][0]['text']
        return jsonify({"result": reply})
    except Exception as e:
        return jsonify({"result": f"Error: {str(e)}"}), 500

@app.route('/api/execute', methods=['POST', 'OPTIONS'])
def execute_code():
    if request.method == 'OPTIONS':
        return '', 200
    data = request.get_json(silent=True) or {}
    code = data.get('code', '')
    language = data.get('language', 'python')

    if not code:
        return jsonify({"output": "No code provided", "error": ""})

    if language == 'python':
        try:
            result = subprocess.run(
                ['python3', '-c', code],
                capture_output=True, text=True, timeout=10
            )
            return jsonify({"output": result.stdout, "error": result.stderr})
        except subprocess.TimeoutExpired:
            return jsonify({"output": "", "error": "Timeout: Code took too long to execute"})
        except Exception as e:
            return jsonify({"output": "", "error": str(e)})
    else:
        return jsonify({"output": "", "error": f"Language '{language}' not supported yet"})

@app.route('/api/analyze-code', methods=['POST', 'OPTIONS'])
def analyze_code():
    if request.method == 'OPTIONS':
        return '', 200
    data = request.get_json(silent=True) or {}
    code = data.get('code', '')
    language = data.get('language', 'python')

    if not code:
        return jsonify({"error": "No code provided"}), 400

    try:
        result = analyzer.detect_bugs(code, language)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/analyze-data', methods=['POST', 'OPTIONS'])
def analyze_data():
    if request.method == 'OPTIONS':
        return '', 200
    data = request.get_json(silent=True) or {}
    csv_data = data.get('data', '')
    question = data.get('question', 'Analyze this data and provide insights')

    if not GEMINI_API_KEY:
        return jsonify({"result": "Error: GEMINI_API_KEY not set"}), 500

    try:
        prompt = f"Analyze this CSV data and answer: {question}\n\nData:\n{csv_data[:3000]}"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        headers = {'Content-Type': 'application/json'}
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        res_data = response.json()

        if 'candidates' not in res_data:
            return jsonify({"result": "Analysis failed"}), 500

        reply = res_data['candidates'][0]['content']['parts'][0]['text']
        return jsonify({"result": reply})
    except Exception as e:
        return jsonify({"result": f"Error: {str(e)}"}), 500

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        "status": "ok",
        "api_key_set": bool(GEMINI_API_KEY),
        "api_key_length": len(GEMINI_API_KEY) if GEMINI_API_KEY else 0
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
