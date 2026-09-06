from pathlib import Path

import pytest
from docx import Document
from PyPDF2 import PdfWriter

from src.document_reader import DocumentReadError, read_document, read_documents


def test_reads_supported_document_types(tmp_path: Path) -> None:
    text_path = tmp_path / "complaint.txt"
    text_path.write_text("Text complaint", encoding="utf-8")

    docx_path = tmp_path / "complaint.docx"
    document = Document()
    document.add_paragraph("DOCX complaint")
    document.save(docx_path)

    pdf_path = tmp_path / "complaint.pdf"
    PdfWriter().write(pdf_path)

    assert read_document(text_path).text == "Text complaint"
    assert read_document(docx_path).text == "DOCX complaint"
    assert read_document(pdf_path).text == ""


def test_unsupported_file_raises_clear_error(tmp_path: Path) -> None:
    csv_path = tmp_path / "complaint.csv"
    csv_path.write_text("not supported", encoding="utf-8")

    with pytest.raises(DocumentReadError, match="Unsupported document type"):
        read_document(csv_path)


def test_batch_reader_skips_bad_file(tmp_path: Path) -> None:
    (tmp_path / "good.txt").write_text("valid complaint", encoding="utf-8")
    (tmp_path / "bad.pdf").write_text("not a PDF", encoding="utf-8")

    documents, errors = read_documents(tmp_path)

    assert [document.source_path.name for document in documents] == ["good.txt"]
    assert len(errors) == 1
    assert "bad.pdf" in errors[0]