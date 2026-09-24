"""MCP server for Masaram Gondi glossary conversion."""
from __future__ import annotations
import base64, tempfile
from pathlib import Path
from typing import Optional
from mcp.server.fastmcp import FastMCP
from gondi_tool import convert_csv_to_csv, convert_pdf_to_csv, convert_to_pdf, normalize_rows, read_csv

mcp = FastMCP("masaram-gondi-transcriber")

def _make(source: Path, output: Path, output_format: str, font_path: Optional[str]):
    rows = read_csv(source) if source.suffix.lower()=='.csv' else __import__('gondi_tool').extract_pdf_tables(source)
    normalized = normalize_rows(rows)
    return convert_to_pdf(normalized, output, font_path) if output_format=='pdf' else __import__('gondi_tool').write_csv(normalized, output)

@mcp.tool()
def transcribe_glossary(file_path: str, output_format: str = "pdf", output_path: Optional[str] = None, gondi_font_path: Optional[str] = None) -> dict:
    """Convert a four-column glossary (Gondi, Hindi pronunciation, Hindi meaning, English meaning).
    Output columns: MG Script, Hindi Pronunciation, Roman Gondi, Hindi अर्थ, English Meaning.
    Input may be PDF or CSV; output_format is pdf or csv."""
    source=Path(file_path).expanduser().resolve()
    if not source.is_file() or source.suffix.lower() not in {'.pdf','.csv'}: raise ValueError('file_path must be an existing PDF or CSV')
    fmt=output_format.lower()
    if fmt not in {'pdf','csv'}: raise ValueError('output_format must be pdf or csv')
    output=Path(output_path).expanduser() if output_path else source.with_name(source.stem+'_masaram_gondi.'+fmt)
    return _make(source, output, fmt, gondi_font_path)

if __name__ == '__main__': mcp.run()
