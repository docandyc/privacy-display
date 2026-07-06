# 中文论文构建

在本目录运行：

```bash
./build.sh
```

脚本通过 `latexmk` 自动执行所需的 XeLaTeX、BibTeX 和后续 XeLaTeX 轮次，并在日志仍含未解析引用时返回失败。

不要在清理 `main.aux` 等辅助文件后只运行一次 `xelatex main.tex`。第一遍只能收集引用和交叉引用信息，生成的 PDF 会出现 `[?]` 与 `??`。

若编辑器支持 TeX magic comment，`main.tex` 已声明使用 `latexmk`；本目录的 `latexmkrc` 会强制采用 XeLaTeX。
