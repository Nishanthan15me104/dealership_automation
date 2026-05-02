# Dealership Creative Automation Tool

## 📌 Project Overview

The **Dealership Creative Automation Tool** is an AI-assisted bulk creative generation system designed for automotive dealership marketing teams.

The system automates the process of generating dealership-specific promotional creatives by intelligently combining:

- Brand dealership panels
- Brand logos
- Uploaded background creatives
- OCR-based intelligent positioning
- Bulk dealership processing

This tool was developed to reduce repetitive manual design work and enable rapid dealership-level campaign generation while maintaining branding consistency.

The project supports:

- Single & bulk dealership creative generation
- Dynamic dealership loading by brand
- Smart logo placement
- OCR-based text collision avoidance
- White-space removal using intelligent pixel scanning
- ZIP export for mass downloads
- Streamlit frontend + FastAPI backend architecture

---

# 📁 Project Directory Structure

```bash
dealership_automation/
│
├── .venv/                             # Python virtual environment
├── temp_outputs/                      # Temporary ZIP/image outputs
│
├── assets/
│   ├── Dealership-panels/
│   │   ├── Tata-dealers/
│   │   └── VW-dealers/
│   │
│   └── Logos/
│       ├── Tata/
│       │   ├── logo-dark.png
│       │   └── logo-light.png
│       │
│       └── Volkswagen/
│           ├── logo-dark.png
│           └── logo-light.png
│
├── src/
│   ├── application/
│   │   ├── __init__.py
│   │   └── creative_builder.py
│   │
│   ├── domain/
│   │   ├── __init__.py
│   │   └── image_engine.py
│   │
│   ├── infrastructure/
│   │   ├── __init__.py
│   │   └── db_handler.py
│   │
│   └── __init__.py
│
├── app.py                             # Streamlit frontend
├── main_api.py                        # FastAPI backend API
├── main_st.py                         # Streamlit launcher
├── database.sql                       # SQL schema + seed data
├── dealerships.db                     # SQLite database
├── requirements.txt                   # Project dependencies
├── README.md
├── .gitignore
└── .gitattributes
```

---

# 🏗 System Architecture

The project follows a modular layered architecture.

```text
Frontend Layer (Streamlit UI)
            │
            ▼
FastAPI API Layer
            │
            ▼
Application Layer
(creative_builder.py)
            │
            ▼
Domain Layer
(image_engine.py)
            │
            ▼
Infrastructure Layer
(db_handler.py + SQLite)
```

---

# ⚙️ Core Technologies Used

| Technology | Purpose |
|---|---|
| Python | Core backend language |
| Streamlit | Web frontend |
| FastAPI | API backend |
| Pillow (PIL) | Image processing |
| EasyOCR | OCR text detection |
| NumPy | Pixel analysis |
| SQLite | Database |
| asyncio | Async API execution |
| Prometheus | Monitoring |
| ZipFile | Bulk export |

---

# 🧠 Intelligent Automation Features

The assignment required at least one intelligent automation capability.

This project implements multiple AI-assisted automation mechanisms.

---

# 🔹 1. OCR-Based Text Detection

The system uses **EasyOCR** to detect existing text regions in uploaded creatives.

```python
ocr_results = reader.readtext(np.array(bg.convert('RGB')))
```

This allows the engine to:

- Detect existing brand headers
- Avoid overlapping logos
- Prevent dealership panels from covering text

---

# 🔹 2. Intelligent Logo Placement

### Function

```python
find_best_logo_position()
```

The engine dynamically searches for empty regions in the image.

### Candidate Regions

- Top-left
- Top-right
- Top-center

### Logic

- OCR bounding boxes are extracted
- Collision buffers are added
- Logo is only placed where overlap does not occur

This prevents:

- Logo overlapping text
- Logo covering vehicles
- Cluttered layouts

---

# 🔹 3. Accordion Collapse Algorithm (AI Void Removal)

### Function

```python
collapse_white_gap()
```

### Problem

AI-generated creatives often contain:

- Dirty-white gradients
- Invisible spacing
- Near-white artifacts

