<div align="center">

# Bibkit：面向 LaTeX 项目的 BibTeX 工具箱

<img src="https://img.shields.io/badge/python-3.10+-blue?style=flat-square&logo=python&logoColor=white" alt="Python">
<img src="https://img.shields.io/badge/tests-81%2F81%20passed-brightgreen?style=flat-square" alt="Tests">
<img src="https://img.shields.io/github/license/ZBigFish/bibkit?style=flat-square" alt="License">
<img src="https://img.shields.io/badge/platform-cross--platform-lightgrey?style=flat-square" alt="Platform">

</div>

> English：[README.md](README.md)

**Bibkit** 是一个命令行 BibTeX 工具箱，用于管理 LaTeX 项目中的 `.bib` 文献文件。它分析你的 `.tex` 源码，找出实际使用的引用，并提供一系列工具保持文献库的整洁与一致性。

---

## 目录

- [安装](#安装)
- [命令](#命令)
  - [`bibkit clean`](#bibkit-clean)
- [路线图](#路线图)
- [支持的引用命令](#支持的引用命令)
- [支持的 BibTeX 特性](#支持的-bibtex-特性)
- [如何贡献](#如何贡献)
- [开源协议](#开源协议)

---

## 安装

```bash
# 从 PyPI 安装（推荐）
pip install bibkit

# 或从源码安装
git clone https://github.com/ZBigFish/bibkit.git
cd bibkit
pip install -e .
```

安装后即可在任意目录使用 `bibkit` 命令，也可通过 `python -m bibkit` 运行。

## 命令

### `bibkit clean`

根据 `.tex` 文件中实际的 `\cite` 引用，移除或注释 `.bib` 文件中的未使用条目。

```bash
# 在论文项目根目录运行
bibkit clean

# 指定项目路径
bibkit clean /path/to/my-paper

# 预览，不修改任何文件
bibkit clean --dry-run
```

**特性：**
- 通过 `\documentclass` 自动检测主 `.tex` 入口；多版本时交互选择
- 递归跟踪 `\input`/`\include` 收集全部子文件中的引用
- 从 `\bibliography{...}` 和 `\addbibresource{...}` 自动定位 `.bib` 文件
- 非破坏性默认——生成 `new_XXX.bib`，不修改原始文件
- `crossref` 父条目自动保留（传递闭包）
- 正确处理 `\nocite{*}`——全部条目保留

**选项：**

| 参数 | 效果 |
|---|---|
| *(无)* | 生成 `new_XXX.bib`，移除未使用条目 |
| `--comment` | 用 `%` 注释未使用条目，保留原结构 |
| `--in-place` | 直接修改原 `.bib` 文件 |
| `--in-place --comment` | 修改原文件，注释未使用条目 |
| `--dry-run` | 仅预览，不修改任何文件 |
| `--keep "key1,key2"` | 逗号分隔的额外保护键列表 |
| `--bib references.bib` | 指定要处理的 bib 文件（覆盖自动发现） |
| `--no-recursive` | 不在子目录中搜索 `.tex` 文件 |

## 路线图

| 命令 | 状态 | 说明 |
|---|---|---|
| `bibkit clean` | 已完成 | 移除 `.bib` 文件中未使用的条目 |
| `bibkit merge` | 计划中 | 合并多个 `.bib` 文件并去重 |
| `bibkit check` | 计划中 | 校验 `.bib` 条目（缺失字段、格式错误、断开的 crossref） |
| `bibkit sort` | 计划中 | 按键、作者或年份排序条目 |
| `bibkit fmt`  | 计划中 | 标准化格式（标题大小写、统一会议缩写） |
| `bibkit diff` | 计划中 | 对比两个 `.bib` 文件的差异 |

有功能需求？[提交 Issue](https://github.com/ZBigFish/bibkit/issues)。

## 支持的引用命令

`\cite` `\citep` `\citet` `\citeauthor` `\citeyear` `\citealp` `\citealt`
`\parencite` `\textcite` `\footcite` `\autocite` `\supercite` `\fullcite`
`\Cite` `\Citep` `\Citet`（大写变体）`\cite*`（星号变体）

支持可选参数（`\cite[page 3]{key}`）、多键（`\cite{key1,key2}`）、`\nocite{*}`。

## 支持的 BibTeX 特性

- 所有标准条目类型：`@article`、`@inproceedings`、`@book`、`@incollection`、`@misc` 等
- `@string`、`@comment`、`@preamble` 块始终保留
- 正确处理字段值中的嵌套花括号（`{CNN}`、`{\L}ukasz`）
- 传递解析 `crossref` 字段，自动保留父条目

## 如何贡献

欢迎贡献！详见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 开源协议

[MIT](LICENSE)

---

<br>
<div align="center">
  <sub>为追求整洁文献库的研究者而构建 ❤️</sub>
</div>
