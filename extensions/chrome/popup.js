document.getElementById('send').addEventListener('click', async () => {
  const prompt = document.getElementById('prompt').value;
  const responseDiv = document.getElementById('response');
  
  if (!prompt.trim()) return;
  
  responseDiv.textContent = '🧠 Thinking...';
  
  try {
    const res = await fetch('http://localhost:8000/v1/chat/completions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        messages: [{ role: 'user', content: prompt }],
        max_new_tokens: 512,
        temperature: 0.7
      })
    });
    
    const data = await res.json();
    responseDiv.textContent = data.response || 'No response';
  } catch (err) {
    responseDiv.textContent = '❌ Error: ' + err.message + '\n\nMake sure cajal-server is running on port 8000.';
  }
});
