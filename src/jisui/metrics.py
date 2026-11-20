"""评测指标。"""

from dataclasses import dataclass

from rapidfuzz.distance import Levenshtein

from jisui.textnorm import normalize


@dataclass
class CerResult:
    ref_chars: int
    distance: int

    @property
    def cer(self) -> float:
        if self.ref_chars == 0:
            return 0.0 if self.distance == 0 else 1.0
        return self.distance / self.ref_chars


def cer(reference: str, hypothesis: str) -> CerResult:
    """CER = 编辑距离 ÷ ground truth 字符数（规范化之后）。可能大于 1。"""
    ref = normalize(reference)
    hyp = normalize(hypothesis)
    return CerResult(ref_chars=len(ref), distance=Levenshtein.distance(ref, hyp))
