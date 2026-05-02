// CAJAL Chrome Extension - Content Script
// Adds floating CAJAL button on academic websites

const CAJAL_SITES = [
  'arxiv.org',
  'scholar.google.com',
  'pubmed.ncbi.nlm.nih.gov',
  'ieee.org',
  'acm.org',
  'springer.com',
  'elsevier.com',
  'researchgate.net'
];

function shouldShowButton() {
  return CAJAL_SITES.some(site => window.location.hostname.includes(site));
}

function createFloatingButton() {
  const btn = document.createElement('div');
  btn.id = 'cajal-float-btn';
  btn.innerHTML = '🧠 CAJAL';
  btn.style.cssText = `
    position: fixed;
    bottom: 20px;
    right: 20px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 12px 20px;
    border-radius: 30px;
    font-family: system-ui, sans-serif;
    font-weight: 600;
    font-size: 14px;
    cursor: pointer;
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    z-index: 999999;
    transition: transform 0.2s, box-shadow 0.2s;
  `;
  
  btn.addEventListener('mouseenter', () => {
    btn.style.transform = 'scale(1.05)';
    btn.style.boxShadow = '0 6px 20px rgba(102, 126, 234, 0.5)';
  });
  
  btn.addEventListener('mouseleave', () => {
    btn.style.transform = 'scale(1)';
    btn.style.boxShadow = '0 4px 12px rgba(102, 126, 234, 0.4)';
  });
  
  btn.addEventListener('click', () => {
    // Extract page content
    const title = document.title;
    const abstract = extractAbstract();
    
    chrome.runtime.sendMessage({
      action: 'generateFromPage',
      title: title,
      abstract: abstract,
      url: window.location.href
    });
  });
  
  document.body.appendChild(btn);
}

function extractAbstract() {
  // Try common abstract selectors
  const selectors = [
    '.abstract',
    '#abstract',
    '[class*="abstract"]',
    '[class*="Abstract"]',
    'section[role="region"]'
  ];
  
  for (const selector of selectors) {
    const el = document.querySelector(selector);
    if (el) return el.textContent.substring(0, 1000);
  }
  
  // Fallback: first 500 chars of main content
  const main = document.querySelector('main') || document.querySelector('article') || document.body;
  return main.textContent.substring(0, 500);
}

// Initialize
if (shouldShowButton()) {
  createFloatingButton();
}