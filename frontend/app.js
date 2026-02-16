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
  resultImage.style.opacity = "0.5"; // Dim the old image while loading

  const formData = new FormData();
  formData.append("file", file);

  try {
    // 2. Request to your Render Backend
    const response = await fetch("https://background-remover-x6cw.onrender.com/remove-bg", {
      method: "POST",
      body: formData,
    });

    // 3. Specific Error Handling
    if (!response.ok) {
        const errorData = await response.json();
        // This will tell you if the API key is invalid or out of credits
        throw new Error(errorData.error || "Server error occurred");
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
    downloadLink.style.display = "block"; // Show the link now that it's ready

  } catch (error) {
    console.error("Full Error Context:", error);
    alert("Error: " + error.message);
  } finally {
    // 5. Reset the button
    removeBtn.disabled = false;
    removeBtn.innerText = "Remove Background";
  }
});