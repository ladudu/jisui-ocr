# 阶段 0 操作手册：OCR 选型实验

目标：20 页照片 × 3 个 OCR 方案 → 一张 CER / 耗时 / 成本对比表 → 定下主力 OCR。

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

- 版权已过期（作者去世超过 70 年）：芥川龙之介、夏目漱石、宫泽贤治、太宰治（1948 年去世，2019 年起已过期）等
- 最好是**实体纸书**（文库本），这样和以后的真实使用场景一致
- 青空文库有同一作品的电子文本，ground truth 省大半工作量
- 20 页里尽量包含：竖排正文（主体）、ルビ多的页、目录或注释等横排混排、插图页各几页

## 3. 拍照

- 同一部手机，室内自然光，书尽量压平，整页入镜（跨页就拍跨页，阶段 1 再切）
- 不开闪光灯、不用 App 的「文档扫描」模式（要的是原始照片）
- 文件名按页码：`data/pages/p012.jpg`、`p013.jpg` …（印刷页码，三位数补零）
- 记下：手机型号、分辨率、光线、是否跨页 → 写进 devlog（博客要用）

## 4. 整理 ground truth

每张图对应一个 `data/ground_truth/<同名>.txt`，UTF-8。

**口径（所有引擎同一标准）**：
1. 页面上印刷的所有文字，按读的顺序（竖排：右列 → 左列，每列从上到下）
2. **包含**柱（页眉）和ノンブル（页码）
3. **不含**ルビ：可以直接粘贴青空文库带《》的文本，评测时自动去掉《…》、｜、［＃…］
4. 换行、空格随意，评测时全部去掉
5. 旧字体、旧假名照书上的写，不改成现代写法

**用青空文库的步骤**：
1. 在青空文库找到同一作品，下载文本版
2. 按书页的起止位置切出对应段落，粘进 txt
3. **逐页对照纸书**：版本不同（底本、新旧字体、表记）会有差异，一定以手上的纸书为准
4. 手动补上柱和页码

20 页预计 1〜2 小时，大部分时间在第 3 步。

## 5. 跑 OCR 和评测

```powershell
uv run jisui ocr --engine ndlocr
```

```powershell
uv run jisui ocr --engine paddle-vl
```

```powershell
uv run jisui ocr --engine claude
```

```powershell
uv run jisui eval
```

输出：
- `outputs/<engine>/<页名>.txt`：各引擎的文本（不提交）
- `outputs/<engine>/raw/`：引擎原始输出（NDLOCR-Lite 的 xml 里有每行坐标和阅读顺序，分析失败例用）
- `results/summary-*.csv`：方案 × CER / 每页秒数 / 每页美元（只有数字，可以提交）
- `results/pages-*.csv`：每页明细，找最差的页看原因

## 6. 人工检查（博客的核心素材）

1. 在 `pages-*.csv` 里按 CER 排序，每个引擎看最差的 3 页
2. 对每页判断错误类型：**阅读顺序错误**（列顺序乱）/ ルビ混入正文 / 单字误识别 / 漏行 / 横排部分出错
3. 统计「阅读顺序错误」页数，记进 devlog
4. 截图只用版权已过期的书

## 7. 阶段 0 完成条件

- [ ] 对比表（summary CSV）存在，3 个方案都有数字（PaddleOCR-VL 如果 CPU 实在跑不动，记录原因和试跑的页数）
- [ ] 每个方案的典型失败例各 1〜2 个
- [ ] 在 devlog 写下结论：主力 OCR 是哪个、为什么
- [ ] 更新 charter.md 的阶段状态和未决问题
