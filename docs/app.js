const imageInput = document.getElementById("imageInput");
const removeBtn = document.getElementById("removeBtn");
const resultImage = document.getElementById("resultImage");
const downloadLink = document.getElementById("downloadLink");

// Initially hide the download link until we have a result
downloadLink.style.display = "none";

removeBtn.addEventListener("click", async () => {
  const file = imageInput.files[0];

  if (!file) {
    alert("Please select an image first!");
    return;
  }

  // 1. UI Feedback
  removeBtn.disabled = true;
  removeBtn.innerText = "Processing with AI...";
  resultImage.style.opacity = "0.5";

  const formData = new FormData();
  formData.append("file", file);

  try {
    // 2. Request to your Render Backend
    // Added 'mode: cors' to ensure the browser handles the cross-origin request correctly
    const response = await fetch("https://background-remover-x6cw.onrender.com/remove-bg", {
      method: "POST",
      body: formData,
      mode: "cors"
    });

    // 3. Specific Error Handling
    if (!response.ok) {
        // If the server sends a JSON error message, we show it.
        // Otherwise, we throw a generic error.
        let errorMessage = "Server error occurred";
        try {
            const errorData = await response.json();
            errorMessage = errorData.error || errorMessage;
        } catch (e) {
            // If response isn't JSON (like a 504 Gateway Timeout while Render wakes up)
            errorMessage = `Status ${response.status}: Server is likely waking up. Please try again in 30 seconds.`;
        }
        throw new Error(errorMessage);
    }

    // 4. Handle the successful image blob
    const blob = await response.blob();
    const imageUrl = URL.createObjectURL(blob);

    // Update the UI
    resultImage.src = imageUrl;
    resultImage.style.opacity = "1";

    // Set up the Download Link
    downloadLink.href = imageUrl;
    downloadLink.download = "removed-background.png";
    downloadLink.innerText = "Download your result!";
    downloadLink.style.display = "block";

  } catch (error) {
    console.error("Full Error Context:", error);
    alert("Error: " + error.message);
  } finally {
    // 5. Reset the button
    removeBtn.disabled = false;
    removeBtn.innerText = "Remove Background";
  }
});