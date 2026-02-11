from fastapi import FastAPI, UploadFile, File
from fastapi.responses import Response
import os

app = FastAPI()


@app.get("/")
async def health():
    return {"status": "ok"}


@app.post("/remove-bg")
async def remove_background(file: UploadFile = File(...)):
    # Import inside the function to save memory on boot
    from rembg import remove

    input_bytes = await file.read()
    output_bytes = remove(input_bytes)

    return Response(content=output_bytes, media_type="image/png")