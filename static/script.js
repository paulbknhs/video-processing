function uploadFile() {
  const formData = new FormData();
  const fileInput = document.querySelector('input[type="file"]');
  formData.append("file", fileInput.files[0]);

  const statusElement = document.getElementById("status");
  const progressBar = document.getElementById("progress-bar");
  const downloadContainer = document.getElementById("download-container");

  fetch("/upload", {
    method: "POST",
    body: formData,
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.error) {
        statusElement.innerText = data.error;
      } else {
        statusElement.innerText = "Verarbeitung läuft...";
        const downloadUrl = data.download_url;

        // Start polling for progress updates
        const intervalId = setInterval(() => {
          fetch("/processing-progress")
            .then((res) => res.json())
            .then((progressData) => {
              const progress = progressData.progress;
              progressBar.style.width = `${progress}%`;
              progressBar.innerText = `${progress}%`;

              if (progress >= 100) {
                clearInterval(intervalId);
                statusElement.innerText = "Verarbeitung abgeschlossen!";
                const downloadLink = document.createElement("a");
                downloadLink.href = downloadUrl;
                downloadLink.innerText = "Datei herunterladen";
                downloadLink.className = "download-button";
                downloadLink.download = ""; // Optional to prompt download
                downloadContainer.innerHTML = ""; // Clear previous links
                downloadContainer.appendChild(downloadLink);
              }
            });
        }, 1000);
      }
    })
    .catch((error) => {
      statusElement.innerText = "Es ist ein Fehler aufgetreten.";
      console.error("Error uploading file:", error);
    });
}
