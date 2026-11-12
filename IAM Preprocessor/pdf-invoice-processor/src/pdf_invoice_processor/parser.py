from .models import ExtractedInvoiceData, InvoiceData


def parse_data(
    extracted_data: ExtractedInvoiceData
) -> InvoiceData:
    return extracted_data