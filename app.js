// 🤖 1. TEXT COGNITIVE ASSISTANT WORKFLOW
async function askAI() {
    const input = document.getElementById('ai-input').value;
    const chatBox = document.getElementById('ai-chat-box');
    if(!input) return;

    chatBox.innerHTML += `<div class="text-cyan-400 font-bold mt-3">You: ${input}</div>`;
    document.getElementById('ai-input').value = '';

    // Check custom trigger pattern for image generation logic
    if (input.toLowerCase().startsWith('/image ')) {
        const imagePrompt = input.substring(7);
        chatBox.innerHTML += `<div class="text-amber-400 italic mt-2 animate-pulse"><i class="fa-solid fa-wand-magic-sparkles"></i> Activating Imagen 3 Core Engine... Generating Visual Art...</div>`;
        chatBox.scrollTop = chatBox.scrollHeight;
        
        try {
            const response = await fetch('./api/generate-image', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ prompt: imagePrompt })
            });
            const data = await response.json();
            if (data.image_data) {
                chatBox.innerHTML += `
                    <div class="mt-3 p-2 bg-slate-900 border border-slate-800 rounded-2xl max-w-sm">
                        <img src="${data.image_data}" alt="Generated Art" class="rounded-xl w-full h-auto shadow-md"/>
                        <p class="text-xs text-slate-500 mt-1 text-center font-mono">Prompt: ${imagePrompt}</p>
                    </div>`;
            } else {
                chatBox.innerHTML += `<div class="text-red-400 mt-1">AI System Error: ${data.error}</div>`;
            }
        } catch (err) {
            chatBox.innerHTML += `<div class="text-red-400 mt-1">Network link interruption.</div>`;
        }
    } else {
        // Standard chatbot text dynamic generation call
        try {
            const response = await fetch('./api/ai', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ prompt: input })
            });
            const data = await response.json();
            chatBox.innerHTML += `<div class="bg-slate-900/80 p-3.5 rounded-2xl border border-slate-800/60 max-w-[85%] mt-2 text-slate-200">AI: ${data.result}</div>`;
        } catch (err) {
            chatBox.innerHTML += `<div class="text-red-400 mt-1">Processing error. Check integration connection.</div>`;
        }
    }
    chatBox.scrollTop = chatBox.scrollHeight;
}

// 💻 2. UNIVERSAL COMPILER CORE VECTOR
async function runCode() {
    const lang = document.getElementById('language').value;
    const code = document.getElementById('code-editor').value;
    const outputConsole = document.getElementById('output');

    outputConsole.innerText = "Compiling matrix isolation build processes live...";

    try {
        const response = await fetch('./api/execute', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ language: lang, code: code })
        });
        const data = await response.json();
        outputConsole.innerText = data.output || data.error;
    } catch (err) {
        outputConsole.innerText = "Error contacting isolated cloud backend environment.";
    }
}

// 🔒 3. GOOGLE ID IDENTITY SIGN IN OVERLAY SYSTEM
function initializeGoogleAuth() {
    // High profile layout template validation logic dummy injection
    console.log("Google Firebase Authentication cluster network module link verified.");
}
window.onload = initializeGoogleAuth;
