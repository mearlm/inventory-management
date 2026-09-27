import csv
from pathlib import Path
from .models import InvoiceData

def export_to_csv(data: InvoiceData, output_file: Path):
    """Exports the processed invoice data to a CSV file."""
    with open(output_file, mode='w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Item ID', 'Description', 'Quantity', 'Unit Price', 'Total']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        invoice_vendor = data.get("vendor", "Unknown Vendor")
        invoice_header = data.get("header", {})
        invoice_number = invoice_header.get("invoice_number", "Unknown")
        invoice_date = invoice_header.get("invoice_date", "Unknown")
        source_file = data.get("source_file", "Unknown")

        writer.writeheader()
        for record in data["items"]:
            writer.writerow({
                'Vendor': invoice_vendor,
                'Invoice #': invoice_number,
                'Invoice Date': invoice_date,
                'Source File': source_file,
                'Item ID': record.get('item_id'),
                'Description': record.get('description'),
                'Quantity': record.get('quantity'),
                'Unit Price': record.get('unit_price'),
                'Total': record.get('total'),
                'Status': record.get('status'),
                'Status Message': record.get('status_message', ''),
            })