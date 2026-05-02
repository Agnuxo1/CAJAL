// CAJAL Chrome Extension - Background Service Worker
// Handles context menu and shortcuts

chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: 'cajal-summarize',
    title: '🧠 Summarize with CAJAL',
    contexts: ['selection']
  });
  
  chrome.contextMenus.create({
    id: 'cajal-explain',
    title: '🧠 Explain with CAJAL',
    contexts: ['selection']
  });
});

chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  const text = info.selectionText;
  let prompt = '';
  
  if (info.menuItemId === 'cajal-summarize') {
    prompt = `Summarize this text concisely:\n\n${text}`;
  } else if (info.menuItemId === 'cajal-explain') {
    prompt = `Explain this in simple terms:\n\n${text}`;
  }
  
  try {
    const res = await fetch('http://localhost:8000/v1/chat/completions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        messages: [{ role: 'user', content: prompt }],
        max_new_tokens: 256
      })
    });
    
    const data = await res.json();
    
    // Send result to content script to show
    chrome.tabs.sendMessage(tab.id, {
      action: 'showCajalResult',
      result: data.response
    });
  } catch (err) {
    console.error('CAJAL error:', err);
  }
});
