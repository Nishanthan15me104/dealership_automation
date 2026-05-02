from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import FileResponse
import zipfile
import io
import os
import uuid
from PIL import Image
from typing import List

# Import your existing engine functions and database handler
from src.application.creative_builder import apply_dealership_branding
from src.infrastructure.db_handler import get_dealerships

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
    
    # 2. Parse Dealers and Fetch Paths from Database
    # Convert string "1,2,3" to integer list [1, 2, 3]
    id_list = [int(x) for x in dealer_ids.split(",")]
    
    # Fetch all dealerships for this brand from your DB
    all_dealers = get_dealerships(brand_id)
    
    # Filter to only keep the dealerships the user selected
    selected_dealers = [d for d in all_dealers if d[0] in id_list]
    
    zip_filename = f"{uuid.uuid4()}.zip"
    zip_path = os.path.join(TEMP_DIR, zip_filename)
    
    with zipfile.ZipFile(zip_path, 'w') as zf:
        for dealer in selected_dealers:
            # Unpack the database row exactly like your old code did
            d_id = dealer[0]
            d_name = dealer[1]
            panel_path = dealer[2]
            logo_path = dealer[3]
            
            # 3. RUN THE ENGINE using the real paths
            result_img = apply_dealership_branding(
                bg_image=bg_image,
                panel_path=panel_path, 
                logo_path=logo_path if use_logo else None,
                output_size=(format_w, format_h)
            )
            
            # 4. Save to ZIP
            img_buffer = io.BytesIO()
            result_img.save(img_buffer, format="JPEG", quality=95)
            
            # Format the filename correctly
            filename = f"creative_{d_name.replace(' ', '_')}.jpg"
            zf.writestr(filename, img_buffer.getvalue())

    return FileResponse(zip_path, filename="bulk_creatives.zip", media_type="application/zip")