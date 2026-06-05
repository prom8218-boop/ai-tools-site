from flask import Flask, request, jsonify, render_template
import subprocess
import os
import base64
import requests
from code_analyzer import CodeAnalyzer
from session_manager import SessionManager
from rate_limiter import RateLimiter, SecurityManager, ErrorHandler
from learning_hub import LearningHub
from flask import render_template

# Initialize Flask app
app = Flask(__name__)

# Initialize modules
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
analyzer = CodeAnalyzer()
session_mgr = SessionManager()
rate_limiter = RateLimiter()
security_mgr = SecurityManager()
error_handler = ErrorHandler()
learning_hub = LearningHub()

@app.route('/')
def home():
    return render_template('index.html')

# ======================== AI & CODE FEATURES ========================

# 🤖 1. CHAT TEXT COGNITIVE MODULE
@app.route('/api/ai', methods=['POST'])
def ai_assistant():
    data = request.get_json(silent=True) or {}
    user_id = data.get('user_id', 'anonymous')
    user_prompt = data.get('prompt', '')
    
    # Security check
    is_valid, msg = security_mgr.validate_input(user_prompt, 'prompt')
    if not is_valid:
        error_handler.log_error('security_error', msg, user_id, '/api/ai')
        return jsonify({"error": msg}), 400
    
    # Rate limit check
    allowed, limit_info = rate_limiter.check_rate_limit(user_id, 'ai_chat')
    if not allowed:
        return jsonify(limit_info), 429
    
    if not user_prompt:
        return jsonify({"result": "Please provide a prompt."})
        
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
        headers = {'Content-Type': 'application/json'}
        payload = {"contents": [{"parts": [{"text": user_prompt}]}]}
        
        response = requests.post(url, json=payload, headers=headers)
        res_data = response.json()
        
        reply = res_data['candidates'][0]['content']['parts'][0]['text']
        
        # Save to history
        session_mgr.save_chat_message(user_id, 'user', user_prompt)
        session_mgr.save_chat_message(user_id, 'ai', reply)
        
        return jsonify({"result": reply, "quota_info": limit_info})
    except Exception as e:
        error_handler.log_error('api_error', str(e), user_id, '/api/ai')
        return jsonify({"result": f"Error: {str(e)}"}), 500

# 🎨 2. IMAGE GENERATION
@app.route('/api/generate-image', methods=['POST', 'HEAD'])
def generate_image():
    if request.method == 'HEAD':
        return '', 200
        
    data = request.get_json(silent=True) or {}
    user_id = data.get('user_id', 'anonymous')
    prompt = data.get('prompt', '')
    
    # Rate limit
    allowed, limit_info = rate_limiter.check_rate_limit(user_id, 'image_generation')
    if not allowed:
        return jsonify(limit_info), 429
    
    if not prompt:
        return jsonify({"error": "Please provide a prompt"}), 400
        
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-002:generateImages?key={GEMINI_API_KEY}"
        headers = {'Content-Type': 'application/json'}
        payload = {
            "prompt": prompt,
            "numberOfImages": 1,
            "outputMimeType": "image/jpeg",
            "aspectRatio": "1:1"
        }
        
        response = requests.post(url, json=payload, headers=headers)
        res_data = response.json()
        
        base64_image_string = res_data['generatedImages'][0]['image']['imageBytes']
        return jsonify({"image_data": f"data:image/jpeg;base64,{base64_image_string}"})
    except Exception as e:
        error_handler.log_error('api_error', str(e), user_id, '/api/generate-image')
        return jsonify({"error": f"Error: {str(e)}"}), 500

