# MGST — Masaram Gondi Script Transcription Tool

<p align="center">
  <strong>PDF/CSV glossary → MG Script · Hindi Pronunciation · Roman Gondi · Hindi अर्थ · English Meaning</strong>
</p>

<p align="center">
  <a href="https://github.com/startpage750/mgst">📦 GitHub Repository</a> ·
  <a href="https://github.com/startpage750/mgst#deploy-from-github">🚀 Deploy the Website</a>
</p>

A web tool and MCP server for converting a glossary PDF or CSV into a five-column Masaram Gondi glossary:

| MG Script | Hindi Pronunciation | Roman Gondi | Hindi अर्थ | English Meaning |
|---|---|---|---|---|

## What it does

- Reads a four-column glossary: Gondi word, Hindi pronunciation, Hindi meaning, English meaning.
- Converts the Gondi word to final Unicode Masaram Gondi.
- Generates Roman Gondi from the source spelling.
- Preserves Hindi pronunciation and both meanings.
- Exports PDF or UTF-8 CSV.
- Handles Masaram Gondi vowel signs, virama, dedicated conjuncts, repha, and ra-kara.
- Rejects the L2/15-090 Unicode proposal when uploaded as if it were a glossary.

## Run locally

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python web_app.py
```

Open `http://localhost:8000`. The server binds to `0.0.0.0` and uses the `PORT` environment variable, so it is ready for deployment.

## MCP server

```bash
python server.py
```

Call:

```text
transcribe_glossary(file_path, output_format="pdf"|"csv", output_path=None, gondi_font_path=None)
```

## Deploy from GitHub

1. Create a new empty GitHub repository.
2. Push this folder:

```bash
git init
git add .
git commit -m "Initial Masaram Gondi transcription tool"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
git push -u origin main
```

3. In Render, choose **New + Web Service**, connect the repository, and use:
   - Build command: `pip install -r requirements.txt`
   - Start command: `python web_app.py`
4. Or use the included `render.yaml` with Render Blueprint deployment.

GitHub Pages alone cannot run the Python PDF parser; GitHub stores the source while Render/Railway/Fly.io runs the web service.

## Font

For PDF output, set `GONDI_FONT_PATH` to a Masaram Gondi TTF on the deployment host. Without an appropriate font, the CSV remains correct but PDF viewers may show missing glyphs. Validate language-sensitive spellings with Gondi speakers before publishing.

## Tests

```bash
python -m pytest -q
```
