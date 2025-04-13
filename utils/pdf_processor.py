"""Utilities for processing PDF documents."""

import os
import pdfplumber
import tempfile

def extract_text_from_pdf(pdf_path):
    """Extract text content from a PDF file."""
    text = ""
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
    
    return text

def save_uploaded_pdf(uploaded_file):
    """Save an uploaded PDF file temporarily and return the path."""
    if uploaded_file is None:
        return None
        
    # Create a temporary file to store the PDF
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, uploaded_file.name)
    
    # Write the file
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    return temp_path