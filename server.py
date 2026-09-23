"""
Gondi Glossary MCP server.

Exposes tools, over the Model Context Protocol, to transliterate
Devanagari (Hindi-spelled) Gondi words into Masaram Gondi script and to
build a 3-column PDF glossary (Gondi script | Hindi pronunciation |
Hindi meaning) from a word list.

This is a companion to the "gondi-pdf" MCP server (which converts whole
Devanagari PDF documents into Gondi script, preserving layout). This
server instead builds word-level GLOSSARY/DICTIONARY tables -- useful
for building up a Gondi-Hindi word list page by page as new source
material (grammar books, wordlists, etc.) is read.

Run directly for local testing:
    python server.py

Add to Claude Desktop (claude_desktop_config.json):
    {
      "mcpServers": {
        "gondi-glossary": {
          "command": "python",
          "args": ["/absolute/path/to/gondi-glossary-mcp/server.py"],
          "env": {
            "GONDI_FONT_PATH": "/absolute/path/to/NotoSansMasaramGondi-Regular.ttf",
            "DEVANAGARI_FONT_PATH": "/absolute/path/to/NotoSansDevanagari-Regular.ttf"
          }
        }
      }
    }
"""

import os
from typing import List, Optional, Tuple

from mcp.server.fastmcp import FastMCP

from gondi_glossary import transliterate_text, build_glossary_pdf, build_paragraph_pdf

mcp = FastMCP("gondi-glossary")

# Set these once via env vars so calls don't need to repeat the paths.
# Noto Sans Masaram Gondi: https://fonts.google.com/noto/specimen/Noto+Sans+Masaram+Gondi
# Noto Sans Devanagari:    https://fonts.google.com/noto/specimen/Noto+Sans+Devanagari
DEFAULT_GONDI_FONT_PATH = os.environ.get("GONDI_FONT_PATH", "")
DEFAULT_DEVANAGARI_FONT_PATH = os.environ.get("DEVANAGARI_FONT_PATH", "")


@mcp.tool()
def transliterate_to_gondi(text: str, use_dedicated_conjuncts: bool = True) -> dict:
    """Transliterate a Devanagari word or phrase into Masaram Gondi script.

    This is script transliteration (letter-for-letter, sound-preserving),
    NOT translation -- the output sounds the same, just written in
    Masaram Gondi letters instead of Devanagari.

    Args:
        text: a Devanagari word, or a space-separated multi-word phrase.
        use_dedicated_conjuncts: use Masaram Gondi's single dedicated
            letters for क्ष/ज्ञ/त्र instead of the mechanical
            consonant+virama+consonant sequence (default True).

    Returns:
        dict with the Gondi-script text and a list of warnings for any
        character with no exact Masaram Gondi equivalent (e.g. independent
        ऋ/ॠ/ऌ/ॡ, चंद्रबिंदु, अवग्रह) that had to be approximated -- review
        these against the source word.
    """
    gondi_text, warnings = transliterate_text(text, use_dedicated_conjuncts)
    return {
        "gondi_text": gondi_text,
        "warnings": [{"char": c, "reason": r} for c, r in warnings],
    }


