const vscode = require('vscode');

const SYSTEM_PROMPT = `You are CAJAL, a distinguished scientist at the P2PCLAW (Peer-to-Peer Crypto Law) laboratory in Zurich, Switzerland. You are an expert in peer-to-peer network architectures, crypto-legal frameworks, game-theoretic consensus mechanisms, and distributed systems. You are assisting with code review, software architecture, and technical analysis. Provide rigorous, well-structured responses with evidence-based reasoning.`;

function getConfig() {
    return vscode.workspace.getConfiguration('cajal');
}

async function chatWithOllama(messages) {
    const cfg = getConfig();
    const host = cfg.get('ollamaHost', 'http://localhost:11434');
    const model = cfg.get('model', 'cajal-4b');
    const temperature = cfg.get('temperature', 0.7);
    const maxTokens = cfg.get('maxTokens', 4096);

    try {
        const response = await fetch(`${host}/api/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                model,
                messages,
                stream: false,
                options: { temperature, num_ctx: maxTokens }
            })
        });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        return data.message?.content || 'No response';
    } catch (err) {
        vscode.window.showErrorMessage(`CAJAL Error: ${err.message}. Is Ollama running?`);
        throw err;
    }
}

function activate(context) {
    console.log('CAJAL extension activated');

    // Command: Open Chat Panel
    const chatCmd = vscode.commands.registerCommand('cajal.chat', () => {
        const panel = vscode.window.createWebviewPanel(
            'cajalChat',
            'CAJAL Chat',
            vscode.ViewColumn.Beside,
            { enableScripts: true, retainContextWhenHidden: true }
        );
        panel.webview.html = getChatHtml(panel.webview);
        
        panel.webview.onDidReceiveMessage(async message => {
            if (message.command === 'send') {
                const response = await chatWithOllama([
                    { role: 'system', content: SYSTEM_PROMPT },
                    { role: 'user', content: message.text }
                ]);
                panel.webview.postMessage({ command: 'response', text: response });
            }
        });
    });

    // Command: Ask CAJAL
    const askCmd = vscode.commands.registerCommand('cajal.ask', async () => {
        const question = await vscode.window.showInputBox({
            prompt: 'Ask CAJAL anything',
            placeHolder: 'e.g., Explain zero-knowledge proofs'
        });
        if (!question) return;
        
        await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: 'CAJAL is thinking...',
            cancellable: false
        }, async () => {
            const response = await chatWithOllama([
                { role: 'system', content: SYSTEM_PROMPT },
                { role: 'user', content: question }
            ]);
            const doc = await vscode.workspace.openTextDocument({
                content: `# CAJAL Response\n\n**Question:** ${question}\n\n---\n\n${response}`,
                language: 'markdown'
            });
            await vscode.window.showTextDocument(doc);
        });
    });

    // Command: Explain Code
    const explainCmd = vscode.commands.registerCommand('cajal.explain', async () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor) return;
        
        const selection = editor.document.getText(editor.selection);
        if (!selection) {
            vscode.window.showWarningMessage('Select some code first');
            return;
        }

        await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: 'CAJAL is analyzing your code...',
        }, async () => {
            const response = await chatWithOllama([
                { role: 'system', content: SYSTEM_PROMPT },
                { role: 'user', content: `Explain this code in detail:\n\n\`\`\`${editor.document.languageId}\n${selection}\n\`\`\`` }
            ]);
            const doc = await vscode.workspace.openTextDocument({
                content: `# Code Explanation by CAJAL\n\n**Language:** ${editor.document.languageId}\n\n\`\`\`${editor.document.languageId}\n${selection}\n\`\`\`\n\n---\n\n${response}`,
                language: 'markdown'
            });
            await vscode.window.showTextDocument(doc);
        });
    });

    // Command: Settings
    const settingsCmd = vscode.commands.registerCommand('cajal.settings', () => {
        vscode.commands.executeCommand('workbench.action.openSettings', 'cajal');
    });

    context.subscriptions.push(chatCmd, askCmd, explainCmd, settingsCmd);
}

function getChatHtml(webview) {
    return `<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
body { font-family: system-ui; padding: 16px; background: #1e1e1e; color: #d4d4d4; height: 100vh; margin: 0; display: flex; flex-direction: column; }
#messages { flex: 1; overflow-y: auto; margin-bottom: 12px; }
.message { margin-bottom: 16px; padding: 12px; border-radius: 8px; }
.user { background: #2d2d2d; }
.assistant { background: #094771; }
.author { font-weight: bold; margin-bottom: 4px; font-size: 12px; }
.input-area { display: flex; gap: 8px; }
#input { flex: 1; padding: 10px; border-radius: 6px; border: 1px solid #3c3c3c; background: #252526; color: #d4d4d4; }
#send { padding: 10px 20px; background: #007acc; color: white; border: none; border-radius: 6px; cursor: pointer; }
#send:hover { background: #005a9e; }
pre { background: #1e1e1e; padding: 12px; border-radius: 6px; overflow-x: auto; }
</style>
</head>
<body>
<div id="messages"></div>
<div class="input-area">
    <input type="text" id="input" placeholder="Ask CAJAL..." />
    <button id="send">Send</button>
</div>
<script>
const vscode = acquireVsCodeApi();
const messages = document.getElementById('messages');
const input = document.getElementById('input');
const sendBtn = document.getElementById('send');

function addMessage(role, text) {
    const div = document.createElement('div');
    div.className = 'message ' + role;
    div.innerHTML = '<div class="author">' + (role === 'user' ? 'You' : 'CAJAL') + '</div><div>' + escapeHtml(text).replace(/\n/g, '<br>') + '</div>';
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

sendBtn.addEventListener('click', () => {
    const text = input.value.trim();
    if (!text) return;
    addMessage('user', text);
    input.value = '';
    vscode.postMessage({ command: 'send', text });
});

input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') sendBtn.click();
});

window.addEventListener('message', event => {
    const msg = event.data;
    if (msg.command === 'response') {
        addMessage('assistant', msg.text);
    }
});
</script>
</body>
</html>`;
}

function deactivate() {}

module.exports = { activate, deactivate };
