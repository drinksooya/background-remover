import os
import io
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
from rembg import remove
from PIL import Image

app = FastAPI()

# 1. Enable CORS so your frontend can talk to your backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Setup Paths - This is the most important part!
# We need to reach OUT of the 'backend' folder to find the 'frontend' folder
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # points to /backend
ROOT_DIR = os.path.dirname(BASE_DIR)  # points to /background-remover (the project root)
FRONTEND_DIR = os.path.join(ROOT_DIR, "frontend")


# 3. Serve index.html at the root URL (https://background-remover-x6cw.onrender.com/)
@app.get("/")
async def read_index():
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"error": f"index.html not found at {index_path}. Check your folder structure!"}


# 4. Mount the frontend folder so styles.css and app.js can be loaded
# These will be found at /frontend/styles.css and /frontend/app.js
app.mount("/frontend", StaticFiles(directory=FRONTEND_DIR), name="frontend")


@app.get("/health")
def health():
    return {"status": "ok"}


# 5. Background Removal Logic
@app.post("/remove-bg")
async def remove_bg(file: UploadFile = File(...)):
    try:
        image_bytes = await file.read()
        input_image = Image.open(io.BytesIO(image_bytes))

        # This uses rembg to process the image
        output_image = remove(input_image)

        buffer = io.BytesIO()
        output_image.save(buffer, format="PNG")
        buffer.seek(0)

        return Response(content=buffer.getvalue(), media_type="image/png")
    except Exception as e:
        return {"error": str(e)}