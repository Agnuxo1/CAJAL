{
  "translatorID": "cajal-p2pclaw-generator",
  "label": "CAJAL Paper Generator",
  "creator": "Francisco Angulo de Lafuente",
  "target": "text/html",
  "minVersion": "5.0",
  "maxVersion": "",
  "priority": 100,
  "inRepository": true,
  "translatorType": 4,
  "browserSupport": "gcsibv",
  "lastUpdated": "2026-05-02 00:00:00"
}

function doWeb(doc, url) {
  // Generate paper from selected items
  var items = Zotero.getActiveZoteroPane().getSelectedItems();
  var titles = items.map(item => item.getField('title'));
  
  // Call CAJAL API
  var xhr = new XMLHttpRequest();
  xhr.open('POST', 'http://localhost:8000/v1/chat/completions', false);
  xhr.setRequestHeader('Content-Type', 'application/json');
  xhr.send(JSON.stringify({
    messages: [{
      role: 'user',
      content: 'Generate a literature review from these papers: ' + titles.join(', ')
    }]
  }));
  
  var response = JSON.parse(xhr.responseText);
  Zotero.write(response.response);
}
