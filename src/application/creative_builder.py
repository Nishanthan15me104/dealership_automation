import io
import zipfile
from PIL import Image
from src.domain.image_engine import apply_dealership_branding

def generate_bulk_zip(uploaded_file, selected_dealers, dimensions, use_logo):
    """
    Generates branded marketing creatives for multiple dealerships and packages them in a ZIP.
    
    This function takes a base background image, iterates through a list of 
    dealerships, applies specific branding (panels/logos) via the image engine, 
    and compresses the results into a single ZIP file for download.

    Args:
        uploaded_file (File): The base background image file uploaded by the user.
        selected_dealers (list[tuple]): List of dealer tuples from the database 
            (id, name, panel_path, logo_path).
        dimensions (tuple): The target output size (width, height) for the images.
        use_logo (bool): Flag to determine whether to overlay the dealer logo.

    Returns:
        bytes: The raw binary content of the generated ZIP file.
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