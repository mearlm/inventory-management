# PDF Invoice Processor

This project is designed to process PDF invoices using the PyMyPDF library. It extracts relevant data from PDF files, validates the information, and exports it in a structured CSV format.

## Features

- Read PDF files and extract raw text data.
- Identify and extract event/header fields and item-record boundaries.
- Assemble structured records including quantity, unit price, and total.
- Validate invoice arithmetic to ensure correctness.
- Export processed data to a CSV file.

## Project Structure

```
pdf-invoice-processor
├── README.md
├── requirements.txt
├── pyproject.toml
├── src
│   └── pdf_invoice_processor
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py
│       ├── config.py
│       ├── pdf_reader.py
│       ├── extractor.py
│       ├── parser.py
│       ├── validator.py
│       ├── csv_exporter.py
│       └── utils.py
├── tests
│   ├── __init__.py
│   ├── test_extractor.py
│   ├── test_parser.py
│   └── test_validator.py
└── data
    └── .gitkeep
```

## Installation

To install the required dependencies, run:

```
pip install -r requirements.txt
```

## Usage

To run the application, use the following command:

```
python -m pdf_invoice_processor
```

You can also use the command-line interface to interact with the application. For more details, refer to the documentation in `cli.py`.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.