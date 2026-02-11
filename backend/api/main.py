from fastapi import FastAPI, UploadFile, File
import os
import uvicorn

app = FastAPI()


@app.get("/")
async def health_check():
    return {"status": "online", "message": "Background remover is ready"}


@app.post("/remove-bg")
async def remove_background(file: UploadFile = File(...)):
    from rembg import remove

    # Read the uploaded file bytes
    input_bytes = await file.read()

    # Process the image
    output_bytes = remove(input_bytes)

    # Return the result
    from fastapi.responses import Response
    return Response(content=output_bytes, media_type="image/png")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("api.main:app", host="0.0.0.0", port=port)