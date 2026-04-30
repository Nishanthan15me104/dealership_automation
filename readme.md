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