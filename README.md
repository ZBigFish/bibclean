<div align="center">

# Bibkit: A BibTeX Toolbox for LaTeX Projects

<img src="https://img.shields.io/badge/python-3.10+-blue?style=flat-square&logo=python&logoColor=white" alt="Python">
<img src="https://img.shields.io/badge/tests-81%2F81%20passed-brightgreen?style=flat-square" alt="Tests">
<img src="https://img.shields.io/github/license/ZBigFish/bibkit?style=flat-square" alt="License">
<img src="https://img.shields.io/badge/platform-cross--platform-lightgrey?style=flat-square" alt="Platform">

</div>

> 中文文档：[README_CN.md](README_CN.md)

**Bibkit** is a command-line toolbox for managing BibTeX (`.bib`) files in LaTeX projects. It analyzes your `.tex` source to understand what references are actually used, and provides utilities to keep your bibliography clean and consistent.

---

## Table of Contents

- [Installation](#installation)
- [Commands](#commands)
  - [`bibkit clean`](#bibkit-clean)
- [Roadmap](#roadmap)
- [Supported Citation Commands](#supported-citation-commands)
- [Supported BibTeX Features](#supported-bibtex-features)
- [Contributing](#contributing)
- [License](#license)

---

## Installation

```bash
git clone https://github.com/ZBigFish/bibkit.git
cd bibkit
pip install -e .
```

The `bibkit` command is available globally after installation. You can also use `python -m bibkit`.

## Commands

### `bibkit clean`

Remove or comment out unused entries from your `.bib` files based on actual `\cite` usage.

```bash
# Run from your LaTeX project root
bibkit clean

# Or specify a path
bibkit clean /path/to/my-paper

# Preview first
bibkit clean --dry-run
```

**Features:**
- Auto-detects the main `.tex` via `\documentclass`; prompts for choice when multiple versions exist
- Recursively follows `\input`/`\include` to collect all citations across sub-files
- Auto-discovers `.bib` files from `\bibliography{...}` and `\addbibresource{...}`
- Non-destructive by default — writes a `new_XXX.bib`, never touches originals
- `crossref` parent entries are kept automatically (transitive resolution)
- Handles `\nocite{*}` — all entries preserved

**Options:**

| Flag | Effect |
|---|---|
| *(none)* | Write `new_XXX.bib` with unused entries removed |
| `--comment` | Comment out unused entries with `%` instead of removing |
| `--in-place` | Modify the original `.bib` file directly |
| `--in-place --comment` | Modify original, comment out unused |
| `--dry-run` | Preview only — no files changed |
| `--keep "key1,key2"` | Comma-separated list of keys to always preserve |
| `--bib references.bib` | Process a specific bib file (overrides auto-discovery) |
| `--no-recursive` | Don't search subdirectories for `.tex` files |

**Example output:**

```
$ bibkit clean /path/to/paper

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

## Roadmap

| Command | Status | Description |
|---|---|---|
| `bibkit clean` | Done | Remove unused entries from `.bib` files |
| `bibkit merge` | Planned | Merge multiple `.bib` files with deduplication |
| `bibkit check` | Planned | Validate `.bib` entries (missing fields, malformed keys, broken crossrefs) |
| `bibkit sort` | Planned | Sort entries by key, author, or year |
| `bibkit fmt`  | Planned | Normalize formatting (capitalize titles, unify venue abbreviations) |
| `bibkit diff` | Planned | Show differences between two `.bib` files |

Have a feature request? [Open an issue](https://github.com/ZBigFish/bibkit/issues).

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

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=ZBigFish/bibkit&type=Date)](https://star-history.com/#ZBigFish/bibkit&Date)

## License

[MIT](LICENSE)

---

<br>
<div align="center">
  <sub>Built with ❤️ for researchers who care about clean bibliographies.</sub>
</div>
