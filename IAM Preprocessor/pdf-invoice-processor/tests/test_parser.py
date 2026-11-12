import unittest
from pdf_invoice_processor.parser import parse_invoice_data

class TestParser(unittest.TestCase):

    def setUp(self):
        self.sample_data = [
            {
                'raw_text': 'Item 1\nQuantity: 2\nUnit Price: 10.00\nTotal: 20.00',
                'expected': {
                    'item': 'Item 1',
                    'quantity': 2,
                    'unit_price': 10.00,
                    'total': 20.00
                }
            },
            {
                'raw_text': 'Item 2\nQuantity: 1\nUnit Price: 15.50\nTotal: 15.50',
                'expected': {
                    'item': 'Item 2',
                    'quantity': 1,
                    'unit_price': 15.50,
                    'total': 15.50
                }
            }
        ]

    def test_parse_invoice_data(self):
        for data in self.sample_data:
            result = parse_invoice_data(data['raw_text'])
            self.assertEqual(result, data['expected'])

if __name__ == '__main__':
    unittest.main()