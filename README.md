# G-TRISP Project — Technical Documentation

> **Gujarat Traffic & Road Incident Safety Processing**
> Submitted as part of the internship/project evaluation at SVNIT

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Repository Structure](#repository-structure)
3. [Task 1 — PDF Crash Report to Structured Excel](#task-1--pdf-crash-report-to-structured-excel)
4. [Task 2 — Vehicle Detection, Tracking & Trajectory Extraction](#task-2--vehicle-detection-tracking--trajectory-extraction)
5. [Tech Stack](#tech-stack)
6. [Setup & Installation](#setup--installation)
7. [How to Run](#how-to-run)
8. [Output Format](#output-format)
9. [Architecture](#architecture)
10. [Troubleshooting](#troubleshooting)

---

## Project Overview

This repository contains two independent data pipeline tools built for road safety and traffic analysis research:

| Task | Description | Output |
|------|-------------|--------|
| Task 1 | Batch-convert Indian police PDF crash reports into a structured Excel file | `.xlsx` with one row per report |
| Task 2 | Detect, track, and extract trajectories of vehicles from a traffic video | Annotated `.mp4` + `trajectories.csv` |

Both tools are production-ready Python scripts designed for reproducibility, batch processing, and research use.

---

## Repository Structure

```
G-TRISP-Project/
│
├── task1/
│   └── crash_pdf_to_excel/
│       ├── main.py              # Entry point — CLI runner
│       ├── extractor.py         # PDF parsing and field extraction logic
│       ├── exporter.py          # Excel file writing and formatting
│       ├── requirements.txt     # Python dependencies for Task 1
│       └── README.md            # (this file covers both tasks)
│
├── task2/
│   ├── main.py                  # Vehicle detection + tracking + CSV export
│   ├── requirements.txt         # Python dependencies for Task 2
│   └── README.md
│
├── SVNIT_Dummy_Crash_Records/   # Sample PDF crash reports for testing Task 1
├── SVNIT Crash Data for TEST.pdf # Single PDF for quick Task 1 test
├── traffic_video.mp4            # Input video for Task 2
├── yolov8n.pt                   # Pretrained YOLOv8 nano model weights
└── output/                      # All generated outputs land here
```

---

## Task 1 — PDF Crash Report to Structured Excel

### What It Does

Task 1 automates the manual, time-consuming process of reading Indian police crash reports (in PDF format) and converting them into a machine-readable Excel spreadsheet. Each PDF becomes one row; each extracted field becomes one column.

### How It Works — Architecture

```
PDF File(s)
    │
    ▼
┌─────────────────────────────────────┐
│           main.py (CLI)             │
│  - Accepts --input and --output     │
│  - Discovers all PDFs in a folder   │
│  - Loops through each PDF           │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│         extractor.py                │
│  CrashExtractor class               │
│                                     │
│  1. Opens PDF with pdfplumber       │
│  2. Extracts all text page by page  │
│  3. Scans for "Label : Value" pairs │
│     using a field_map dictionary    │
│  4. Parses the persons table        │
│     (Killed/Injured/Total counts)   │
└────────────┬────────────────────────┘
             │  Returns dict {field: value}
             ▼
┌─────────────────────────────────────┐
│          exporter.py                │
│  CrashExporter class                │
│                                     │
│  1. Creates (or appends to) .xlsx   │
│  2. Writes styled header row        │
│  3. Writes one row per PDF          │
│  4. Auto-sizes columns              │
│  5. Freezes header row              │
└─────────────────────────────────────┘
             │
             ▼
    output/crash_data.xlsx
```

### Fields Extracted (70+ columns)

The extractor captures fields across 6 categories:

| Category | Sample Fields |
|----------|---------------|
| FIR / Police Station | Accident ID, FIR Number, Station Name, District, Officer |
| Accident Details | Date/Time, Location, Severity, Collision Type, Weather |
| Vehicle Information | Reg No, Make/Model, Fuel Type, Insurance Validity, Hit & Run |
| Driver Information | Name, Age, DL Type, Drunk Driving, Injury Type |
| Road Conditions | Road Width, Surface Type, Speed Limit, Road Markings |
| Persons Involved | Killed (Driver/Passenger/Pedestrian), Grievous/Minor Injury, Total |

---

## Task 2 — Vehicle Detection, Tracking & Trajectory Extraction

### What It Does

Task 2 runs a pretrained deep learning model on a traffic video to automatically detect every vehicle, assign each one a unique tracking ID that persists across frames, record where each vehicle moves (trajectory), and produce both a visual annotated video and a structured data CSV.

### How It Works — Architecture

```
traffic_video.mp4
    │
    ▼
┌─────────────────────────────────────────┐
│               main.py                   │
│  Reads frames START_FRAME → END_FRAME   │
└──────────────┬──────────────────────────┘
               │  frame-by-frame
               ▼
┌─────────────────────────────────────────┐
│        YOLOv8n Detection Model          │
│  (yolov8n.pt — pretrained on COCO)      │
│                                         │
│  Detects: car, truck, bus,              │
│           motorcycle, bicycle, etc.     │
│  Output: bounding boxes + class labels  │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│        ByteTrack Tracker                │
│  (bytetrack.yaml — built into YOLO)     │
│                                         │
│  Assigns stable Track IDs across frames │
│  Handles partial occlusion gracefully   │
└──────────────┬──────────────────────────┘
               │
       ┌───────┴────────┐
       ▼                ▼
┌─────────────┐  ┌──────────────────────┐
│ Annotated   │  │  trajectories.csv    │
│ Video (.mp4)│  │                      │
│             │  │  frame, track_id,    │
│ - Bounding  │  │  class, bbox_x1/y1/  │
│   boxes     │  │  x2/y2, centroid_x/y │
│ - Track IDs │  └──────────────────────┘
│ - Trail     │
│   lines     │
└─────────────┘
```

### Detection Model

| Property | Value |
|----------|-------|
| Model | YOLOv8 Nano (`yolov8n.pt`) |
| Framework | Ultralytics YOLOv8 |
| Trained On | COCO dataset (80 classes) |
| Relevant Classes | car, truck, bus, motorcycle, bicycle |
| Tracker | ByteTrack (built-in, `bytetrack.yaml`) |

### Trajectory CSV Format

| Column | Description |
|--------|-------------|
| `frame` | Frame number in the video |
| `track_id` | Unique integer ID assigned to each vehicle |
| `class` | Vehicle type (car, truck, etc.) |
| `bbox_x1`, `bbox_y1` | Top-left corner of bounding box (pixels) |
| `bbox_x2`, `bbox_y2` | Bottom-right corner of bounding box (pixels) |
| `centroid_x`, `centroid_y` | Center point of the bounding box |

---

## Tech Stack

### Task 1

| Library | Version | Purpose |
|---------|---------|---------|
| `pdfplumber` | ≥0.9 | PDF text extraction |
| `openpyxl` | ≥3.1 | Excel file creation and styling |
| `pandas` | ≥2.0 | Data handling utilities |
| `pathlib` | stdlib | File path management |
| `argparse` | stdlib | Command-line interface |

### Task 2

| Library | Version | Purpose |
|---------|---------|---------|
| `ultralytics` | ≥8.0 | YOLOv8 model + ByteTrack |
| `opencv-python` | ≥4.8 | Video reading, frame annotation, writing |
| `pandas` | ≥2.0 | CSV export |
| `tqdm` | ≥4.0 | Progress bar |
| `torch` | ≥2.0 | Deep learning backend (PyTorch) |

### Environment

- **Python**: 3.9 or higher
- **OS**: Windows / Linux / macOS
- **GPU**: Optional but recommended for Task 2 (CUDA-enabled GPU speeds up inference significantly)

---

## Setup & Installation

### Step 1 — Clone the Repository

```bash
git clone <your-repo-url>
cd G-TRISP-Project
```

### Step 2 — Create a Virtual Environment

```bash
python -m venv .venv

# Activate on Windows
.venv\Scripts\activate

# Activate on Linux/macOS
source .venv/bin/activate
```

### Step 3 — Install Dependencies

**For Task 1:**
```bash
pip install -r task1/crash_pdf_to_excel/requirements.txt
```

**For Task 2:**
```bash
pip install -r task2/requirements.txt
```

> **Note:** PyTorch installation varies by system. If the above fails for Task 2, install PyTorch first from [https://pytorch.org/get-started/locally](https://pytorch.org/get-started/locally), then re-run the requirements install.

### Step 4 — Verify Files Are Present

Make sure these files exist before running:
- `SVNIT_Dummy_Crash_Records/` folder — with PDF files inside (for Task 1)
- `traffic_video.mp4` — in the root folder (for Task 2)
- `yolov8n.pt` — in the root folder (for Task 2)

---

## How to Run

### Task 1 — Convert PDFs to Excel

Navigate to the task1 folder:
```bash
cd task1/crash_pdf_to_excel
```

**Process a single PDF:**
```bash
python main.py --input "../../SVNIT Crash Data for TEST (1).pdf" --output ../../output/crash_data.xlsx
```

**Process an entire folder of PDFs:**
```bash
python main.py --input ../../SVNIT_Dummy_Crash_Records --output ../../output/crash_data.xlsx
```

**Process only the first N PDFs (useful for quick testing):**
```bash
python main.py --input ../../SVNIT_Dummy_Crash_Records --output ../../output/crash_data.xlsx --limit 5
```

**Arguments:**

| Argument | Required | Description |
|----------|----------|-------------|
| `--input` | Yes | Path to a single `.pdf` file or a folder containing PDFs |
| `--output` | No | Path for the output Excel file (default: `output/crash_data.xlsx`) |
| `--limit` | No | Max number of PDFs to process (useful for testing) |

**Expected output:**
```
Found 25 PDF(s) to process.
Processing: crash_001.pdf
Processing: crash_002.pdf
...
  Excel file saved to: output/crash_data.xlsx
Done. 25 reports processed -> output/crash_data.xlsx
```

---

### Task 2 — Vehicle Detection & Tracking

Navigate to task2:
```bash
cd task2
```

**Before running**, open `main.py` and confirm/adjust these configuration variables at the top:

```python
VIDEO_PATH  = "traffic_video.mp4"   # Input video path
OUTPUT_DIR  = "output"              # Where outputs are saved
MODEL_PATH  = "yolov8n.pt"          # Model weights file
START_FRAME = 0                     # Start processing from this frame
END_FRAME   = 500                   # Stop processing at this frame (None = whole video)
TRACKER     = "bytetrack.yaml"      # Tracking algorithm
TRAIL_LENGTH = 30                   # How many past positions draw the trail line
```

**Run the script:**
```bash
python main.py
```

**Expected output:**
```
Processing Video: 100%|████████████| 500/500 [02:14<00:00,  3.72it/s]

Processing complete. Outputs saved in output/
```

**Generated files:**
```
output/
├── annotated_video.mp4    ← Video with bounding boxes, IDs, and trail lines
└── trajectories.csv       ← Structured data for every detection
```

---

## Output Format

### Task 1 Output — crash_data.xlsx

- Row 1: Styled header (dark blue background, white bold text)
- Row 2 onward: One row per crash report PDF
- Columns auto-sized for readability
- Header row is frozen (stays visible when scrolling)
- If you run the tool again on more PDFs, new rows are **appended** to the existing file

### Task 2 Output — trajectories.csv (sample)

```
frame,track_id,class,bbox_x1,bbox_y1,bbox_x2,bbox_y2,centroid_x,centroid_y
0,1,car,102.3,45.1,198.7,120.4,150.5,82.75
0,2,truck,312.0,88.2,490.5,210.3,401.25,149.25
1,1,car,105.1,46.0,201.4,121.8,153.25,83.9
...
```

---

## Architecture

### Task 1 — Class Diagram

```
main.py (CLI)
    │
    ├── CrashExtractor (extractor.py)
    │       ├── field_map: Dict[str, List[str]]   ← Maps output columns to PDF label variants
    │       ├── extract_from_pdf(path) → Dict     ← Main extraction method
    │       ├── _parse_label_value_fields()        ← Handles "Label : Value" lines
    │       └── _parse_persons_table()             ← Handles Killed/Injured table rows
    │
    └── CrashExporter (exporter.py)
            ├── export(data_list)                  ← Writes/appends Excel
            └── Styling: header fill, fonts,       ← openpyxl formatting
                         column widths, freeze panes
```

### Task 2 — Data Flow

```
Video Frame
    → YOLO Inference (object detection)
    → ByteTrack (assigns/maintains track IDs)
    → Centroid Calculation (cx, cy from bbox)
    → Trail History Buffer (last 30 centroids per ID)
    → Frame Annotation (cv2 rectangle + text + polyline)
    → VideoWriter (save annotated frame)
    → trajectory_data list append
    [After all frames]
    → pandas DataFrame → .csv export
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `pdfplumber` not found | Run `pip install pdfplumber` |
| Excel file shows empty columns | The PDF layout may not match expected label patterns; check with `--limit 1` and inspect output |
| `ultralytics` not found | Run `pip install ultralytics` |
| `yolov8n.pt` not found | Place the weights file in the same directory as `main.py`, or update `MODEL_PATH` |
| CUDA/GPU errors | Add `device='cpu'` to the `model.track(...)` call in task2/main.py |
| Video not opening | Verify `VIDEO_PATH` is correct; check the video file is not corrupted |
| Output folder missing | The scripts create it automatically; if permission error, create `output/` manually |

---

## Authors

Developed as part of the G-TRISP internship project evaluation.
Tools built for research use by SVNIT Road Safety Lab.

---

*Last updated: May 2026*
