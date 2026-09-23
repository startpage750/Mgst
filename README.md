# Gondi Glossary MCP Server

हिंदी अक्षरों में लिखे गए **गोंडी शब्दों** को **Masaram Gondi स्क्रिप्ट** में
ट्रांसलिटरेट करने और उनसे एक 3-कॉलम **PDF शब्द-कोश** (glossary) बनाने के लिए
MCP सर्वर।

आउटपुट PDF में हर शब्द की तीन जानकारी होती है:

| गोंडी लिपि | हिंदी उच्चारण | हिंदी अर्थ |
|---|---|---|
| (Masaram Gondi script) | (वही शब्द देवनागरी में) | (Hindi meaning) |

यह सर्वर साथ वाले **gondi-pdf** MCP सर्वर का पूरक (companion) है — वह पूरी
PDF किताब को layout-preserving तरीके से Gondi स्क्रिप्ट में बदलता है, जबकि
यह सर्वर **word-level शब्द-सूची / dictionary table** बनाता है — जैसे-जैसे
नई किताबों/पन्नों से नए शब्द मिलते जाएं, उन्हें इकट्ठा करके एक साफ़-सुथरी
शब्द-कोश PDF में ढालने के लिए उपयोगी।

## क्या-क्या शामिल है

```
gondi-glossary-mcp/
  server.py                   # MCP सर्वर (FastMCP), दो tools एक्सपोज़ करता है
  gondi_glossary/
    mapping.py                # Devanagari -> Masaram Gondi की पूरी mapping table
    translit.py                # शब्द/वाक्यांश transliteration इंजन
    pdf_builder.py              # raqm-shaped text rendering + PDF table बनाना
  requirements.txt
```

## Mapping कहाँ से आया

`mapping.py` की mapping भी उसी सिद्धांत पर बनी है जो साथ वाले **gondi-pdf**
प्रोजेक्ट में इस्तेमाल हुआ है — हर Devanagari अक्षर को Masaram Gondi Unicode
block (U+11D00–U+11D5F) के आधिकारिक Unicode Names से मिलाकर, यानी अंदाज़े
से नहीं। यह mapping सीधे 2015 के आधिकारिक Unicode encoding proposal
(**L2/15-090**, Anshuman Pandey) से बनाई गई और असली Noto Sans Masaram
Gondi फ़ॉन्ट के glyph-coverage से verify की गई है (सभी 75 characters मैच
करते हैं)। यह `gondi-pdf` वाले प्रोजेक्ट की `mapping.py` से **स्वतंत्र**
(independent) है — दोनों अलग-अलग बनी हैं।

कुछ characters के लिए Masaram Gondi में ठीक बराबर वर्ण नहीं है (स्वतंत्र
ऋ/ॠ/ऌ/ॡ, चंद्रबिंदु ँ, अवग्रह ऽ) — वहाँ नज़दीकी approximation होता है और हर
ऐसा केस **warning** के तौर पर लौटाया जाता है।

**र (RA) का खास ध्यान रखा गया है:** Masaram Gondi में conjunct के अंदर र
आम तरीके से नहीं, बल्कि दो अलग characters से लिखा जाता है —
- **REPHA** — जब र क्लस्टर के शुरू में हो (जैसे "मर्री" में)
- **RA-KARA** — जब र क्लस्टर के अंत में हो (जैसे "क्र" में)

यह logic Unicode proposal के section 4.8.1 के मुताबिक implement की गई है।

## Setup

```bash
cd gondi-glossary-mcp
pip install -r requirements.txt
```

### ज़रूरी फ़ॉन्ट (दोनों चाहिए)

1. **Masaram Gondi फ़ॉन्ट** — "Noto Sans Masaram Gondi":
   https://fonts.google.com/noto/specimen/Noto+Sans+Masaram+Gondi
2. **Devanagari फ़ॉन्ट** — "Noto Sans Devanagari" (या कोई भी Devanagari
   फ़ॉन्ट जैसे Mangal, Lohit Devanagari — कुछ common paths अपने-आप try
   होते हैं, पर स्पष्ट देना ज़्यादा भरोसेमंद है):
   https://fonts.google.com/noto/specimen/Noto+Sans+Devanagari

पाथ हर बार पास करने की बजाय environment variable में सेट कर दें:
```bash
export GONDI_FONT_PATH=/absolute/path/to/NotoSansMasaramGondi-Regular.ttf
export DEVANAGARI_FONT_PATH=/absolute/path/to/NotoSansDevanagari-Regular.ttf
```

### `raqm` (ज़रूरी — text shaping के लिए)

यह सर्वर Pillow के `raqm` layout engine (HarfBuzz + FriBidi) से टेक्स्ट
render करता है, ताकि संयुक्ताक्षर (conjuncts), मात्रा-पोज़िशनिंग, और
REPHA/RA-KARA सही जगह पर बनें। बिना इसके अक्षर अलग-अलग/ग़लत क्रम में दिख
सकते हैं। ज़्यादातर सिस्टम पर libraqm पहले से मौजूद pip-Pillow wheel में
आ जाता है; अगर `layout_engine=RAQM` की error आए तो:

- **Ubuntu/Debian:** `sudo apt install libraqm-dev` फिर `pip install --force-reinstall Pillow`
- **macOS (Homebrew):** `brew install raqm` फिर `pip install --force-reinstall Pillow`
- **Windows:** आमतौर पर आधिकारिक Pillow wheel में raqm पहले से बंडल होता है