Traditional cropping failed because pixels were not pure white.

### Solution

The engine performs:

- Vertical pixel scanning
- Brightness averaging
- Gap detection using NumPy

```python
row_means = np.mean(pixels, axis=1)
```

If a large whitespace band is detected:

- The gap is sliced out
- Top and bottom regions are merged seamlessly

This creates:

✅ No visible white gaps  
✅ Seamless creative stacking  
✅ No image distortion  

---

# 🔹 4. OCR-Based Brand Guard

### Function

```python
is_already_branded()
```

### Problem

Manufacturer creatives often already contain:

- Existing logos
- Service branding
- Headers

Adding another logo caused duplicate branding.

### Solution

The engine scans the top 30% of the image.

If OCR detects keywords such as:

```python
['volkswagen', 'vw', 'tata', 'kia']
```

Then:

```python
Skipped logo placement
```

This preserves original manufacturer designs.

---

# 🔹 5. Bulk Processing Engine

### Function

```python
generate_bulk_zip()
```

The system:

- Processes multiple dealerships
- Generates multiple creatives
- Compresses outputs into ZIP format

Supports:

✅ 5 creatives  
✅ 15 creatives  
✅ Large dealership batches  

---

# 🔹 6. Async API Offloading

### Functionality

```python
await asyncio.to_thread()
```

### Problem

OCR + PIL processing is CPU intensive.

If executed directly inside FastAPI routes:

- API freezes
- Health endpoints become unresponsive

### Solution

Heavy processing is offloaded to worker threads.

Benefits:

✅ Non-blocking API  
✅ Responsive health checks  
✅ Better scalability  
✅ Improved concurrent requests  

---

# 🗄 Database Design

The project uses SQLite.

## Tables

### brands

Stores account/brand data.

| id | name |
|---|---|
| 1 | Tata |
| 2 | Volkswagen |

---

### dealerships

Stores dealership mappings.

| Column | Purpose |
|---|---|
| brand_id | Linked brand |
| name | Dealer name |
| panel_image_path | Dealer panel |
| logo_image_path | Brand logo |

---

# 🧩 Database Functions

## init_db()

Initializes database schema.

```python
conn.executescript(f.read())
```

---

## get_brands()

Loads all brands dynamically.

Used for dropdown population.

---

## get_dealerships(brand_id)

Loads dealerships based on selected brand.

This satisfies assignment requirement:

✅ Dynamic dealership loading

---

# 🖼 Creative Generation Flow

```text
Upload Background
        │
        ▼
OCR Text Detection
        │
        ▼
Resize & Scale Image
        │
        ▼
Attach Dealership Panel
        │
        ▼
Collapse White Gaps
        │
        ▼
Check Existing Branding
        │
        ▼
Smart Logo Placement
        │
        ▼
Export Final Creative
```

---

# ✅ Functional Requirements Coverage

| Requirement | Status |
|---|---|
| Account dropdown | ✅ |
| Dynamic dealership loading | ✅ |
| Multi-select dealerships | ✅ |
| Optional logo enable/disable | ✅ |
| JPG/PNG support | ✅ |
| No distortion scaling | ✅ |
| Bulk generation | ✅ |
| ZIP download | ✅ |
| Instagram formats | ✅ |
| AI automation | ✅ |
| SQL dump included | ✅ |
| README included | ✅ |

---

# 📐 Supported Output Formats

| Format | Resolution |
|---|---|
| Instagram Post | 1080 × 1080 |
| Instagram Portrait | 1080 × 1350 |
| Instagram Story | 1080 × 1920 |

---

# 🚀 Setup Instructions

## 1️⃣ Clone / Extract Repository

```powershell
git clone <your-repository-url>
cd dealership_automation
```

OR

Extract the ZIP file and open the folder.

---

## 2️⃣ Create Virtual Environment

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

---

## 3️⃣ Install Dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## 4️⃣ Initialize Database

```powershell
python
```

```python
from src.infrastructure.db_handler import init_db
init_db()
```

This creates:

```text
dealerships.db
```

with all brand + dealership mappings.

---

## 5️⃣ Run Streamlit Frontend

