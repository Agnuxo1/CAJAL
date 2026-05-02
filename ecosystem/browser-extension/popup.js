// CAJAL Browser Extension — Popup Script

const DEFAULT_CONFIG = {
    host: 'http://localhost:11434',
    model: 'cajal-4b',
    temperature: 0.7,
    maxTokens: 4096,
    sidebarEnabled: true
};

let config = { ...DEFAULT_CONFIG };
let messages = [];

async function loadConfig() {
    const stored = await chrome.storage.sync.get(['cajalHost', 'cajalModel', 'cajalTemperature']);
    config.host = stored.cajalHost || DEFAULT_CONFIG.host;
    config.model = stored.cajalModel || DEFAULT_CONFIG.model;
    config.temperature = stored.cajalTemperature || DEFAULT_CONFIG.temperature;
}

async function checkStatus() {
    const dot = document.getElementById('statusDot');
    const text = document.getElementById('statusText');
    try {
        const response = await fetch(`${config.host}/api/tags`, { method: 'GET', timeout: 3000 });
        if (response.ok) {
            dot.className = 'status-dot';
            text.textContent = 'Ollama Connected';
            return true;
        }
    } catch (e) {
        // Try API bridge
        try {
            const r2 = await fetch(`http://localhost:8765/health`, { method: 'GET', timeout: 3000 });
            if (r2.ok) {
                dot.className = 'status-dot';
                text.textContent = 'CAJAL Server Connected';
                return true;
            }
        } catch (e2) {}
    }
    dot.className = 'status-dot offline';
    text.textContent = 'Offline — Start Ollama';
    return false;
}

function addMessage(role, text) {
    const area = document.getElementById('chatArea');
    const div = document.createElement('div');
    div.className = `message ${role}`;
    div.innerHTML = `<div class="author">${role === 'user' ? 'You' : 'CAJAL'}</div>${escapeHtml(text)}`;
    area.appendChild(div);
    area.scrollTop = area.scrollHeight;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML.replace(/\n/g, '<br>');
}

async function chatWithCajal(text) {
    addMessage('user', text);
    messages.push({ role: 'user', content: text });

    const systemPrompt = `You are CAJAL, a distinguished scientist at the P2PCLAW laboratory in Zurich. You are an expert in peer-to-peer networks, crypto-legal frameworks, and distributed systems. Provide concise, well-structured responses.`;

    try {
        const response = await fetch(`${config.host}/api/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                model: config.model,
                messages: [
                    { role: 'system', content: systemPrompt },
                    ...messages.slice(-6)
                ],
                stream: false,
                options: {
                    temperature: config.temperature,
                    num_ctx: config.maxTokens
                }
            })
        });
        const data = await response.json();
        const reply = data.message?.content || 'No response from CAJAL';
        addMessage('assistant', reply);
        messages.push({ role: 'assistant', content: reply });
    } catch (err) {
        addMessage('assistant', 'Error: Could not connect to CAJAL. Is Ollama running?');
    }
}

// Event Listeners
document.getElementById('send').addEventListener('click', () => {
    const input = document.getElementById('input');
    const text = input.value.trim();
    if (!text) return;
    input.value = '';
    chatWithCajal(text);
});

document.getElementById('input').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') document.getElementById('send').click();
});

document.getElementById('btnSummarize').addEventListener('click', async () => {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: () => {
            const text = document.body.innerText.substring(0, 8000);
            return text;
        }
    }, (results) => {
        if (results && results[0]) {
            chatWithCajal(`Summarize this webpage concisely:\n\n${results[0].result.substring(0, 4000)}`);
        }
    });
});

document.getElementById('btnExplain').addEventListener('click', async () => {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: () => window.getSelection().toString()
    }, (results) => {
        if (results && results[0] && results[0].result) {
            chatWithCajal(`Explain this text:\n\n${results[0].result}`);
        } else {
            addMessage('assistant', 'Please select some text on the page first.');
        }
    });
});

document.getElementById('btnSidebar').addEventListener('click', async () => {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    chrome.scripting.executeScript({
        target: { tabId: tab.id },
        files: ['sidebar.js']
    });
});

document.getElementById('btnSettings').addEventListener('click', () => {
    chrome.runtime.openOptionsPage?.() || window.open('options.html');
});

document.getElementById('openSettings').addEventListener('click', (e) => {
    e.preventDefault();
    chrome.runtime.openOptionsPage?.() || window.open('options.html');
});

// Initialize
loadConfig().then(() => {
    checkStatus();
    addMessage('assistant', 'Hello! I am CAJAL. How can I help you today?');
});
