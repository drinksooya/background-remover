import os
import io
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
from rembg import remove
from PIL import Image

app = FastAPI()

# 1. Enable CORS so your browser doesn't block the request
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Setup Paths
# This looks for the 'frontend' folder one level up from the 'api' folder
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")


# 3. Serve the index.html at the root URL (https://your-app.onrender.com/)
@app.get("/")
async def read_index():
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    return FileResponse(index_path)


# 4. Mount the frontend folder to serve styles.css and app.js
# These will be accessible at /frontend/styles.css etc.
app.mount("/frontend", StaticFiles(directory=FRONTEND_DIR), name="frontend")


@app.get("/health")
def health():
    return {"status": "ok"}


# 5. The Background Removal Logic
@app.post("/remove-bg")
async def remove_bg(file: UploadFile = File(...)):
    try:
        # Read uploaded file
        image_bytes = await file.read()
        input_image = Image.open(io.BytesIO(image_bytes))

        # Remove background
        output_image = remove(input_image)

        # Save result to a byte stream
        buffer = io.BytesIO()
        output_image.save(buffer, format="PNG")
        buffer.seek(0)

        return Response(content=buffer.getvalue(), media_type="image/png")
    except Exception as e:
        return {"error": str(e)}