from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from rembg import remove, new_session
import uvicorn
import asyncio
import io

app = FastAPI()

# Enable CORS so your HTML file can communicate with this server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pre-load the ML model into memory once at startup for maximum speed
# 'isnet-general-use' is the best balance of speed and edge accuracy
session = new_session("isnet-general-use")

def process_image(file_bytes: bytes) -> bytes:
    """Internal function to handle the heavy CPU lifting."""
    return remove(
        file_bytes,
        session=session,
        alpha_matting=True,
        alpha_matting_foreground_threshold=240,
        alpha_matting_background_threshold=10,
        alpha_matting_erode_size=10
    )

@app.post("/remove-bg")
async def remove_background(file: UploadFile = File(...)):
    try:
        # Read file into memory
        input_data = await file.read()
        
        # Run the removal in a separate thread so multiple requests can run in parallel
        output_data = await asyncio.to_thread(process_image, input_data)
        
        return Response(content=output_data, media_type="image/png")
    except Exception as e:
        print(f"Error processing image: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Standard FastAPI port
    uvicorn.run(app, host="127.0.0.1", port=8000)