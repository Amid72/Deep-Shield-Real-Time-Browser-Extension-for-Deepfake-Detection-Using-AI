async function analyzeMedia(media) {
  let url = media.type === "image"
    ? "http://127.0.0.1:8000/analyze/image"
    : "http://127.0.0.1:8000/analyze/video";

  try {
    let response;
    try {
        response = await fetch(media.src);
    } catch(e) {
        throw new Error("Failed to download media: " + e.message);
    }
    
    let blob = await response.blob();
    let formData = new FormData();
    formData.append("file", blob, media.type + (media.type === 'video' ? '.mp4' : '.jpg'));

    let res;
    try {
        res = await fetch(url, {
          method: "POST",
          body: formData
        });
    } catch(e) {
        throw new Error("Backend server not running (127.0.0.1:8000 expected)");
    }
    
    if (!res.ok) {
        throw new Error("Backend returned status " + res.status);
    }
    
    let result = await res.json();
    return result;
  } catch (err) {
    console.error("Error analyzing media:", err);
    return { result: "ERROR", confidence: 0, error: err.message };
  }
}

document.addEventListener("DOMContentLoaded", async () => {
  const resultDiv = document.getElementById("result");

  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    chrome.tabs.sendMessage(tabs[0].id, { action: "getMedia" }, async (response) => {
      if (chrome.runtime.lastError) {
        resultDiv.innerHTML = "<div class='no-media'>Extension just installed or updated. Please <strong>refresh the page</strong> (F5) and try again!</div>";
        return;
      }
      if (!response || !response.data || response.data.length === 0) {
        resultDiv.innerHTML = "<div class='no-media'>No supported media found on this page.</div>";
        return;
      }
      
      let pageMedia = response.data;

      resultDiv.innerHTML = `
        <div class="loader-container">
          <div class="spinner"></div>
          <div>Scanning ${pageMedia.length} Media items...</div>
        </div>
      `;

      // Clear the loading text once we start displaying results
      resultDiv.innerHTML = '<div id="results-list"></div>';
      const resultsList = document.getElementById("results-list");

      for (let media of pageMedia) {
        let scanResult = await analyzeMedia(media);

        let isFake = scanResult.result === "FAKE";
        let isError = scanResult.result === "ERROR" || !!scanResult.error;
        
        let typeText = media.type === "image" ? "Image" : "Video";
        let status = isError ? "⚠️ ERROR: " + (scanResult.error || "Unknown error") : (isFake ? `⚠️ FAKE ${typeText}` : `✅ REAL ${typeText}`);
        let badgeClass = isError ? "fake-badge" : (isFake ? "fake-badge" : "safe-badge");
        let fillStyle = isFake ? "background: var(--fake-gradient);" : "background: var(--safe-gradient);";
        let confidencePct = Math.round(scanResult.confidence * 100) || 0;

        let mediaElement = "";
        if (media.type === "image") {
          mediaElement = `<img src="${media.src}" />`;
        } else if (media.type === "video") {
          mediaElement = `<video src="${media.src}" controls muted></video>`;
        }

        resultsList.insertAdjacentHTML('beforeend', `
          <div class="media-block">
            ${mediaElement}
            <div class="status-container">
              <div class="status-badge ${badgeClass}">${status}</div>
              <div class="confidence">${confidencePct}% Confidence</div>
            </div>
            ${!isError ? `
            <div class="confidence-bar-bg">
              <div class="confidence-fill" style="width: ${confidencePct}%; ${fillStyle}"></div>
            </div>` : ''}
          </div>
        `);
      }
    });
  });
});
