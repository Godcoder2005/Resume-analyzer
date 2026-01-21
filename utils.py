"""
Utility functions for Resume Analyzer
Contains file extraction and helper functions
"""


def extract_text_from_file(path: str) -> str:
    """
    Extract text from resume files (PDF, DOCX, HTML)
    
    Args:
        path: Path to the resume file
        
    Returns:
        Extracted text content
        
    Raises:
        ValueError: If file format is unsupported
    """
    with open(path, "rb") as f:
        header = f.read(20)

    # ---------- PDF ----------
    if header.startswith(b"%PDF"):
        try:
            from langchain_community.document_loaders import PyPDFLoader
            loader = PyPDFLoader(path)
            pages = loader.load()
            return "\n".join(p.page_content for p in pages)
        except Exception:
            # fallback only for REAL PDFs
            import pypdf
            reader = pypdf.PdfReader(path)
            return "\n".join(page.extract_text() or "" for page in reader.pages)

    # ---------- DOCX ----------
    elif header.startswith(b"PK"):
        from langchain_community.document_loaders import Docx2txtLoader
        pages = Docx2txtLoader(path).load()
        return "\n".join(p.page_content for p in pages)

    # ---------- HTML ----------
    elif b"<html" in header.lower():
        from langchain_community.document_loaders import BSHTMLLoader
        pages = BSHTMLLoader(path).load()
        return "\n".join(p.page_content for p in pages)

    else:
        raise ValueError("Unsupported or corrupted resume file")