## Claude Desktop में जोड़ना

`claude_desktop_config.json` में:

```json
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
```

Claude Desktop रीस्टार्ट करें, फिर बोलें जैसे: *"इन शब्दों की गोंडी शब्द-कोश
PDF बना दो: मावा=हमारा, तादो=दादा, ..."* या *"इस पैराग्राफ को गोंडी लिपि
में बदलकर PDF बना दो"* (पूरा paragraph paste करके)।

## Tools

- **`transliterate_to_gondi(text, use_dedicated_conjuncts=True)`**
  एक Devanagari शब्द/वाक्यांश को सीधे Masaram Gondi स्क्रिप्ट में बदलता है
  (बिना PDF बनाए) — टेस्टिंग/quick-check के लिए उपयोगी। Warnings भी लौटाता है।

- **`generate_gondi_glossary_pdf(words, output_path, gondi_font_path=None, devanagari_font_path=None, title=..., subtitle=None, use_dedicated_conjuncts=True)`**
  `words` की हर entry इनमें से एक हो सकती है:
  - `[गोंडी_शब्द, हिंदी_अर्थ]` — सामान्य row
  - `[गोंडी_शब्द, हिंदी_अर्थ, English]` — English gloss के साथ (अगर सूची
    में कहीं भी एक भी English value दी हो, तो पूरी टेबल में English
    कॉलम अपने-आप जुड़ जाता है)
  - `[शीर्षक]` — सिर्फ़ एक value वाली entry पूरी चौड़ाई का **category/
    section header row** बन जाती है (जैसे "Parts of Body", "Clothes",
    "Food" — लंबी सूची को अध्यायों में बांटने के लिए)

  ये तीनों तरह की entries एक ही सूची में मिलाई जा सकती हैं। हर शब्द को
  transliterate करता है, राक़्म (raqm) से सही shaping के साथ render
  करता है, table के रूप में PDF बनाकर `output_path`, `word_count`
  (section rows को छोड़कर गिनती), `warning_count`, और `warnings` (शब्द,
  अर्थ, और approximate हुए characters की सूची) लौटाता है।

- **`transliterate_paragraph_to_pdf(text, output_path, style="paragraph"|"table", include_devanagari=True, gondi_font_path=None, devanagari_font_path=None, title=..., subtitle=None, use_dedicated_conjuncts=True)`**
  पूरे पैराग्राफ/वाक्यों (एक साथ कई sentences) को Masaram Gondi में
  transliterate करके PDF बनाता है — शब्द-सूची नहीं, बल्कि **किताब के
  पन्ने जैसा running text**। वाक्यों में बांटने के लिए `। ॥ . ! ?` जैसे
  विराम-चिह्नों का इस्तेमाल होता है (चिह्न उसी वाक्य के अंत में जुड़ा
  रहता है)। दो layout उपलब्ध हैं:
  - `style="paragraph"` — Devanagari पैराग्राफ ऊपर, Masaram Gondi
    पैराग्राफ नीचे, दोनों अपने-आप word-wrap होकर पन्ने की चौड़ाई में
    फ़िट होते हैं (जैसे कोई पूरा अनुवादित पन्ना)।
  - `style="table"` — हर वाक्य एक अलग row में, 2 कॉलम (हिंदी मूल वाक्य |
    गोंडी लिपि), हर cell अपने-आप wrap होता है — तुलना करने के लिए
    सुविधाजनक।

  `include_devanagari=False` देने पर सिर्फ़ Gondi-script वाला हिस्सा
  बनता है (मूल हिंदी टेक्स्ट नहीं दिखाया जाता)। यह भी `word_count` की
  जगह `sentence_count`, और per-sentence warnings लौटाता है।

## सीधे टेस्ट करना (MCP client के बिना)

```bash
python3 -c "
from gondi_glossary import transliterate_text, build_glossary_pdf
print(transliterate_text('मर्री'))
build_glossary_pdf(
    vocab=[('मावा','हमारा'), ('तादो','दादा')],
    output_path='test.pdf',
    gondi_font_path='/path/to/NotoSansMasaramGondi-Regular.ttf',
    devanagari_font_path='/path/to/NotoSansDevanagari-Regular.ttf',
)
"
```

## जाँच की सलाह

चूंकि यह भाषा-संरक्षण का काम है, हर नई शब्द-सूची के बाद `warning_count`
ज़रूर देखें, और संयुक्ताक्षर वाले शब्दों (जिनमें ् हो) को कम से कम एक बार
किसी Gondi भाषी से confirm करवा लें — ख़ासकर र (रेफ/रकार) वाले शब्दों को,
क्योंकि इस mapping की testing सीमित PDF pages पर ही हुई है।

## gondi-pdf प्रोजेक्ट से अंतर

| | gondi-pdf | gondi-glossary (यह) |
|---|---|---|
| इनपुट | पूरी PDF किताब | शब्दों/अर्थों की सूची |
| आउटपुट | layout-preserving पूरा दस्तावेज़ | 3-कॉलम शब्द-कोश टेबल |
| उपयोग | किताब का पूरा अनुवाद | नए शब्द जमा करके dictionary बनाना |
