import os
import io
import gc  # Garbage collector to force memory release
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
from rembg import remove, new_session
from PIL import Image

app = FastAPI()

# Initialize the tiny model session globally
# u2netp is ~4MB on disk vs u2net's ~176MB
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
    input_image = None
    output_image = None
    try:
        image_bytes = await file.read()
        input_image = Image.open(io.BytesIO(image_bytes))

        # 1. AGGRESSIVE RESIZE
        # 600px is the "Safe Zone" for 512MB RAM
        if max(input_image.size) > 600:
            input_image.thumbnail((600, 600), Image.Resampling.LANCZOS)

        # 2. REMOVE BACKGROUND
        output_image = remove(input_image, session=session)

        # 3. CONVERT TO BYTES
        buffer = io.BytesIO()
        output_image.save(buffer, format="PNG")
        result = buffer.getvalue()

        return Response(content=result, media_type="image/png")

    except Exception as e:
        return {"error": str(e)}
    finally:
        # 4. EXPLICIT CLEANUP
        # This tells Python: "I am done with these huge objects, get them out of RAM!"
        del input_image
        del output_image
        gc.collect()


@app.get("/health")
def health():
    return {"status": "ok"}