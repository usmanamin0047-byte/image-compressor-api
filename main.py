import io
from fastapi import FastAPI, UploadFile, File, Response, Query
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image

app = FastAPI(title="Image Compressor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/compress")
async def compress_image(
    file: UploadFile = File(...), 
    quality: int = Query(85, ge=50, le=95)
):
    try:
        contents = await file.read()
        img = Image.open(io.BytesIO(contents))
        
        # Sab images ko RGB mein convert karo (safest for compression)
        if img.mode != "RGB":
            img = img.convert("RGB")
        
        bio = io.BytesIO()
        
        if img.format in ["JPEG", "JPG"]:
            img.save(bio, format="JPEG", quality=quality, optimize=True)
            ext = "jpg"
            filename = file.filename.rsplit('.', 1)[0] + "_compressed.jpg"
        else:
            # PNG ke liye simple but effective compression
            img.save(bio, format="PNG", optimize=True, compress_level=9)
            ext = "png"
            filename = file.filename.rsplit('.', 1)[0] + "_compressed.png"
        
        bio.seek(0)
        
        return Response(
            content=bio.getvalue(),
            media_type=f"image/{ext}",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        return Response(
            content=f"Error: {str(e)}",
            status_code=500,
            media_type="text/plain"
        )

@app.get("/")
async def root():
    return {"message": "Image Compressor API Ready! Use /compress endpoint"}
