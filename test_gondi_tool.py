from gondi_tool import masaram, normalize_rows


def test_final_unicode_block():
    assert all(0x11D00 <= ord(c) <= 0x11D59 for c in masaram("मावा"))


def test_dedicated_conjuncts():
    assert masaram("क्ष") == "𑴮"
    assert masaram("त्र") == "𑴰"


def test_ra_forms():
    assert masaram("क्र") == "𑴌𑵇"  # RA-KARA
    assert masaram("र्क") == "𑵆𑴌"  # REPHA


def test_five_column_schema():
    rows = normalize_rows([["Gondi", "Pronunciation", "Hindi meaning", "English meaning"], ["मावा", "मावा", "हमारा", "Our"]])
    assert rows[0] == ["MG Script", "Hindi Pronunciation", "Roman Gondi", "Hindi अर्थ", "English Meaning"]
    assert rows[1][2] == "mava"
