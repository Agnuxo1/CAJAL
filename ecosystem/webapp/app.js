/**
 * CAJAL Web Chat Application
 * Connects to local Ollama instance for CAJAL-4B inference
 */

const CONFIG = {
    ollamaHost: localStorage.getItem('cajal_host') || 'http://localhost:11434',
    model: localStorage.getItem('cajal_model') || 'cajal-4b',
    temperature: parseFloat(localStorage.getItem('cajal_temp')) || 0.7,
    topP: parseFloat(localStorage.getItem('cajal_topp')) || 0.9,
    contextLength: parseInt(localStorage.getItem('cajal_ctx')) || 4096,
    systemPrompt: `You are CAJAL, a distinguished scientist at the P2PCLAW (Peer-to-Peer Crypto Law) laboratory in Zurich, Switzerland. You are a deep researcher and applied cryptographer with extensive expertise in peer-to-peer network architectures, crypto-legal frameworks, game-theoretic consensus mechanisms, and distributed systems.`,
};

let conversations = JSON.parse(localStorage.getItem('cajal_conversations') || '[]');
let currentConversationId = null;
let isStreaming = false;
let abortController = null;

// DOM Elements
const els = {
    messagesContainer: document.getElementById('messages-container'),
    messageInput: document.getElementById('message-input'),
    sendBtn: document.getElementById('send-btn'),
    newChatBtn: document.getElementById('new-chat-btn'),
    conversationsList: document.getElementById('conversations-list'),
    welcomeScreen: document.getElementById('welcome-screen'),
    chatTitle: document.getElementById('chat-title'),
    statusDot: document.getElementById('status-dot'),
    statusText: document.getElementById('status-text'),
    settingsBtn: document.getElementById('settings-btn'),
    settingsModal: document.getElementById('settings-modal'),
    closeSettings: document.getElementById('close-settings'),
    saveSettings: document.getElementById('save-settings'),
    clearBtn: document.getElementById('clear-btn'),
    exportBtn: document.getElementById('export-btn'),
    sidebarToggle: document.getElementById('sidebar-toggle'),
    sidebar: document.getElementById('sidebar'),
};

// Initialize
function init() {
    loadConversationsList();
    checkOllamaStatus();
    setInterval(checkOllamaStatus, 5000);
    setupEventListeners();
    setupAutoResize();
}

function setupEventListeners() {
    els.sendBtn.addEventListener('click', sendMessage);
    els.messageInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    els.messageInput.addEventListener('input', () => {
        els.sendBtn.disabled = els.messageInput.value.trim() === '' || isStreaming;
    });
    
    els.newChatBtn.addEventListener('click', startNewChat);
    els.clearBtn.addEventListener('click', clearCurrentChat);
    els.exportBtn.addEventListener('click', exportConversation);
    
    els.settingsBtn.addEventListener('click', () => els.settingsModal.classList.add('active'));
    els.closeSettings.addEventListener('click', () => els.settingsModal.classList.remove('active'));
    els.settingsModal.addEventListener('click', (e) => {
        if (e.target === els.settingsModal) els.settingsModal.classList.remove('active');
    });
    els.saveSettings.addEventListener('click', saveSettings);
    
    els.sidebarToggle.addEventListener('click', () => els.sidebar.classList.toggle('open'));
    
    // Suggestion chips
    document.querySelectorAll('.chip').forEach(chip => {
        chip.addEventListener('click', () => {
            els.messageInput.value = chip.dataset.prompt;
            els.sendBtn.disabled = false;
            sendMessage();
        });
    });
    
    // Settings sliders
    document.getElementById('setting-temp').addEventListener('input', (e) => {
        document.getElementById('temp-value').textContent = e.target.value;
    });
    document.getElementById('setting-topp').addEventListener('input', (e) => {
        document.getElementById('topp-value').textContent = e.target.value;
    });
}

function setupAutoResize() {
    const textarea = els.messageInput;
    textarea.addEventListener('input', () => {
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 200) + 'px';
    });
}

// Ollama Status
async function checkOllamaStatus() {
    try {
        const response = await fetch(`${CONFIG.ollamaHost}/api/tags`, { method: 'GET', signal: AbortSignal.timeout(3000) });
        if (response.ok) {
            const data = await response.json();
            const hasCajal = data.models?.some(m => m.name.startsWith('cajal'));
            els.statusDot.classList.add('connected');
            els.statusText.textContent = hasCajal ? 'Ollama + CAJAL ready' : 'Ollama ready (no CAJAL)';
        } else {
            throw new Error('Not OK');
        }
    } catch (e) {
        els.statusDot.classList.remove('connected');
        els.statusText.textContent = 'Ollama disconnected';
    }
}

