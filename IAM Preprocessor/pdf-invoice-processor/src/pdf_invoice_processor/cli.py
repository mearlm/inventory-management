import argparse
import json
from pathlib import Path

from pdf_invoice_processor.reporting import print_session_summary
from pdf_invoice_processor.publish_batch import publish_batch
from pdf_invoice_processor.process_batch import process_batch
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


def parse_arguments():
    parser = argparse.ArgumentParser(description="Process PDF invoices.")
    parser.add_argument(
        "input",
        type=str,
        help="Path to the input PDF file or directory containing PDF files",
    )
    parser.add_argument(
        "output",
        type=str,
        help="Directory where processed CSV output files will be written",
    )
    parser.add_argument(
        "--vendor",
        type=str,
        required=True,
        help="Vendor name used to load data/vendors/<vendor>.json",
    )

    return parser.parse_args()


def resolve_input_files(args) -> list[Path]:
    input_path = Path(args.input)

    if input_path.is_file() and input_path.suffix.lower() == ".pdf":
        return [input_path]

    if input_path.is_dir():
        pdf_files = sorted(input_path.glob("*.pdf"), key=lambda p: p.name.lower())
        if not pdf_files:
            raise FileNotFoundError(
                f"No PDF files found in directory: {input_path}"
            )
        return pdf_files

    raise ValueError(
        f"Invalid input path: {input_path}. "
        "Must be a PDF file or a directory containing PDF files."
    )


def main():
    args = parse_arguments()
    output_path = Path(args.output)

    config = load_vendor_config(args.vendor)
    input_files = resolve_input_files(args)

    invoices, stats = process_batch(input_files, config)

    artifacts = publish_batch(invoices, output_path)

    print_session_summary(stats, artifacts, output_path)




if __name__ == "__main__":
    main()