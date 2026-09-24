from pdf_invoice_processor.pdf_reader import read_pdf
from pdf_invoice_processor.extractor import extract_invoice_data
from pdf_invoice_processor.parser import parse_data
from pdf_invoice_processor.validator import validate_invoice
from .vendor_config import VendorConfig
from .models import ExtractedInvoiceData, InvoiceData, ProcessedInvoice
from .status import rollup_status, add_status_message


def process_invoice(
    input_file: str,
    config: VendorConfig,
) -> ProcessedInvoice:
    raw_text: str = read_pdf(input_file)
    extracted_data: ExtractedInvoiceData = extract_invoice_data(raw_text, config)
    structured_data: InvoiceData = parse_data(extracted_data)
    is_valid: bool
    validation_message: str

    is_valid, validation_message = validate_invoice(structured_data)
    validation_status = "READY" if is_valid else "ERROR"

    return {
        "source_file": input_file,
        "invoice": structured_data,
        "validation_status": validation_status,
        "validation_message": validation_message,
        "status": rollup_status(
            structured_data["status"],
            validation_status,
        ),
        "status_message": add_status_message(
            structured_data,
            validation_message,
        ),
    }