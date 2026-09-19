from typing import Pattern, TypedDict


class VendorConfig(TypedDict):
    vendor_name: str
    currency: str
    order_number_pattern: Pattern[str]
    order_date_pattern: Pattern[str]
    item_start_pattern: Pattern[str]
    quantity_pattern: Pattern[str]
    unit_price_pattern: Pattern[str]
    total_price_pattern: Pattern[str]
    summary_patterns: dict[str, Pattern[str]]