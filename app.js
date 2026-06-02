// 🔒 1. GOOGLE IDENTITY AUTHENTICATION FLOW
function handleCredentialResponse(response) {
    // Google JWT Token extract block
    const base64Url = response.credential.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(window.atob(base64).split('').map(function(c) {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
    }).join(''));

    const user = JSON.parse(jsonPayload);
    
    // UI states manipulation mapping
    document.getElementById('google-btn').classList.add('hidden');
    document.getElementById('user-profile').classList.remove('hidden');
    
    document.getElementById('user-name').innerText = user.name;
    document.getElementById('user-avatar').src = user.picture;

    const chatBox = document.getElementById('ai-chat-box');
    chatBox.innerHTML += `<div class="text-emerald-400 font-semibold mt-2"><i class="fa-solid fa-circle-check"></i> Welcome ${user.name}! Secure Google context linked successfully.</div>`;
    chatBox.scrollTop = chatBox.scrollHeight;
}

function logout() {
    document.getElementById('google-btn').classList.remove('hidden');
    document.getElementById('user-profile').classList.add('hidden');
    location.reload();
}

window.onload = function () {
    // Google API Initialization Core
    google.accounts.id.initialize({
        client_id: "718038529129-dummyclientid12345.apps.googleusercontent.com", // ⚠️ Ekhane future-e real client id boshabo
        callback: handleCredentialResponse
    });
    google.accounts.id.renderButton(
        document.getElementById("google-btn"),
        { theme: "dark", size: "medium", type: "standard", shape: "pill" }
    );
};

// 🤖 2. COGNITIVE ENGINE (TEXT & IMAGEN 3 ART GENERATOR)
async function askAI() {
    const input = document.getElementById('ai-input').value;
    const chatBox = document.getElementById('ai-chat-box');
    if(!input) return;

    chatBox.innerHTML += `<div class="text-cyan-400 font-bold mt-3">You: ${input}</div>`;
    document.getElementById('ai-input').value = '';

    // Check configuration layer endpoint route maps
    if (input.toLowerCase().startsWith('/image ')) {
        const imagePrompt = input.substring(7);
        chatBox.innerHTML += `<div class="text-amber-400 italic mt-2 animate-pulse"><i class="fa-solid fa-wand-magic-sparkles"></i> Activating Imagen 3... Building premium visual framework...</div>`;
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
                    <div class="mt-3 p-2 bg-slate-900 border border-slate-800 rounded-2xl max-w-sm shadow-xl">
                        <img src="${data.image_data}" alt="AI Generated Graphic" class="rounded-xl w-full h-auto"/>
                        <p class="text-xs text-slate-500 mt-2 text-center font-mono">Engine: Imagen 3.0</p>
                    </div>`;
            } else {
                chatBox.innerHTML += `<div class="text-red-400 mt-1">SaaS Fail: ${data.error}</div>`;
            }
        } catch (err) {
            chatBox.innerHTML += `<div class="text-red-400 mt-1">Network runtime error.</div>`;
        }
    } else {
        try {
            const response = await fetch('./api/ai', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ prompt: input })
            });
            const data = await response.json();
            chatBox.innerHTML += `<div class="bg-slate-900/80 p-3.5 rounded-2xl border border-slate-800/60 max-w-[85%] mt-2 text-slate-200">AI: ${data.result}</div>`;
        } catch (err) {
            chatBox.innerHTML += `<div class="text-red-400 mt-1">Processing error. Check backend link.</div>`;
        }
    }
    chatBox.scrollTop = chatBox.scrollHeight;
}

// 💻 3. DISTRIBUTED CODE ENGINE CALL RUNNER
async function runCode() {
    const lang = document.getElementById('language').value;
    const code = document.getElementById('code-editor').value;
    const outputConsole = document.getElementById('output');

    outputConsole.innerText = "Compiling in cloud isolation matrix...";

    try {
        const response = await fetch('./api/execute', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ language: lang, code: code })
        });
        const data = await response.json();
        outputConsole.innerText = data.output || data.error;
    } catch (err) {
        outputConsole.innerText = "Error establishing link layer to compilation node.";
    }
}
