import pymupdf


def read_pdf(file_path):
    """
     Reads a PDF file and
     extracts raw text data from all pages.
     
     Args:
         file_path (str): The path to the PDF file.
     
     Returns:
         str: The extracted text from the PDF.
    """

    with pymupdf.open(file_path) as document:
        return "\n".join(page.get_text() for page in document)