from flask import Flask, request, jsonify, render_template
import subprocess
import os
from google import genai
from google.genai import types

app = Flask(__name__, template_folder='.')

# System level environments read kora
os.environ["GEMINI_API_KEY"] = os.environ.get("GEMINI_API_KEY")
client = genai.Client()

@app.route('/')
def home():
    return render_template('index.html')

# 🤖 1. TEXT AI COGNITIVE ASSISTANT
@app.route('/api/ai', methods=['POST'])
def ai_assistant():
    data = request.json
    user_prompt = data.get('prompt', '')
    
    if not user_prompt:
        return jsonify({"result": "Blank prompt received."})
        
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=user_prompt,
        )
        return jsonify({"result": response.text})
    except Exception as e:
        return jsonify({"result": f"AI Text Engine Error: {str(e)}"})

# 🎨 2. PREMIUM IMAGE GENERATION ENGINE (Imagen 3)
@app.route('/api/generate-image', methods=['POST'])
def generate_image():
    data = request.json
    prompt = data.get('prompt', '')
    
    if not prompt:
        return jsonify({"error": "Prompt cannot be empty"})
        
    try:
        # Google Imagen 3 model diye ultra-realistic picture toiri
        result = client.models.generate_images(
            model='imagen-3.0-generate-002',
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                output_mime_type="image/jpeg",
                aspect_ratio="1:1"
            )
        )
        
        # Base64 images array string extract kora
        generated_image = result.generated_images[0]
        image_base64 = generated_image.image.image_bytes
        
        import base64
        encoded_image = base64.b64encode(image_base64).decode('utf-8')
        return jsonify({"image_data": f"data:image/jpeg;base64,{encoded_image}"})
        
    except Exception as e:
        return jsonify({"error": f"Image Generation Failed: {str(e)}"})

# 💻 3. MULTI-LANGUAGE UNIVERSAL COMPILER ENGINE
@app.route('/api/execute', methods=['POST'])
def execute_code():
    data = request.json
    lang = data.get('language')
    code = data.get('code')
    
    output = ""
    try:
        if lang == 'python':
            process = subprocess.run(['python3', '-c', code], capture_output=True, text=True, timeout=5)
            output = process.stdout if process.returncode == 0 else process.stderr
        elif lang == 'c':
            with open('temp.c', 'w') as f: f.write(code)
            compile_process = subprocess.run(['gcc', 'temp.c', '-o', 'temp_c'], capture_output=True, text=True)
            if compile_process.returncode == 0:
                run_process = subprocess.run(['./temp_c'], capture_output=True, text=True, timeout=5)
                output = run_process.stdout
            else: output = compile_process.stderr
        elif lang == 'cpp':
            with open('temp.cpp', 'w') as f: f.write(code)
            compile_process = subprocess.run(['g++', 'temp.cpp', '-o', 'temp_cpp'], capture_output=True, text=True)
            if compile_process.returncode == 0:
                run_process = subprocess.run(['./temp_cpp'], capture_output=True, text=True, timeout=5)
                output = run_process.stdout
            else: output = compile_process.stderr
        elif lang == 'java':
            with open('Main.java', 'w') as f: f.write(code)
            compile_process = subprocess.run(['javac', 'Main.java'], capture_output=True, text=True)
            if compile_process.returncode == 0:
                run_process = subprocess.run(['java', 'Main'], capture_output=True, text=True, timeout=5)
                output = run_process.stdout
            else: output = compile_process.stderr
    except subprocess.TimeoutExpired:
        output = "Error: Code execution timed out (Max 5 seconds)."
    except Exception as e:
        output = f"System Error: {str(e)}"
        
    return jsonify({"output": output})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
