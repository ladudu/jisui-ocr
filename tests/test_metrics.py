from jisui.metrics import cer
from jisui.textnorm import normalize


def test_normalize_strips_aozora_ruby_and_notes():
    src = "吾輩《わがはい》は｜猫《ねこ》である。\n［＃改ページ］名前はまだ無い。"
    assert normalize(src) == "吾輩は猫である。名前はまだ無い。"


def test_normalize_nfkc_and_whitespace():
    assert normalize("ＡＢＣ　１２３\n あ") == "ABC123あ"


def test_cer_identical_ignores_line_breaks():
    r = cer("吾輩は猫である。\n名前はまだ無い。", "吾輩は猫\nである。名前はまだ無い。")
    assert r.distance == 0 and r.cer == 0.0


def test_cer_one_substitution():
    r = cer("吾輩は猫である", "吾輩は犬である")
    assert r.ref_chars == 7 and r.distance == 1
    assert abs(r.cer - 1 / 7) < 1e-9


def test_cer_reading_order_error_is_counted():
    # 竖排列顺序颠倒：字符都对，但顺序错 → CER 不为 0
    r = cer("一行目二行目", "二行目一行目")
    assert r.cer > 0
