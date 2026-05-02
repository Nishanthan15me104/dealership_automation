import streamlit as st
import requests
import io
from src.infrastructure.db_handler import init_db, get_brands, get_dealerships

# 1. Setup & DB Initialization
init_db()
st.set_page_config(page_title="Dealership Automation API Client", layout="wide")
st.title("🚗 Dealership Creative Automation")

# 2. UI Layout - Sidebar/Columns for inputs
with st.sidebar:
    st.header("1. Configuration")
    
    # Brand Selection
    brands = get_brands()
    brand_dict = {b[1]: b[0] for b in brands}
    selected_brand_name = st.selectbox("Select Brand", options=list(brand_dict.keys()))
    brand_id = brand_dict[selected_brand_name] if selected_brand_name else None
    
    # Dealership Multi-select
    selected_dealers = []
    if brand_id:
        dealers = get_dealerships(brand_id)
        dealer_dict = {d[1]: d for d in dealers}
        selected_dealer_names = st.multiselect("Select Dealerships", options=list(dealer_dict.keys()))
        selected_dealers = [dealer_dict[name] for name in selected_dealer_names]

    use_logo = st.checkbox("Include Logo", value=True)
    
    format_option = st.selectbox(
        "Output Format", 
        options=["Post (1080x1080)", "Portrait (1080x1350)", "Story (1080x1920)"]
    )
    
    dim_map = {
        "Post (1080x1080)": (1080, 1080),
        "Portrait (1080x1350)": (1080, 1350),
        "Story (1080x1920)": (1080, 1920)
    }

# 3. Main Area - File Upload
st.header("2. Background Image")
uploaded_file = st.file_uploader("Upload Image (JPG/PNG)", type=['jpg', 'jpeg', 'png'])

if uploaded_file:
    st.image(uploaded_file, caption="Preview", width=400)

# 4. Generate Action (Talking to FastAPI)
if st.button("🚀 Generate Bulk Creatives", type="primary"):
    if not uploaded_file or not selected_dealers:
        st.error("Please upload an image and select at least one dealership.")
    else:
        with st.spinner("API is analyzing image and generating creatives..."):
            
            # Prepare the data for the API
            files = {"background": uploaded_file.getvalue()}
            data = {
                "brand_id": brand_id,
                "dealer_ids": ",".join([str(d[0]) for d in selected_dealers]),
                "format_w": dim_map[format_option][0],
                "format_h": dim_map[format_option][1],
                "use_logo": use_logo
            }

            try:
                # --- ADDED FOR PRODUCTION SECURITY ---
                # This key must match the 'api_key' in your main_api.py settings
                headers = {"X-API-Key": "dev-secret-key-1234"}
                
                # Ensure main_api.py is running on port 8000
                response = requests.post(
                    "http://localhost:8000/generate-bulk/", 
                    files=files, 
                    data=data,
                    headers=headers  # <-- Pass the security headers here
                )
                
                if response.status_code == 200:
                    st.success(f"Generated {len(selected_dealers)} creatives via API!")
                    st.download_button(
                        label="📦 Download All as ZIP",
                        data=response.content,
                        file_name="dealership_creatives.zip",
                        mime="application/zip"
                    )
                elif response.status_code == 403:
                    st.error("Authentication Failed: Invalid API Key.")
                else:
                    st.error(f"API Error: {response.text}")
            except Exception as e:
                st.error(f"Could not connect to the API. Is main_api.py running? Error: {e}")