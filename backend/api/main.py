import os
import io
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
from rembg import remove
from PIL import Image

app = FastAPI()

# 1. CORS Middleware: Crucial for the frontend to talk to the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Path Setup: Finds the frontend folder relative to this file
# BASE_DIR is 'background-remover/', FRONTEND_DIR is 'background-remover/frontend'
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")


# 3. Serve index.html: Fixes the {"detail":"Not Found"} error
@app.get("/")
async def read_index():
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    return FileResponse(index_path)


# 4. Static Files: Allows the browser to load styles.css and app.js
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

        # This is where onnxruntime is used internally by rembg
        output_image = remove(input_image)

        buffer = io.BytesIO()
        output_image.save(buffer, format="PNG")
        buffer.seek(0)

        return Response(content=buffer.getvalue(), media_type="image/png")
    except Exception as e:
        return {"error": str(e)}