from pathlib import Path

from .exporter import export_activity_headers, export_activity_lines
from .models import ProcessedInvoice

def publish_batch(
    invoices: list[ProcessedInvoice],
    output_path: Path,
) -> list[Path]:

    output_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    header_file = output_path / "activity_headers.csv"
    line_file = output_path / "activity_lines.csv"

    export_activity_headers(
        invoices,
        header_file,
    )

    export_activity_lines(
        invoices,
        line_file,
    )

    return [
        header_file,
        line_file,
    ]