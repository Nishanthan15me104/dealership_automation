from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import FileResponse
import zipfile
import io
import os
import uuid
from PIL import Image
from typing import List

# Import your existing engine functions
# from your_script import apply_dealership_branding 
from src.application.creative_builder import apply_dealership_branding

app = FastAPI(title="Creative Automation API")

# Temporary storage for bulk zips
TEMP_DIR = "temp_outputs"
os.makedirs(TEMP_DIR, exist_ok=True)

@app.post("/generate-bulk/")
async def generate_bulk(
    background: UploadFile = File(...),
    brand_id: int = Form(...),
    dealer_ids: str = Form(...), # Pass as comma-separated string: "1,2,3"
    format_w: int = Form(1080),
    format_h: int = Form(1080),
    use_logo: bool = Form(True)
):
    # 1. Load Background
    bg_bytes = await background.read()
    bg_image = Image.open(io.BytesIO(bg_bytes))
    
    # 2. Parse Dealers (In a real app, fetch these from your DB)
    id_list = dealer_ids.split(",")
    
    zip_filename = f"{uuid.uuid4()}.zip"
    zip_path = os.path.join(TEMP_DIR, zip_filename)
    
    with zipfile.ZipFile(zip_path, 'w') as zf:
        for d_id in id_list:
            # logic: fetch panel_path and logo_path from DB based on d_id
            # panel_path = db.get_panel(d_id)
            
            # 3. RUN THE ENGINE
            result_img = apply_dealership_branding(
                bg_image=bg_image,
                panel_path="path/to/panel.png", # Dynamic from DB
                logo_path="path/to/logo.png" if use_logo else None,
                output_size=(format_w, format_h)
            )
            
            # 4. Save to ZIP
            img_buffer = io.BytesIO()
            result_img.save(img_buffer, format="JPEG", quality=95)
            zf.writestr(f"creative_dealer_{d_id}.jpg", img_buffer.getvalue())

    return FileResponse(zip_path, filename="bulk_creatives.zip", media_type="application/zip")