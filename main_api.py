import os
import io
import uuid
import zipfile
import logging
import asyncio
from typing import List
from PIL import Image

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.security.api_key import APIKeyHeader
from pydantic_settings import BaseSettings

# Import your existing engine functions and database handler
from src.application.creative_builder import apply_dealership_branding
from src.infrastructure.db_handler import get_dealerships

# --- 1. CONFIGURATION ---
class Settings(BaseSettings):
    app_name: str = "Dealership Automation API"
    api_version: str = "v1.0.0"
    api_key: str = "dev-secret-key-1234" # In production, this loads from a .env file
    temp_dir: str = "temp_outputs"
    
    class Config:
        env_file = ".env"

settings = Settings()
os.makedirs(settings.temp_dir, exist_ok=True)

# --- 2. LOGGING & MONITORING ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from prometheus_fastapi_instrumentator import Instrumentator
    HAS_PROMETHEUS = True
except ImportError:
    HAS_PROMETHEUS = False

# --- 3. APP INITIALIZATION & MIDDLEWARE ---
app = FastAPI(title=settings.app_name, version=settings.api_version)

# Crucial for allowing other web frontends (React, Angular) to talk to your API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if HAS_PROMETHEUS:
    instrumentator = Instrumentator().instrument(app)

@app.on_event("startup")
async def startup_event():
    logger.info(f"Starting {settings.app_name}...")
    if HAS_PROMETHEUS:
        instrumentator.expose(app, endpoint="/metrics", tags=["System"])

# --- 4. SECURITY (AuthN) ---
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def verify_api_key(api_key: str = Depends(api_key_header)):
    """Validates the incoming API key to prevent unauthorized batch generation."""
    if api_key != settings.api_key:
        logger.warning("Unauthorized generation attempt rejected.")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate API credentials"
        )
    return api_key

# --- 5. CPU-BOUND TASK OFFLOADING ---
def process_and_zip_images(bg_bytes: bytes, brand_id: int, id_list: List[int], format_w: int, format_h: int, use_logo: bool, zip_path: str):
    """
    Runs the heavy image processing sequentially. 
    Isolated here so it can be passed to a background thread.
    """
    bg_image = Image.open(io.BytesIO(bg_bytes))
    
    all_dealers = get_dealerships(brand_id)
    selected_dealers = [d for d in all_dealers if d[0] in id_list]
    
    if not selected_dealers:
        raise ValueError("No matching dealerships found in the database.")

    with zipfile.ZipFile(zip_path, 'w') as zf:
        for dealer in selected_dealers:
            d_id, d_name, panel_path, logo_path = dealer[0], dealer[1], dealer[2], dealer[3]
            
            # Run the AI Image Engine
            result_img = apply_dealership_branding(
                bg_image=bg_image,
                panel_path=panel_path, 
                logo_path=logo_path if use_logo else None,
                output_size=(format_w, format_h)
            )
            
            img_buffer = io.BytesIO()
            result_img.save(img_buffer, format="JPEG", quality=95)
            
            filename = f"creative_{d_name.replace(' ', '_')}.jpg"
            zf.writestr(filename, img_buffer.getvalue())

# --- 6. ROUTES ---
@app.get("/health", tags=["System"])
def health_check():
    """Endpoint for load balancers to verify system stability."""
    return {
        "status": "active", 
        "monitoring_active": HAS_PROMETHEUS,
        "temp_storage_ok": os.path.exists(settings.temp_dir)
    }

@app.post("/generate-bulk/", tags=["Generation"])
async def generate_bulk(
    background: UploadFile = File(...),
    brand_id: int = Form(...),
    dealer_ids: str = Form(...),
    format_w: int = Form(1080),
    format_h: int = Form(1080),
    use_logo: bool = Form(True),
    api_key: str = Depends(verify_api_key) # Ensures endpoint is protected
):
    try:
        # Read file asynchronously
        bg_bytes = await background.read()
        id_list = [int(x) for x in dealer_ids.split(",")]
        
        zip_filename = f"{uuid.uuid4()}.zip"
        zip_path = os.path.join(settings.temp_dir, zip_filename)
        
        # OFFLOAD CPU WORK: Send the heavy processing to a separate thread 
        # so the API remains responsive to other health checks and requests.
        await asyncio.to_thread(
            process_and_zip_images,
            bg_bytes, brand_id, id_list, format_w, format_h, use_logo, zip_path
        )

        return FileResponse(zip_path, filename="bulk_creatives.zip", media_type="application/zip")
        
    except ValueError as ve:
        logger.error(f"Validation Error: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Generation Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error during image generation.")