"""Masaram Gondi glossary converter: PDF/CSV input -> PDF/CSV output."""
from __future__ import annotations
import csv, io, re
from pathlib import Path
from typing import Sequence

# Verified against the Masaram Gondi Unicode names in the supplied
# L2/15-090 proposal and the final Unicode block. The proposal uses provisional
# code points; production text must use U+11D00..U+11D59.
_CONSONANTS = "कखगघङचछजझञटठडढणतथदधनपफबभमयरलवशषसह"
_CONSONANT_CODES = [0x11D0C,0x11D0D,0x11D0E,0x11D0F,0x11D10,0x11D11,0x11D12,0x11D13,0x11D14,0x11D15,0x11D16,0x11D17,0x11D18,0x11D19,0x11D1A,0x11D1B,0x11D1C,0x11D1D,0x11D1E,0x11D1F,0x11D20,0x11D21,0x11D22,0x11D23,0x11D24,0x11D25,0x11D26,0x11D27,0x11D28,0x11D29,0x11D2A,0x11D2B,0x11D2C]
_MAP = dict(zip(_CONSONANTS, map(chr, _CONSONANT_CODES)))
_MAP.update({
    "अ":"\U00011D00", "आ":"\U00011D01", "इ":"\U00011D02", "ई":"\U00011D03", "उ":"\U00011D04", "ऊ":"\U00011D05", "ए":"\U00011D06", "ऐ":"\U00011D08", "ओ":"\U00011D09", "औ":"\U00011D0B",
    "ा":"\U00011D31", "ि":"\U00011D32", "ी":"\U00011D33", "ु":"\U00011D34", "ू":"\U00011D35", "ृ":"\U00011D36", "े":"\U00011D3A", "ै":"\U00011D3C", "ो":"\U00011D3D", "ौ":"\U00011D3F",
    "ं":"\U00011D40", "ः":"\U00011D41", "ँ":"\U00011D40", "्":"\U00011D45", "़":"\U00011D42", "ॅ":"\U00011D3A\U00011D43", "ॉ":"\U00011D3D\U00011D43", "।":"।", "॥":"॥",
})
_DEDICATED = {"क्ष":"\U00011D2E", "ज्ञ":"\U00011D2F", "त्र":"\U00011D30"}
_REPHA, _RAKARA = chr(0x11D46), chr(0x11D47)
_ROMAN = {
    "अ":"a","आ":"aa","इ":"i","ई":"ii","उ":"u","ऊ":"uu","ए":"e","ऐ":"ai","ओ":"o","औ":"au",
    "क":"k","ख":"kh","ग":"g","घ":"gh","ङ":"ng","च":"ch","छ":"chh","ज":"j","झ":"jh","ञ":"ny",
    "ट":"t","ठ":"th","ड":"d","ढ":"dh","ण":"n","त":"t","थ":"th","द":"d","ध":"dh","न":"n",
    "प":"p","फ":"ph","ब":"b","भ":"bh","म":"m","य":"y","र":"r","ल":"l","व":"v","श":"sh","ष":"sh","स":"s","ह":"h",
    "ा":"aa","ि":"i","ी":"ii","ु":"u","ू":"uu","े":"e","ै":"ai","ो":"o","ौ":"au","ं":"n","ँ":"n","ः":"h","्":"",
}

def masaram(text: str) -> str:
    """Transliterate Devanagari to final Unicode Masaram Gondi.

    Handles the three dedicated conjunct letters and the proposal's special
    repha/ra-kara behavior instead of emitting a generic Devanagari halant.
    """
    text = re.sub(r"क्ष", _DEDICATED["क्ष"], text)
    text = re.sub(r"ज्ञ", _DEDICATED["ज्ञ"], text)
    text = re.sub(r"त्र", _DEDICATED["त्र"], text)
    out, i = [], 0
    while i < len(text):
        ch = text[i]
        # r + virama + consonant: cluster-initial r is a repha.
        if ch == "र" and i + 2 < len(text) and text[i + 1] == "्" and text[i + 2] in _MAP:
            out.extend([_REPHA, _MAP[text[i + 2]]]); i += 3; continue
        # consonant + virama + r: cluster-final r is RA-KARA.
        if ch in _MAP and i + 2 < len(text) and text[i + 1] == "्" and text[i + 2] == "र":
            out.extend([_MAP[ch], _RAKARA]); i += 3; continue
        out.append(_MAP.get(ch, ch)); i += 1
    return "".join(out)

