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

// 🔍 4. CODE ANALYSIS & OPTIMIZATION ENGINE (NEW FEATURE)

// 4.1 - Full Comprehensive Analysis
async function analyzeCode() {
    const code = document.getElementById('code-editor').value;
    const language = document.getElementById('language').value;
    
    if (!code.trim()) {
        showAnalysisError('Please enter code to analyze');
        return;
    }

    const analysisPanel = document.getElementById('analysis-panel');
    analysisPanel.innerHTML = '<div class="text-center py-4"><div class="text-blue-400 animate-pulse">🔍 Analyzing code...</div></div>';

    try {
        const response = await fetch('./api/analyze-code', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ code, language })
        });

        const data = await response.json();

        if (data.status === 'success') {
            displayAnalysisResults(data.analysis);
        } else {
            showAnalysisError(data.error || 'Analysis failed');
        }
    } catch (err) {
        showAnalysisError('Error connecting to analysis engine');
    }
}

// 4.2 - Display Full Analysis Results
function displayAnalysisResults(analysis) {
    const panel = document.getElementById('analysis-panel');
    
    // Score card
    const scoreColor = analysis.overall_score >= 80 ? 'text-green-400' : 
                       analysis.overall_score >= 60 ? 'text-yellow-400' : 'text-red-400';
    
    let html = `
        <div class="bg-slate-800 border border-slate-700 rounded-lg p-4 mb-4">
            <div class="text-center">
                <div class="text-4xl font-bold ${scoreColor}">${analysis.overall_score}</div>
                <div class="text-sm text-slate-400">Overall Code Quality Score</div>
            </div>
        </div>
    `;

    // Bugs Section
    html += `<div class="mb-4">
        <h3 class="text-lg font-semibold text-red-400 mb-2">🐛 Bug Detection</h3>
        <div class="text-sm text-slate-300">Total Issues: ${analysis.bugs.total_bugs}</div>`;
    
    if (analysis.bugs.total_bugs === 0) {
        html += '<div class="text-green-400">✅ No bugs detected!</div>';
    } else {
        html += `<div class="text-yellow-400">⚠️ Found ${analysis.bugs.total_bugs} potential issues</div>`;
        analysis.bugs.issues.forEach(bug => {
            const severityColor = bug.severity === 'CRITICAL' ? 'text-red-500' :
                                 bug.severity === 'HIGH' ? 'text-red-400' :
                                 bug.severity === 'MEDIUM' ? 'text-yellow-400' : 'text-blue-400';
            html += `
                <div class="mt-2 p-2 bg-slate-900 rounded border-l-4 border-red-500">
                    <div class="flex justify-between">
                        <span class="${severityColor} font-semibold">${bug.severity}</span>
                        <span class="text-slate-400">${bug.type}</span>
                    </div>
                    <div class="text-slate-400 text-xs mt-1">${bug.message}</div>
                    <div class="text-green-400 text-xs mt-1">✓ Fix: ${bug.fix}</div>
                </div>
            `;
        });
    }
    html += '</div>';

    // Performance Section
    html += `<div class="mb-4">
        <h3 class="text-lg font-semibold text-blue-400 mb-2">📊 Performance Metrics</h3>
        <div class="grid grid-cols-2 gap-2 text-sm">
            <div class="bg-slate-900 p-2 rounded">
                <div class="text-slate-400">Cyclomatic Complexity</div>
                <div class="text-lg font-bold text-cyan-400">${analysis.performance.cyclomatic_complexity}</div>
            </div>
            <div class="bg-slate-900 p-2 rounded">
                <div class="text-slate-400">Max Nesting Depth</div>
                <div class="text-lg font-bold text-cyan-400">${analysis.performance.max_nesting_depth}</div>
            </div>
            <div class="bg-slate-900 p-2 rounded">
                <div class="text-slate-400">Lines of Code</div>
                <div class="text-lg font-bold text-cyan-400">${analysis.performance.lines_of_code}</div>
            </div>
            <div class="bg-slate-900 p-2 rounded">
                <div class="text-slate-400">Perf Rating</div>
                <div class="text-lg font-bold">${analysis.performance.performance_rating}</div>
            </div>
        </div>
    </div>`;

    // Refactoring Suggestions
    html += `<div class="mb-4">
        <h3 class="text-lg font-semibold text-green-400 mb-2">💡 Refactoring Suggestions</h3>`;
    
    if (analysis.refactoring_suggestions.length === 0) {
        html += '<div class="text-slate-400">No refactoring suggestions at this time.</div>';
    } else {
        analysis.refactoring_suggestions.forEach(sug => {
            const priorityColor = sug.priority === 'HIGH' ? 'text-red-400' :
                                 sug.priority === 'MEDIUM' ? 'text-yellow-400' : 'text-blue-400';
            html += `
                <div class="mt-2 p-2 bg-slate-900 rounded border-l-4 border-green-500">
                    <div class="flex justify-between">
                        <span class="${priorityColor} font-semibold">${sug.priority}</span>
                        <span class="text-slate-400">${sug.type}</span>
                    </div>
                    <div class="text-slate-400 text-xs mt-1">${sug.message}</div>
                    <div class="text-green-400 text-xs mt-1">💡 ${sug.suggestion}</div>
                    <div class="text-blue-400 text-xs mt-1">↑ Benefit: ${sug.benefit}</div>
                </div>
            `;
        });
    }
    html += '</div>';

    panel.innerHTML = html;
}

