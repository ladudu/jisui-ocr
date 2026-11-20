"""PaddleOCR-VL。

安装（单独的 venv，PaddlePaddle CPU 版和 GPU 版不能同时装）:
    uv venv .venv-paddle --python 3.12
    uv pip install --python .venv-paddle paddlepaddle==3.2.1 --index-url https://www.paddlepaddle.org.cn/packages/stable/cpu/
    uv pip install --python .venv-paddle "paddleocr[doc-parser]"
没有 GPU 时用 CPU 能跑但很慢；首次运行会自动下载模型。
"""

import json
import re
import subprocess
import sys
from pathlib import Path

from jisui.engines import RunLog, list_pages

RUNNER = Path(__file__).with_name("paddle_runner.py")
DEFAULT_PYTHON = Path(".venv-paddle") / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")

_MD_IMAGE = re.compile(r"!\[[^\]]*\]\([^)]*\)|<img[^>]*>")
_MD_MARKUP = re.compile(r"^\s{0,3}(#{1,6}\s+|[-*+]\s+|>\s+)", re.MULTILINE)
_HTML_TAG = re.compile(r"<[^>]+>")


def markdown_to_text(md: str) -> str:
    md = _MD_IMAGE.sub("", md)
    md = _MD_MARKUP.sub("", md)
    return _HTML_TAG.sub("", md)


def run(pages_dir: Path, out_dir: Path, python: Path = DEFAULT_PYTHON, device: str = "cpu") -> Path:
    if not python.exists():
        raise SystemExit(f"{python} が見つかりません。src/jisui/engines/paddle.py 冒頭の手順で venv を作成してください。")
    pages = list_pages(pages_dir)
    raw_dir = out_dir / "raw"
    log = RunLog(engine="paddle-vl", out_dir=out_dir, extra={"device": device})

    subprocess.run([str(python), str(RUNNER), str(pages_dir), str(raw_dir), device], check=True)

    timings = json.loads((raw_dir / "timings.json").read_text(encoding="utf-8"))
    log.extra["model_load_seconds"] = timings["model_load_seconds"]
    for page in pages:
        md = raw_dir / f"{page.stem}.md"
        if not md.exists():
            print(f"[warn] {page.name}: {md.name} が出力されていません")
            continue
        log.write_page(page.stem, markdown_to_text(md.read_text(encoding="utf-8")),
                       seconds=timings["pages"].get(page.stem), cost_usd=0.0)
    return log.save()
