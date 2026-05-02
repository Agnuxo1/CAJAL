// CAJAL Browser Extension — Background Service Worker

chrome.runtime.onInstalled.addListener(() => {
    // Create context menu items
    chrome.contextMenus.create({
        id: 'cajal-explain',
        title: 'Explain with CAJAL',
        contexts: ['selection']
    });
    chrome.contextMenus.create({
        id: 'cajal-summarize',
        title: 'Summarize with CAJAL',
        contexts: ['page']
    });
    chrome.contextMenus.create({
        id: 'cajal-code',
        title: 'Explain Code with CAJAL',
        contexts: ['selection']
    });
    chrome.contextMenus.create({
        id: 'cajal-sidebar',
        title: 'Open CAJAL Sidebar',
        contexts: ['all']
    });
});

chrome.contextMenus.onClicked.addListener(async (info, tab) => {
    if (info.menuItemId === 'cajal-explain') {
        await sendToPopup(tab.id, `Explain this:\n\n${info.selectionText}`);
    } else if (info.menuItemId === 'cajal-summarize') {
        chrome.scripting.executeScript({
            target: { tabId: tab.id },
            func: () => document.body.innerText.substring(0, 6000)
        }, (results) => {
            if (results && results[0]) {
                sendToPopup(tab.id, `Summarize this page:\n\n${results[0].result}`);
            }
        });
    } else if (info.menuItemId === 'cajal-code') {
        await sendToPopup(tab.id, `Explain this code:\n\n\`\`\`\n${info.selectionText}\n\`\`\``);
    } else if (info.menuItemId === 'cajal-sidebar') {
        chrome.scripting.executeScript({
            target: { tabId: tab.id },
            files: ['sidebar.js']
        });
    }
});

async function sendToPopup(tabId, text) {
    // Store the pending query for the popup to pick up
    await chrome.storage.session.set({ pendingQuery: text });
    chrome.action.openPopup();
}

// Handle keyboard shortcuts
chrome.commands.onCommand.addListener((command) => {
    if (command === '_execute_action') {
        chrome.action.openPopup();
    }
});
