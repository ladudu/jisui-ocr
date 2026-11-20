"""jisui 命令行。

    jisui ocr --engine ndlocr            # data/pages → outputs/ndlocr/
    jisui ocr --engine paddle-vl
    jisui ocr --engine claude
    jisui eval                           # 对照 data/ground_truth → results/summary-*.csv
"""

import argparse
import sys
from pathlib import Path

ENGINES = ["ndlocr", "paddle-vl", "claude"]


def main() -> None:
    parser = argparse.ArgumentParser(prog="jisui")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_ocr = sub.add_parser("ocr", help="ページ画像を OCR する")
    p_ocr.add_argument("--engine", choices=ENGINES, required=True)
    p_ocr.add_argument("--pages", type=Path, default=Path("data/pages"))
    p_ocr.add_argument("--out", type=Path, default=Path("outputs"))
    p_ocr.add_argument("--device", default="cpu", help="ndlocr / paddle-vl: cpu または cuda / gpu")

    p_eval = sub.add_parser("eval", help="CER を計算して比較表を出力する")
    p_eval.add_argument("--gt", type=Path, default=Path("data/ground_truth"))
    p_eval.add_argument("--outputs", type=Path, default=Path("outputs"))
    p_eval.add_argument("--results", type=Path, default=Path("results"))

    # Windows の日本語環境（cp932）で表示できない文字があっても落ちないように
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(errors="replace")
    args = parser.parse_args()

    if args.cmd == "ocr":
        out_dir = args.out / args.engine
        if args.engine == "ndlocr":
            from jisui.engines import ndlocr
            path = ndlocr.run(args.pages, out_dir, device=args.device)
        elif args.engine == "paddle-vl":
            from jisui.engines import paddle
            path = paddle.run(args.pages, out_dir, device=args.device)
        else:
            from jisui.engines import claude
            path = claude.run(args.pages, out_dir)
        print(f"完了: {path}")
    elif args.cmd == "eval":
        from jisui.evaluate import evaluate
        print(f"比較表: {evaluate(args.gt, args.outputs, args.results)}")


if __name__ == "__main__":
    main()
