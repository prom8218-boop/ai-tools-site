from flask import Flask, request, jsonify, render_template
import subprocess
import os
# Google GenAI library import korun
from google import genai

app = Flask(__name__)

# Ekhane apnar Google AI Studio theke gathra API Key-ti boshaben
# (Nirapottar jonne eta environment variable-e rakha valo)
# API Key code theke sorasori soriye environment variable theke call kora
os.environ["GEMINI_API_KEY"] = os.environ.get("GEMINI_API_KEY") 
# Client initialize korun
client = genai.Client()

@app.route('/')
def home():
    return render_template('index.html')

# 🔥 AI Dynamic Endpoint (Ekhon eta sotti kaj korbe!)
@app.route('/api/ai', methods=['POST'])
def ai_assistant():
    data = request.json
    user_prompt = data.get('prompt', '')
    
    if not user_prompt:
        return jsonify({"result": "Blank prompt received."})
        
    try:
        # Gemini 2.5 Flash model use kore response generate kora
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=user_prompt,
        )
        ai_response = response.text
    except Exception as e:
        ai_response = f"AI Processing Engine Error: {str(e)}"
        
    return jsonify({"result": ai_response})

# ... (Baki compiler routing code jemon chilo temoni thakbe)
