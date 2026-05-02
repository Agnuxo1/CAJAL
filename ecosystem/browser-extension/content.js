// CAJAL Content Script — Page Integration

(function() {
    'use strict';
    
    // Prevent double injection
    if (window.__cajalInjected) return;
    window.__cajalInjected = true;
    
    let sidebar = null;
    let messages = [];
    
    function createSidebar() {
        if (sidebar) {
            sidebar.classList.toggle('open');
            return;
        }
        
        sidebar = document.createElement('div');
        sidebar.className = 'cajal-sidebar';
        sidebar.innerHTML = `
            <div class="cajal-header">
                <h2>🧠 CAJAL</h2>
                <button class="cajal-close">×</button>
            </div>
            <div class="cajal-messages"></div>
            <div class="cajal-input-area">
                <input type="text" class="cajal-input" placeholder="Ask CAJAL..." />
                <button class="cajal-send">Send</button>
            </div>
        `;
        document.body.appendChild(sidebar);
        
        // Close button
        sidebar.querySelector('.cajal-close').addEventListener('click', () => {
            sidebar.classList.remove('open');
        });
        
        // Send message
        const input = sidebar.querySelector('.cajal-input');
        const sendBtn = sidebar.querySelector('.cajal-send');
        
        sendBtn.addEventListener('click', () => sendMessage(input.value));
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') sendMessage(input.value);
        });
        
        sidebar.classList.add('open');
        addMessage('assistant', 'Hello! I am CAJAL. Select text and right-click to analyze, or ask me anything.');
    }
    
    function addMessage(role, text) {
        const area = sidebar.querySelector('.cajal-messages');
        const div = document.createElement('div');
        div.className = `cajal-msg ${role}`;
        div.innerHTML = `<div class="author">${role === 'user' ? 'You' : 'CAJAL'}</div>${escapeHtml(text)}`;
        area.appendChild(div);
        area.scrollTop = area.scrollHeight;
        messages.push({ role, content: text });
    }
    
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML.replace(/\n/g, '<br>');
    }
    
    async function sendMessage(text) {
        if (!text.trim()) return;
        const input = sidebar.querySelector('.cajal-input');
        input.value = '';
        addMessage('user', text);
        
        try {
            const response = await fetch('http://localhost:11434/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    model: 'cajal-4b',
                    messages: [
                        { role: 'system', content: 'You are CAJAL, P2PCLAW AI assistant. Be concise and helpful.' },
                        ...messages.slice(-6)
                    ],
                    stream: false,
                    options: { temperature: 0.7, num_ctx: 4096 }
                })
            });
            const data = await response.json();
            addMessage('assistant', data.message?.content || 'No response');
        } catch (err) {
            addMessage('assistant', 'Error: Cannot connect to CAJAL. Make sure Ollama is running.');
        }
    }
    
    // Listen for messages from background script
    chrome.runtime?.onMessage?.addListener((request, sender, sendResponse) => {
        if (request.action === 'openSidebar') {
            createSidebar();
        } else if (request.action === 'chat') {
            createSidebar();
            setTimeout(() => sendMessage(request.text), 300);
        }
    });
    
    // Keyboard shortcut to toggle sidebar
    document.addEventListener('keydown', (e) => {
        if (e.ctrlKey && e.shiftKey && e.key === 'A') {
            e.preventDefault();
            createSidebar();
        }
    });
    
})();
