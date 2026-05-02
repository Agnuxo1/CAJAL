// CAJAL Chrome Extension - Background Script
chrome.runtime.onInstalled.addListener(() => {
  // Create context menu items
  chrome.contextMenus.create({
    id: 'cajal-summarize',
    title: '🧠 CAJAL: Summarize for paper',
    contexts: ['selection']
  });
  
  chrome.contextMenus.create({
    id: 'cajal-explain',
    title: '🧠 CAJAL: Explain for methodology',
    contexts: ['selection']
  });
  
  chrome.contextMenus.create({
    id: 'cajal-generate',
    title: '🧠 CAJAL: Generate paper from page',
    contexts: ['page']
  });
});

chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  const text = info.selectionText || '';
  const pageUrl = tab.url;
  
  switch (info.menuItemId) {
    case 'cajal-summarize':
      await callCajal(`Summarize the following text for inclusion in a scientific paper:\n\n${text}`);
      break;
      
    case 'cajal-explain':
      await callCajal(`Explain the following concept in a way suitable for a methodology section:\n\n${text}`);
      break;
      
    case 'cajal-generate':
      await callCajal(`Based on the content of ${pageUrl}, suggest a research paper topic and generate an abstract.`);
      break;
  }
});

async function callCajal(prompt) {
  try {
    const response = await fetch('http://localhost:11434/api/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: 'cajal',
        prompt: prompt,
        stream: false,
        options: { temperature: 0.3, num_ctx: 32768 }
      })
    });
    
    if (response.ok) {
      const data = await response.json();
      // Store result for popup access
      chrome.storage.local.set({ lastResult: data.response });
    }
  } catch (error) {
    console.error('CAJAL error:', error);
  }
}