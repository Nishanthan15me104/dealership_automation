import io
import zipfile
from PIL import Image
from src.domain.image_engine import apply_dealership_branding

def generate_bulk_zip(uploaded_file, selected_dealers, dimensions, use_logo):
    """
    Loops through selected dealerships, generates images, and packages them in a ZIP.
    Returns a BytesIO object of the ZIP file.
    """
    bg_image = Image.open(uploaded_file)
    
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        for dealer in selected_dealers:
            dealer_name = dealer[1]
            panel_path = dealer[2]
            logo_path = dealer[3] if use_logo else None
            
            # Call our AI image engine
            final_img = apply_dealership_branding(
                bg_image=bg_image,
                panel_path=panel_path,
                logo_path=logo_path,
                output_size=dimensions
            )
            
            # Save to temporary bytes buffer
            img_byte_arr = io.BytesIO()
            final_img.save(img_byte_arr, format='JPEG', quality=95)
            
            # Write to ZIP
            filename = f"creative_{dealer_name.replace(' ', '_')}.jpg"
            zip_file.writestr(filename, img_byte_arr.getvalue())
            
    return zip_buffer.getvalue()