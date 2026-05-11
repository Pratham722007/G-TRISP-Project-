# Crash PDF to Excel Conversion Tool

## Overview
This tool automates the extraction of structured data from Indian Police crash report PDFs (SVNIT format) into a formatted Excel file. It supports single-file processing, batch processing, and intelligent data appending.

## Tech Stack
- **Python 3.9+**
- **pdfplumber**: PDF text extraction.
- **openpyxl**: Excel generation, styling, and appending.
- **argparse**: CLI interface.

## Installation
1. Ensure you have Python installed.
2. Activate your virtual environment:
   ```powershell
   .venv\Scripts\Activate.ps1
   ```
3. Install dependencies:
   ```powershell
   pip install -r task1/crash_pdf_to_excel/requirements.txt
   ```

## Usage

### Process a single PDF:
```powershell
python task1/crash_pdf_to_excel/main.py --input "path/to/report.pdf"
```

### Process all PDFs in a folder:
```powershell
python task1/crash_pdf_to_excel/main.py --input "path/to/folder/"
```

### Process a limited number of files:
```powershell
python task1/crash_pdf_to_excel/main.py --input "path/to/folder/" --limit 5
```

### Specify a custom output:
```powershell
python task1/crash_pdf_to_excel/main.py --input "path/to/folder/" --output "results/my_data.xlsx"
```

## Features
- **Smart Append**: Automatically detects if the output file exists and adds new records as new rows at the bottom.
- **Rich Formatting**: Headers are styled with colors, columns are auto-resized, and the top row is frozen.
- **Batch Processing**: Easily process hundreds of PDFs with a single command.
