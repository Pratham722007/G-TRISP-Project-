import argparse
import sys
from pathlib import Path
from extractor import CrashExtractor
from exporter import CrashExporter

def main():
    parser = argparse.ArgumentParser(description="Convert Indian Police Crash Report PDFs to Structured Excel.")
    parser.add_argument("--input", required=True, help="Path to a PDF file or a directory containing PDFs.")
    parser.add_argument("--output", help="Path to the output Excel file (default: output/crash_data.xlsx).")
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = Path("output/crash_data.xlsx")

    # Resolve PDFs to process
    pdf_files = []
    if input_path.is_file():
        if input_path.suffix.lower() == ".pdf":
            pdf_files.append(input_path)
        else:
            print(f"Error: {input_path} is not a PDF file.")
            sys.exit(1)
    elif input_path.is_dir():
        pdf_files = list(input_path.rglob("*.pdf"))
        if not pdf_files:
            print(f"Error: No PDF files found in {input_path}.")
            sys.exit(1)
    else:
        print(f"Error: Input path {input_path} does not exist.")
        sys.exit(1)

    print(f"Found {len(pdf_files)} PDF(s) to process.")

    extractor = CrashExtractor()
    all_data = []

    for pdf_file in pdf_files:
        print(f"Processing: {pdf_file.name}")
        data = extractor.extract_from_pdf(pdf_file)
        # Always add the filename for reference
        data["Filename"] = pdf_file.name
        all_data.append(data)

    # Reorder keys to put Filename first
    if all_data:
        processed_data = []
        for entry in all_data:
            reordered = {"Filename": entry.pop("Filename")}
            reordered.update(entry)
            processed_data.append(reordered)
        
        exporter = CrashExporter(output_path)
        exporter.export(processed_data)
        
        print(f"Done. {len(pdf_files)} reports processed -> {output_path}")
    else:
        print("No data extracted.")

if __name__ == "__main__":
    main()
