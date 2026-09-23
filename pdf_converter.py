"""PDF extraction and simple Masaram Gondi PDF generation."""
from __future__ import annotations

from pathlib import Path
import csv
import io
from typing import Iterable

from pypdf import PdfReader
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak

# Devanagari letters to the corresponding Masaram Gondi code points.
# The table intentionally covers common Hindi text; unsupported symbols remain
# unchanged so that punctuation and numbers are not silently lost.
_CONSONANTS = "कखगघङचछजझञटठडढणतथदधनपफबभमयरलवशषसह"
_GONDI_CONSONANTS = [chr(x) for x in range(0x11D0A, 0x11D0A + len(_CONSONANTS))]
_VOWELS = {
    "अ": "\U00011D00", "आ": "\U00011D01", "इ": "\U00011D02", "ई": "\U00011D03",
    "उ": "\U00011D04", "ऊ": "\U00011D05", "ए": "\U00011D06", "ऐ": "\U00011D07",
    "ओ": "\U00011D08", "औ": "\U00011D09",
}
_MATRAS = {"ा": "\U00011D01", "ि": "\U00011D02", "ी": "\U00011D03", "ु": "\U00011D04",
           "ू": "\U00011D05", "े": "\U00011D06", "ै": "\U00011D07", "ो": "\U00011D08",
           "ौ": "\U00011D09", "ं": "\U00011D5A", "ः": "\U00011D5B", "ँ": "\U00011D5A"}
_MAP = dict(zip(_CONSONANTS, _GONDI_CONSONANTS)) | _VOWELS | _MATRAS
_MAP.update({"्": "\U00011D44", "़": "", "।": "।", "॥": "॥"})


def transliterate(text: str) -> str:
    """Convert Devanagari characters while preserving whitespace and punctuation."""
    return "".join(_MAP.get(char, char) for char in text)


def convert_csv(source: Path, destination: Path, encoding: str = "utf-8-sig") -> dict:
    """Copy a CSV while adding a Gondi transliteration column for each text cell."""
    with source.open("r", encoding=encoding, newline="") as handle:
        rows = list(csv.reader(handle))
    if not rows:
        raise ValueError("The CSV file is empty")
    header = rows[0]
    if not header:
        raise ValueError("The CSV file has no columns")
    output_rows = [header + ["Masaram Gondi"]]
    for row in rows[1:]:
        if not row or not any(cell.strip() for cell in row):
            continue
        source_text = " | ".join(row)
        output_rows.append(row + [transliterate(source_text)])
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8-sig", newline="") as handle:
        csv.writer(handle).writerows(output_rows)
    return {"output_path": str(destination.resolve()), "row_count": len(output_rows) - 1, "bytes": destination.stat().st_size}


def pdf_to_csv(source: Path, destination: Path) -> dict:
    """Extract one CSV row per PDF page: page number, original, and Gondi text."""
    reader = PdfReader(str(source))
    rows = [["Page", "Original text", "Masaram Gondi"]]
    for index, page in enumerate(reader.pages, 1):
        text = (page.extract_text() or "").strip()
        rows.append([index, text, transliterate(text)])
    if len(rows) == 1:
        raise ValueError("No pages were found in the PDF")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8-sig", newline="") as handle:
        csv.writer(handle).writerows(rows)
    return {"output_path": str(destination.resolve()), "page_count": len(rows) - 1, "bytes": destination.stat().st_size}


def convert_pdf(source: Path, destination: Path, title: str = "Gondi PDF") -> dict:
    reader = PdfReader(str(source))
    pages = [(page.extract_text() or "").strip() for page in reader.pages]
    if not any(pages):
        raise ValueError("No extractable text was found. This PDF may be scanned; OCR it first.")
    destination.parent.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet()
    devanagari = ParagraphStyle("devanagari", parent=styles["BodyText"], fontSize=11, leading=16, spaceAfter=5)
    gondi = ParagraphStyle("gondi", parent=styles["BodyText"], fontSize=13, leading=18, spaceAfter=12)
    heading = ParagraphStyle("heading", parent=styles["Title"], fontSize=18, leading=23, spaceAfter=12)
    story = [Paragraph(title, heading)]
    for index, text in enumerate(pages, 1):
        safe_original = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        safe_gondi = transliterate(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        story.extend([Paragraph(f"Page {index}", styles["Heading3"]), Paragraph(safe_original.replace("\n", "<br/>"), devanagari), Paragraph(safe_gondi.replace("\n", "<br/>"), gondi)])
        if index != len(pages):
            story.append(PageBreak())
    doc = SimpleDocTemplate(str(destination), pagesize=A4, rightMargin=18*mm, leftMargin=18*mm, topMargin=16*mm, bottomMargin=16*mm)
    doc.build(story)
    return {"output_path": str(destination.resolve()), "page_count": len(pages), "bytes": destination.stat().st_size}
