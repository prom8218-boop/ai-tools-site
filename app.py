from flask import Flask, request, jsonify, render_template
import subprocess
import os
import base64
import requests

# Root layout tracking definition
app = Flask(__name__)

# System environments mapping extraction
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

@app.route('/')
def home():
    return render_template('index.html')

# 🤖 1. CHAT TEXT COGNITIVE MODULE (Using direct native HTTP requests to bypass SDK Pillow crash)
@app.route('/api/ai', methods=['POST'])
def ai_assistant():
    data = request.get_json(silent=True) or {}
    user_prompt = data.get('prompt', '')
    if not user_prompt:
        return jsonify({"result": "Null token string."})
        
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
        headers = {'Content-Type': 'application/json'}
        payload = {"contents": [{"parts": [{"text": user_prompt}]}]}
        
        response = requests.post(url, json=payload, headers=headers)
        res_data = response.json()
        
        reply = res_data['candidates'][0]['content']['parts'][0]['text']
        return jsonify({"result": reply})
    except Exception as e:
        return jsonify({"result": f"Cognitive Framework Exception Error: {str(e)}"})

# 🎨 2. PREMIUM IMAGEN 3 GRAPHICS STUDIO (Bypassing SDK constraints via standard HTTP pipeline)
@app.route('/api/generate-image', methods=['POST', 'HEAD'])
def generate_image():
    if request.method == 'HEAD':
        return '', 200
        
    data = request.get_json(silent=True) or {}
    prompt = data.get('prompt', '')
    if not prompt:
        return jsonify({"error": "Empty tracking description token."}), 400
        
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
        
        # Standard dynamic base64 extraction routing map
        base64_image_string = res_data['generatedImages'][0]['image']['imageBytes']
        return jsonify({"image_data": f"data:image/jpeg;base64,{base64_image_string}"})
    except Exception as e:
        return jsonify({"error": f"Imagen Endpoint Core Communication Failure: {str(e)}"}), 500

# 💻 3. UNIVERSAL COMPILE ENVIROMENTS (Python/Java/C/C++)
@app.route('/api/execute', methods=['POST'])
def execute_code():
    data = request.get_json(silent=True) or {}
    lang = data.get('language')
    code = data.get('code')
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
        output = "Error: Code compilation limits processing window (Max 5s)."
    except Exception as e:
        output = f"Container Core System Crash Error: {str(e)}"
    return jsonify({"output": output})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
