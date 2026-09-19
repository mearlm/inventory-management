from typing import TypedDict


class InvoiceHeader(TypedDict):
    vendor: str
    invoice_number: str
    invoice_date: str


class InvoiceItem(TypedDict):
    item_id: str
    seller: str
    description: str
    quantity: int
    unit_price: float
    total: float


class InvoiceSummary(TypedDict):
    subtotal: float
    discount: float
    shipping: float
    tax: float
    total: float


class InvoiceData(TypedDict):
    header: InvoiceHeader
    items: list[InvoiceItem]
    summary: InvoiceSummary