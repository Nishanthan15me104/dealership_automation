import os
import easyocr
import numpy as np
from PIL import Image, ImageStat

# Initialize OCR
reader = easyocr.Reader(['en'], gpu=False)

def find_best_logo_position(bg_w, bg_h, logo_w, logo_h, ocr_results):
    """
    Determines an optimal (x, y) coordinate for logo placement by checking candidate 
    locations against detected text regions to prevent overlap.

    Args:
        bg_w (int): Width of the background image.
        bg_h (int): Height of the background image.
        logo_w (int): Width of the logo to be placed.
        logo_h (int): Height of the logo to be placed.
        ocr_results (list): Output from easyocr.Reader.readtext() containing 
                           bounding boxes and detected text.

    Returns:
        tuple: (x, y) coordinates for the top-left corner of the logo.
    """
    margin = 40
    candidates = [(margin, margin), (bg_w - logo_w - margin, margin), ((bg_w // 2) - (logo_w // 2), margin)]
    buffer = 10
    text_boxes = []
    for result in ocr_results:
        bbox = result[0]
        xs = [pt[0] for pt in bbox]; ys = [pt[1] for pt in bbox]
        if min(ys) < (bg_h * 0.4):
            text_boxes.append((min(xs) - buffer, min(ys) - buffer, max(xs) + buffer, max(ys) + buffer))

    for cx, cy in candidates:
        logo_box = (cx, cy, cx + logo_w, cy + logo_h)
        if all(not (logo_box[0] > tb[2] or logo_box[2] < tb[0] or logo_box[1] > tb[3] or logo_box[3] < tb[1]) for tb in text_boxes):
            return (cx, cy)
    return candidates[1]

def collapse_white_gap(image, sensitivity=250):
    """
        Scans an image vertically to detect and remove large horizontal bands of 
        near-white pixels (gaps) often found in AI-generated backgrounds.

        Args:
            image (PIL.Image): The combined image containing the background and panel.
            sensitivity (int): Brightness threshold (0-255). Rows with an average 
                            brightness above this are considered 'white'.

        Returns:
            PIL.Image: A new image with the detected gap 'collapsed' (removed).
        """
    img_gray = image.convert("L")
    pixels = np.array(img_gray)
    h, w = pixels.shape
    
    # Calculate row brightness. 255 is pure white. 
    # AI noise usually sits around 250-254.
    row_means = np.mean(pixels, axis=1)
    is_white = row_means >= sensitivity 

    # Find where the top content ends and the panel begins
    content_rows = np.where(~is_white)[0]
    if len(content_rows) < 2: return image

    # Find the biggest jump in row indices (this is our gap)
    gaps = np.diff(content_rows)
    if len(gaps) == 0: return image
    
    max_gap_idx = np.argmax(gaps)
    
    if gaps[max_gap_idx] > 30: # If gap is bigger than 30px
        top_end = content_rows[max_gap_idx] + 10
        bottom_start = content_rows[max_gap_idx + 1] - 10
        
        top_part = image.crop((0, 0, w, top_end))
        bottom_part = image.crop((0, bottom_start, w, h))
        
        final = Image.new("RGBA", (w, top_part.height + bottom_part.height))
        final.paste(top_part, (0, 0))
        final.paste(bottom_part, (0, top_part.height))
        return final
    return image

def is_already_branded(ocr_results, bg_h):
    """
    Analyzes OCR detections in the upper region of an image to identify 
    existing manufacturer or dealership branding.

    Args:
        ocr_results (list): The list of detections from EasyOCR.
        bg_h (int): Total height of the background image.

    Returns:
        bool: True if a known brand keyword is detected in the top 30% of the image, 
              False otherwise.
    """
    # Add any other brands your dealerships work with
    brand_keywords = [
        'volkswagen', 'vw', 'tata', 'skoda', 'kia', 
        'hyundai', 'maruti', 'suzuki', 'mahindra', 'honda', 'toyota'
    ]

    for result in ocr_results:
        bbox = result[0]
        text = str(result[1]).lower()
        ys = [pt[1] for pt in bbox]
        
        # Only check the header area (top 30% of the image)
        if min(ys) < (bg_h * 0.3):
            # If a brand keyword is in the detected text, it's already branded
            if any(brand in text for brand in brand_keywords):
                return True
                
    return False

def apply_dealership_branding(bg_image, panel_path, logo_path=None, output_size=(1080, 1080)):
    """
    Coordinates the full image processing pipeline: scaling, OCR analysis, 
    footer panel attachment, white-gap removal, and intelligent logo placement.

    Args:
        bg_image (PIL.Image): The raw background car image.
        panel_path (str): File path to the dealership footer panel image.
        logo_path (str, optional): File path to the dealership logo.
        output_size (tuple): The desired (width, height) for the final output.

    Returns:
        PIL.Image: The fully processed and branded image in RGB format.
    """
    # 1. Scale
    target_w = output_size[0]
    w_ratio = target_w / float(bg_image.size[0])
    target_h = int(float(bg_image.size[1]) * w_ratio)
    bg = bg_image.convert("RGBA").resize((target_w, target_h), Image.Resampling.LANCZOS)
    
    # 2. OCR
    ocr_results = reader.readtext(np.array(bg.convert('RGB')))

    # 3. Panel
    panel_h = 0
    panel = None
    if os.path.exists(panel_path):
        panel = Image.open(panel_path).convert("RGBA")
        p_ratio = target_w / float(panel.size[0])
        panel_h = int(float(panel.size[1]) * p_ratio)
        panel = panel.resize((target_w, panel_h), Image.Resampling.LANCZOS)

    # 4. Merge
    combined = Image.new("RGBA", (target_w, target_h + panel_h), (255, 255, 255, 255))
    combined.paste(bg, (0, 0), bg)
    if panel: combined.paste(panel, (0, target_h), panel)

    # 5. Fix Gap
    final_img = collapse_white_gap(combined)

    # 6. LOGO PLACEMENT (With Duplicate Check)
    if logo_path and os.path.exists(logo_path):
        
        # --- NEW CHECK: Do not add if already branded ---
        # Pass target_h to perfectly match the OCR coordinate scale
        if not is_already_branded(ocr_results, target_h):
            lw, lh = 160, 160
            pos = find_best_logo_position(final_img.width, final_img.height, lw, lh, ocr_results)
            
            if pos:
                lx, ly = pos
                logo = Image.open(logo_path).convert("RGBA")
                logo.thumbnail((lw, lh), Image.Resampling.LANCZOS)
                final_img.paste(logo, (lx, ly), logo)
        else:
            print("Skipped logo placement: Existing branding detected in header.")

    return final_img.convert("RGB")