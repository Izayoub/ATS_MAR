import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ATS_MA.settings')
django.setup()
import sys
import os

# Forcer l'import du bon torch
torch_path = os.path.join(os.environ['VIRTUAL_ENV'], 'Lib', 'site-packages')
if torch_path not in sys.path:
    sys.path.insert(0, torch_path)

# Nettoyer tout mauvais import de torch
if 'torch' in sys.modules:
    del sys.modules['torch']

from ai_engine.services.cv_parser import CVParserService

import fitz  # PyMuPDF
import json


def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text


def main():
    parser = CVParserService()

    pdf_path = "AYOUB_IZEM_CV.pdf"
    cv_text = extract_text_from_pdf(pdf_path)

    result = parser.process(cv_text)

    print("=== Résultat parsing CV ===")
    print(json.dumps(result, indent=4, ensure_ascii=False))


if __name__ == "__main__":
    main()
