import os
import io
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
from rembg import remove
from PIL import Image

app = FastAPI()

# 1. CORS is mandatory for your app.js to work
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Path Logic: This finds 'frontend' relative to 'backend/api/main.py'
# We go up two levels: main.py -> api -> backend -> project_root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

# 3. ROOT ROUTE: This fixes the {"detail":"Not Found"} error
@app.get("/")
async def read_index():
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    # If the file exists, serve it. If not, tell us where the server is looking.
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {
        "error": "Frontend not found",
        "looking_at": index_path,
        "current_dir": os.getcwd()
    }

# 4. Mount the frontend folder for CSS/JS
if os.path.exists(FRONTEND_DIR):
    app.mount("/frontend", StaticFiles(directory=FRONTEND_DIR), name="frontend")

# 5. Background Removal Logic
@app.post("/remove-bg")
async def remove_bg(file: UploadFile = File(...)):
    try:
        image_bytes = await file.read()
        input_image = Image.open(io.BytesIO(image_bytes))
        output_image = remove(input_image)
        buffer = io.BytesIO()
        output_image.save(buffer, format="PNG")
        buffer.seek(0)
        return Response(content=buffer.getvalue(), media_type="image/png")
    except Exception as e:
        return {"error": str(e)}

@app.get("/health")
def health():
    return {"status": "ok"}