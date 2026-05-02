// CAJAL Chrome Extension - Popup Script
document.getElementById('generate').addEventListener('click', async () => {
  const topic = document.getElementById('topic').value.trim();
  const format = document.getElementById('format').value;
  const references = document.getElementById('references').value;
  const status = document.getElementById('status');
  const button = document.getElementById('generate');
  
  if (!topic) {
    status.className = 'status error';
    status.textContent = 'Please enter a research topic';
    return;
  }
  
  button.disabled = true;
  status.className = 'status loading';
  status.textContent = 'Generating paper... (this may take 1-3 minutes)';
  
  try {
    // Call Ollama API
    const response = await fetch('http://localhost:11434/api/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: 'cajal',
        prompt: `Generate a ${format === 'abstract' ? 'paper abstract (150-250 words)' : format === 'methods' ? 'detailed methodology section' : `complete scientific paper in ${format} format`} on: ${topic}. ${format === 'full' ? `Include Abstract, Introduction, Related Work, Methodology, Results, Discussion, Conclusion, and ${references} references.` : ''}`,
        stream: false,
        options: {
          temperature: 0.3,
          num_ctx: 32768
        }
      })
    });
    
    if (!response.ok) {
      throw new Error(`Ollama error: ${response.status}. Make sure Ollama is running with the 'cajal' model.`);
    }
    
    const data = await response.json();
    const paper = data.response;
    
    // Copy to clipboard
    await navigator.clipboard.writeText(paper);
    
    status.className = 'status success';
    status.innerHTML = `✅ Paper generated (${paper.length} chars) and copied to clipboard!<br><br><strong>Preview:</strong><br><pre style="white-space: pre-wrap; font-size: 11px; max-height: 150px; overflow-y: auto; background: #f0f0f0; padding: 8px; border-radius: 4px;">${paper.substring(0, 500)}...</pre>`;
    
  } catch (error) {
    status.className = 'status error';
    status.textContent = `Error: ${error.message}`;
  } finally {
    button.disabled = false;
  }
});

// Check Ollama status on load
async function checkOllama() {
  const status = document.getElementById('status');
  try {
    const response = await fetch('http://localhost:11434/api/tags', { method: 'GET' });
    if (response.ok) {
      const data = await response.json();
      const hasCajal = data.models?.some(m => m.name.includes('cajal'));
      if (!hasCajal) {
        status.className = 'status error';
        status.innerHTML = '⚠️ Ollama running but "cajal" model not found.<br>Run: <code>ollama create cajal -f Modelfile</code>';
      }
    }
  } catch {
    status.className = 'status error';
    status.innerHTML = '⚠️ Ollama not detected at localhost:11434.<br>Please start Ollama first.';
  }
}

checkOllama();