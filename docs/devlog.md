# 开发日志

每次干完活写一条，新的在上面。写博客时从这里挑素材。

模板：

```
## YYYY-MM-DD（阶段 N）

**做了什么**
-

**数字**（CER、耗时、漏页率等。注明条件：几页、哪个引擎、CPU/GPU）
-

**踩坑 / 意外**
-

**博客素材**（截图路径、值得写的发现、标题灵感）
-

**下一步**
-
```

---

## 2026-11-20（立项）

**做了什么**
- 根据调研报告立项，写了 [charter.md](charter.md)
- 搭好项目骨架：uv + Python 3.12，`jisui ocr` / `jisui eval` 两个命令
- OCR 封装了 3 个引擎：NDLOCR-Lite（`uv tool`）、PaddleOCR-VL（`.venv-paddle`）、Claude（`claude-opus-5-5`）
- CER 计算：NFKC + 去空白换行 + 去青空文库ルビ记法，用 rapidfuzz 算编辑距离

**数字**
- 无（还没有测试数据）

**踩坑 / 意外**
- NDLOCR-Lite 不在 PyPI，要 clone 后 `uv tool install`；而且依赖钉死了版本（numpy、opencv 等），和 PaddleOCR 冲突 → 三个引擎分三个环境
- NDLOCR-Lite 不会自己创建输出目录
- 开发 PC 没有 NVIDIA GPU，PaddleOCR-VL 只能用 CPU 跑

**博客素材**
- 「Python 的依赖隔离」用 .NET 类比：每个引擎一个独立的 venv ≈ 每个工具独立部署，避免 NuGet 版本冲突
- ground truth 口径（包含柱和页码、去掉ルビ）的取舍，第 1 篇要写清楚

**下一步**
- 选书、拍 20 页、整理 ground truth（见 [stage0-guide.md](stage0-guide.md)）
- 确认家里服务器有没有 GPU
