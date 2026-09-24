from decimal import Decimal
from .models import InvoiceData


def validate_invoice(invoice_data: InvoiceData) -> tuple[bool, str]:
    total_calculated = Decimal("0.00")

    for item in invoice_data.get("items", []):
        quantity = item.get("quantity", 0)
        unit_price = item.get("unit_price", Decimal("0.00"))
        total = item.get("total", Decimal("0.00"))

        expected_total = Decimal(quantity) * unit_price
        total_calculated += total

        if total != expected_total:
            return False, (
                f"Item {item.get('item_id', '<unknown>')}: "
                f"line total {total} != expected {expected_total}"
            )

    summary = invoice_data.get("summary", {})

    subtotal = summary.get("subtotal", Decimal("0.00"))

    if total_calculated != subtotal:
        return False, (
            f"Invoice subtotal mismatch: "
            f"sum of item totals {total_calculated} != subtotal {subtotal}"
        )

    expected_invoice_total = (
        summary.get("subtotal", Decimal("0.00"))
        + summary.get("shipping", Decimal("0.00"))
        + summary.get("discount", Decimal("0.00"))
        + summary.get("other_fee", Decimal("0.00"))
        + summary.get("import_fee", Decimal("0.00"))
        + summary.get("tax", Decimal("0.00"))
        + summary.get("points", Decimal("0.00"))
        + summary.get("gift_card", Decimal("0.00"))
    )

    invoice_total = summary.get("total", Decimal("0.00"))

    if expected_invoice_total != invoice_total:
        return False, (
            f"Invoice total mismatch: "
            f"calculated {expected_invoice_total} != reported {invoice_total}"
        )

    return True, ""