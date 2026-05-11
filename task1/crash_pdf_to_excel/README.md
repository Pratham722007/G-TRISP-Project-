# Crash PDF to Excel Conversion Tool

## Overview
This tool is a self-contained Python utility designed to convert Indian police crash report PDFs (specifically the SVNIT format) into a single, structured Excel file. Each PDF report is converted into one row in the Excel sheet, with extracted fields mapped to corresponding columns.

## Installation
1. Ensure you have Python 3.9+ installed.
2. Install the required dependencies using pip:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
The tool can process a single PDF file or a folder containing multiple PDFs.

### Process a single PDF:
```bash
python main.py --input reports/crash1.pdf
```

### Process all PDFs in a folder:
```bash
python main.py --input reports/
```

### Specify a custom output path:
```bash
python main.py --input reports/ --output results/crash_data.xlsx
```

## Output Format
The tool generates an Excel file (`.xlsx`) with the following characteristics:
- **Sheet Name**: `Crash_Data`
- **Header Row**: Bold, white font on a dark blue background (#1F4E79).
- **Freezing**: The top header row is frozen for easy scrolling.
- **Auto-sizing**: Column widths are automatically adjusted based on content (capped at 40 characters).
- **Columns**: Organized by sections including Accident Summary, Accident Details, Persons Involved, Vehicle Details, Driver Details, and Road Details.

## How It Works
1. **Extraction**: Uses `pdfplumber` to extract raw text from all pages of the PDF.
2. **Parsing**: A regex and keyword-based parser scans the text for `Label : Value` patterns. It uses a flexible mapping to handle common variations in field labels.
3. **Table Processing**: Specifically detects the "Persons Involved" table to extract numeric counts for Killed and Injured categories.
4. **Export**: Uses `openpyxl` to construct the structured Excel file with the requested styling and layout.

## Limitations
- **Scanned PDFs**: This tool is designed for text-based PDFs. Scanned or image-based PDFs (which require OCR) are not supported in this version.
- **Field Variations**: If a PDF uses a significantly different format or labels not included in the mapping, some fields may appear blank.
- **Table Structure**: The persons table extraction assumes a standard layout (Driver, Passenger, Pedestrian, Total rows).
