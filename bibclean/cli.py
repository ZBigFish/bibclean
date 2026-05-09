"""CLI entry point for bibclean."""

import re
import argparse
import sys
from pathlib import Path
from collections import OrderedDict


# ── citation extraction ────────────────────────────────────────────────

_CITE_CMD_RE = re.compile(
    r'\\(?:[a-zA-Z]*cite[a-zA-Z]*|[a-z]*[Cc]ite[a-zA-Z]*)'
    r'(?:\*)?'
    r'(?:\[[^\]]*\])*'
    r'\{([^}]+)\}',
)


def extract_citation_keys(tex_content: str) -> set[str]:
    """Return the set of citation keys found in .tex content."""
    keys: set[str] = set()
    for match in _CITE_CMD_RE.finditer(tex_content):
        key_list = match.group(1)
        for raw in key_list.split(','):
            k = raw.strip()
            if k and k != '*':
                keys.add(k)
            elif k == '*':
                return {'*'}
    return keys


# ── include / input resolution ─────────────────────────────────────────

_INPUT_RE = re.compile(r'\\(?:input|include)\s*\{([^}]+)\}')


def resolve_includes(main_tex: Path, project_dir: Path,
                     visited: set[Path] | None = None) -> list[Path]:
    """Recursively resolve \\input and \\include to collect all .tex files."""
    if visited is None:
        visited = set()
    resolved = [main_tex]
    visited.add(main_tex.resolve())
    content = main_tex.read_text(encoding='utf-8', errors='replace')
    for m in _INPUT_RE.finditer(content):
        name = m.group(1).strip()
        if not name.endswith('.tex'):
            name += '.tex'
        child = (main_tex.parent / name).resolve()
        if not child.exists():
            child = (project_dir / name).resolve()
        if child.exists() and child not in visited:
            resolved.extend(resolve_includes(child, project_dir, visited))
    return resolved


# ── main .tex detection ────────────────────────────────────────────────

def find_main_tex_candidates(project_dir: Path, recursive: bool = True) -> list[Path]:
    """Return .tex files that contain \\documentclass (main file candidates)."""
    candidates: list[Path] = []
    glob_fn = project_dir.rglob if recursive else project_dir.glob
    for tf in sorted(glob_fn('*.tex')):
        try:
            content = tf.read_text(encoding='utf-8', errors='replace')
        except Exception:
            continue
        if r'\documentclass' in content:
            candidates.append(tf)
    return candidates


# ── bib-resource extraction from .tex ───────────────────────────────────

_BIBLIOGRAPHY_RE = re.compile(r'\\bibliography\s*\{([^}]+)\}')
_ADDBIB_RE = re.compile(r'\\addbibresource(?:\[[^\]]*\])?\s*\{([^}]+\.bib)\}')


def extract_bib_filenames_from_tex(tex_content: str) -> list[str]:
    """Extract .bib filenames referenced via \\bibliography or \\addbibresource."""
    names: list[str] = []
    for m in _BIBLIOGRAPHY_RE.finditer(tex_content):
        for raw in m.group(1).split(','):
            name = raw.strip()
            if name:
                if not name.endswith('.bib'):
                    name += '.bib'
                names.append(name)
    for m in _ADDBIB_RE.finditer(tex_content):
        name = m.group(1).strip()
        if name:
            names.append(name)
    return names


def resolve_bib_files(project_dir: Path, main_tex: Path,
                      specified: str | None) -> list[Path]:
    """Resolve .bib files. Priority: --bib > auto-discovery from main .tex."""
    if specified:
        for base in [project_dir, main_tex.parent, Path('.')]:
            p = (base / specified).resolve()
            if p.exists():
                return [p]
        p = Path(specified)
        if p.exists():
            return [p]
        print(f"Warning: specified bib file '{specified}' not found.", file=sys.stderr)
        return []

    main_content = main_tex.read_text(encoding='utf-8', errors='replace')
    discovered = extract_bib_filenames_from_tex(main_content)

    bibs: list[Path] = []
    for name in discovered:
        for base in [project_dir, main_tex.parent]:
            p = (base / name).resolve()
            if p.exists():
                bibs.append(p)
                break
        else:
            p = Path(name)
            if p.exists():
                bibs.append(p)
            else:
                print(f"Warning: referenced bib file '{name}' not found.", file=sys.stderr)

    if bibs:
        return bibs

    # Fallback: glob all .bib in project
    return sorted(project_dir.rglob('*.bib'))


# ── bib parsing ────────────────────────────────────────────────────────

_ENTRY_HEAD_RE = re.compile(r'@(\w+)\s*\{\s*([^\s,]+)\s*,')


