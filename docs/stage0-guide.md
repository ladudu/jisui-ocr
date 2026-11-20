# 阶段 0 操作手册：OCR 选型实验

目标：20 页照片 × 3 个 OCR 方案 → 一张 CER / 耗时 / 成本对比表 → 定下主力 OCR。

分两步（2026-11-20 变更，见 charter.md）：

| 阶段 | 数据集 | 数据目录 | 结果目录 |
|---|---|---|---|
| 0a | 日文**横排**书 | `data/horizontal/` | `outputs/horizontal/`、`results/horizontal/` |
| 0b | 日文**竖排**书 | `data/vertical/` | `outputs/vertical/`、`results/vertical/` |

每个数据目录下都是 `pages/`（照片）和 `ground_truth/`（正确文本）。0a 先把环境、拍摄、ground truth、评测整套流程跑通，0b 照搬。

## 1. 准备环境（一次）

PowerShell，在仓库根目录：

```powershell
uv sync --extra cloud
```

```powershell
uv run pytest
```

NDLOCR-Lite（装成独立命令，不进本项目 venv）：

```powershell
git clone https://github.com/ndl-lab/ndlocr-lite vendor/ndlocr-lite
```

```powershell
uv tool install --python 3.12 ./vendor/ndlocr-lite
```

PaddleOCR-VL（单独 venv；CPU 版。没有 GPU 时会很慢，先拿 2〜3 页试）：

```powershell
uv venv .venv-paddle --python 3.12
```

```powershell
uv pip install --python .venv-paddle paddlepaddle==3.2.1 --index-url https://www.paddlepaddle.org.cn/packages/stable/cpu/
```

```powershell
uv pip install --python .venv-paddle "paddleocr[doc-parser]"
```

Claude：设置 `ANTHROPIC_API_KEY`，或用 `ant auth login`。20 页大约几十美分（每页成本会记在 `run.json`）。

## 2. 选书

### 横排的选书（0a）

版权已过期的日文横排书几乎没有（战前的书基本是竖排），所以有两种做法：

| 做法 | 优点 | 缺点 | 能公开什么 |
|---|---|---|---|
| **A. 自己排版打印**：把青空文库的作品用横排排版（Word，明朝体 10〜10.5pt，文库或 A5 大小，带页眉和页码），打印后拍照 | ground truth 就是原文，几乎零成本；内容版权已过期、排版是自己做的 | 不是真正的书（纸张、装订弯曲、印刷质量不同） | 图片、文本、数字都能公开 |
| **B. 手上的日文技术书**（有版权） | 真实场景 | ground truth 要逐字手打，很花时间 | **只能公开 CER 等数字** |

**建议**：0a 以 A 为主（20 页），能抽出时间再加 B 的 5 页左右作为「真书」的参考。B 选页时避开代码、图、表多的页。

### 竖排的选书（0b）

- 版权已过期（作者去世超过 70 年）：芥川龙之介、夏目漱石、宫泽贤治、太宰治（1948 年去世，2019 年起已过期）等
- 最好是**实体纸书**（文库本），这样和以后的真实使用场景一致
- 青空文库有同一作品的电子文本，ground truth 省大半工作量
- 20 页里尽量包含：竖排正文（主体）、ルビ多的页、目录或注释等横排混排、插图页各几页

## 3. 拍照

- 同一部手机，室内自然光，书尽量压平，整页入镜（跨页就拍跨页，阶段 1 再切）
- 不开闪光灯、不用 App 的「文档扫描」模式（要的是原始照片）
- 文件名按页码：`data/horizontal/pages/p012.jpg`、`p013.jpg` …（印刷页码，三位数补零）
- 记下：手机型号、分辨率、光线、是否跨页 → 写进 devlog（博客要用）
- 0a 和 0b 用相同的拍摄条件，两边的 CER 才能比较

## 4. 整理 ground truth

每张图对应一个 `ground_truth/<同名>.txt`，UTF-8。

**口径（所有引擎、横排竖排都用同一标准）**：
1. 页面上印刷的文字，按读的顺序：
   - 竖排：右列 → 左列，每列从上到下
   - 横排：上行 → 下行，每行从左到右；有分栏就一栏一栏读
2. **包含**柱（页眉）和ノンブル（页码）
3. **不含**ルビ：可以直接粘贴青空文库带《》的文本，评测时自动去掉《…》、｜、［＃…］
4. **不含**图、表里的文字
5. 换行、空格随意，评测时全部去掉
6. 旧字体、旧假名照书上的写，不改成现代写法

**做法 A（自己排版打印）**：排版用的文本直接存成 ground truth，再补上页眉和页码。注意 Word 自动换页的位置，按打印出来的纸切分。

**用青空文库整理竖排书的步骤**：
1. 在青空文库找到同一作品，下载文本版
2. 按书页的起止位置切出对应段落，粘进 txt
3. **逐页对照纸书**：版本不同（底本、新旧字体、表记）会有差异，一定以手上的纸书为准
4. 手动补上柱和页码

## 5. 跑 OCR 和评测

以横排（0a）为例。竖排把 `horizontal` 换成 `vertical`。

```powershell
uv run jisui ocr --engine ndlocr --pages data/horizontal/pages --out outputs/horizontal
```

```powershell
uv run jisui ocr --engine paddle-vl --pages data/horizontal/pages --out outputs/horizontal
```

```powershell
uv run jisui ocr --engine claude --pages data/horizontal/pages --out outputs/horizontal
```

```powershell
uv run jisui eval --gt data/horizontal/ground_truth --outputs outputs/horizontal --results results/horizontal
```

输出：
- `outputs/horizontal/<engine>/<页名>.txt`：各引擎的文本（不提交）
- `outputs/horizontal/<engine>/raw/`：引擎原始输出（NDLOCR-Lite 的 xml 里有每行坐标和阅读顺序，分析失败例用）
- `results/horizontal/summary-*.csv`：方案 × CER / 每页秒数 / 每页美元（只有数字，可以提交）
- `results/horizontal/pages-*.csv`：每页明细，找最差的页看原因

## 6. 人工检查（博客的核心素材）

1. 在 `pages-*.csv` 里按 CER 排序，每个引擎看最差的 3 页
2. 对每页判断错误类型：**阅读顺序错误**（行/列顺序乱）/ ルビ混入正文 / 单字误识别 / 漏行 / 页眉页码出错
3. 统计「阅读顺序错误」页数，记进 devlog
4. 截图只用版权已过期的内容（做法 A 的打印页可以）

## 7. 完成条件

0a（横排）：
- [ ] 横排对比表存在，3 个方案都有数字（PaddleOCR-VL 如果 CPU 实在跑不动，记录原因和试跑的页数）
- [ ] 每个方案的典型失败例各 1〜2 个
- [ ] devlog 里记下流程上踩的坑，为 0b 做准备

0b（竖排）：
- [ ] 竖排对比表存在，和横排并列成一张表
- [ ] 每个方案的典型失败例各 1〜2 个
- [ ] 在 devlog 写下结论：主力 OCR 是哪个、为什么
- [ ] 更新 charter.md 的阶段状态和未决问题
