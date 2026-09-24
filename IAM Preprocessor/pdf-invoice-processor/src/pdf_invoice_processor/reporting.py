from pathlib import Path
from .models import InvoiceStats


def print_session_summary(
        stats: InvoiceStats,
        artifacts: list[Path],
        output_path: Path,
) -> None:
    print("Batch processing complete")
    print(f"  Invoices processed: {stats['processed']}")
    print(f"  READY:             {stats['ready']}")
    print(f"  REVIEW:            {stats['review']}")
    print(f"  ERROR:             {stats['errors']}")
    print(f"  Item rows:         {stats['total_rows']}")
    print(f"  Unique Items by ID: {stats['unique_item_ids']}")

    print()
    print(f"Output files written to:", output_path)
    for artifact in artifacts:
        print(f"  Output artifact:   {artifact}")