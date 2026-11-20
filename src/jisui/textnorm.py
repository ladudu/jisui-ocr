"""CER 计算前的文本规范化。

OCR 结果和 ground truth 都经过同一个函数，保证比较口径一致：
- NFKC 规范化（全角英数 → 半角等，消除字形编码差异）
- 去掉青空文库记法：ルビ《…》、ルビ起点｜、注记［＃…］
- 去掉所有空白和换行（竖排的换行位置因工具而异，不计入错误）
"""

import re
import unicodedata

_AOZORA_RUBY = re.compile(r"《[^》]*》")
_AOZORA_NOTE = re.compile(r"［＃[^］]*］")
_AOZORA_RUBY_START = re.compile(r"[｜|]")
_WHITESPACE = re.compile(r"\s+")


def normalize(text: str, strip_aozora: bool = True) -> str:
    if strip_aozora:
        # NFKC 前处理：NFKC 会把全角［＃ 变成半角，正则就匹配不上了
        text = _AOZORA_RUBY.sub("", text)
        text = _AOZORA_NOTE.sub("", text)
        text = _AOZORA_RUBY_START.sub("", text)
    text = unicodedata.normalize("NFKC", text)
    return _WHITESPACE.sub("", text)
