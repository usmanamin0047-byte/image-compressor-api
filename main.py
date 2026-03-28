import io
from fastapi import FastAPI, UploadFile, File, Response
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image, ImageOps

app = FastAPI(title="Image Compressor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/compress")
async def compress_image(file: UploadFile = File(...), quality: int = 85):
    contents = await file.read()
    img = Image.open(io.BytesIO(contents))
    
    # Convert to RGB if it has alpha (for better compression)
    if img.mode in ('RGBA', 'LA', 'P'):
        img = img.convert('RGB')
    
    bio = io.BytesIO()
    
    if img.format in ['JPEG', 'JPG']:
        # Lossy compression for JPEG
        img.save(bio, format="JPEG", quality=quality, optimize=True)
        ext = "jpg"
    else:
        # PNG ke liye strong optimization
        img = ImageOps.optimize(img)
        img.save(bio, format="PNG", optimize=True, compress_level=9)
        ext = "png"
    
    bio.seek(0)
    
    filename = file.filename.rsplit('.', 1)[0] + f"_compressed.{ext}"
    
    return Response(
        content=bio.getvalue(),
        media_type=f"image/{ext}",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@app.get("/")
async def root():
    return {"message": "Image Compressor API Ready! Use /compress endpoint"}
