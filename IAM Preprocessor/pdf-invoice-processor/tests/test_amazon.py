import unittest
from decimal import Decimal
from pathlib import Path
from pdf_invoice_processor.amazon import extract_amazon_invoice
from pdf_invoice_processor.pdf_reader import read_pdf
from pdf_invoice_processor.validator import validate_invoice

SAMPLE = Path(__file__).parent / 'data' / 'amazon' / 'sample.pdf'

class TestAmazon(unittest.TestCase):
    def test_sample_order(self):
        invoice = extract_amazon_invoice(read_pdf(str(SAMPLE)))
        self.assertEqual(len(invoice['items']), 39)
        self.assertEqual(invoice['summary']['subtotal'], Decimal('1552.11'))
        self.assertEqual(invoice['summary']['discount'], Decimal('-4.20'))
        self.assertEqual(invoice['summary']['total'], Decimal('1547.91'))
        self.assertEqual(len(invoice['payments']), 3)
        self.assertEqual(sum(p['amount'] for p in invoice['payments']), Decimal('1547.91'))
        self.assertTrue(all(item['item_id'] == '' for item in invoice['items']))
        self.assertEqual(validate_invoice(invoice), (True, ''))

if __name__ == '__main__':
    unittest.main()
