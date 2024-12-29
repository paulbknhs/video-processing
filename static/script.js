function uploadFile() {
  const formData = new FormData();
  const fileInput = document.querySelector('input[type="file"]');
  formData.append("file", fileInput.files[0]);

  fetch("/upload", {
    method: "POST",
    body: formData,
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.error) {
        document.getElementById("status").innerText = data.error;
      } else {
        document.getElementById("status").innerText =
          "Verarbeitung abgeschlossen!";
        const downloadLink = document.createElement("a");
        downloadLink.href = data.download_url;
        downloadLink.innerText = "Datei herunterladen";
        downloadLink.className = "download-button";
        downloadLink.download = ""; // Optional to prompt download
        document.getElementById("download-container").innerHTML = ""; // Clear previous links
        document.getElementById("download-container").appendChild(downloadLink);
      }
    })
    .catch((error) => {
      document.getElementById("status").innerText =
        "Es ist ein Fehler aufgetreten.";
      console.error("Error uploading file:", error);
    });
}
