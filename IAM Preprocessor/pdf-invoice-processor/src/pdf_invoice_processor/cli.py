import argparse
import json
import os
from pathlib import Path

from pdf_invoice_processor.pdf_reader import read_pdf
from pdf_invoice_processor.extractor import extract_invoice_data
from pdf_invoice_processor.parser import parse_data
from pdf_invoice_processor.validator import validate_invoice
from pdf_invoice_processor.csv_exporter import export_to_csv
from .vendor_config import VendorConfig


def choose_pdf_files():
    # Placeholder for file selection logic: INSERT FILE CHOOSER HERE
    return input("Enter the path to the PDF file: ")


def choose_vendor_config():
    # Placeholder for vendor config selection logic: INSERT FILE CHOOSER HERE
    return input("Enter the vendor name for the vendor config file: ")


def load_vendor_config(vendor_name: str) -> VendorConfig:
    normalized_vendor_name = vendor_name.strip().removesuffix(".json").lower()
    config_path = (
        Path(__file__).resolve().parents[2]
        / "data"
        / "vendors"
        / f"{normalized_vendor_name}.json"
    )

    if not config_path.exists():
        raise FileNotFoundError(
            f"Vendor config not found for '{vendor_name}'. Expected file: {config_path}"
        )

    with config_path.open("r", encoding="utf-8") as config_file:
        config = json.load(config_file)

    return config


def main():
    parser = argparse.ArgumentParser(description="Process PDF invoices.")
    parser.add_argument('input', type=str, help='Path to the input PDF file')
    parser.add_argument('output', type=str, help='Path to the output CSV file')
    parser.add_argument(
        '--vendor',
        type=str,
        help='Vendor name used to load data/vendors/<vendor>.json',
    )

    args = parser.parse_args()

    if args.input:
        input_files = args.input
    else:
        input_files = choose_pdf_files()

    if args.vendor:
        vendor_name = args.vendor
    else:
        vendor_name = choose_vendor_config()

    config = load_vendor_config(vendor_name)

    if not os.path.exists(input_files):
        print(f"Error: The file {input_files} does not exist.")
        return

    # Read PDF
    raw_text = read_pdf(input_files)

    # Extract data
    extracted_data = extract_invoice_data(raw_text, config)

    # Parse data
    structured_data = parse_data(extracted_data)

    # Validate data
    is_valid, validation_message = validate_invoice(structured_data)

    if not is_valid:
        print(f"Error: Invoice validation failed: {validation_message}")
        return

    # Export to CSV
    export_to_csv(structured_data, args.output)
    print(f"Data successfully exported to {args.output}")
    print(
        f"Validation passed for {len(structured_data['items'])} items.\nData exported to {args.output}"
    )


if __name__ == "__main__":
    main()