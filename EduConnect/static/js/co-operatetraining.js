function openVideo(videoUrl) {
    const videoPopup = document.getElementById("videoPopup");
    const popupVideo = document.getElementById("popupVideo");
  
    // Convert YouTube URL to embed URL
    const embedUrl = videoUrl.replace("youtu.be/", "www.youtube.com/embed/").replace("watch?v=", "embed/");
    
    // Set the iframe source
    popupVideo.src = embedUrl;
  
    // Show the popup
    videoPopup.style.display = "flex";
  }
  
  // Close the video popup
  function closeVideo() {
    const videoPopup = document.getElementById("videoPopup");
    const popupVideo = document.getElementById("popupVideo");
  
    // Hide the popup
    videoPopup.style.display = "none";
  
    // Stop the video
    popupVideo.src = "";
  }