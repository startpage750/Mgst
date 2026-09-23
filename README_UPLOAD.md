# PDF upload tool

This project now includes both an MCP tool and a lightweight browser upload app.

## Browser app

```bash
pip install -r requirements.txt
python web_app.py
```

Open `http://localhost:8000`, choose a text-based PDF, and download the converted PDF. Set `PORT=8080` to use another port. The app accepts files up to 25 MB.

## MCP tool

Run:

```bash
python server.py
```

The MCP tool is named `upload_pdf`. Set `output_format="csv"` to export one row per PDF page with the original text and Gondi transliteration. It accepts exactly one of:

- `pdf_path`: an existing local `.pdf` path
- `pdf_base64`: base64-encoded PDF bytes

Optional `output_path` and `title` arguments are supported. It returns the generated PDF path, page count, and file size.

## Notes

- The converter works with PDFs that contain extractable text. Scanned/image-only PDFs should be OCR'd first.
- Original extracted text and a Masaram Gondi transliteration are placed on each output page.
- A font with Masaram Gondi glyph coverage may be needed for correct display in the generated PDF viewer. The included mapping is a starter mapping; for language-preservation work, validate words and conjuncts against the project's complete mapping table.
