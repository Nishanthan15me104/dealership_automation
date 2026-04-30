import streamlit as st
import io
from PIL import Image
from src.infrastructure.db_handler import init_db, get_brands, get_dealerships
from src.application.creative_builder import generate_bulk_zip

# Initialize DB on first run
init_db()

st.set_page_config(page_title="Dealership Creative Automation", layout="wide")

st.title("🚗 Dealership Creative Automation Tool")
st.markdown("Automate bulk creative generation with AI-powered layout optimization.")

# Layout
col1, col2 = st.columns([1, 2])

with col1:
    st.header("1. Asset Configuration")
    
    # Brand Selection
    brands = get_brands()
    brand_dict = {b[1]: b[0] for b in brands}
    selected_brand_name = st.selectbox("Select Brand (Account)", options=list(brand_dict.keys()))
    
    # Dealership Selection (Bulk)
    if selected_brand_name:
        brand_id = brand_dict[selected_brand_name]
        dealers = get_dealerships(brand_id)
        dealer_dict = {d[1]: d for d in dealers}
        
        selected_dealer_names = st.multiselect(
            "Select Dealerships (Multi-select for Bulk)", 
            options=list(dealer_dict.keys())
        )
        selected_dealers = [dealer_dict[name] for name in selected_dealer_names]

    # Options
    use_logo = st.checkbox("Include Dealership Logo", value=True)
    
    format_option = st.selectbox(
        "Output Format", 
        options=["Instagram Post (1080x1080)", "Instagram Portrait (1080x1350)", "Instagram Story (1080x1920)"]
    )
    
    dim_map = {
        "Instagram Post (1080x1080)": (1080, 1080),
        "Instagram Portrait (1080x1350)": (1080, 1350),
        "Instagram Story (1080x1920)": (1080, 1920)
    }

with col2:
    st.header("2. Background Image")
    uploaded_file = st.file_uploader("Upload Background Image (JPG/PNG)", type=['jpg', 'jpeg', 'png'])
    
    if uploaded_file:
        st.image(uploaded_file, caption="Input Image", use_column_width=True)

# Generate Action
if st.button("🚀 Generate Bulk Creatives", type="primary"):
    if not uploaded_file or not selected_dealers:
        st.error("Please upload an image and select at least one dealership.")
    else:
        with st.spinner("AI is analyzing image and generating creatives..."):
            zip_data = generate_bulk_zip(
                uploaded_file=uploaded_file,
                selected_dealers=selected_dealers,
                dimensions=dim_map[format_option],
                use_logo=use_logo
            )
            
            st.success(f"Successfully generated {len(selected_dealers)} creatives!")
            
            st.download_button(
                label="📦 Download All as ZIP",
                data=zip_data,
                file_name="dealership_creatives.zip",
                mime="application/zip"
            )