import csv

from pathlib import Path
from .models import ProcessedInvoice


def export_activity_lines(
    invoices: list[ProcessedInvoice],
    output_file: Path,
) -> None:
    fieldnames = [
        "Vendor",
        "Invoice #",
        "Invoice Date",
        "Source File",
        "Item Sequence",
        "Item ID",
        "Seller",
        "Description",
        "Quantity",
        "Unit Price",
        "Total",
        "Status",
        "Status Message",
    ]

    with output_file.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as csvfile:

        writer = csv.DictWriter(
            csvfile,
            fieldnames=fieldnames,
        )
        writer.writeheader()

        for processed in invoices:
            invoice = processed["invoice"]
            header = invoice["header"]

            for sequence, item in enumerate(
                invoice["items"],
                start=1,
            ):
                writer.writerow({
                    "Vendor":
                        header.get("vendor", ""),
                    "Invoice #":
                        header.get("invoice_number", ""),
                    "Invoice Date":
                        header.get("invoice_date", "").replace(",", ""),
                    "Source File":
                        processed["source_file"],
                    "Item Sequence":
                        sequence,
                    "Item ID":
                        item.get("item_id", ""),
                    "Seller":
                        item.get("seller", ""),
                    "Description":
                        item.get("description", ""),
                    "Quantity":
                        item.get("quantity", ""),
                    "Unit Price":
                        item.get("unit_price", ""),
                    "Total":
                        item.get("total", ""),
                    "Status":
                        item.get("status", "READY"),
                    "Status Message":
                        item.get("status_message", ""),
                })


def export_activity_headers(
    invoices: list[ProcessedInvoice],
    output_file: Path,
) -> None:
    fieldnames = [
        "Vendor",
        "Invoice #",
        "Invoice Date",
        "Source File",
        "Item Count",
        "Subtotal",
        "Shipping",
        "Discount",
        "Other Fee",
        "Tax",
        "Import Fee",
        "Points",
        "Gift Card",
        "Total",
        "Invoice Status",
        "Invoice Status Message",
        "Validation Status",
        "Validation Message",
    ]

    with output_file.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as csvfile:

        writer = csv.DictWriter(
            csvfile,
            fieldnames=fieldnames,
        )
        writer.writeheader()

        for processed in invoices:
            invoice = processed["invoice"]
            header = invoice["header"]
            summary = invoice["summary"]

            writer.writerow({
                "Vendor":
                    header.get("vendor", ""),
                "Invoice #":
                    header.get("invoice_number", ""),
                "Invoice Date":
                    header.get("invoice_date", ""),
                "Source File":
                    processed["source_file"],
                "Item Count":
                    len(invoice["items"]),
                "Subtotal":
                    summary.get("subtotal", ""),
                "Shipping":
                    summary.get("shipping", ""),
                "Discount":
                    summary.get("discount", ""),
                "Other Fee":
                    summary.get("other_fee", ""),
                "Tax":
                    summary.get("tax", ""),
                "Import Fee":
                    summary.get("import_fee", ""),
                "Points":
                    summary.get("points", ""),
                "Gift Card":
                    summary.get("gift_card", ""),
                "Total":
                    summary.get("total", ""),
                "Invoice Status":
                    processed["status"],
                "Invoice Status Message":
                    processed["status_message"],
                "Validation Status":
                    processed["validation_status"],
                "Validation Message":
                    processed["validation_message"],
            })