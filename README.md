# bibclean

根据 LaTeX 论文项目中对 `.tex` 文件的实际引用，精简 `.bib` 文献库——自动移除（或注释）未被引用的条目。

---

## 特性

- **零参数运行** — 在项目根目录直接运行 `bibclean`，自动完成所有工作
- **主文件自动检测** — 扫描 `\documentclass` 定位主 `.tex` 入口；多版本时交互选择
- **非破坏性默认** — 默认生成 `new_XXX.bib`，绝不修改原始文件
- **`\input`/`\include` 跟踪** — 递归解析所有包含的子 tex 文件，收集完整引用
- **Bib 自动发现** — 从 `\bibliography{...}` 和 `\addbibresource{...}` 定位正在使用的 bib 文件
- **crossref 依赖链** — 被引用条目的 `crossref` 父条目自动保留（传递闭包）
- **注释模式** — `--comment` 将未引用条目用 `%` 注释而非删除，保持原 bib 结构
- **安全预览** — `--dry-run` 在修改前预览结果

## 依赖

仅需 **Python 3.10+**，无第三方库依赖。

## 安装

```bash
pip install -e /path/to/bibdel
```

或从 PyPI（后续发布）：

```bash
pip install bibclean
```

安装后即可在任意目录使用 `bibclean` 命令。也可通过 `python -m bibclean` 运行。

## 快速开始

```bash
# 在论文项目根目录直接运行（默认：生成 new_XXX.bib）
bibclean

# 指定项目路径
bibclean /path/to/latex/project

# 先预览，不修改任何文件
bibclean --dry-run
```

## 使用案例

### 1. 默认模式：生成精简后的新文件

```bash
bibclean /path/to/paper-project
```

输出示例：

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
    - kingma2013auto
    ...
  Wrote to new_refs.bib (20 entries removed).

Done.
```

原始 `refs.bib`（75 条）未被修改，`new_refs.bib`（55 条）为新生成的精简文件。

### 2. 注释模式：保留原 bib 结构

```bash
bibclean /path/to/paper-project --comment
```

效果：未引用条目的每一行加 `% ` 前缀，已引用条目保持不变，`@string`、`@comment` 块保留原样。

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

### 3. 原地修改

```bash
# 直接修改原 bib 文件（移除未引用条目）
bibclean --in-place

# 直接修改原 bib 文件（注释未引用条目）
bibclean --in-place --comment
```

### 4. 手动保护特定条目

```bash
# 保留 lecun1998gradient 和 kingma2013auto，即使未被引用
bibclean --keep "lecun1998gradient,kingma2013auto"
```

### 5. 多版本项目

当项目中存在多个带 `\documentclass` 的 tex 文件（例如论文的多个修订版本）时，程序会列出所有候选项：

```
Multiple main .tex files detected:

  [1] paper_v1.tex
  [2] paper_v2_final.tex

Select main file [1-2]:
```

输入序号选择要作为主入口的文件。

### 6. 指定 bib 文件（覆盖自动发现）

```bash
bibclean --bib references.bib
```

### 7. 仅扫描根目录（不搜索子目录中的 tex 文件）

```bash
bibclean --no-recursive
```

注意：`--no-recursive` 只影响 glob 级别的 tex 搜索，**不会阻止**主 tex 中 `\input`/`\include` 的子文件引用跟踪。

## 模式速查

| 参数 | 输出文件 | 对未引用条目的操作 |
|---|---|---|
| *(无)* | `new_XXX.bib` | 删除 |
| `--comment` | `new_XXX.bib` | 用 `%` 注释 |
| `--in-place` | 原文件 | 删除 |
| `--in-place --comment` | 原文件 | 用 `%` 注释 |
| `--dry-run` | 无 | 仅预览 |

## 支持的引用命令

程序能识别所有常见的 LaTeX 引用命令变体：

`\cite` `\citep` `\citet` `\citeauthor` `\citeyear` `\citealp` `\citealt`
`\parencite` `\textcite` `\footcite` `\autocite` `\supercite` `\fullcite`
`\Cite` `\Citep` `\Citet`（大写变体）`\cite*`（星号变体）

支持可选参数：`\cite[page 3]{key}`、`\citep[see][chap 2]{key}`
支持多键：`\cite{key1,key2,key3}`
完全支持 `\nocite{*}`（检测到后保留全部条目）

## 支持的 Bib 格式

- 所有标准条目类型：`@article`、`@inproceedings`、`@book`、`@incollection`、`@misc` 等
- `@string`、`@comment`、`@preamble` 块自动保留
- 正确处理字段值中的嵌套花括号（如 `{CNN}`、`{\L}ukasz`）
- 自动解析 `crossref` 字段，保留引用链中的父条目

## 测试

项目包含 21 个自动化测试用例，覆盖全部模式、边界情况和引用模式。

```bash
python tests/test_bib_cleaner.py
```

预期输出：`81/81 passed — all passed!`

## 许可证

MIT
