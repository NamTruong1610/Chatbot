# app/utils/file_parser.py
import os
from app.config.config import settings

def parse_file(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        return _parse_pdf(file_path)
    elif ext == ".docx":
        return _parse_docx(file_path)
    elif ext == ".txt":
        return _parse_txt(file_path)
    elif ext == ".json":
        return _parse_json(file_path)
    elif ext == ".html":
        return _parse_html(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")

def _parse_pdf(file_path: str) -> str:
    from unstructured.partition.pdf import partition_pdf
    elements = partition_pdf(filename=file_path)
    return "\n".join([str(e) for e in elements])

def _parse_docx(file_path: str) -> str:
    from unstructured.partition.docx import partition_docx
    elements = partition_docx(filename=file_path)
    return "\n".join([str(e) for e in elements])

def _parse_txt(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def _parse_json(file_path: str) -> str:
    import json
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    # Flatten JSON into readable text for embedding
    return json.dumps(data, indent=2)

def _parse_html(file_path: str) -> str:
    from bs4 import BeautifulSoup
    with open(file_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
    # Strip tags, return clean text
    return soup.get_text(separator="\n", strip=True)