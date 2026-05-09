# Contributing to Bibkit

Thanks for your interest in contributing! Here's how to get started.

## Getting Started

### Prerequisites

- Python 3.10+
- Git

### Setup

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/bibkit.git
cd bibkit
pip install -e .
```

### Running Tests

The test suite covers all modes, edge cases, and citation patterns:

```bash
python tests/test_bib_cleaner.py
```

All 81 checks must pass before submitting a PR.

## How to Contribute

### Reporting Bugs

Open an issue on GitHub with:
- Your OS and Python version (`python --version`)
- The exact `bibkit clean` command you ran
- A minimal `.tex` and `.bib` snippet that reproduces the issue

### Suggesting Features

Open an issue with the `enhancement` label. Describe:
- The use case / problem you're trying to solve
- How you'd expect the feature to work
- Why it fits within bibkit's scope

### Pull Requests

1. **Create a branch**: `git checkout -b feat/my-feature` (or `fix/my-bug`)
2. **Make your changes**: Keep them focused — one PR = one logical change
3. **Add tests** if you're adding new functionality
4. **Run the full test suite**: `python tests/test_bib_cleaner.py`
5. **Follow existing code style**: plain Python, no comments unless the _why_ is non-obvious
6. **Write a clear PR description**: what changed, why, and how to test it

### Code Style

- No external dependencies unless absolutely necessary
- Keep functions small and single-purpose
- Type hints where they add clarity
- Short docstrings for public functions — one line is enough

## Project Structure

```
bibkit/
├── bibkit/            # Package source
│   ├── __init__.py
│   ├── __main__.py    # python -m bibkit entry
│   └── cli.py         # Core logic + CLI subcommands
├── tests/
│   ├── fixtures/      # Test project fixtures
│   │   ├── simple/
│   │   ├── multi_input/
│   │   ├── crossref/
│   │   └── ...
│   └── test_bib_cleaner.py  # Test suite
├── pyproject.toml     # Package metadata
├── README.md
├── README_CN.md
└── LICENSE
```

## Questions?

Open a [discussion](https://github.com/ZBigFish/bibkit/discussions) or file an [issue](https://github.com/ZBigFish/bibkit/issues).