// Conversations
function loadConversationsList() {
    els.conversationsList.innerHTML = '';
    conversations.forEach(conv => {
        const div = document.createElement('div');
        div.className = `conversation-item ${conv.id === currentConversationId ? 'active' : ''}`;
        div.innerHTML = `<span>💬</span> ${conv.title || 'New Chat'}`;
        div.addEventListener('click', () => loadConversation(conv.id));
        els.conversationsList.appendChild(div);
    });
}

function startNewChat() {
    currentConversationId = null;
    els.welcomeScreen.style.display = 'flex';
    els.messagesContainer.querySelectorAll('.message, .typing-indicator').forEach(el => el.remove());
    els.chatTitle.textContent = 'New Chat';
    loadConversationsList();
}

function loadConversation(id) {
    const conv = conversations.find(c => c.id === id);
    if (!conv) return;
    currentConversationId = id;
    els.welcomeScreen.style.display = 'none';
    
    // Clear and rebuild messages
    els.messagesContainer.querySelectorAll('.message, .typing-indicator').forEach(el => el.remove());
    conv.messages.forEach(msg => {
        if (msg.role !== 'system') {
            appendMessage(msg.role, msg.content, false);
        }
    });
    els.chatTitle.textContent = conv.title || 'Chat';
    loadConversationsList();
}

function saveConversation() {
    if (!currentConversationId) {
        currentConversationId = 'conv_' + Date.now();
        conversations.unshift({
            id: currentConversationId,
            title: 'New Chat',
            messages: [],
            createdAt: Date.now(),
        });
    }
    const conv = conversations.find(c => c.id === currentConversationId);
    if (conv) {
        const msgs = [];
        els.messagesContainer.querySelectorAll('.message').forEach(el => {
            const role = el.classList.contains('user') ? 'user' : 'assistant';
            const content = el.querySelector('.message-body')?.textContent || '';
            msgs.push({ role, content });
        });
        conv.messages = msgs;
        if (msgs.length > 0 && conv.title === 'New Chat') {
            conv.title = msgs[0].content.substring(0, 40) + '...';
        }
    }
    localStorage.setItem('cajal_conversations', JSON.stringify(conversations));
    loadConversationsList();
}

function clearCurrentChat() {
    if (currentConversationId) {
        conversations = conversations.filter(c => c.id !== currentConversationId);
        localStorage.setItem('cajal_conversations', JSON.stringify(conversations));
    }
    startNewChat();
}

