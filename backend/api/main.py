from fastapi import FastAPI, UploadFile, File
import os
import uvicorn

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Background Remover API is Running"}


@app.post("/remove-bg")
async def remove_background(file: UploadFile = File(...)):
    from rembg import remove
    from fastapi.responses import Response

    input_bytes = await file.read()
    output_bytes = remove(input_bytes)

    return Response(content=output_bytes, media_type="image/png")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("api.main:app", host="0.0.0.0", port=port)