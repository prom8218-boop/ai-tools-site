from flask import Flask, request, jsonify, render_template
import subprocess
import os

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

# AI Fake Endpoint (Ekhane apni OpenAI/Gemini/Ollama API connect korte parben)
@app.route('/api/ai', classification=['POST'])
@app.route('/api/ai', methods=['POST'])
def ai_assistant():
    data = request.json
    user_prompt = data.get('prompt', '')
    # Sample Mock Response - Apni ekhane real AI API model dynamic korte parben
    ai_response = f"Processed your request for tools with code optimization logic."
    return jsonify({"result": ai_response})

# Multi-Language Compiler System (Python, C, C++, Java)
@app.route('/api/execute', methods=['POST'])
def execute_code():
    data = request.json
    lang = data.get('language')
    code = data.get('code')
    
    output = ""
    try:
        if lang == 'python':
            # Run Python Code safely using subprocess
            process = subprocess.run(['python3', '-c', code], capture_output=True, text=True, timeout=5)
            output = process.stdout if process.returncode == 0 else process.stderr
            
        elif lang == 'c':
            with open('temp.c', 'w') as f: f.write(code)
            compile_process = subprocess.run(['gcc', 'temp.c', '-o', 'temp_c'], capture_output=True, text=True)
            if compile_process.returncode == 0:
                run_process = subprocess.run(['./temp_c'], capture_output=True, text=True, timeout=5)
                output = run_process.stdout
            else:
                output = compile_process.stderr
                
        elif lang == 'cpp':
            with open('temp.cpp', 'w') as f: f.write(code)
            compile_process = subprocess.run(['g++', 'temp.cpp', '-o', 'temp_cpp'], capture_output=True, text=True)
            if compile_process.returncode == 0:
                run_process = subprocess.run(['./temp_cpp'], capture_output=True, text=True, timeout=5)
                output = run_process.stdout
            else:
                output = compile_process.stderr

        elif lang == 'java':
            # Java structural execution handler
            with open('Main.java', 'w') as f: f.write(code)
            compile_process = subprocess.run(['javac', 'Main.java'], capture_output=True, text=True)
            if compile_process.returncode == 0:
                run_process = subprocess.run(['java', 'Main'], capture_output=True, text=True, timeout=5)
                output = run_process.stdout
            else:
                output = compile_process.stderr
                
    except subprocess.TimeoutExpired:
        output = "Error: Code execution timed out (Max 5 seconds)."
    except Exception as e:
        output = f"System Error: {str(e)}"
        
    return jsonify({"output": output})

if __name__ == '__main__':
    app.run(debug=True, port=5000)