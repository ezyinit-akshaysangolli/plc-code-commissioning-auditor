import io
import pandas as pd
from pypdf import PdfReader

class UnsupportedFileError(Exception):
    """Custom exception raised when an invalid or unsupported file format is encountered."""
    pass

def parse_pdf(file_bytes: bytes) -> str:
    """Extracts raw string content from a PDF binary stream."""
    try:
        pdf_file = io.BytesIO(file_bytes)
        reader = PdfReader(pdf_file)
        text_content = []
        for index, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                text_content.append(page_text)
        return "\n".join(text_content)
    except Exception as error:
        raise ValueError(f"Failed to securely parse PDF document: {str(error)}")

def parse_spreadsheet(file_bytes: bytes, file_name: str) -> str:
    """Parses Excel and CSV files into standard textual row-by-row representations."""
    try:
        file_stream = io.BytesIO(file_bytes)
        if file_name.endswith('.csv'):
            dataframe = pd.read_csv(file_stream)
        else:
            dataframe = pd.read_excel(file_stream, engine='openpyxl')
        
        # Convert spreadsheet rows into explicit text representations for semantic RAG chunking
        string_buffer = io.StringIO()
        dataframe.to_csv(string_buffer, index=False)
        return string_buffer.getvalue()
    except Exception as error:
        raise ValueError(f"Structured dataset processing failure: {str(error)}")

def process_uploaded_document(file_bytes: bytes, file_name: str) -> str:
    """
    Validates file extensions and routes binary inputs to appropriate document parsers.
    Strictly intercepts unsupported formats (.jpg, .zip) using error handling guardrails.
    """
    lowercase_name = file_name.lower()
    
    # Explicit Extension Interception & Filtering (Requirement 1b & 6)
    if lowercase_name.endswith(('.jpg', '.jpeg', '.png')):
        raise UnsupportedFileError(
            f"Unsupported format: '{file_name.split('.')[-1]}'. Image parsing is not supported. "
            f"Please upload text-based PDF, CSV, Excel, or TXT documentation."
        )
    
    if lowercase_name.endswith(('.zip', '.rar', '.tar', '.gz')):
        raise UnsupportedFileError(
            f"Archived format detected: '{file_name.split('.')[-1]}'. Compressed bundles cannot be audited. "
            f"Please upload individual uncompressed text, spreadsheet, or PDF documents."
        )
    
    # Core Format Routing Logic (Requirement 1a)
    if lowercase_name.endswith('.pdf'):
        return parse_pdf(file_bytes)
    
    elif lowercase_name.endswith(('.csv', '.xlsx', '.xls')):
        return parse_spreadsheet(file_bytes, lowercase_name)
    
    elif lowercase_name.endswith('.txt'):
        return file_bytes.decode('utf-8', errors='ignore')
    
    else:
        raise UnsupportedFileError(
            f"Unknown extension: Code Auditor cannot read '{file_name}'. "
            f"Please verify file content matches PDF, TXT, CSV, or Excel formats."
        )
