// AI Response Handler
async function askAI() {
    const input = document.getElementById('ai-input').value;
    const chatBox = document.getElementById('ai-chat-box');
    if(!input) return;

    chatBox.innerHTML += `<p class="text-cyan-300 font-semibold mt-2">You: ${input}</p>`;
    document.getElementById('ai-input').value = '';

    try {
        const response = await fetch('/api/ai', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ prompt: input })
        });
        const data = await response.json();
        chatBox.innerHTML += `<p class="text-gray-300 mt-1">AI: ${data.result}</p>`;
    } catch (err) {
        chatBox.innerHTML += `<p class="text-red-400 mt-1">AI: Processing error. Check backend connection.</p>`;
    }
    chatBox.scrollTop = chatBox.scrollHeight;
}

// Code Execution Handler
async function runCode() {
    const lang = document.getElementById('language').value;
    const code = document.getElementById('code-editor').value;
    const outputConsole = document.getElementById('output');

    outputConsole.innerText = "Compiling and executing...";

    try {
        const response = await fetch('/api/execute', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ language: lang, code: code })
        });
        const data = await response.json();
        outputConsole.innerText = data.output || data.error;
    } catch (err) {
        outputConsole.innerText = "Error contacting compilation server.";
    }
}