def roman_gondi(text: str) -> str:
    # Readable Latin transliteration for the source Gondi/Hindi spelling.
    out = "".join(_ROMAN.get(ch, ch) for ch in text)
    out = re.sub(r"([aeiou])a", r"\1", out)
    return out

def normalize_rows(rows: Sequence[Sequence[str]]) -> list[list[str]]:
    rows = [[str(x or "").strip() for x in row] for row in rows if any(str(x or "").strip() for x in row)]
    if not rows: raise ValueError("No glossary rows found")
    header = rows[0]
    # If the source has no header, still produce a predictable schema.
    header_text = " ".join(header).lower()
    has_header = any(x in header_text for x in ("अर्थ", "meaning", "pron", "gondi", "शब्द"))
    data = rows[1:] if has_header else rows
    if len(header) < 4: header = ["Gondi Word", "Hindi Pronunciation", "Hindi Meaning", "English Meaning"]
    if len(header) > 4: header = header[:4]
    output = [["MG Script", "Hindi Pronunciation", "Roman Gondi", "Hindi अर्थ", "English Meaning"]]
    for row in data:
        row = (row + [""] * 4)[:4]
        output.append([masaram(row[0]), row[1], roman_gondi(row[0]), row[2], row[3]])
    return output

def read_csv(path: Path) -> list[list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f: return list(csv.reader(f))

def write_csv(rows: Sequence[Sequence[str]], path: Path) -> dict:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f: csv.writer(f).writerows(rows)
    return {"output_path": str(path.resolve()), "row_count": max(0, len(rows)-1), "format": "csv"}

def extract_pdf_tables(path: Path) -> list[list[str]]:
    import pdfplumber
    rows = []
    with pdfplumber.open(str(path)) as pdf:
        first_page_text = pdf.pages[0].extract_text() or "" if pdf.pages else ""
        if "Proposal to Encode the Masaram Gondi Script" in first_page_text:
            raise ValueError("This is the Masaram Gondi Unicode reference proposal, not a glossary. Upload the glossary PDF containing the word, pronunciation, Hindi meaning, and English meaning columns.")
        for page in pdf.pages:
            for table in (page.extract_tables() or []):
                for row in table: rows.append([cell or "" for cell in row])
    if not rows: raise ValueError("No table found. Use a text PDF with a clear table, or upload CSV.")
    return rows

def convert_pdf_to_csv(source: Path, destination: Path) -> dict:
    return write_csv(normalize_rows(extract_pdf_tables(source)), destination)

def convert_csv_to_csv(source: Path, destination: Path) -> dict:
    return write_csv(normalize_rows(read_csv(source)), destination)

def convert_to_pdf(rows: Sequence[Sequence[str]], destination: Path, font_path: str | None = None) -> dict:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
    if font_path and Path(font_path).is_file(): pdfmetrics.registerFont(TTFont("Gondi", font_path)); font = "Gondi"
    else: font = "Helvetica"
    styles = getSampleStyleSheet(); cell = ParagraphStyle("cell", parent=styles["BodyText"], fontName=font, fontSize=8.5, leading=11)
    table = Table([[Paragraph(str(x).replace("&","&amp;"), cell) for x in row] for row in rows], colWidths=[38*mm, 35*mm, 35*mm, 40*mm, 40*mm], repeatRows=1)
    table.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#243b63")),("TEXTCOLOR",(0,0),(-1,0),colors.white),("GRID",(0,0),(-1,-1),.35,colors.HexColor("#b9c4d0")),("VALIGN",(0,0),(-1,-1),"TOP"),("LEFTPADDING",(0,0),(-1,-1),5),("RIGHTPADDING",(0,0),(-1,-1),5)]))
    destination.parent.mkdir(parents=True, exist_ok=True)
    SimpleDocTemplate(str(destination), pagesize=landscape(A4), rightMargin=10*mm,leftMargin=10*mm,topMargin=10*mm,bottomMargin=10*mm).build([table])
    return {"output_path": str(destination.resolve()), "row_count": len(rows)-1, "format": "pdf"}