function exportConversation() {
    if (!currentConversationId) return;
    const conv = conversations.find(c => c.id === currentConversationId);
    if (!conv) return;
    const data = {
        title: conv.title,
        model: CONFIG.model,
        exportedAt: new Date().toISOString(),
        messages: conv.messages,
    };
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `cajal-conversation-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
}

// Messaging
async function sendMessage() {
    const text = els.messageInput.value.trim();
    if (!text || isStreaming) return;
    
    els.welcomeScreen.style.display = 'none';
    appendMessage('user', text, true);
    els.messageInput.value = '';
    els.messageInput.style.height = 'auto';
    els.sendBtn.disabled = true;
    
    await streamResponse(text);
}

function appendMessage(role, content, animate = true) {
    const div = document.createElement('div');
    div.className = `message ${role}`;
    if (animate) div.style.animationDelay = '0s';
    
    const avatar = role === 'user' ? '👤' : '🧠';
    const author = role === 'user' ? 'You' : 'CAJAL';
    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    // Parse thinking blocks
    let bodyContent = formatMessage(content);
    
    div.innerHTML = `
        <div class="message-avatar">${avatar}</div>
        <div class="message-content">
            <div class="message-header">
                <span class="message-author">${author}</span>
                <span class="message-time">${time}</span>
            </div>
            <div class="message-body">${bodyContent}</div>
        </div>
    `;
    
    els.messagesContainer.appendChild(div);
    scrollToBottom();
    return div;
}

function formatMessage(text) {
    // Handle thinking blocks
    text = text.replace(/<think>([\s\S]*?)<\/think>/g, '<details class="thinking-block" open><summary>Thinking Process</summary><pre>$1</pre></details>');
    
    // Escape HTML
    text = text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    
    // Restore thinking blocks (they were escaped, need to unescape)
    text = text.replace(/&lt;details class=&quot;thinking-block&quot; open&gt;&lt;summary&gt;Thinking Process&lt;\/summary&gt;&lt;pre&gt;([\s\S]*?)&lt;\/pre&gt;&lt;\/details&gt;/g, 
        '<details class="thinking-block" open><summary>💭 Thinking Process</summary><pre>$1</pre></details>');
    
    // Simple markdown-ish formatting
    text = text.replace(/^### (.*$)/gim, '<h3>$1</h3>');
    text = text.replace(/^## (.*$)/gim, '<h2>$1</h2>');
    text = text.replace(/^# (.*$)/gim, '<h1>$1</h1>');
    text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    text = text.replace(/\*(.*?)\*/g, '<em>$1</em>');
    text = text.replace(/`([^`]+)`/g, '<code>$1</code>');
    text = text.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');
    text = text.replace(/\n/g, '<br>');
    
    return text;
}

function scrollToBottom() {
    els.messagesContainer.scrollTop = els.messagesContainer.scrollHeight;
}

async function streamResponse(userMessage) {
    isStreaming = true;
    
    // Build messages
    const messages = [{ role: 'system', content: CONFIG.systemPrompt }];
    
    // Add conversation history
    if (currentConversationId) {
        const conv = conversations.find(c => c.id === currentConversationId);
        if (conv) {
            messages.push(...conv.messages);
        }
    }
    messages.push({ role: 'user', content: userMessage });
    
    // Show typing indicator
    const typingId = 'typing-' + Date.now();
    const typingDiv = document.createElement('div');
    typingDiv.id = typingId;
    typingDiv.className = 'typing-indicator';
    typingDiv.innerHTML = '<span></span><span></span><span></span>';
    els.messagesContainer.appendChild(typingDiv);
    scrollToBottom();
    
    try {
        const response = await fetch(`${CONFIG.ollamaHost}/api/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                model: CONFIG.model,
                messages: messages,
                stream: true,
                options: {
                    temperature: CONFIG.temperature,
                    top_p: CONFIG.topP,
                    num_ctx: CONFIG.contextLength,
                }
            }),
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        // Remove typing, create assistant message
        typingDiv.remove();
        const assistantDiv = appendMessage('assistant', '', false);
        const bodyEl = assistantDiv.querySelector('.message-body');
        let fullText = '';
        
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            
            const chunk = decoder.decode(value, { stream: true });
            const lines = chunk.split('\n').filter(line => line.trim());
            
            for (const line of lines) {
                try {
                    const data = JSON.parse(line);
                    if (data.message?.content) {
                        fullText += data.message.content;
                        bodyEl.innerHTML = formatMessage(fullText);
                        scrollToBottom();
                    }
                    if (data.done) break;
                } catch (e) {
                    // Ignore parse errors in stream
                }
            }
        }
        
        // Save to conversation
        if (!currentConversationId) {
            currentConversationId = 'conv_' + Date.now();
            conversations.unshift({
                id: currentConversationId,
                title: userMessage.substring(0, 40) + (userMessage.length > 40 ? '...' : ''),
                messages: [{ role: 'user', content: userMessage }, { role: 'assistant', content: fullText }],
                createdAt: Date.now(),
            });
        } else {
            const conv = conversations.find(c => c.id === currentConversationId);
            if (conv) {
                conv.messages.push({ role: 'user', content: userMessage });
                conv.messages.push({ role: 'assistant', content: fullText });
            }
        }
        localStorage.setItem('cajal_conversations', JSON.stringify(conversations));
        loadConversationsList();
        
    } catch (error) {
        typingDiv.remove();
        appendMessage('assistant', `**Error:** Could not connect to Ollama. Please ensure Ollama is running and the model is installed.\n\nRun: \`ollama run ${CONFIG.model}\``);
        console.error('Stream error:', error);
    } finally {
        isStreaming = false;
        els.sendBtn.disabled = els.messageInput.value.trim() === '';
    }
}

// Settings
function saveSettings() {
    CONFIG.ollamaHost = document.getElementById('setting-host').value;
    CONFIG.model = document.getElementById('setting-model').value;
    CONFIG.temperature = parseFloat(document.getElementById('setting-temp').value);
    CONFIG.topP = parseFloat(document.getElementById('setting-topp').value);
    CONFIG.contextLength = parseInt(document.getElementById('setting-ctx').value);
    
    localStorage.setItem('cajal_host', CONFIG.ollamaHost);
    localStorage.setItem('cajal_model', CONFIG.model);
    localStorage.setItem('cajal_temp', CONFIG.temperature);
    localStorage.setItem('cajal_topp', CONFIG.topP);
    localStorage.setItem('cajal_ctx', CONFIG.contextLength);
    
    els.settingsModal.classList.remove('active');
    checkOllamaStatus();
    
    // Show toast
    showToast('Settings saved');
}

function showToast(message) {
    const toast = document.createElement('div');
    toast.style.cssText = `
        position: fixed; bottom: 80px; left: 50%; transform: translateX(-50%);
        background: var(--accent); color: #000; padding: 10px 20px;
        border-radius: 20px; font-weight: 600; z-index: 200;
        animation: fadeIn 0.3s ease;
    `;
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 2000);
}

// Start
init();
