<div align="center">

# Bibclean：自动移除 BibTeX 文件中未使用的文献条目

<img src="https://img.shields.io/badge/python-3.10+-blue?style=flat-square&logo=python&logoColor=white" alt="Python">
<img src="https://img.shields.io/badge/tests-81%2F81%20passed-brightgreen?style=flat-square" alt="Tests">
<img src="https://img.shields.io/github/license/ZBigFish/bibclean?style=flat-square" alt="License">
<img src="https://img.shields.io/badge/platform-cross--platform-lightgrey?style=flat-square" alt="Platform">

</div>

> English：[README.md](README.md)

**Bibclean** 扫描你的 LaTeX 项目，提取所有 `\cite{...}` 实际引用的键，并移除（或注释）`.bib` 文件中未被引用的条目。

---

## 目录

- [特性](#特性)
- [安装](#安装)
- [快速开始](#快速开始)
- [使用案例](#使用案例)
  - [1. 默认模式：生成精简后的新文件](#1-默认模式生成精简后的新文件)
  - [2. 注释模式：保留原 bib 结构](#2-注释模式保留原-bib-结构)
  - [3. 原地修改](#3-原地修改)
  - [4. 手动保护特定条目](#4-手动保护特定条目)
  - [5. 多版本项目](#5-多版本项目)
  - [6. 指定 bib 文件](#6-指定-bib-文件)
  - [7. 限制搜索范围](#7-限制搜索范围)
- [模式速查](#模式速查)
- [支持的引用命令](#支持的引用命令)
- [支持的 BibTeX 特性](#支持的-bibtex-特性)
- [工作原理](#工作原理)
- [测试](#测试)
- [开源协议](#开源协议)

---

## 特性

| | |
|---|---|
| **零配置运行** | 在项目根目录直接运行 `bibclean`，自动检测主文件、定位 bib、输出精简结果。 |
| **主文件自动检测** | 扫描 `\documentclass` 识别主 `.tex` 入口；多版本时交互选择。 |
| **非破坏性默认** | 默认生成 `new_XXX.bib`，绝不修改原始文件。 |
| **`\input`/`\include` 跟踪** | 递归解析所有包含的子 tex 文件，收集完整引用。 |
| **Bib 自动发现** | 从 `\bibliography{...}` 和 `\addbibresource{...}` 定位正在使用的 bib 文件。 |
| **`crossref` 依赖链** | 被引用条目的 `crossref` 父条目自动保留（传递闭包）。 |
| **注释模式** | `--comment` 用 `%` 注释未引用条目而非删除，保持原有 bib 结构。 |
| **安全预览** | `--dry-run` 在实际修改前预览变化。 |

无需第三方依赖，仅需 **Python 3.10+**。

## 安装

```bash
# 从源码安装（可编辑模式）
git clone https://github.com/ZBigFish/bibclean.git
cd bibclean
pip install -e .
```

安装后即可在任意目录使用 `bibclean` 命令，也可通过 `python -m bibclean` 运行。

## 快速开始

```bash
# 在论文项目根目录运行
cd /path/to/my-paper
bibclean

# 指定项目路径
bibclean /path/to/my-paper

# 预览，不修改任何文件
bibclean --dry-run
```

## 使用案例

### 1. 默认模式：生成精简后的新文件

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

原始 `refs.bib`（75 条）未被修改，`new_refs.bib`（55 条）为新生成的精简文件。

### 2. 注释模式：保留原 bib 结构

```bash
bibclean /path/to/paper-project --comment
```

未引用条目的每一行加 `% ` 前缀，已引用条目保持不变：

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

`@string`、`@comment`、`@preamble` 块始终保留原样。

### 3. 原地修改

```bash
# 直接修改原 bib 文件（移除未引用条目）
bibclean --in-place

# 直接修改原 bib 文件（注释未引用条目）
bibclean --in-place --comment
```

### 4. 手动保护特定条目

```bash
# 保留指定条目，即使未被引用
bibclean --keep "lecun1998gradient,kingma2013auto"
```

### 5. 多版本项目

当项目中有多个带 `\documentclass` 的 tex 文件（如论文修订版），程序会提示选择：

```
Multiple main .tex files detected:

  [1] paper_v1.tex
  [2] paper_v2_final.tex

Select main file [1-2]:
```

### 6. 指定 bib 文件

```bash
# 覆盖自动发现
bibclean --bib references.bib
```

### 7. 限制搜索范围

```bash
# 不在子目录中搜索 tex 文件
# （仍会跟踪主 tex 中的 \input/\include）
bibclean --no-recursive
```

## 模式速查

| 参数 | 输出文件 | 对未引用条目的操作 |
|---|---|---|
| *(无)* | `new_XXX.bib` | 删除 |
| `--comment` | `new_XXX.bib` | 用 `%` 注释 |
| `--in-place` | 原文件 | 删除 |
| `--in-place --comment` | 原文件 | 用 `%` 注释 |
| `--dry-run` *（任意组合）* | 无 | 仅预览 |

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

## 工作原理

```
项目目录
  │
  ├─ 查找含 \documentclass 的 .tex 文件 ──→ main.tex
  │
  ├─ 解析 \input{...} / \include{...}  ──→ 全部 .tex 文件
  │
  ├─ 提取 \cite{...} 键                  ──→ 引用键集合
  │
  ├─ 从主文件读取 \bibliography{...}     ──→ .bib 文件
  │
  ├─ 解析 .bib 条目                       ──→ 条目映射
  │
  └─ 筛选：保留引用 + crossref 链        ──→ new_XXX.bib
```

## 测试

```bash
python tests/test_bib_cleaner.py
# 预期输出：81/81 passed — all passed!
```

21 个测试用例，覆盖所有模式、边界情况、crossref 链、特殊字符和引用变体。

## 开源协议

[MIT](LICENSE)

---

<br>
<div align="center">
  <sub>为追求整洁文献库的研究者而构建 ❤️</sub>
</div>
