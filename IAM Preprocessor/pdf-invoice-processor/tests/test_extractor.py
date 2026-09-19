import unittest
from pdf_invoice_processor.extractor import extract_event_header, identify_item_boundaries, assemble_wrapped_descriptions

class TestExtractor(unittest.TestCase):

    def test_extract_event_header(self):
        raw_text = "Invoice Number: 12345\nDate: 2023-10-01\n"
        expected_output = {
            "invoice_number": "12345",
            "date": "2023-10-01"
        }
        self.assertEqual(extract_event_header(raw_text), expected_output)

    def test_identify_item_boundaries(self):
        raw_text = "Item 1\nDescription of item 1\nQuantity: 2\nUnit Price: 10.00\nTotal: 20.00\n\nItem 2\nDescription of item 2\nQuantity: 1\nUnit Price: 15.00\nTotal: 15.00\n"
        expected_output = [
            {"description": "Description of item 1", "quantity": 2, "unit_price": 10.00, "total": 20.00},
            {"description": "Description of item 2", "quantity": 1, "unit_price": 15.00, "total": 15.00}
        ]
        self.assertEqual(identify_item_boundaries(raw_text), expected_output)

    def test_assemble_wrapped_descriptions(self):
        raw_descriptions = ["Description of item 1", "Description of item 2"]
        expected_output = "Description of item 1, Description of item 2"
        self.assertEqual(assemble_wrapped_descriptions(raw_descriptions), expected_output)

if __name__ == '__main__':
    unittest.main()