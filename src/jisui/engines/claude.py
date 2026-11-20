"""云端 VLM：Claude（对照组，只在阶段 0 少量试用）。

需要 `uv sync --extra cloud`，以及 ANTHROPIC_API_KEY 或 `ant auth login`。
注意：页面图片会发送到 Anthropic。只用版权已过期的书或自己的书做私人实验，
见 docs/charter.md「版权与合规」。
"""

import base64
import io
import time
from pathlib import Path

from jisui.engines import RunLog, list_pages

MODEL = "claude-opus-5-5"
# 美元 / 100 万 token（2026-11 时点的官方价格；变更时改这里）
PRICE_INPUT = 4.00
PRICE_OUTPUT = 20.00
MAX_IMAGE_BYTES = 4_500_000

SYSTEM = (
    "あなたは日本語の書籍ページを書き起こす OCR エンジンです。"
    "画像に印刷されている文字だけを、正確に、読む順番どおりに出力します。"
)
INSTRUCTION = """この書籍ページの文字をすべて書き起こしてください。

- 縦書きは右の行から左の行へ、各行は上から下へ読む
- 横書きは上の行から下の行へ、各行は左から右へ読む。段組みがあれば段ごとに読む
- 柱（ヘッダー）とノンブル（ページ番号）も、ページ上の位置の読み順で含める
- 図・表の中の文字は出力しない
- ルビ（振り仮名）は出力しない。親文字だけを出力する
- 旧字体・旧仮名づかいは画像のとおりに残し、現代表記に直さない
- 読めない文字は〓にする。推測で補わない
- 説明や前置きは書かず、書き起こした本文だけを出力する"""


def _encode(page: Path) -> tuple[str, str]:
    data = page.read_bytes()
    media = "image/png" if page.suffix.lower() == ".png" else "image/jpeg"
    if len(data) > MAX_IMAGE_BYTES:
        from PIL import Image

        img = Image.open(io.BytesIO(data)).convert("RGB")
        quality = 90
        while True:
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=quality)
            if buf.tell() <= MAX_IMAGE_BYTES or quality <= 60:
                break
            quality -= 10
            img = img.resize((int(img.width * 0.85), int(img.height * 0.85)))
        data, media = buf.getvalue(), "image/jpeg"
    return base64.standard_b64encode(data).decode("ascii"), media


def run(pages_dir: Path, out_dir: Path, model: str = MODEL) -> Path:
    import anthropic

    client = anthropic.Anthropic()
    pages = list_pages(pages_dir)
    log = RunLog(engine="claude", out_dir=out_dir, extra={"model": model})

    for page in pages:
        b64, media = _encode(page)
        t = time.perf_counter()
        response = client.beta.messages.create(
            model=model,
            max_tokens=16000,
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
            output_config={"effort": "medium"},
            system=SYSTEM,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "image", "source": {"type": "base64", "media_type": media, "data": b64}},
                    {"type": "text", "text": INSTRUCTION},
                ],
            }],
        )
        seconds = time.perf_counter() - t
        if response.stop_reason == "refusal":
            print(f"[warn] {page.name}: 拒否されました（{response.stop_details}）")
            continue
        if response.stop_reason == "max_tokens":
            print(f"[warn] {page.name}: 出力が途中で切れました")
        text = "".join(b.text for b in response.content if b.type == "text")
        usage = response.usage
        cost = (usage.input_tokens * PRICE_INPUT + usage.output_tokens * PRICE_OUTPUT) / 1_000_000
        log.write_page(page.stem, text, seconds=round(seconds, 2), cost_usd=round(cost, 5),
                       input_tokens=usage.input_tokens, output_tokens=usage.output_tokens,
                       served_by=response.model)
        print(f"{page.name}: {seconds:.1f}s ${cost:.4f}", flush=True)
    return log.save()