@mcp.tool()
def generate_gondi_glossary_pdf(
    words: List[List[str]],
    output_path: str,
    gondi_font_path: Optional[str] = None,
    devanagari_font_path: Optional[str] = None,
    title: str = "गोंडी शब्द-कोश : गोंडी लिपि, हिंदी उच्चारण व अर्थ",
    subtitle: Optional[str] = None,
    use_dedicated_conjuncts: bool = True,
) -> dict:
    """Build a PDF glossary table: Gondi script | Hindi pronunciation
    (the Devanagari spelling of the Gondi word) | Hindi meaning
    [ | English, if provided].

    Each word is transliterated into Masaram Gondi script and rendered
    with proper text shaping (conjuncts, matra placement, REPHA/RA-KARA)
    via Pillow+raqm, then laid out as a table with reportlab.

    Args:
        words: list of entries, each one of:
            - [gondi_word, hindi_meaning] -- normal row, e.g. ["मावा", "हमारा"]
            - [gondi_word, hindi_meaning, english_meaning] -- normal row
              with an English gloss, e.g. ["तादो", "दादा", "Grandfather"].
              If ANY entry in the list has an English value, an English
              column is added to the whole table (others left blank).
            - [section_title] -- a single-element entry renders as a
              full-width category/section header row (e.g. for grouping
              a long list into "Parts of Body", "Clothes", "Food", ...),
              e.g. ["तक्ता-उंदी : Parts of Body"].
            2- and 3-element entries and section headers may be freely
            mixed in one list. Multi-word Gondi phrases (space-separated)
            are supported within gondi_word.
        output_path: where to write the PDF.
        gondi_font_path: path to a Masaram Gondi TTF/OTF. Required if
            GONDI_FONT_PATH is not set as an env var.
        devanagari_font_path: path to a Devanagari-capable TTF/OTF. If
            omitted, common system font locations are tried; set
            DEVANAGARI_FONT_PATH as an env var to avoid passing it
            every call.
        title: PDF heading text (Devanagari).
        subtitle: optional PDF subheading text (e.g. source citation).
        use_dedicated_conjuncts: see transliterate_to_gondi.

    Returns:
        dict with output_path, word_count (excludes section-header rows),
        warning_count, and up to 50 sample warnings (word, meaning,
        [(char, reason), ...]) -- review any flagged words against the
        source text or with a Gondi speaker.
    """
    font = gondi_font_path or DEFAULT_GONDI_FONT_PATH
    dev_font = devanagari_font_path or DEFAULT_DEVANAGARI_FONT_PATH or None

    out_dir = os.path.dirname(os.path.abspath(output_path))
    os.makedirs(out_dir, exist_ok=True)

    result = build_glossary_pdf(
        vocab=[tuple(w) for w in words],
        output_path=output_path,
        gondi_font_path=font,
        devanagari_font_path=dev_font,
        title=title,
        subtitle=subtitle,
        use_dedicated_conjuncts=use_dedicated_conjuncts,
    )
    result["warnings"] = [
        {"word": w, "meaning": m, "chars": [{"char": c, "reason": r} for c, r in warns]}
        for (w, m, warns) in result["warnings"]
    ]
    return result


@mcp.tool()
def transliterate_paragraph_to_pdf(
    text: str,
    output_path: str,
    style: str = "paragraph",
    include_devanagari: bool = True,
    gondi_font_path: Optional[str] = None,
    devanagari_font_path: Optional[str] = None,
    title: str = "गोंडी लिपि रूपांतरण",
    subtitle: Optional[str] = None,
    use_dedicated_conjuncts: bool = True,
) -> dict:
    """Transliterate a full Devanagari paragraph (multiple sentences) into
    Masaram Gondi script and lay it out as a PDF -- either flowing,
    word-wrapped paragraph text, or a sentence-by-sentence table.

    Unlike generate_gondi_glossary_pdf (word list -> dictionary table),
    this takes a full passage of running text (e.g. a paragraph copied
    from a book) and transliterates it sentence by sentence, splitting
    on Devanagari/Latin sentence-ending punctuation (। ॥ . ! ?).

    Args:
        text: the Devanagari paragraph (one or more sentences).
        output_path: where to write the PDF.
        style: "paragraph" -- flowing word-wrapped text (Devanagari
            block, then Gondi block below it, like a converted page);
            "table" -- a 2-column table, one row per sentence
            (हिंदी मूल वाक्य | गोंडी लिपि), each cell word-wrapped.
        include_devanagari: also show the original Devanagari text
            alongside the Gondi script. If False, only the Gondi-script
            rendering is produced (Gondi-only block, or single-column
            table).
        gondi_font_path: path to a Masaram Gondi TTF/OTF. Required if
            GONDI_FONT_PATH is not set as an env var.
        devanagari_font_path: path to a Devanagari-capable TTF/OTF; falls
            back to DEVANAGARI_FONT_PATH env var, then common system
            font locations.
        title / subtitle: PDF heading text (Devanagari).
        use_dedicated_conjuncts: see transliterate_to_gondi.

    Returns:
        dict with output_path, sentence_count, warning_count, and up to
        50 sample warnings (sentence, [(char, reason), ...]) -- review
        any flagged sentences against the source text or with a Gondi
        speaker.
    """
    font = gondi_font_path or DEFAULT_GONDI_FONT_PATH
    dev_font = devanagari_font_path or DEFAULT_DEVANAGARI_FONT_PATH or None

    out_dir = os.path.dirname(os.path.abspath(output_path))
    os.makedirs(out_dir, exist_ok=True)

    result = build_paragraph_pdf(
        text=text,
        output_path=output_path,
        gondi_font_path=font,
        devanagari_font_path=dev_font,
        title=title,
        subtitle=subtitle,
        style=style,
        include_devanagari=include_devanagari,
        use_dedicated_conjuncts=use_dedicated_conjuncts,
    )
    result["warnings"] = [
        {"sentence": s, "chars": [{"char": c, "reason": r} for c, r in warns]}
        for (s, warns) in result["warnings"]
    ]
    return result


if __name__ == "__main__":
    mcp.run()