```powershell
streamlit run app.py
```

OR

```powershell
streamlit run main_st.py
```

---

## 6️⃣ Run FastAPI Backend

```powershell
uvicorn main_api:app --reload
```

---

# 🌐 API Endpoints

## Health Check

```http
GET /health
```

Used for:

- Monitoring
- Load balancer checks
- Deployment validation

---

## Bulk Generation

```http
POST /generate-bulk/
```

### Required Headers

```http
X-API-Key: dev-secret-key-1234
```

---

# 📦 Example API Workflow

```text
Upload Image
      ↓
Select Brand
      ↓
Select Dealerships
      ↓
Generate Creatives
      ↓
Download ZIP File
```

---

# 📥 Output

The system generates:

✅ Individual dealership creatives  
✅ ZIP archive for bulk downloads  

Generated files are stored temporarily inside:

```text
temp_outputs/
```

---

# 🛡 Security Features

## API Key Authentication

Implemented using:

```python
APIKeyHeader
```

Unauthorized requests return:

```http
403 Forbidden
```

---

# 📊 Monitoring Support

Integrated with:

```python
prometheus-fastapi-instrumentator
```

If Prometheus is installed:

```http
/metrics
```

becomes available automatically.

---

# ⚡ Performance Optimizations

## OCR Optimization

OCR results are reused across functions instead of scanning multiple times.

Benefits:

✅ Reduced latency  
✅ Faster bulk generation  
✅ Lower CPU usage  

---

## Async Offloading

Heavy processing runs in background threads.

Prevents:

- API blocking
- Timeout issues
- UI freezing

---

# 🧪 Challenges Faced & Improvements

## 1️⃣ The "AI Void" Problem

### Challenge

AI-generated backgrounds contained dirty-white gradients.

This caused visible gaps after merging panels.

### Improvement

Implemented:

```python
collapse_white_gap()
```

using NumPy pixel scanning.

---

## 2️⃣ Recursive Branding Issue

### Challenge

Some creatives already contained logos.

Adding another logo created duplicate branding.

### Improvement

Implemented OCR-based header detection.

---

## 3️⃣ Complex Template Layouts

### Challenge

Standard corner placement failed with vertical design elements.

### Improvement

Added:

✅ Top-center placement  
✅ Collision buffers  
✅ OCR-aware positioning  

---

## 4️⃣ Streamlit Reload Stability

### Challenge

Database recreation caused:

```python
sqlite3.OperationalError
```

### Improvement

Added safer initialization strategy.

---

# 🔮 Future Improvements

## Possible Production Enhancements

### Docker Deployment

Containerize:

- FastAPI
- Streamlit
- OCR Engine

---

### Cloud Storage Integration

Store outputs in:

- AWS S3
- Azure Blob
- GCP Storage

---

### Redis Queue System

Move bulk processing into worker queues.

Useful for:

- Large campaigns
- High concurrency

---

### GPU OCR Processing

Enable GPU acceleration for:

```python
easyocr.Reader(gpu=True)
```

---

### CRM Integration

Expose APIs for:

- Dealership CRMs
- Marketing dashboards
- Internal portals

---

### Advanced AI Layout Engine

Future AI features:

- Vehicle detection
- Text-safe region prediction
- Smart branding heatmaps

---

# ✅ Features Summary

✔ Dynamic brand & dealership mapping  
✔ Multi-dealership bulk generation  
✔ OCR-based intelligent automation  
✔ Smart logo placement  
✔ White-space removal engine  
✔ OCR-based duplicate branding prevention  
✔ ZIP export support  
✔ FastAPI backend integration  
✔ Streamlit frontend  
✔ SQLite database integration  
✔ Async API execution  
✔ API key security  
✔ Prometheus monitoring support  
✔ Modular architecture  
✔ Error handling & logging  
✔ No-distortion image scaling  
✔ Multiple Instagram output formats  

---

# 👨‍💻 Author

**Nishanthan S**

AI / ML & MLOps Enthusiast  
Focused on intelligent automation systems, scalable AI pipelines, and production-ready ML applications.