# 💻 3. CODE EXECUTION
@app.route('/api/execute', methods=['POST'])
def execute_code():
    data = request.get_json(silent=True) or {}
    user_id = data.get('user_id', 'anonymous')
    lang = data.get('language')
    code = data.get('code')
    
    # Rate limit
    allowed, limit_info = rate_limiter.check_rate_limit(user_id, 'code_execution')
    if not allowed:
        return jsonify(limit_info), 429
    
    # Security check
    is_valid, msg = security_mgr.validate_input(code, 'code')
    if not is_valid:
        error_handler.log_error('security_error', msg, user_id, '/api/execute')
        return jsonify({"error": msg}), 400
    
    output = ""
    try:
        if lang == 'python':
            process = subprocess.run(['python3', '-c', code], capture_output=True, text=True, timeout=5)
            output = process.stdout if process.returncode == 0 else process.stderr
        elif lang == 'c':
            with open('temp.c', 'w') as f: f.write(code)
            c_build = subprocess.run(['gcc', 'temp.c', '-o', 'temp_c'], capture_output=True, text=True)
            if c_build.returncode == 0:
                output = subprocess.run(['./temp_c'], capture_output=True, text=True, timeout=5).stdout
            else: output = c_build.stderr
        elif lang == 'cpp':
            with open('temp.cpp', 'w') as f: f.write(code)
            cpp_build = subprocess.run(['g++', 'temp.cpp', '-o', 'temp_cpp'], capture_output=True, text=True)
            if cpp_build.returncode == 0:
                output = subprocess.run(['./temp_cpp'], capture_output=True, text=True, timeout=5).stdout
            else: output = cpp_build.stderr
        elif lang == 'java':
            with open('Main.java', 'w') as f: f.write(code)
            java_build = subprocess.run(['javac', 'Main.java'], capture_output=True, text=True)
            if java_build.returncode == 0:
                output = subprocess.run(['java', 'Main'], capture_output=True, text=True, timeout=5).stdout
            else: output = java_build.stderr
    except subprocess.TimeoutExpired:
        output = "Error: Code execution timed out (Max 5s)"
        error_handler.log_error('timeout', 'Code execution timeout', user_id, '/api/execute')
    except Exception as e:
        output = f"Error: {str(e)}"
        error_handler.log_error('execution_error', str(e), user_id, '/api/execute')
    
    return jsonify({"output": output})

# 🔍 4. CODE ANALYSIS
@app.route('/api/analyze-code', methods=['POST'])
def analyze_code():
    data = request.get_json(silent=True) or {}
    user_id = data.get('user_id', 'anonymous')
    code = data.get('code', '')
    language = data.get('language', 'python')
    
    # Rate limit
    allowed, limit_info = rate_limiter.check_rate_limit(user_id, 'code_analysis')
    if not allowed:
        return jsonify(limit_info), 429
    
    if not code or len(code.strip()) < 10:
        return jsonify({"error": "Code is too short for analysis"}), 400
    
    try:
        analysis = analyzer.full_analysis(code, language)
        return jsonify({
            "status": "success",
            "analysis": {
                "overall_score": analysis['overall_score'],
                "bugs": analysis['bugs'],
                "performance": analysis['performance'],
                "refactoring_suggestions": analysis['refactoring_suggestions']
            },
            "quota_info": limit_info
        })
    except Exception as e:
        error_handler.log_error('analysis_error', str(e), user_id, '/api/analyze-code')
        return jsonify({"error": f"Analysis Failed: {str(e)}"}), 500

@app.route('/api/detect-bugs', methods=['POST'])
def detect_bugs():
    data = request.get_json(silent=True) or {}
    code = data.get('code', '')
    language = data.get('language', 'python')
    user_id = data.get('user_id', 'anonymous')
    
    if not code:
        return jsonify({"error": "No code provided"}), 400
    
    try:
        bugs = analyzer.detect_bugs(code, language)
        return jsonify({"status": "success", "bugs": bugs})
    except Exception as e:
        error_handler.log_error('bug_detection_error', str(e), user_id, '/api/detect-bugs')
        return jsonify({"error": str(e)}), 500

