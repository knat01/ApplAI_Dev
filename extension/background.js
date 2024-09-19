chrome.runtime.onInstalled.addListener(function() {
  console.log("AI Job Application Assistant installed");
});

chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
  if (request.action === "extractJobDetails") {
    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
      chrome.tabs.sendMessage(tabs[0].id, {action: "getJobDetails"}, function(response) {
        sendResponse(response);
      });
    });
    return true;
  }
});
