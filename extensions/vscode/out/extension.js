"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.activate = activate;
exports.deactivate = deactivate;
const vscode = __importStar(require("vscode"));
const CAJAL_API = 'http://localhost:8000/v1/chat/completions';
async function callCajal(prompt) {
    const config = vscode.workspace.getConfiguration('cajal');
    const serverUrl = config.get('serverUrl') || CAJAL_API;
    try {
        const res = await fetch(serverUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                messages: [{ role: 'user', content: prompt }],
                max_new_tokens: 512,
                temperature: 0.7
            })
        });
        const data = await res.json();
        return data.response || 'No response from CAJAL';
    }
    catch (err) {
        return `❌ Error: ${err}. Make sure cajal-server is running.`;
    }
}
function activate(context) {
    // Chat command
    const chatCmd = vscode.commands.registerCommand('cajal.chat', async () => {
        const prompt = await vscode.window.showInputBox({
            prompt: 'Ask CAJAL anything...',
            placeHolder: 'Explain Byzantine consensus in P2P networks'
        });
        if (!prompt)
            return;
        vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: '🧠 CAJAL is thinking...'
        }, async () => {
            const response = await callCajal(prompt);
            const doc = await vscode.workspace.openTextDocument({
                content: `## CAJAL Response\n\n${response}`,
                language: 'markdown'
            });
            await vscode.window.showTextDocument(doc);
        });
    });
    // Explain selection
    const explainCmd = vscode.commands.registerCommand('cajal.explain', async () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor)
            return;
        const selection = editor.document.getText(editor.selection);
        if (!selection) {
            vscode.window.showWarningMessage('No text selected');
            return;
        }
        const response = await callCajal(`Explain this code/text:\n\n${selection}`);
        vscode.window.showInformationMessage(response.slice(0, 200) + '...');
    });
    // Generate command
    const generateCmd = vscode.commands.registerCommand('cajal.generate', async () => {
        const prompt = await vscode.window.showInputBox({
            prompt: 'What should CAJAL generate?',
            placeHolder: 'Generate a Python function for SHA-256 hashing'
        });
        if (!prompt)
            return;
        const response = await callCajal(`Generate code:\n\n${prompt}`);
        const doc = await vscode.workspace.openTextDocument({
            content: response,
            language: 'python'
        });
        await vscode.window.showTextDocument(doc);
    });
    context.subscriptions.push(chatCmd, explainCmd, generateCmd);
}
function deactivate() { }
