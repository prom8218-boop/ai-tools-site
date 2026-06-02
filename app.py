from flask import Flask, request, jsonify, render_template
import subprocess
import os
import base64
from google import genai
from google.genai import types

# Flask routing setup matching template directory architecture root context
app = Flask(__name__, template_folder='.')

os.environ["GEMINI_API_KEY"] = os.environ.get("GEMINI_API_KEY")
client = genai.Client()

@app.route('/')
def home():
    return render_template('index.html')

# 🤖 AI TEXT RESPONSE GATEWAY
@app.route('/api/ai', methods=['POST'])
def ai_assistant():
    data = request.json
    user_prompt = data.get('prompt', '')
    if not user_prompt:
        return jsonify({"result": "Null token vector."})
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=user_prompt,
        )
        return jsonify({"result": response.text})
    except Exception as e:
        return jsonify({"result": f"Cognitive Core Error: {str(e)}"})

# 🎨 HIGH-PROFILE IMAGEN 3 LIVE GRAPHICS STUDIO 
@app.route('/api/generate-image', methods=['POST', 'HEAD'])
def generate_image():
    if request.method == 'HEAD':
        return '', 200
        
    data = request.get_json(silent=True) or {}
    prompt = data.get('prompt', '')
    try:
        result = client.models.generate_images(
            model='imagen-3.0-generate-002',
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                output_mime_type="image/jpeg",
                aspect_ratio="1:1"
            )
        )
        generated_image = result.generated_images[0]
        image_base64 = generated_image.image.image_bytes
        encoded_image = base64.b64encode(image_base64).decode('utf-8')
        return jsonify({"image_data": f"data:image/jpeg;base64,{encoded_image}"})
    except Exception as e:
        return jsonify({"error": f"Imagen Render Collapse: {str(e)}"})

# 💻 UNIVERSAL CODE ISOLATION HOST ROUTING EXECUTION UNIT
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
        output = "Error: Computation processing timed out limit matrix threshold."
    except Exception as e:
        output = f"Core Runtime Layer Error Matrix: {str(e)}"
    return jsonify({"output": output})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
