chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'showCajalResult') {
    // Show floating result box
    const div = document.createElement('div');
    div.style.cssText = `
      position: fixed; top: 20px; right: 20px; width: 400px;
      background: #fff; border: 2px solid #0066ff; border-radius: 8px;
      padding: 16px; z-index: 999999; box-shadow: 0 4px 12px rgba(0,0,0,0.15);
      font-family: system-ui, sans-serif; font-size: 14px; line-height: 1.5;
    `;
    div.innerHTML = `
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
        <strong>🧠 CAJAL Result</strong>
        <button onclick="this.parentElement.parentElement.remove()" style="border:none;background:none;cursor:pointer;font-size:18px;">×</button>
      </div>
      <div>${request.result.replace(/\n/g, '<br>')}</div>
    `;
    document.body.appendChild(div);
  }
});
