import * as vscode from 'vscode';

const CAJAL_API = 'http://localhost:8000/v1/chat/completions';

async function callCajal(prompt: string): Promise<string> {
  const config = vscode.workspace.getConfiguration('cajal');
  const serverUrl = config.get<string>('serverUrl') || CAJAL_API;
  
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
    const data = await res.json() as { response: string };
    return data.response || 'No response from CAJAL';
  } catch (err) {
    return `❌ Error: ${err}. Make sure cajal-server is running.`;
  }
}

export function activate(context: vscode.ExtensionContext) {
  // Chat command
  const chatCmd = vscode.commands.registerCommand('cajal.chat', async () => {
    const prompt = await vscode.window.showInputBox({
      prompt: 'Ask CAJAL anything...',
      placeHolder: 'Explain Byzantine consensus in P2P networks'
    });
    if (!prompt) return;
    
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
    if (!editor) return;
    
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
    if (!prompt) return;
    
    const response = await callCajal(`Generate code:\n\n${prompt}`);
    const doc = await vscode.workspace.openTextDocument({
      content: response,
      language: 'python'
    });
    await vscode.window.showTextDocument(doc);
  });

  context.subscriptions.push(chatCmd, explainCmd, generateCmd);
}

export function deactivate() {}
