from .models import InvoiceData

def parse_data(extracted_data: InvoiceData) -> InvoiceData:
    items = extracted_data.get("items", [])
    structured_records = []

    for item in items:
        structured_records.append({
            "item_id": item.get("item_id", ""),
            "seller": item.get("seller", ""),
            "description": item.get("description", ""),
            "quantity": item.get("quantity"),
            "unit_price": item.get("unit_price"),
            "total": item.get("total"),
        })

    return {
        "header": extracted_data.get("header", {}),
        "items": structured_records,
        "summary": extracted_data.get("summary", {}),
    }
