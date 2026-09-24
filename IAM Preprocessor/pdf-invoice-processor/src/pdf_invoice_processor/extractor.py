import re
from decimal import Decimal
from shlex import join
from .models import ExtractedInvoiceData, InvoiceHeader, InvoiceItem, InvoiceSummary
from .vendor_config import VendorConfig
from .status import rollup_status, add_status_message, build_component_status_message


def _parse_money(value: str) -> float:
    cleaned = value.replace("$", "").replace(",", "").strip()
    return Decimal(cleaned)

def _is_page_boilerplate(line: str, config: VendorConfig) -> bool:
    return any(
        re.fullmatch(pattern, line)
        for pattern in config.get("page_break_patterns", [])
    )

# return the header dictionary, the index of the item-section start, and optionally the index of the summary-section start
def extract_event_header(
    lines: list[str],
    config: VendorConfig,
    start_index: int,
) -> tuple[InvoiceHeader, int | None, int | None]:

    header: InvoiceHeader = {
        "vendor": config["vendor_name"],
        "status": "READY",
        "status_message": "",
    }

    field_map = config["header_fields"]

    item_start = None
    summary_start = None

    i = start_index

    while i < len(lines):
        line = lines[i]

        # found start of item section, note the index
        if item_start is None and line == "Item #":
            item_start = i
            break

        # found start of summary section, note the index
        if summary_start is None and line == "Payment Method":
            summary_start = i

        for vendor_label, canonical_name in field_map.items():
            if line.startswith(vendor_label):
                value = line[len(vendor_label):].strip()
                header[canonical_name] = value
                break

        i += 1

    required_header_fields = {
        "vendor",
    } | set(field_map.values())

    missing = required_header_fields - header.keys()
    if missing:
        header["status"] = "REVIEW"
        header["status_message"] = (
            f"Missing summary fields: {', '.join(sorted(missing))}"
        )

    return header, item_start, summary_start


def extract_items(
    lines: list[str],
    config: VendorConfig,
    start_index: int,
    summary_start: int | None
) -> tuple[list[InvoiceItem], int]:

    items = []

    item_start_pattern = re.compile(
        config["item_start_pattern"]
    )
    money_pattern = re.compile(
        r"^\$(?P<value>[\d,]+\.\d{2})$"
    )
    critical_fields = {
        "item_id",
        "quantity",
        "unit_price",
        "total",
    }
    review_fields = {
        "seller",
        "description",
    }

    for i in range(start_index, len(lines) - 1):
        line = lines[i]

        # found start of summary section, note the index
        if summary_start is None and line == "Payment Method":
            summary_start = i
            continue

        item_match = item_start_pattern.match(line)
        if not item_match:
            continue

        item_id = item_match.group("item_id")
        i += 1

        seller = lines[i]
        i += 1

        description_lines = []

        while i < len(lines):
            # Quantity is followed by unit price and total price.
            if (
                re.fullmatch(r"\d+", lines[i])
                and i + 2 < len(lines)
                and money_pattern.match(lines[i + 1])
                and money_pattern.match(lines[i + 2])
            ):
                break

            description_lines.append(lines[i])
            i += 1

        quantity = int(lines[i])
        unit_price = _parse_money(lines[i + 1])
        total = _parse_money(lines[i + 2])

        item = {
            "item_id": item_id,
            "seller": seller,
            "description": " ".join(description_lines),
            "quantity": quantity,
            "unit_price": unit_price,
            "total": total,
            "status": "READY",
            "status_message": "",
        }
        items.append(item)

        i += 3

        continuation_lines = []
        j = i

        # Skip known page-break boilerplate.
        while (
            j < len(lines)
            and _is_page_boilerplate(lines[j], config)
        ):
            j += 1

        # If what follows is neither a new item nor a known section label,
        # treat it as continuation text for the item just completed.
        while j < len(lines):
            if item_start_pattern.match(lines[j]):
                break

            if lines[j] in config.get("section_labels", []):
                break

            continuation_lines.append(lines[j])
            j += 1

        if continuation_lines:
            continuation = " ".join(continuation_lines).strip()
            if continuation:
                item["description"] = (
                    item["description"].rstrip()
                    + " "
                    + continuation
                )

        missing_critical = {
            field
            for field in critical_fields
            if item.get(field) is None
        }
        missing_review = {
            field
            for field in review_fields
            if not item.get(field)
        }

        if missing_review:
            item["status"] = "REVIEW"
            add_status_message(
                item,
                f"Missing descriptive fields: {', '.join(sorted(missing_review))}"
            )

        if missing_critical:
            item["status"] = "ERROR"
            add_status_message(
                item,
                f"Missing required fields: {', '.join(sorted(missing_critical))}"
            )

    return items, summary_start if summary_start is not None else len(lines)
    

def extract_summary(
    lines: list[str],
    config: VendorConfig,
    start_index: int,
) -> tuple[InvoiceSummary, int]:

    summary: InvoiceSummary = {
        "status": "READY",
        "status_message": "",
    }

    field_map = config["summary_fields"]

    i = start_index

    for i in range(start_index, len(lines) - 1):
        line = lines[i]

        if line in field_map:
            summary[field_map[line]] = _parse_money(lines[i + 1])

    required_summary_fields = {
        "subtotal",
        "shipping",
        "discount",
        "other_fee",
        "tax",
        "total",
    }
    missing = required_summary_fields - summary.keys()
    if missing:
        summary["status"] = "REVIEW"
        summary["status_message"] = (
            f"Missing summary fields: {', '.join(sorted(missing))}"
        )

    return summary, i


def extract_invoice_data(raw_text: str, config: VendorConfig) -> ExtractedInvoiceData:
    lines = [
        line.strip()
        for line in raw_text.splitlines()
        if line.strip()
    ]

    header, item_start, summary_start = extract_event_header(
        lines, config, 0
    )

    items, discovered_summary_start = extract_items(
        lines,
        config,
        item_start if item_start is not None else 0,
        summary_start,
    )
    item_status = rollup_status(
        *(item.get("status", "READY") for item in items)
    )

    if summary_start is None:
        summary_start = discovered_summary_start

    summary, _ = extract_summary(
        lines,
        config,
        summary_start if summary_start is not None else 0,
    )

    return {
        "header": header,
        "items": items,
        "summary": summary,
        "status": rollup_status(
            header["status"],
            item_status,
            summary.get("status", "READY"),
        ),
        "status_message": build_component_status_message(
            header["status_message"],
            item_status,
            summary["status_message"],
        ),
    }