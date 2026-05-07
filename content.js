chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "getMedia") {
    let imagesSet = new Set();
    
    function makeAbsolute(urlStr) {
      if (!urlStr) return null;
      try {
        return new URL(urlStr, window.location.href).href;
      } catch(e) {
        return null;
      }
    }

    document.querySelectorAll("img").forEach(img => {
      let src = img.src || img.getAttribute("data-src");
      if (!src && img.getAttribute("srcset")) {
        src = img.getAttribute("srcset").split(',')[0].trim().split(' ')[0];
      }
      src = makeAbsolute(src);
      if (src && src.length > 5 && !src.startsWith("chrome-extension://")) {
        imagesSet.add(src);
      }
    });

    document.querySelectorAll("[style*='background-image']").forEach(el => {
      if (el.style && el.style.backgroundImage) {
        let match = el.style.backgroundImage.match(/url\(['"]?(.*?)['"]?\)/);
        if (match && match[1]) {
          let src = makeAbsolute(match[1]);
          if (src && src.length > 5 && !src.startsWith("chrome-extension://")) {
            imagesSet.add(src);
          }
        }
      }
    });

    let images = Array.from(imagesSet).map(src => ({
      type: "image",
      src: src
    }));

    // Collect all videos
    let videos = Array.from(document.getElementsByTagName("video"))
      .filter(video => video.currentSrc || video.src || video.getAttribute("data-src"))
      .map(video => ({
        type: "video",
        src: video.currentSrc || video.src || video.getAttribute("data-src")
      }));

    // Send media list directly back to popup
    sendResponse({ data: images.concat(videos) });
  }
  return true; // Keep the message channel open for async response if needed
});
