import re
from decimal import Decimal
from shlex import join
from .models import InvoiceData
from .vendor_config import VendorConfig


def _parse_money(value: str) -> float:
    cleaned = value.replace("$", "").replace(",", "").strip()
    return Decimal(cleaned)

def _is_page_boilerplate(line: str, config: VendorConfig) -> bool:
    return any(
        re.fullmatch(pattern, line)
        for pattern in config.get("page_break_patterns", [])
    )

def extract_event_header(
    lines: list[str],
    config: VendorConfig,
    start_index: int,
) -> tuple[dict, int]:

    header = {
        "vendor": config["vendor_name"],
    }

    field_map = config["header_fields"]
    i = start_index

    while i < len(lines):
        line = lines[i]

        # Stop when we reach the item section.
        if line == "Item #":
            break

        for vendor_label, canonical_name in field_map.items():
            if line.startswith(vendor_label):
                value = line[len(vendor_label):].strip()
                header[canonical_name] = value
                break

        i += 1

    return header, i


def extract_items(
    lines: list[str],
    config: VendorConfig,
    start_index: int
) -> tuple[list[dict], int]:

    items = []
    summary_start: int | None = None

    item_start_pattern = re.compile(
        config["item_start_pattern"]
    )
    money_pattern = re.compile(
        r"^\$(?P<value>[\d,]+\.\d{2})$"
    )

    for i in range(start_index, len(lines) - 1):
        line = lines[i]

        # End of item section
        if line == "Payment Method":
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

        items.append({
            "item_id": item_id,
            "seller": seller,
            "description": " ".join(description_lines),
            "quantity": quantity,
            "unit_price": unit_price,
            "total": total,
        })

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
                items[-1]["description"] = (
                    items[-1]["description"].rstrip()
                    + " "
                    + continuation
                )

    return items, summary_start if summary_start is not None else len(lines)


def extract_summary(
    lines: list[str],
    config: VendorConfig,
    start_index: int
) -> tuple[list[dict], int]:

    summary = {}
    field_map = config["summary_fields"]

    for i in range(start_index, len(lines) - 1):
        line = lines[i]
        if line in field_map:
            summary[field_map[line]] = _parse_money(lines[i + 1])

    return summary, i


def extract_invoice_data(raw_text: str, config: VendorConfig) -> InvoiceData:
    lines = [
        line.strip()
        for line in raw_text.splitlines()
        if line.strip()
    ]

    header, i = extract_event_header(lines, config, 0)
    items, i = extract_items(lines, config, i)
    summary, i = extract_summary(lines, config, i)

    return {
        "header": header,
        "items": items,
        "summary": summary,
    }