"""对照 ground truth 计算每个引擎的 CER / 耗时 / 成本，输出对比表。"""

import csv
import json
from datetime import datetime
from pathlib import Path

from jisui.metrics import cer


def evaluate(gt_dir: Path, outputs_dir: Path, results_dir: Path) -> Path:
    gts = sorted(gt_dir.glob("*.txt"))
    if not gts:
        raise SystemExit(f"{gt_dir} に ground truth（<ページ名>.txt）がありません")
    engines = sorted(d for d in outputs_dir.iterdir() if (d / "run.json").exists())
    if not engines:
        raise SystemExit(f"{outputs_dir} に OCR 結果がありません。先に `jisui ocr` を実行してください")

    page_rows, summary_rows = [], []
    for eng_dir in engines:
        run = json.loads((eng_dir / "run.json").read_text(encoding="utf-8"))
        total_dist = total_chars = 0
        seconds = cost = 0.0
        for gt in gts:
            hyp_path = eng_dir / f"{gt.stem}.txt"
            stats = run["pages"].get(gt.stem, {})
            hyp = hyp_path.read_text(encoding="utf-8") if hyp_path.exists() else ""
            r = cer(gt.read_text(encoding="utf-8"), hyp)
            total_dist += r.distance
            total_chars += r.ref_chars
            seconds += stats.get("seconds") or 0.0
            cost += stats.get("cost_usd") or 0.0
            page_rows.append({
                "engine": run["engine"], "page": gt.stem, "ref_chars": r.ref_chars,
                "distance": r.distance, "cer": round(r.cer, 4),
                "missing": not hyp_path.exists(), "seconds": stats.get("seconds"),
                "cost_usd": stats.get("cost_usd"),
            })
        n = len(gts)
        summary_rows.append({
            "engine": run["engine"],
            "detail": run.get("model") or run.get("device", ""),
            "pages": n,
            "cer": round(total_dist / total_chars, 4) if total_chars else None,
            "mean_page_cer": round(sum(r["cer"] for r in page_rows[-n:]) / n, 4),
            "sec_per_page": round(seconds / n, 2),
            "total_seconds_incl_load": run.get("total_seconds"),
            "usd_per_page": round(cost / n, 5),
        })

    results_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M")
    _write_csv(results_dir / f"pages-{stamp}.csv", page_rows)
    summary = results_dir / f"summary-{stamp}.csv"
    _write_csv(summary, summary_rows)
    _print_table(summary_rows)
    return summary


def _write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8-sig") as f:  # BOM: Excel 直接打开不乱码
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def _print_table(rows: list[dict]) -> None:
    cols = list(rows[0])
    widths = {c: max(len(c), *(len(str(r[c])) for r in rows)) for c in cols}
    print("  ".join(c.ljust(widths[c]) for c in cols))
    for r in rows:
        print("  ".join(str(r[c]).ljust(widths[c]) for c in cols))
