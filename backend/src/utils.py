import os, io, docx
from pypdf import PdfReader
from pathlib import Path
from flask import request, current_app
from werkzeug.exceptions import InternalServerError

def extract_request_text():
    if "file" in request.files:
        file = request.files["file"]

        if file.filename != "":
            try:
                return extract_text(file, filename=file.filename)
            except Exception as e:
                current_app.logger.exception(f"Text extraction failed: {e}")
                raise InternalServerError("Failed to extract text from the uploaded file.")

    json_payload = request.get_json(silent=True) or {}

    return str(json_payload.get("text", "")).strip()

def extract_text(source, filename=None) -> str:
  if filename is None:
    if hasattr(source, 'name'):
      filename = source.name
    else:
      raise ValueError("Filename must be provided if source has no 'name' attribute.")
  
  ext = Path(filename).suffix.lower()
  
  if ext == '.pdf':
    if PdfReader is None: return "Error: pypdf not installed."
    return extract_text_from_pdf(source)
  
  elif ext in ['.txt', '.csv', '.json', '.log', '.md', '.xml']:
    return extract_text_from_txt(source)
  
  elif ext == '.docx': 
    if docx is None: return "Error: python-docx not installed."
    return extract_text_from_docx(source)
  else:
    raise ValueError(f"Unsupported file extension: {ext}")

def extract_text_from_pdf(source) -> str:
  if isinstance(source, (str, os.PathLike)):
    with open(source, 'rb') as f:
      reader = PdfReader(f)
      text = "\n".join((page.extract_text() or "") for page in reader.pages)
  else:
    if hasattr(source, 'seek'): source.seek(0)
    reader = PdfReader(source)
    text = "\n".join((page.extract_text() or "") for page in reader.pages)
  return text

def extract_text_from_txt(source) -> str:
  if isinstance(source, (str, os.PathLike)):
    with open(source, 'r', encoding='utf-8', errors='ignore') as f:
      text = f.read()
  else:
    if hasattr(source, 'seek'): source.seek(0)
    text = source.read().decode('utf-8', errors='replace')
  return text

def extract_text_from_docx(source) -> str:
  if isinstance(source, (str, os.PathLike)):
    doc = docx.Document(source)
  else:
    if hasattr(source, 'seek'): source.seek(0)
    doc = docx.Document(io.BytesIO(source.read()))
    
  text = "\n".join(paragraph.text for paragraph in doc.paragraphs)
  return text