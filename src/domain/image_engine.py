import os
import easyocr
import numpy as np
from PIL import Image, ImageStat

# Initialize OCR
reader = easyocr.Reader(['en'], gpu=False)

def find_best_logo_position(bg_w, bg_h, logo_w, logo_h, ocr_results):
    """Finds a corner farthest from text, strictly in the top 70% of the image."""
    margin = 50
    # We only look at Top-Left and Top-Right to keep it away from the bottom template
    candidates = [
        (margin, margin),                         # Top-Left
        (bg_w - logo_w - margin, margin)          # Top-Right
    ]

    text_boxes = []
    for result in ocr_results:
        bbox = result[0]
        xs = [pt[0] for pt in bbox]; ys = [pt[1] for pt in bbox]
        text_boxes.append((min(xs), min(ys), max(xs), max(ys)))

    # Simple logic: If Top-Left is crowded, go Top-Right
    tl_box = (margin, margin, margin + logo_w, margin + logo_h)
    for tb in text_boxes:
        # Check if text is in Top-Left area
        if not (tl_box[0] > tb[2] or tl_box[2] < tb[0] or tl_box[1] > tb[3] or tl_box[3] < tb[1]):
            return candidates[1] # Return Top-Right
            
    return candidates[0] # Default Top-Left

def get_optimal_logo_path(bg_crop, current_logo_path):
    grayscale = bg_crop.convert("L")
    stat = ImageStat.Stat(grayscale)
    avg_brightness = stat.mean[0] 
    directory = os.path.dirname(current_logo_path)
    target = "logo-light.png" if avg_brightness < 127 else "logo-dark.png"
    new_path = os.path.join(directory, target)
    return new_path if os.path.exists(new_path) else current_logo_path

def apply_dealership_branding(bg_image, panel_path, logo_path=None, output_size=(1080, 1080)):
    # 1. SCALE BACKGROUND (Width only, preserve Aspect Ratio)
    target_w = output_size[0]
    w_ratio = target_w / float(bg_image.size[0])
    target_h = int(float(bg_image.size[1]) * w_ratio)
    bg = bg_image.convert("RGBA").resize((target_w, target_h), Image.Resampling.LANCZOS)
    
    # 2. DETECT BOTTOM TEXT
    np_img = np.array(bg.convert('RGB'))
    ocr_results = reader.readtext(np_img)
    bottom_limit = target_h * 0.88 # The last 12% of the image
    has_bottom_text = any(max([pt[1] for pt in res[0]]) > bottom_limit for res in ocr_results)

    # 3. PREPARE PANEL
    panel_h = 0
    if os.path.exists(panel_path):
        panel = Image.open(panel_path).convert("RGBA")
        p_ratio = target_w / float(panel.size[0])
        panel_h = int(float(panel.size[1]) * p_ratio)
        panel = panel.resize((target_w, panel_h), Image.Resampling.LANCZOS)

    # 4. CREATE COMPOSITION (No Cropping)
    if has_bottom_text:
        # Create extra space at the bottom
        final_h = target_h + panel_h
        comp = Image.new("RGBA", (target_w, final_h), (255, 255, 255, 255))
        comp.paste(bg, (0, 0), bg)
        comp.paste(panel, (0, target_h), panel)
    else:
        # Place panel on top of the image
        final_h = target_h
        comp = bg.copy()
        comp.paste(panel, (0, target_h - panel_h), panel)

    # 5. LOGO (Strictly on the BG part)
    if logo_path and os.path.exists(logo_path):
        lw, lh = 180, 180
        lx, ly = find_best_logo_position(target_w, target_h, lw, lh, ocr_results)
        
        # Color Check
        bg_crop = bg.crop((lx, ly, lx + lw, ly + lh))
        final_logo_path = get_optimal_logo_path(bg_crop, logo_path)
        
        logo = Image.open(final_logo_path).convert("RGBA")
        logo.thumbnail((lw, lh), Image.Resampling.LANCZOS)
        comp.paste(logo, (lx, ly), logo)

    # 6. FINAL FIT (Resize to 1080x1080 WITHOUT squashing)
    # If image is too tall, we scale it down to fit 1080 height
    if comp.size[1] > output_size[1]:
        scale = output_size[1] / float(comp.size[1])
        new_w = int(comp.size[0] * scale)
        comp = comp.resize((new_w, output_size[1]), Image.Resampling.LANCZOS)
    
    # Place on final white square
    final_square = Image.new("RGB", output_size, (255, 255, 255))
    x_offset = (output_size[0] - comp.size[0]) // 2
    y_offset = (output_size[1] - comp.size[1]) // 2
    final_square.paste(comp.convert("RGB"), (x_offset, y_offset))
    
    return final_square