from pdf_invoice_processor.process_invoice import process_invoice
from .vendor_config import VendorConfig
from .models import ProcessedInvoice, InvoiceStats

def process_batch(
    input_files: list[str],
    config: VendorConfig,
) -> tuple[list[ProcessedInvoice], InvoiceStats]:

    invoices: list[ProcessedInvoice] = []

    stats: InvoiceStats = {
        "processed": 0,
        "ready": 0,
        "review": 0,
        "errors": 0,
        "total_rows": 0,
        "unique_item_ids": 0,
    }
    
    for input_file in input_files:
        invoice: ProcessedInvoice = process_invoice(input_file, config)
        invoices.append(invoice)

        stats["processed"] += 1
        stats["total_rows"] += len(invoice["invoice"]["items"])

        status = invoice["status"]

        if status == "READY":
            stats["ready"] += 1
        elif status == "REVIEW":
            stats["review"] += 1
        else:
            stats["errors"] += 1

    stats["unique_item_ids"] = len({
        item["item_id"]
        for processed in invoices
        for item in processed["invoice"]["items"]
        if item.get("item_id")
    })

    invoices.sort(
        key=lambda processed: (
            processed["invoice"]["header"].get("invoice_date", ""),
            processed["invoice"]["header"].get("invoice_number", ""),
        )
    )

    return invoices, stats