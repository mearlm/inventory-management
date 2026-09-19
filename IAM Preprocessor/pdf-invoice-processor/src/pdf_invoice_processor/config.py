# Configuration settings for the PDF invoice processor

VENDOR_CONFIG = {
    "vendor_name": "Your Vendor Name",
    "item_id_pattern": r"\bITEM\s+\d+\b",  # Regex pattern for identifying item IDs
    "currency": "USD",  # Default currency
    "quantity_pattern": r"\b\d+\b",  # Regex pattern for identifying quantities
    "unit_price_pattern": r"\$\d+(\.\d{2})?",  # Regex pattern for identifying unit prices
    "total_pattern": r"Total:\s*\$?\d+(\.\d{2})?",  # Regex pattern for identifying totals
}