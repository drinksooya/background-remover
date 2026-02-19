import os
import io
import requests
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response

app = FastAPI()

origins = [
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "https://drinksooya.github.io",
]

production_url = os.getenv("RENDER_EXTERNAL_URL")
if production_url:
    origins.append(production_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

REMOVE_BG_API_KEY = os.getenv("REMOVE_BG_API_KEY")

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
    return FileResponse(index_path) if os.path.exists(index_path) else {"error": "Frontend not found"}

if os.path.exists(FRONTEND_DIR):
    app.mount("/frontend", StaticFiles(directory=FRONTEND_DIR), name="frontend")

@app.post("/remove-bg")
async def remove_bg(file: UploadFile = File(...)):
    try:
        # Read the uploaded file
        image_bytes = await file.read()

        # Forward the image to remove.bg API
        response = requests.post(
            'https://api.remove.bg/v1.0/removebg',
            files={'image_file': image_bytes},
            data={'size': 'auto'}, # 'auto' is free for previews
            headers={'X-Api-Key': REMOVE_BG_API_KEY},
        )

        if response.status_code == requests.codes.ok:
            # Send the resulting PNG back to your frontend
            return Response(content=response.content, media_type="image/png")
        else:
            return {"error": f"API Error {response.status_code}: {response.text}"}

    except Exception as e:
        return {"error": str(e)}

@app.get("/health")
def health():
    return {"status": "ok"}