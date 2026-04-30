import os
import easyocr
import numpy as np
from PIL import Image

# Initialize OCR reader globally so it doesn't reload on every loop
reader = easyocr.Reader(['en'], gpu=False)

def apply_dealership_branding(bg_image, panel_path, logo_path=None, output_size=(1080, 1350)):
    """
    Combines the background, panel, and logo.
    Uses AI (OCR) to detect existing text and avoid overlapping the logo.
    """
    # 1. Resize Background cleanly
    bg = bg_image.convert("RGBA").resize(output_size, Image.Resampling.LANCZOS)
    
    # 2. AI Spatial Awareness (OCR)
    # We scan the image to find where text is. 
    np_img = np.array(bg.convert('RGB'))
    ocr_results = reader.readtext(np_img)
    
    # Default logo position: Top-Left
    logo_x, logo_y = 50, 50 
    
    for (bbox, text, prob) in ocr_results:
        y1 = bbox[0][1]
        x1 = bbox[0][0]
        # If OCR detects text in the top-left quadrant, shift our logo to the top-right!
        if y1 < (output_size[1] * 0.3) and x1 < (output_size[0] * 0.5):
            logo_x = output_size[0] - 250 # Shift right
            break 

    # 3. Paste Dealership Panel at the absolute bottom
    if os.path.exists(panel_path):
        panel = Image.open(panel_path).convert("RGBA")
        # Scale panel width to match background width
        p_ratio = output_size[0] / float(panel.size[0])
        p_height = int(float(panel.size[1]) * float(p_ratio))
        panel = panel.resize((output_size[0], p_height), Image.Resampling.LANCZOS)
        
        # Paste at bottom (Background Height - Panel Height)
        bg.paste(panel, (0, output_size[1] - p_height), panel)

    # 4. Paste Logo using AI-determined coordinates
    if logo_path and os.path.exists(logo_path):
        logo = Image.open(logo_path).convert("RGBA")
        # Ensure logo isn't massive
        logo.thumbnail((200, 200), Image.Resampling.LANCZOS)
        bg.paste(logo, (logo_x, logo_y), logo)

    return bg.convert("RGB") # Convert back to RGB for standard JPG saving