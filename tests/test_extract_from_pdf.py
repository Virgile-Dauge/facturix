import pytest
from pathlib import Path
from extract_from_pdf import extraire_num_facture
from pypdf import PdfWriter

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter


def create_simple_pdf(output_filename, text):
    output_filename = str(output_filename)
    c = canvas.Canvas(output_filename, pagesize=letter)
    c.drawString(100, 750, text)
    c.save()
    
    return output_filename

@pytest.fixture
def pdf_with_num_facture(tmp_path):
    return create_simple_pdf(tmp_path / "facture_avec_num.pdf", "N° de facture : 12345678901234")

@pytest.fixture
def pdf_without_num_facture(tmp_path):
    return create_simple_pdf(tmp_path / "facture_sans_num.pdf", "N° de qweasfactuqwere : 123da9012eq34")

@pytest.fixture
def pdf_with_num_custom(tmp_path):
    return create_simple_pdf(tmp_path / "facture_avec_num_custom.pdf", "Facture Number: 98765432109876")

def test_extraire_num_facture_present(pdf_with_num_facture):
    num_facture = extraire_num_facture(pdf_with_num_facture)
    assert num_facture == "12345678901234"

def test_extraire_num_facture_absent(pdf_without_num_facture):
    num_facture = extraire_num_facture(pdf_without_num_facture)
    assert num_facture is None

def test_extraire_num_facture_custom_pattern(pdf_with_num_custom):
    custom_pattern = r'Facture Number\s*:\s*(\d{14})'
    num_facture = extraire_num_facture(pdf_with_num_custom, custom_pattern)
    assert num_facture == "98765432109876"

def test_extraire_num_facture_no_pages(tmp_path):
    pdf_path = tmp_path / "facture_vide.pdf"
    PdfWriter().write(pdf_path.open("wb"))

    with pytest.raises(IndexError):
        extraire_num_facture(pdf_path)

def test_extraire_num_facture_malformed_pdf(tmp_path):
    pdf_path = tmp_path / "malformed.pdf"
    pdf_path.write_bytes(b'%PDF-1.4\n%malformed')

    with pytest.raises(Exception):
        extraire_num_facture(pdf_path)