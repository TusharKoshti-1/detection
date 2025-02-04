// Get references to the hidden capture video element and the processed image element.
const captureVideo = document.getElementById('captureVideo'); // hidden video element
const processedImg = document.getElementById('processedImg'); // image element for processed frames

// Set up WebSocket using the secure protocol as before.
const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const ws = new WebSocket(protocol + '//' + window.location.host + '/ws');

// Access the user's camera.
navigator.mediaDevices.getUserMedia({ video: true })
  .then(function(stream) {
    captureVideo.srcObject = stream;
    captureVideo.play();
    // Capture frames every 300ms.
    setInterval(() => {
      const canvas = document.createElement('canvas');
      // Set a lower resolution (e.g., 320x240).
      canvas.width = 240;
      canvas.height = 180;
      const context = canvas.getContext('2d');
      // Draw the video frame onto the canvas (scale the video to our lower resolution).
      context.drawImage(captureVideo, 0, 0, canvas.width, canvas.height);
      // Convert the canvas to a JPEG blob with quality 0.7.
      canvas.toBlob(blob => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.send(blob);
        }
      }, 'image/jpeg', 0.6);
    }, 400); // capture every 300ms
  })
  .catch(function(error) {
    console.error("Error accessing the camera:", error);
  });

// When a processed frame is received from the server, display it.
ws.onmessage = async (event) => {
  if (event.data instanceof Blob) {
    const imgURL = URL.createObjectURL(event.data);
    processedImg.src = imgURL;
  }
};

ws.onclose = () => {
  console.log('WebSocket disconnected. Reconnecting...');
  setTimeout(() => location.reload(), 1000);
};