def parse_bib_entries(bib_path: Path) -> tuple[str, OrderedDict[str, str],
                                                dict[str, tuple[int, int]]]:
    """
    Parse a .bib file into (preamble, entries, entry_positions).
    entry_positions maps key -> (start_byte, end_byte) in the source file.
    """
    text = bib_path.read_text(encoding='utf-8', errors='replace')
    entries: OrderedDict[str, str] = OrderedDict()
    entry_positions: dict[str, tuple[int, int]] = {}
    preamble = ''
    i = 0
    n = len(text)

    while i < n:
        while i < n:
            ch = text[i]
            if ch == '%':
                while i < n and text[i] != '\n':
                    i += 1
                continue
            if ch.isspace():
                i += 1
                continue
            break

        if i >= n:
            break

        if text[i] != '@':
            preamble += text[i]
            i += 1
            continue

        start = i
        brace_start = text.find('{', i)
        if brace_start == -1:
            preamble += text[i:]
            break

        comma_pos = text.find(',', brace_start + 1)
        if comma_pos == -1:
            preamble += text[i:]
            break

        head = text[start:comma_pos + 1]
        head_match = _ENTRY_HEAD_RE.match(head)
        if head_match is None:
            depth = 1
            j = brace_start + 1
            while j < n and depth > 0:
                if text[j] == '{':
                    depth += 1
                elif text[j] == '}':
                    depth -= 1
                j += 1
            preamble += text[start:j]
            i = j
            continue

        entry_type = head_match.group(1).lower()
        entry_key = head_match.group(2)

        depth = 1
        j = brace_start + 1
        while j < n and depth > 0:
            if text[j] == '{':
                depth += 1
            elif text[j] == '}':
                depth -= 1
            j += 1

        if depth != 0:
            preamble += text[start:]
            break

        raw_entry = text[start:j]

        non_entry_types = {'string', 'comment', 'preamble'}
        if entry_type in non_entry_types:
            preamble += raw_entry
        else:
            entries[entry_key] = raw_entry
            entry_positions[entry_key] = (start, j)

        preamble += '\n'
        i = j

    return preamble, entries, entry_positions


# ── crossref extraction ─────────────────────────────────────────────────

_CROSSREF_RE = re.compile(
    r'crossref\s*=\s*\{([^}]+)\}|\bcrossref\s*=\s*(\w+)', re.IGNORECASE
)


def extract_crossref_deps(entries: OrderedDict[str, str]) -> dict[str, str]:
    deps: dict[str, str] = {}
    for key, body in entries.items():
        m = _CROSSREF_RE.search(body)
        if m:
            deps[key] = (m.group(1) or m.group(2)).strip()
    return deps


def resolve_crossref_closure(cited: set[str],
                              entries: OrderedDict[str, str]) -> set[str]:
    deps = extract_crossref_deps(entries)
    closure = set(cited)
    changed = True
    while changed:
        changed = False
        for entry_key, parent_key in deps.items():
            if entry_key in closure and parent_key not in closure:
                closure.add(parent_key)
                changed = True
    return closure


# ── bib writing ────────────────────────────────────────────────────────

def write_bib(path: Path, preamble: str, entries: OrderedDict[str, str]):
    """Write preamble + selected entries to a .bib file."""
    with open(path, 'w', encoding='utf-8') as f:
        f.write(preamble.rstrip('\n'))
        if preamble and not preamble.endswith('\n'):
            f.write('\n')
        for i, (key, body) in enumerate(entries.items()):
            if i > 0 or preamble:
                f.write('\n\n')
            f.write(body)
        f.write('\n')


def write_commented_bib(output_path: Path, source_text: str,
                        entry_positions: dict[str, tuple[int, int]],
                        kept_keys: set[str]):
    """
    Write .bib with unused entries commented out (% prefix per line).
    Preserves all preamble text, @string blocks, and entry ordering.
    """
    sorted_entries = sorted(entry_positions.items(), key=lambda x: x[1][0])

    parts: list[str] = []
    cursor = 0

    for key, (s, e) in sorted_entries:
        parts.append(source_text[cursor:s])
        entry_text = source_text[s:e]
        if key in kept_keys:
            parts.append(entry_text)
        else:
            lines = entry_text.split('\n')
            commented_lines = [
                '% ' + line if line.strip() else line
                for line in lines
            ]
            parts.append('\n'.join(commented_lines))
        cursor = e

    parts.append(source_text[cursor:])
    output_path.write_text(''.join(parts), encoding='utf-8')


# ── old-style scanning (fallback when no \\documentclass detected) ─────

def find_tex_files(project_dir: Path) -> list[Path]:
    return sorted(project_dir.rglob('*.tex'))


