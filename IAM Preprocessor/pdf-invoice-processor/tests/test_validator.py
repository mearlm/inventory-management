import unittest
from pdf_invoice_processor.validator import validate_invoice

class TestValidator(unittest.TestCase):

    def test_valid_invoice(self):
        invoice_data = {
            'items': [
                {'description': 'Item 1', 'quantity': 2, 'unit_price': 50.00, 'total': 100.00},
                {'description': 'Item 2', 'quantity': 1, 'unit_price': 150.00, 'total': 150.00}
            ],
            'subtotal': 250.00,
            'tax': 25.00,
            'total': 275.00
        }
        self.assertTrue(validate_invoice(invoice_data))

    def test_invalid_invoice_total(self):
        invoice_data = {
            'items': [
                {'description': 'Item 1', 'quantity': 2, 'unit_price': 50.00, 'total': 100.00},
                {'description': 'Item 2', 'quantity': 1, 'unit_price': 150.00, 'total': 150.00}
            ],
            'subtotal': 250.00,
            'tax': 25.00,
            'total': 300.00  # Incorrect total
        }
        self.assertFalse(validate_invoice(invoice_data))

    def test_invalid_invoice_subtotal(self):
        invoice_data = {
            'items': [
                {'description': 'Item 1', 'quantity': 2, 'unit_price': 50.00, 'total': 100.00},
                {'description': 'Item 2', 'quantity': 1, 'unit_price': 150.00, 'total': 150.00}
            ],
            'subtotal': 240.00,  # Incorrect subtotal
            'tax': 25.00,
            'total': 265.00
        }
        self.assertFalse(validate_invoice(invoice_data))

if __name__ == '__main__':
    unittest.main()