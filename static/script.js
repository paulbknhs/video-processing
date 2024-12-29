function uploadFile() {
  const formData = new FormData();
  const fileInput = document.querySelector('input[type="file"]');

  if (!fileInput.files.length) {
    document.getElementById("status").innerText = "Please select a file.";
    return;
  }

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
        document.getElementById("status").innerText = "Processing completed!";
        const downloadLink = document.createElement("a");
        downloadLink.href = data.download_url;
        downloadLink.innerText = "Download File";
        downloadLink.className = "download-button";
        downloadLink.download = ""; // Optional to prompt download
        document.getElementById("download-container").innerHTML = ""; // Clear previous links
        document.getElementById("download-container").appendChild(downloadLink);
      }
    })
    .catch((error) => {
      document.getElementById("status").innerText = "An error occurred.";
      console.error("Error uploading file:", error);
    });
}
