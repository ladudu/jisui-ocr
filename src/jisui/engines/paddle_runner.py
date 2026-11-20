"""PaddleOCR-VL 的独立运行脚本，由 .venv-paddle 里的 Python 执行。

故意不 import jisui：paddle 的依赖很重，放在单独的 venv 里。
用法: python paddle_runner.py <pages_dir> <out_dir> <device>
输出: <out_dir>/<stem>.md 和 <out_dir>/timings.json
"""

import json
import sys
import time
from pathlib import Path

from paddleocr import PaddleOCRVL

EXTS = {".jpg", ".jpeg", ".png"}


def main() -> None:
    pages_dir, out_dir, device = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
    out_dir.mkdir(parents=True, exist_ok=True)

    t0 = time.perf_counter()
    pipeline = PaddleOCRVL(device=device)
    timings = {"model_load_seconds": round(time.perf_counter() - t0, 2), "pages": {}}

    for page in sorted(p for p in pages_dir.iterdir() if p.suffix.lower() in EXTS):
        t = time.perf_counter()
        for res in pipeline.predict(str(page)):
            res.save_to_markdown(save_path=str(out_dir))
            res.save_to_json(save_path=str(out_dir))
        timings["pages"][page.stem] = round(time.perf_counter() - t, 2)
        print(f"{page.name}: {timings['pages'][page.stem]}s", flush=True)

    (out_dir / "timings.json").write_text(json.dumps(timings, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
