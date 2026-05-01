Directory Structure
```
dealership_automation/
│
├── app.py                     # Main Streamlit frontend
├── database.sql               # Required SQL dump file
├── README.md                  # Required setup instructions
├── requirements.txt           # Python dependencies
│
├── assets/                    # (Put the provided folders here)
│   ├── panels/                # Dealership PNG panels
│   ├── logos/                 # Brand logos
│   ├── inputs/                # Sample background images
│   └── outputs/               # Expected output examples
│
└── src/                       # Core Python Modules
    ├── __init__.py
    ├── infrastructure/
    │   └── db_handler.py      # SQLite connection and queries
    ├── domain/
    │   └── image_engine.py    # Pillow & EasyOCR (AI) logic
    └── application/
        └── creative_builder.py # Bulk processing & ZIP creation


1. The "AI Void" Challenge
Challenge: Initially, the engine used a 1080x1080 "Letterbox" strategy to center images. However, AI-generated backgrounds often contain subtle noise or "dirty white" gradients (brightness values of 250–254) rather than pure 255 white. This caused the cropping logic to fail, leaving awkward white gaps between the car and the dealership footer.

Improvement: Developed an "Accordion Collapse" algorithm. Instead of forcing a square, the engine now merges the creative and panel into a tall canvas and then performs a vertical pixel-scan. It identifies the "void" bands of near-white pixels and slices them out, collapsing the creative and the branding into a single, seamless vertical stack regardless of the original aspect ratio.

2. Infrastructure & Local Stability
Challenge: Rapid prototyping in Streamlit caused the database initialization to trigger on every hot-reload, leading to sqlite3.OperationalError when trying to recreate existing tables. Additionally, a Dell Inspiron with 8GB RAM environment meant that redundant OCR calls were causing significant latency.

Improvement:

Idempotent DB Schema: Updated the db_handler.py to use IF NOT EXISTS syntax, ensuring the app remains stable across refreshes.

OCR Optimization: Refactored the image_engine.py to pass existing OCR results between functions, cutting the processing time in half by avoiding multiple scans of the same image.

3. Spatial Intelligence v2
Challenge: Manufacturer templates often have vertical design elements or logos in the corners that standard "Corner-only" placement logic would collide with.

Improvement: Expanded the find_best_logo_position engine to include a Top-Center candidate with tighter collision buffers. This allows the branding to find "breathing room" in complex headers without overlapping existing dealership text.