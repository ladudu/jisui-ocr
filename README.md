# jisui-ocr

縦書きの日本語の紙の本を、スマホでめくりながら撮った動画から縦書き EPUB にする「自炊」パイプラインの PoC です。

> 手元の本を自分で読むためのツールです（著作権法第 30 条第 1 項の私的複製）。スキャン代行や、スキャンデータの共有・公開には使わないでください。

## ステータス

| フェーズ | 内容 | 状態 |
|---|---|---|
| 0a | OCR の比較：横書きの本（NDLOCR-Lite / PaddleOCR-VL / Claude、CER で評価） | 進行中 |
| 0b | OCR の比較：縦書きの本（同上、横書きとの差も比較） | 未着手 |
| 1 | 写真 → テキスト（透視補正、見開き分割、ヘッダー除去） | 未着手 |
| 2 | 動画 → 各ページのベストフレーム（静止区間検出、鮮明度、重複除去） | 未着手 |
| 3 | 縦書き EPUB 出力、LLM による差分校正、校正画面 | 未着手 |

## 使い方（フェーズ 0）

```powershell
uv sync --extra cloud
uv run jisui ocr --engine ndlocr --pages data/horizontal/pages --out outputs/horizontal
uv run jisui eval --gt data/horizontal/ground_truth --outputs outputs/horizontal --results results/horizontal
```

セットアップの詳細は [docs/stage0-guide.md](docs/stage0-guide.md)（中国語）を参照してください。

## ドキュメント

- [docs/charter.md](docs/charter.md)：目的・範囲・フェーズ計画・評価指標・著作権の制約
- [docs/devlog.md](docs/devlog.md)：開発ログ

## データについて

`data/` と `outputs/` は Git の管理外です。リポジトリに含める画像やテキストは、著作権の保護期間が終了した本か、自作の文書に限ります。
