from typing import TypedDict

class InvoiceHeader(TypedDict, total=False):
    vendor: str
    invoice_number: str
    invoice_date: str
    status: str
    status_message: str

class InvoiceItem(TypedDict, total=False):
    item_id: str
    seller: str
    description: str
    quantity: int
    unit_price: float
    total: float
    status: str
    status_message: str

class InvoiceSummary(TypedDict, total=False):
    subtotal: float
    discount: float
    shipping: float
    tax: float
    total: float
    import_fee: float
    points: float
    gift_card: float
    status: str
    status_message: str

class ExtractedInvoiceData(TypedDict):
    header: InvoiceHeader
    items: list[InvoiceItem]
    summary: InvoiceSummary
    status: str
    status_message: str

class InvoiceData(TypedDict):
    header: InvoiceHeader
    items: list[InvoiceItem]
    summary: InvoiceSummary
    status: str
    status_message: str

class ProcessedInvoice(TypedDict):
    source_file: str
    invoice: InvoiceData
    validation_status: str
    validation_message: str
    status: str
    status_message: str

class InvoiceStats(TypedDict):
    total_invoices: int
    ready_invoices: int
    review_invoices: int
    error_invoices: int
    total_items: int
    unique_item_ids: int