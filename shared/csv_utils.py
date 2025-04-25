import csv
from io import StringIO
from typing import Dict, List


def generate_csv_template() -> str:
    """Generate a CSV template with headers and example row"""
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=[
        'product_id',
        'title',
        'description',
        'category',
        'price',
        'attributes'
    ])

    writer.writeheader()
    writer.writerow({
        'product_id': 'prod_123',
        'title': 'Wireless Headphones',
        'description': 'Noise cancelling Bluetooth headphones',
        'category': 'Electronics|Audio|Headphones',
        'price': '99.99',
        'attributes': "{'brand': 'Sony', 'color': 'black', 'wireless': True}"
    })

    return output.getvalue()


def validate_csv_format(file_content: str) -> bool:
    """Basic validation of CSV structure"""
    reader = csv.DictReader(StringIO(file_content))
    required_fields = {'product_id', 'title', 'category', 'price'}
    return required_fields.issubset(set(reader.fieldnames))