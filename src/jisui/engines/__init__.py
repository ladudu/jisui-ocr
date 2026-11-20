"""OCR 引擎封装。每个引擎把结果写成 outputs/<engine>/<页名>.txt + run.json。

run.json 记录耗时和成本，eval 读它来生成对比表：
{
  "engine": "ndlocr",
  "started_at": "...",
  "total_seconds": 12.3,           # 含模型加载
  "pages": {"p001": {"seconds": 1.2, "cost_usd": 0.0, ...}}
}
"""

import json
import platform
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from jisui import IMAGE_EXTS


def list_pages(pages_dir: Path) -> list[Path]:
    pages = sorted(p for p in pages_dir.iterdir() if p.suffix.lower() in IMAGE_EXTS)
    if not pages:
        raise SystemExit(f"{pages_dir} に画像がありません（対応形式: {sorted(IMAGE_EXTS)}）")
    return pages


@dataclass
class RunLog:
    engine: str
    out_dir: Path
    pages: dict[str, dict] = field(default_factory=dict)
    started_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
    _t0: float = field(default_factory=time.perf_counter)
    extra: dict = field(default_factory=dict)

    def write_page(self, stem: str, text: str, **stats) -> None:
        self.out_dir.mkdir(parents=True, exist_ok=True)
        (self.out_dir / f"{stem}.txt").write_text(text, encoding="utf-8")
        self.pages[stem] = stats

    def save(self) -> Path:
        data = {
            "engine": self.engine,
            "started_at": self.started_at,
            "total_seconds": round(time.perf_counter() - self._t0, 2),
            "machine": {"platform": platform.platform(), "processor": platform.processor()},
            **self.extra,
            "pages": self.pages,
        }
        path = self.out_dir / "run.json"
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return path
