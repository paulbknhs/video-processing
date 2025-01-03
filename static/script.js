function uploadFile() {
  const formData = new FormData();
  const fileInput = document.querySelector('input[type="file"]');
  const file = fileInput.files[0];
  formData.append("file", file);

  const statusElement = document.getElementById("status");
  const progressBar = document.getElementById("progress-bar");
  const downloadContainer = document.getElementById("download-container");

  // Reset UI
  statusElement.innerText = "Datei wird hochgeladen...";
  progressBar.style.width = "0%";
  progressBar.innerText = "0%";
  downloadContainer.innerHTML = "";

  const xhr = new XMLHttpRequest();

  // Upload Progress Handler
  let lastLoaded = 0;
  let lastTime = Date.now();
  let uploadSpeed = 0;

  xhr.upload.addEventListener("progress", (event) => {
    if (event.lengthComputable) {
      const currentTime = Date.now();
      const timeDiff = (currentTime - lastTime) / 1000; // in Sekunden
      const loadedDiff = event.loaded - lastLoaded;

      // Berechne Upload-Geschwindigkeit (Bytes pro Sekunde)
      if (timeDiff > 0) {
        uploadSpeed = loadedDiff / timeDiff;
      }

      // Aktualisiere die Werte für die nächste Berechnung
      lastLoaded = event.loaded;
      lastTime = currentTime;

      const uploadProgress = Math.round((event.loaded / event.total) * 100);

      // Schätze die verbleibende Zeit
      const remainingBytes = event.total - event.loaded;
      const remainingSeconds =
        uploadSpeed > 0 ? remainingBytes / uploadSpeed : 0;
      const remainingTime = Math.ceil(remainingSeconds);

      progressBar.style.width = `${uploadProgress}%`;
      progressBar.innerText = `Upload: ${uploadProgress}%`;
      statusElement.innerText = `Datei wird hochgeladen... (etwa ${remainingTime} Sekunden verbleibend`;
    }
  });

  xhr.onload = function () {
    if (xhr.status === 200) {
      const data = JSON.parse(xhr.responseText);
      statusElement.innerText = "Datei wird konvertiert...";
      const downloadUrl = data.download_url;

      // Reset progress bar for processing
      progressBar.style.width = "0%";
      progressBar.innerText = "Konvertierung: 0%";

      const intervalId = setInterval(() => {
        fetch("/processing-progress")
          .then((res) => res.json())
          .then((progressData) => {
            const progress = progressData.progress;
            progressBar.style.width = `${progress}%`;
            progressBar.innerText = `Konvertierung: ${progress}%`;

            if (progress >= 100) {
              clearInterval(intervalId);
              statusElement.innerText = "Verarbeitung abgeschlossen!";
              const downloadLink = document.createElement("a");
              downloadLink.href = downloadUrl;
              downloadLink.innerText = "Datei herunterladen";
              downloadLink.className = "download-button";
              downloadLink.download = "";
              downloadContainer.innerHTML = "";
              downloadContainer.appendChild(downloadLink);

              // Datei-Input zurücksetzen
              fileInput.value = "";

              // Seite neu laden um die neue Datei in der Liste anzuzeigen
              setTimeout(() => {
                window.location.reload();
              }, 1000);
            }
          });
      }, 1000);
    } else {
      const data = JSON.parse(xhr.responseText);
      statusElement.innerText = data.error || "Es ist ein Fehler aufgetreten.";
    }
  };

  xhr.onerror = function () {
    statusElement.innerText = "Es ist ein Fehler aufgetreten.";
    console.error("Error uploading file:", xhr.statusText);
  };

  xhr.open("POST", "/upload", true);
  xhr.send(formData);
}