@app.route('/api/performance-analysis', methods=['POST'])
def performance_analysis():
    data = request.get_json(silent=True) or {}
    code = data.get('code', '')
    language = data.get('language', 'python')
    
    if not code:
        return jsonify({"error": "No code provided"}), 400
    
    try:
        metrics = analyzer.analyze_performance(code, language)
        return jsonify({"status": "success", "metrics": metrics})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/refactoring-suggestions', methods=['POST'])
def refactoring_suggestions():
    data = request.get_json(silent=True) or {}
    code = data.get('code', '')
    language = data.get('language', 'python')
    
    if not code:
        return jsonify({"error": "No code provided"}), 400
    
    try:
        suggestions = analyzer.suggest_refactoring(code, language)
        return jsonify({"status": "success", "suggestions": suggestions})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ======================== SESSION & HISTORY ========================

@app.route('/api/chat-history', methods=['GET'])
def get_chat_history():
    user_id = request.args.get('user_id', 'anonymous')
    history = session_mgr.get_chat_history(user_id)
    return jsonify({"status": "success", "history": history})

@app.route('/api/save-favorite', methods=['POST'])
def save_favorite():
    data = request.get_json(silent=True) or {}
    user_id = data.get('user_id', 'anonymous')
    prompt = data.get('prompt', '')
    category = data.get('category', 'general')
    
    result = session_mgr.save_favorite(user_id, prompt, category)
    return jsonify(result)

@app.route('/api/get-favorites', methods=['GET'])
def get_favorites():
    user_id = request.args.get('user_id', 'anonymous')
    favorites = session_mgr.get_favorites(user_id)
    return jsonify({"status": "success", "favorites": favorites})

@app.route('/api/export-session', methods=['GET'])
def export_session():
    user_id = request.args.get('user_id', 'anonymous')
    format = request.args.get('format', 'json')  # json, csv
    
    if format == 'json':
        data = session_mgr.export_session_json(user_id)
        return jsonify(data)
    elif format == 'csv':
        csv_data = session_mgr.export_session_csv(user_id)
        return csv_data, 200, {'Content-Type': 'text/csv'}
    
    return jsonify({"error": "Unsupported format"}), 400

@app.route('/api/session-stats', methods=['GET'])
def session_stats():
    user_id = request.args.get('user_id', 'anonymous')
    stats = session_mgr.get_session_stats(user_id)
    return jsonify({"status": "success", "stats": stats})

# ======================== LEARNING HUB ========================

@app.route('/api/tutorials', methods=['GET'])
def get_tutorials():
    category = request.args.get('category')
    tutorials = learning_hub.get_tutorials(category)
    return jsonify(tutorials)

@app.route('/api/code-snippets', methods=['GET'])
def get_code_snippets():
    language = request.args.get('language')
    snippets = learning_hub.get_code_snippets(language)
    return jsonify(snippets)

@app.route('/api/search-snippets', methods=['GET'])
def search_snippets():
    query = request.args.get('query', '')
    results = learning_hub.search_snippets(query)
    return jsonify(results)

@app.route('/api/api-docs', methods=['GET'])
def get_api_docs():
    endpoint = request.args.get('endpoint')
    docs = learning_hub.get_api_docs(endpoint)
    return jsonify(docs)

# ======================== RATE LIMIT & QUOTA ========================

@app.route('/api/user-quota', methods=['GET'])
def user_quota():
    user_id = request.args.get('user_id', 'anonymous')
    endpoint = request.args.get('endpoint')
    quota = rate_limiter.get_user_quota(user_id, endpoint)
    return jsonify({"status": "success", "quota": quota})

@app.route('/api/error-stats', methods=['GET'])
def error_stats():
    hours = request.args.get('hours', 24, type=int)
    stats = error_handler.get_error_stats(hours)
    return jsonify({"status": "success", "stats": stats})

@app.route('/data-analyzer')
def data_analyzer():
    return render_template('data_analyzer.html')
if __name__ == '__main__':
    app.run(debug=True, port=5000)
