<div align="center">

<img src="https://img.shields.io/badge/python-3.10+-blue?style=flat-square&logo=python&logoColor=white" alt="Python">
<img src="https://img.shields.io/badge/tests-81%2F81%20passed-brightgreen?style=flat-square" alt="Tests">
<img src="https://img.shields.io/github/license/ZBigFish/bibclean?style=flat-square" alt="License">
<img src="https://img.shields.io/badge/platform-cross--platform-lightgrey?style=flat-square" alt="Platform">

</div>

# bibclean

> Keep your `.bib` files clean — automatically remove (or comment out) unused bibliography entries based on actual `\cite` usage in your LaTeX project.

[中文文档](#中文文档)

---

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage Examples](#usage-examples)
  - [1. Default: generate a cleaned new file](#1-default-generate-a-cleaned-new-file)
  - [2. Comment mode: preserve bib structure](#2-comment-mode-preserve-bib-structure)
  - [3. In-place modification](#3-in-place-modification)
  - [4. Protect specific entries](#4-protect-specific-entries)
  - [5. Multi-version projects](#5-multi-version-projects)
  - [6. Specify a bib file](#6-specify-a-bib-file)
  - [7. Limit search scope](#7-limit-search-scope)
- [Mode Reference](#mode-reference)
- [Supported Citation Commands](#supported-citation-commands)
- [Supported BibTeX Features](#supported-bibtex-features)
- [How It Works](#how-it-works)
- [Testing](#testing)
- [License](#license)

---

## Features

| | |
|---|---|
| **Zero-config default** | Run `bibclean` with no arguments — auto-detects the main `.tex`, finds the right `.bib`, and produces a cleaned copy. |
| **Main file auto-detection** | Scans for `\documentclass` to identify the entry point. Prompts for choice when multiple versions exist. |
| **Non-destructive by default** | Writes a new `new_XXX.bib` file. Never touches your originals unless you explicitly ask. |
| **`\input`/`\include` following** | Recursively resolves included sub-files to collect all citations across the entire project. |
| **Bib auto-discovery** | Reads `\bibliography{...}` and `\addbibresource{...}` from your main `.tex` to find which `.bib` files are in use. |
| **`crossref` dependency chain** | Automatically keeps cross-referenced parent entries (transitive closure). |
| **Comment mode** | `--comment` comments out unused entries with `%` instead of deleting them — preserving your original bib structure. |
| **Safe preview** | `--dry-run` shows exactly what would change before touching any files. |

No external dependencies — just **Python 3.10+**.

## Installation

```bash
# From source (editable install)
git clone https://github.com/ZBigFish/bibclean.git
cd bibclean
pip install -e .
```

After installation, the `bibclean` command is available globally. You can also run `python -m bibclean`.

## Quick Start

```bash
# Run from your LaTeX project root
cd /path/to/my-paper
bibclean

# Or specify the project path
bibclean /path/to/my-paper

# Preview before making changes
bibclean --dry-run
```

## Usage Examples

### 1. Default: generate a cleaned new file

```bash
bibclean /path/to/paper-project
```

```
Main file: main.tex
  (with 7 included .tex file(s))

Scanned 8 .tex file(s), found 55 unique citation key(s).

--- refs.bib ---
  Total entries: 75
  Entries to keep:   55
  Entries to removed: 20
    - spencer2016causes
    - goodfellow2014generative
    ...
  Wrote to new_refs.bib (20 entries removed).

Done.
```

The original `refs.bib` (75 entries) is untouched. `new_refs.bib` (55 entries) is the cleaned result.

### 2. Comment mode: preserve bib structure

```bash
bibclean /path/to/paper-project --comment
```

Unused entries get `% ` prefixed to every line; cited entries remain unchanged:

```bib
% @article{goodfellow2014generative,
%   title={Generative adversarial nets},
%   author={Goodfellow, Ian and ...},
%   ...
% }

@inproceedings{he2016deep,
  title={Deep residual learning for image recognition},
  ...
}
```

`@string`, `@comment`, and `@preamble` blocks are always preserved as-is.

### 3. In-place modification

```bash
# Remove unused entries directly from the original file
bibclean --in-place

# Comment out unused entries in the original file
bibclean --in-place --comment
```

### 4. Protect specific entries

```bash
# Keep selected keys even if not cited
bibclean --keep "lecun1998gradient,kingma2013auto"
```

### 5. Multi-version projects

When multiple `.tex` files with `\documentclass` are found (e.g., paper revisions), you'll be prompted:

```
Multiple main .tex files detected:

  [1] paper_v1.tex
  [2] paper_v2_final.tex

Select main file [1-2]:
```

### 6. Specify a bib file

```bash
# Override auto-discovery
bibclean --bib references.bib
```

### 7. Limit search scope

```bash
# Don't search subdirectories for .tex files
# (still follows \input/\include from the main .tex)
bibclean --no-recursive
```

## Mode Reference

| Flags | Output File | Action on Unused |
|---|---|---|
| *(none)* | `new_XXX.bib` | Remove |
| `--comment` | `new_XXX.bib` | Comment with `%` |
| `--in-place` | Original file | Remove |
| `--in-place --comment` | Original file | Comment with `%` |
| `--dry-run` *(with any)* | None | Preview only |

## Supported Citation Commands

`\cite` `\citep` `\citet` `\citeauthor` `\citeyear` `\citealp` `\citealt`
`\parencite` `\textcite` `\footcite` `\autocite` `\supercite` `\fullcite`
`\Cite` `\Citep` `\Citet` (capitalized) `\cite*` (starred)

Supports optional arguments (`\cite[page 3]{key}`), multi-key (`\cite{key1,key2}`), and `\nocite{*}`.

## Supported BibTeX Features

- All standard entry types: `@article`, `@inproceedings`, `@book`, `@incollection`, `@misc`, and more
- `@string`, `@comment`, `@preamble` blocks are always preserved
- Nested braces in field values (`{CNN}`, `{\L}ukasz`) handled correctly
- `crossref` fields resolved transitively — parent entries kept automatically

## How It Works

```
Project directory
  │
  ├─ Find .tex files with \documentclass ──→ main.tex
  │
  ├─ Resolve \input{...} / \include{...} ──→ all .tex files
  │
  ├─ Extract \cite{...} keys ──────────────→ cited keys set
  │
  ├─ Read \bibliography{...} from main ────→ .bib file(s)
  │
  ├─ Parse .bib entries ───────────────────→ entry map
  │
  └─ Filter: keep cited + crossref chain ──→ new_XXX.bib
```

## Testing

```bash
python tests/test_bib_cleaner.py
# Expected: 81/81 passed — all passed!
```

21 test cases covering all modes, edge cases, crossref chains, special characters, and citation pattern variants.

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=ZBigFish/bibclean&type=Date)](https://star-history.com/#ZBigFish/bibclean&Date)

## License

[MIT](LICENSE)

---

<br>

# 中文文档

## bibclean

> 根据 LaTeX 论文项目中的实际 `\cite` 引用，自动精简 `.bib` 文献库——移除（或注释）未使用的条目。

## 特性

- **零参数运行** — 在项目根目录直接 `bibclean`，自动完成所有工作
- **主文件自动检测** — 扫描 `\documentclass` 定位主 `.tex`；多版本时交互选择
- **非破坏性默认** — 默认生成 `new_XXX.bib`，绝不修改原始文件
- **`\input`/`\include` 跟踪** — 递归解析所有子 tex 文件，收集完整引用
- **Bib 自动发现** — 从 `\bibliography{...}` 和 `\addbibresource{...}` 定位正在使用的 bib
- **crossref 依赖链** — 被引用条目的 `crossref` 父条目自动保留（传递闭包）
- **注释模式** — `--comment` 用 `%` 注释未引用条目，保持原 bib 结构
- **安全预览** — `--dry-run` 在修改前预览结果

无需第三方依赖，仅需 **Python 3.10+**。

## 安装

```bash
git clone https://github.com/ZBigFish/bibclean.git
cd bibclean
pip install -e .
```

安装后即可在任意目录使用 `bibclean` 命令，也可通过 `python -m bibclean` 运行。

## 快速开始

```bash
cd /path/to/my-paper
bibclean                # 自动检测、生成 new_refs.bib
bibclean --dry-run      # 先预览，不修改文件
bibclean --comment      # 注释未引用条目而非删除
```

## 模式速查

| 参数 | 输出文件 | 对未引用条目的操作 |
|---|---|---|
| *(无)* | `new_XXX.bib` | 删除 |
| `--comment` | `new_XXX.bib` | 用 `%` 注释 |
| `--in-place` | 原文件 | 删除 |
| `--in-place --comment` | 原文件 | 用 `%` 注释 |
| `--dry-run` | 无 | 仅预览 |

## 支持的引用命令

`\cite` `\citep` `\citet` `\citeauthor` `\citeyear` `\citealp` `\citealt`
`\parencite` `\textcite` `\footcite` `\autocite` `\supercite` `\fullcite`
`\Cite` `\Citep` `\Citet` `\cite*` `\nocite{*}`

支持可选参数 `\cite[page 3]{key}`、多键 `\cite{a,b,c}`、`\nocite{*}`。

## 测试

```bash
python tests/test_bib_cleaner.py
# 预期：81/81 passed — all passed!
```

21 个测试用例，覆盖所有模式、边界情况、crossref 链、特殊字符和引用变体。

## 许可证

[MIT](LICENSE)

---

<br>
<div align="center">
  <sub>Built with ❤️ for researchers who care about clean bibliographies.</sub>
</div>
