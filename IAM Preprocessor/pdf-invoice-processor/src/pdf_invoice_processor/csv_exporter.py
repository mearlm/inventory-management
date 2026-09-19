import csv

def export_to_csv(data, output_file):
    """Exports the processed invoice data to a CSV file."""
    with open(output_file, mode='w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Item ID', 'Description', 'Quantity', 'Unit Price', 'Total']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for record in data["items"]:
            writer.writerow({
                'Item ID': record.get('item_id'),
                'Description': record.get('description'),
                'Quantity': record.get('quantity'),
                'Unit Price': record.get('unit_price'),
                'Total': record.get('total')
            })