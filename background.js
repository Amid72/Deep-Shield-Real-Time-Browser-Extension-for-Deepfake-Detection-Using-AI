chrome.runtime.onInstalled.addListener(() => {
  console.log("DeepShield extension installed.");
});

// Listen for messages from content.js
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === "storeMedia") {
    chrome.storage.local.set(
      { pageMedia: message.data },
      () => console.log("Stored media from page:", message.data)
    );
  }
});
