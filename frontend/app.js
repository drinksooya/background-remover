const imageInput = document.getElementById("imageInput");
const removeBtn = document.getElementById("removeBtn");
const resultImage = document.getElementById("resultImage");
const downloadLink = document.getElementById("downloadLink");

removeBtn.addEventListener("click", async () => {
  const file = imageInput.files[0];

  if (!file) {
    alert("Please select an image first!");
    return;
  }

  // 1. Give the user feedback that the app is working
  removeBtn.disabled = true;
  removeBtn.innerText = "Processing... (may take a moment)";

  const formData = new FormData();
  formData.append("file", file);

  try {
    // 2. Make the request to your Render Backend
    const response = await fetch("https://background-remover-x6cw.onrender.com/remove-bg", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
        // Try to get the specific error message from your Python 'except' block
        const errorDetail = await response.json();
        throw new Error(errorDetail.error || "Server error occurred");
    }

  } catch (error) {
    console.error(error);
    alert("Error: " + error.message);
  } finally {
    // 3. Reset the button
    removeBtn.disabled = false;
    removeBtn.innerText = "Remove Background";
  }
});