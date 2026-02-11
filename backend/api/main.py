from fastapi import FastAPI, UploadFile, File
from rembg import remove
import io
import os
import uvicorn

app = FastAPI()


@app.post("/remove-bg")
async def remove_background(file: UploadFile = File(...)):
    # Read the uploaded file bytes
    input_bytes = await file.read()

    # Process the image
    output_bytes = remove(input_bytes)

    # Return the result as a streaming response or bytes
    from fastapi.responses import Response
    return Response(content=output_bytes, media_type="image/png")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("api.main:app", host="0.0.0.0", port=port)