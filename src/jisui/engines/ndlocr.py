"""NDLOCR-Lite（国立国会図書館）。

安装（独立环境，不进本项目的 venv，避免依赖冲突）:
    git clone https://github.com/ndl-lab/ndlocr-lite vendor/ndlocr-lite
    uv tool install --python 3.12 ./vendor/ndlocr-lite
之后 `ndlocr-lite` 命令可用。它对目录一次性处理，所以只能拿到总耗时，
每页耗时按平均值记录。
"""

import shutil
import subprocess
import time
from pathlib import Path

from jisui.engines import RunLog, list_pages


def run(pages_dir: Path, out_dir: Path, exe: str = "ndlocr-lite", device: str = "cpu") -> Path:
    if shutil.which(exe) is None:
        raise SystemExit(f"{exe} が見つかりません。src/jisui/engines/ndlocr.py 冒頭の手順でインストールしてください。")
    pages = list_pages(pages_dir)
    raw_dir = out_dir / "raw"  # NDLOCR-Lite 原始输出（txt/json/xml），保留以便分析阅读顺序
    raw_dir.mkdir(parents=True, exist_ok=True)  # 它不会自己建输出目录

    log = RunLog(engine="ndlocr", out_dir=out_dir, extra={"device": device, "exe": exe})
    t0 = time.perf_counter()
    subprocess.run(
        [exe, "--sourcedir", str(pages_dir), "--output", str(raw_dir), "--device", device],
        check=True,
    )
    per_page = (time.perf_counter() - t0) / len(pages)

    for page in pages:
        txt = raw_dir / f"{page.stem}.txt"
        if not txt.exists():
            print(f"[warn] {page.name}: {txt.name} が出力されていません")
            continue
        log.write_page(page.stem, txt.read_text(encoding="utf-8"),
                       seconds=round(per_page, 2), seconds_is_average=True, cost_usd=0.0)
    return log.save()
