import os
import io
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
from rembg import remove, new_session  # Added new_session
from PIL import Image

app = FastAPI()

session = new_session("u2netp")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")


@app.get("/")
async def read_index():
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"error": "Frontend not found"}


if os.path.exists(FRONTEND_DIR):
    app.mount("/frontend", StaticFiles(directory=FRONTEND_DIR), name="frontend")


@app.post("/remove-bg")
async def remove_bg(file: UploadFile = File(...)):
    try:
        image_bytes = await file.read()
        input_image = Image.open(io.BytesIO(image_bytes))

        # --- OPTIMIZATION: Resize if the image is too large ---
        max_size = 800
        if max(input_image.size) > max_size:
            input_image.thumbnail((max_size, max_size), Image.LANCZOS)

        # Use the lightweight session we created earlier
        output_image = remove(input_image, session=session)

        buffer = io.BytesIO()
        output_image.save(buffer, format="PNG")

        # Explicitly clear internal buffers to free RAM immediately
        image_bytes = None

        return Response(content=buffer.getvalue(), media_type="image/png")
    except Exception as e:
        return {"error": str(e)}


@app.get("/health")
def health():
    return {"status": "ok"}