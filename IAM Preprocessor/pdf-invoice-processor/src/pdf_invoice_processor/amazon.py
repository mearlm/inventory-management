"""Amazon Printable Order Summary adapter (text-based PDFs)."""
import re
from decimal import Decimal
from datetime import datetime
from .models import ExtractedInvoiceData

MONEY = re.compile(r'^-?\$[\d,]+\.\d{2}$')
ITEM = re.compile(r'^(\d+) of:\s*(.*)$')
PAYMENT = re.compile(r'^(?P<method>.+? ending in (?P<last4>\d{4})):\s*(?P<date>[A-Za-z]+ \d{1,2}, \d{4}):\s*\$(?P<amount>[\d,]+\.\d{2})$')
SELLER = 'Sold by and invoiced on behalf of:'
IGNORED = ('Business Price', 'Condition:', 'Seller Credentials:', 'part 1 of ')

def money(s):
    return Decimal(s.replace('$', '').replace(',', '').strip())

def date(s):
    return datetime.strptime(s.strip(), '%B %d, %Y').date().isoformat()

def field(lines, label, required=True):
    for i, line in enumerate(lines):
        if line.startswith(label):
            remainder = line[len(label):].strip()
            if remainder:
                return money(remainder)
            if i + 1 < len(lines) and MONEY.fullmatch(lines[i + 1]):
                return money(lines[i + 1])
    if required:
        raise ValueError(f'Missing Amazon field: {label}')
    return Decimal('0.00')

def parse_items(lines):
    items = []
    i = 0
    while i < len(lines):
        m = ITEM.match(lines[i])
        if not m:
            i += 1
            continue
        qty = int(m.group(1))
        desc = [m.group(2)] if m.group(2) else []
        seller = ''
        price = None
        i += 1
        while i < len(lines):
            line = lines[i]
            if ITEM.match(line) or line.startswith('Shipping Address:'):
                break
            if line.startswith(SELLER):
                seller = line[len(SELLER):].strip().removesuffix('(seller profile)').strip()
            elif MONEY.fullmatch(line):
                if price is not None:
                    raise ValueError('Multiple item prices before next item')
                price = money(line)
            elif line.startswith(IGNORED) or line in ('Items Ordered', 'Price'):
                pass
            elif price is None and not seller:
                desc.append(line)
            i += 1
        if price is None:
            raise ValueError(f'Missing price for Amazon item: {" ".join(desc)}')
        items.append({'item_id': '', 'seller': seller, 'description': ' '.join(desc).strip(),
                      'quantity': qty, 'unit_price': price, 'total': price * qty,
                      'status': 'READY' if seller and desc else 'REVIEW',
                      'status_message': '' if seller and desc else 'Missing seller or description'})
    return items

def extract_amazon_invoice(raw_text: str) -> ExtractedInvoiceData:
    lines = [s.strip() for s in raw_text.splitlines() if s.strip()]
    match = re.search(r'Amazon\.com order number:\s*([\d-]+)', raw_text)
    if not match:
        raise ValueError('Not an Amazon Printable Order Summary: missing order number')
    order_number = match.group(1)
    placed = re.search(r'Order Placed:\s*([A-Za-z]+ \d{1,2}, \d{4})', raw_text)
    if not placed:
        raise ValueError('Missing order date')
    payment_index = next((i for i, s in enumerate(lines) if s == 'Payment information'), None)
    if payment_index is None:
        raise ValueError('Missing payment information section')
    payment_lines = lines[payment_index:]
    grand_total = field(payment_lines, 'Grand Total:')
    summary = {'subtotal': field(payment_lines, 'Item(s) Subtotal:'),
               'shipping': field(payment_lines, 'Shipping & Handling:'),
               'discount': field(payment_lines, 'Promotion applied:', required=False),
               'tax': field(payment_lines, 'Estimated Tax:'), 'total': grand_total,
               'status': 'READY', 'status_message': ''}
    sections = re.split(r'(?=^Shipped on [A-Za-z]+ \d{1,2}, \d{4}$)', '\n'.join(lines[:payment_index]), flags=re.M)
    items = []
    shipment_discounts = Decimal('0.00')
    shipment_total = Decimal('0.00')
    shipment_count = 0
    for section in sections:
        sec = section.splitlines()
        if not sec or not sec[0].startswith('Shipped on '):
            continue
        shipment_count += 1
        section_items = parse_items(sec)
        items.extend(section_items)
        subtotal = field(sec, 'Item(s) Subtotal:')
        shipping = field(sec, 'Shipping & Handling:')
        discount = field(sec, 'Promotion applied:', required=False)
        tax = field(sec, 'Sales Tax:')
        total = field(sec, 'Total for This Shipment:')
        if sum((x['total'] for x in section_items), Decimal('0.00')) != subtotal:
            raise ValueError(f'Shipment {shipment_count} item subtotal does not reconcile')
        if subtotal + shipping + discount + tax != total:
            raise ValueError(f'Shipment {shipment_count} total does not reconcile')
        shipment_discounts += discount
        shipment_total += total
    if not items:
        raise ValueError('No Amazon items found')
    if shipment_total != grand_total:
        raise ValueError(f'Shipments total {shipment_total} differs from order total {grand_total}')
    if shipment_discounts != summary['discount']:
        raise ValueError('Shipment promotions do not reconcile to order promotions')
    payments = []
    for line in payment_lines:
        match = PAYMENT.match(line)
        if match:
            payments.append({'payment_date': date(match.group('date')),
                             'payment_method': match.group('method'),
                             'last4': match.group('last4'),
                             'amount': Decimal(match.group('amount').replace(',', ''))})
    payment_total = sum((p['amount'] for p in payments), Decimal('0.00'))
    status = 'READY'
    message = ''
    if not payments or payment_total != grand_total:
        status = 'REVIEW'
        message = f'Payment transactions total {payment_total}; invoice total {grand_total}'
    return {'header': {'vendor': 'Amazon', 'invoice_number': order_number,
                       'invoice_date': date(placed.group(1)), 'status': 'READY', 'status_message': ''},
            'items': items, 'summary': summary, 'payments': payments,
            'status': status, 'status_message': message}