# ── main ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='Manage unused entries in .bib files based on '
                    '\\cite usage in .tex files. By default, auto-detects '
                    'the main .tex file and writes a new "new_<name>.bib" '
                    'for each bib file without touching the originals.'
    )
    parser.add_argument(
        'project', type=str, nargs='?', default='.',
        help='Path to the LaTeX project directory (default: current directory).'
    )
    parser.add_argument(
        '--bib', type=str, default=None,
        help='Specific .bib file to process (default: auto-discover from main .tex).'
    )
    parser.add_argument(
        '--dry-run', action='store_true',
        help='Print what would happen without modifying any files.'
    )
    parser.add_argument(
        '--in-place', action='store_true',
        help='Modify the original .bib file directly (default: write new_<name>.bib).'
    )
    parser.add_argument(
        '--comment', action='store_true',
        help='Comment out unused entries with %% instead of removing them.'
    )
    parser.add_argument(
        '--keep', type=str, default='',
        help='Comma-separated list of extra citation keys to preserve.'
    )
    parser.add_argument(
        '--no-recursive', action='store_true',
        help='Do not search subdirectories for .tex files '
             '(\\input/\\include following is always active).'
    )
    args = parser.parse_args()

    project = Path(args.project).resolve()
    if not project.is_dir():
        print(f"Error: '{project}' is not a directory.", file=sys.stderr)
        sys.exit(1)

    # ── 1. Find main .tex ──────────────────────────────────────────────
    recursive = not args.no_recursive
    candidates = find_main_tex_candidates(project, recursive=recursive)

    if not candidates:
        print("No .tex file with \\documentclass found. Using all .tex files.\n")
        tex_files = (find_tex_files(project) if recursive
                     else sorted(project.glob('*.tex')))
        main_tex = tex_files[0] if tex_files else None
        if not tex_files:
            print("No .tex files found in the project directory.", file=sys.stderr)
            sys.exit(1)
    elif len(candidates) == 1:
        main_tex = candidates[0]
        print(f"Main file: {main_tex.relative_to(project)}")
        tex_files = resolve_includes(main_tex, project)
        print(f"  (with {len(tex_files) - 1} included .tex file(s))\n")
    else:
        print("Multiple main .tex files detected:\n")
        for i, c in enumerate(candidates):
            try:
                rel = c.relative_to(project)
            except ValueError:
                rel = c
            print(f"  [{i + 1}] {rel}")
        print()
        try:
            choice = input(f"Select main file [1-{len(candidates)}]: ").strip()
            idx = int(choice) - 1
            if idx < 0 or idx >= len(candidates):
                raise ValueError
            main_tex = candidates[idx]
        except (ValueError, EOFError):
            print("Invalid selection.", file=sys.stderr)
            sys.exit(1)
        tex_files = resolve_includes(main_tex, project)
        print()

    # ── 2. Find .bib files ─────────────────────────────────────────────
    bib_files = resolve_bib_files(project, main_tex, args.bib)

    if not bib_files:
        print("No .bib files found. Use --bib to specify one.", file=sys.stderr)
        sys.exit(1)

    # ── 3. Extract citation keys ───────────────────────────────────────
    cited_keys: set[str] = set()
    for tf in tex_files:
        content = tf.read_text(encoding='utf-8', errors='replace')
        keys = extract_citation_keys(content)
        if '*' in keys:
            print(f"Found \\nocite{{*}} in {tf.name} — all bib entries are considered cited.\n")
            cited_keys = {'*'}
            break
        cited_keys |= keys

    for k in args.keep.split(','):
        k = k.strip()
        if k:
            cited_keys.add(k)

    n_files = len(tex_files)
    n_keys = len(cited_keys) if '*' not in cited_keys else '∞'
    print(f"Scanned {n_files} .tex file(s), found {n_keys} unique citation key(s).\n")

    # ── 4. Process each .bib file ──────────────────────────────────────
    for bib_path in bib_files:
        print(f"--- {bib_path.name} ---")
        source_text = bib_path.read_text(encoding='utf-8', errors='replace')
        preamble, entries, entry_positions = parse_bib_entries(bib_path)
        print(f"  Total entries: {len(entries)}")

        if '*' in cited_keys:
            print("  All entries are cited (\\nocite{*}). Nothing to do.\n")
            continue

        effective = resolve_crossref_closure(cited_keys, entries)
        crossref_added = effective - cited_keys

        if crossref_added:
            print(f"  Crossref parents kept: {len(crossref_added)}")
            for k in sorted(crossref_added):
                print(f"    + {k} (referenced via crossref)")

        kept = OrderedDict()
        unused: list[str] = []
        for key, body in entries.items():
            if key in effective:
                kept[key] = body
            else:
                unused.append(key)

        action_word = "commented out" if args.comment else "removed"
        output_path = bib_path if args.in_place else bib_path.parent / f"new_{bib_path.name}"

        print(f"  Entries to keep:   {len(kept)}")
        print(f"  Entries to {action_word}: {len(unused)}")

        if unused:
            if len(unused) <= 30:
                for key in unused:
                    print(f"    - {key}")
            else:
                for key in unused[:15]:
                    print(f"    - {key}")
                print(f"    ... and {len(unused) - 15} more")

        if args.dry_run:
            if unused:
                print(f"  (dry-run: would write {output_path.name} "
                      f"with {len(unused)} entries {action_word})\n")
            else:
                print(f"  (dry-run: no unused entries; nothing to do)\n")
            continue

        if not unused:
            print("  No unused entries. Skipping.\n")
            continue

        if args.comment:
            write_commented_bib(output_path, source_text, entry_positions, effective)
        else:
            write_bib(output_path, preamble, kept)

        print(f"  Wrote to {output_path.name} ({len(unused)} entries {action_word}).\n")

    print("Done.")


if __name__ == '__main__':
    main()
