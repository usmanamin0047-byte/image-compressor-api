import io
from fastapi import FastAPI, UploadFile, File, Response
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
async def compress_image(file: UploadFile = File(...), quality: int = 85):
    contents = await file.read()
    img = Image.open(io.BytesIO(contents))
    
    # PNG ke liye extra optimization
    if img.format == "PNG":
        # Color reduce (lossy feel deta hai lekin quality achhi rakhta hai)
        if img.mode in ("RGBA", "RGB"):
            img = img.convert("P", palette=Image.ADAPTIVE, colors=256)
    
    # Output buffer
    bio = io.BytesIO()
    
    if img.format == "JPEG" or img.format == "JPG":
        img.save(bio, format="JPEG", quality=quality, optimize=True)
        output_format = "JPEG"
        filename = file.filename.rsplit('.', 1)[0] + "_compressed.jpg"
    else:
        # PNG ke liye best optimization
        img.save(bio, format="PNG", optimize=True, compress_level=9)
        output_format = "PNG"
        filename = file.filename.rsplit('.', 1)[0] + "_compressed.png"
    
    bio.seek(0)
    
    return Response(
        content=bio.getvalue(),
        media_type=f"image/{output_format.lower()}",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@app.get("/")
async def root():
    return {"message": "Image Compressor API Ready! /compress endpoint use karo."}