// 4.3 - Quick Bug Detection
async function detectBugs() {
    const code = document.getElementById('code-editor').value;
    const language = document.getElementById('language').value;
    
    if (!code.trim()) {
        showAnalysisError('Please enter code');
        return;
    }

    try {
        const response = await fetch('./api/detect-bugs', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ code, language })
        });
        const data = await response.json();
        
        if (data.status === 'success') {
            const panel = document.getElementById('analysis-panel');
            panel.innerHTML = `<div class="text-lg font-semibold text-red-400 mb-2">Found ${data.bugs.total_bugs} bug(s)</div>`;
            
            data.bugs.issues.forEach(bug => {
                panel.innerHTML += `<div class="bg-slate-900 p-2 rounded mb-2 border-l-4 border-red-500">
                    <div class="text-${bug.severity === 'CRITICAL' ? 'red-500' : 'red-400'} font-bold">${bug.severity}: ${bug.type}</div>
                    <div class="text-slate-400 text-sm">${bug.message}</div>
                </div>`;
            });
        }
    } catch (err) {
        showAnalysisError('Bug detection failed');
    }
}

// 4.4 - Performance Analysis
async function analyzePerformance() {
    const code = document.getElementById('code-editor').value;
    const language = document.getElementById('language').value;
    
    if (!code.trim()) {
        showAnalysisError('Please enter code');
        return;
    }

    try {
        const response = await fetch('./api/performance-analysis', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ code, language })
        });
        const data = await response.json();
        
        if (data.status === 'success') {
            const metrics = data.metrics;
            const panel = document.getElementById('analysis-panel');
            panel.innerHTML = `
                <div class="text-lg font-semibold text-blue-400 mb-4">Performance Metrics</div>
                <div class="grid grid-cols-2 gap-3">
                    <div class="bg-slate-900 p-3 rounded text-center">
                        <div class="text-slate-400 text-sm">Complexity Score</div>
                        <div class="text-2xl font-bold text-cyan-400">${metrics.cyclomatic_complexity}</div>
                    </div>
                    <div class="bg-slate-900 p-3 rounded text-center">
                        <div class="text-slate-400 text-sm">Nesting Depth</div>
                        <div class="text-2xl font-bold text-cyan-400">${metrics.nested_depth}</div>
                    </div>
                    <div class="bg-slate-900 p-3 rounded text-center">
                        <div class="text-slate-400 text-sm">Performance Score</div>
                        <div class="text-2xl font-bold text-green-400">${metrics.performance_score}/100</div>
                    </div>
                    <div class="bg-slate-900 p-3 rounded text-center">
                        <div class="text-slate-400 text-sm">Rating</div>
                        <div class="text-xl font-bold">${metrics.performance_rating}</div>
                    </div>
                </div>
                <div class="mt-3 text-slate-400 text-sm">Lines of Code: ${metrics.lines_of_code}</div>
            `;
        }
    } catch (err) {
        showAnalysisError('Performance analysis failed');
    }
}

// 4.5 - Refactoring Suggestions
async function getRefactoringTips() {
    const code = document.getElementById('code-editor').value;
    const language = document.getElementById('language').value;
    
    if (!code.trim()) {
        showAnalysisError('Please enter code');
        return;
    }

    try {
        const response = await fetch('./api/refactoring-suggestions', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ code, language })
        });
        const data = await response.json();
        
        if (data.status === 'success') {
            const panel = document.getElementById('analysis-panel');
            panel.innerHTML = `<div class="text-lg font-semibold text-green-400 mb-2">Refactoring Tips (${data.suggestions.length})</div>`;
            
            data.suggestions.forEach(sug => {
                panel.innerHTML += `
                    <div class="bg-slate-900 p-2 rounded mb-2 border-l-4 border-green-500">
                        <div class="font-semibold text-${sug.priority === 'HIGH' ? 'red-400' : 'yellow-400'}">${sug.type}</div>
                        <div class="text-slate-400 text-sm mt-1">${sug.suggestion}</div>
                        <div class="text-blue-400 text-xs mt-1">Benefit: ${sug.benefit}</div>
                    </div>
                `;
            });
        }
    } catch (err) {
        showAnalysisError('Failed to get refactoring suggestions');
    }
}

// Helper function to show analysis errors
function showAnalysisError(message) {
    const panel = document.getElementById('analysis-panel');
    panel.innerHTML = `<div class="text-red-400 p-3 bg-slate-900 rounded">❌ ${message}</div>`;
}
