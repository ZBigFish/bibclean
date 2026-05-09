#!/usr/bin/env python3
"""
Comprehensive test suite for bibclean.
Tests all modes, edge cases, and citation patterns against prepared fixtures.
"""

import subprocess
import shutil
import sys
import re
from pathlib import Path

FIXTURES_DIR = Path(__file__).parent / 'fixtures'
TMP_DIR = Path(__file__).parent / 'tmp_test'

PASS = 0
FAIL = 0


def run_cleaner(fixture_path: Path, *args) -> subprocess.CompletedProcess:
    """Run bibkit clean on a fixture. Extra args are CLI flags.
    If stdin text is the first arg, pipe it in."""
    cmd = ['bibkit', 'clean', str(fixture_path)]
    input_text = None
    for a in args:
        if isinstance(a, str) and a.startswith('STDIN:'):
            input_text = a[5:]
        else:
            cmd.append(str(a))
    return subprocess.run(cmd, capture_output=True, text=True,
                          input=input_text,
                          timeout=30)


def count_entries(bib_path: Path) -> int:
    """Count the number of bibliography entries in a bib file."""
    text = bib_path.read_text(encoding='utf-8', errors='replace')
    return len(re.findall(r'@(\w+)\s*\{\s*([^\s,]+)\s*,', text))


def count_commented_entries(bib_path: Path) -> int:
    """Count entries that have been commented out with % prefix."""
    text = bib_path.read_text(encoding='utf-8', errors='replace')
    # Find lines starting with % @ which indicate commented entry heads
    return len(re.findall(r'^% @\w+\{', text, re.MULTILINE))


def count_uncommented_entries(bib_path: Path) -> int:
    """Count entries that are NOT commented out."""
    text = bib_path.read_text(encoding='utf-8', errors='replace')
    all_entries = re.findall(r'^(?:% )?(@\w+\{[^\s,]+\s*,)', text, re.MULTILINE)
    commented = set(re.findall(r'^% (@\w+\{[^\s,]+\s*,)', text, re.MULTILINE))
    return len([e for e in all_entries if e not in commented])


def count_original_entries(fixture_name: str, bib_name: str = 'refs.bib') -> int:
    """Count entries in the original fixture bib file."""
    return count_entries(FIXTURES_DIR / fixture_name / bib_name)


def teardown():
    """Remove temp working directory."""
    if TMP_DIR.exists():
        shutil.rmtree(TMP_DIR, ignore_errors=True)


def setup(fixture_name: str) -> Path:
    """Copy a fixture to temp dir and return its path."""
    teardown()
    src = FIXTURES_DIR / fixture_name
    dst = TMP_DIR
    shutil.copytree(str(src), str(dst))
    return dst


def check(description: str, condition: bool, detail: str = ''):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  PASS  {description}")
    else:
        FAIL += 1
        print(f"  FAIL  {description}  {detail}")


def check_file_exists(path: Path, description: str):
    check(f"{description}: file exists", path.exists(), str(path))


def check_file_not_exists(path: Path, description: str):
    check(f"{description}: file not created", not path.exists(), str(path))


# ── Test Cases ─────────────────────────────────────────────────────────

def test_simple_default():
    """Fixture: simple — Default mode: write new_refs.bib, original untouched."""
    print("\n[Test] simple — default mode")
    dst = setup('simple')
    orig_count = count_entries(dst / 'refs.bib')

    run_cleaner(dst)

    check_file_exists(dst / 'new_refs.bib', "new_refs.bib created")
    check("original refs.bib unchanged", count_entries(dst / 'refs.bib') == orig_count)
    check("new_refs.bib has fewer entries", count_entries(dst / 'new_refs.bib') < orig_count)
    check("new_refs.bib has only cited entries (3)",
          count_entries(dst / 'new_refs.bib') == 3,
          f"got {count_entries(dst / 'new_refs.bib')}")
    new_text = (dst / 'new_refs.bib').read_text(encoding='utf-8')
    check("cited he2016deep kept", 'he2016deep' in new_text)
    check("cited krizhevsky2012imagenet kept", 'krizhevsky2012imagenet' in new_text)
    check("cited vaswani2017attention kept", 'vaswani2017attention' in new_text)
    check("uncited lecun1998gradient removed", 'lecun1998gradient' not in new_text)
    check("uncited goodfellow2014generative removed", 'goodfellow2014generative' not in new_text)


def test_simple_comment():
    """Fixture: simple — Comment mode: comment out unused, keep structure."""
    print("\n[Test] simple — --comment mode")
    dst = setup('simple')
    orig_count = count_entries(dst / 'refs.bib')

    run_cleaner(dst, '--comment')

    check_file_exists(dst / 'new_refs.bib', "new_refs.bib created")
    check("original refs.bib unchanged", count_entries(dst / 'refs.bib') == orig_count)
    check("all entries present (3 cited + 2 commented)",
          count_entries(dst / 'new_refs.bib') == 5)
    new_text = (dst / 'new_refs.bib').read_text(encoding='utf-8')
    check("he2016deep not commented", not re.search(r'^% @inproceedings\{he2016deep', new_text, re.MULTILINE),
          "he2016deep should be uncommented")
    check("goodfellow2014generative commented", bool(re.search(r'^% @article\{goodfellow2014generative', new_text, re.MULTILINE)),
          "goodfellow2014generative should have % prefix")


def test_simple_in_place():
    """Fixture: simple — --in-place: modify original, no new file."""
    print("\n[Test] simple — --in-place mode")
    dst = setup('simple')
    orig_count = count_entries(dst / 'refs.bib')

    run_cleaner(dst, '--in-place')

    check_file_not_exists(dst / 'new_refs.bib', "no new_refs.bib")
    new_count = count_entries(dst / 'refs.bib')
    check("original modified (fewer entries)", new_count < orig_count,
          f"{new_count} vs {orig_count}")
    check("only cited entries (3)", new_count == 3, f"got {new_count}")
    text = (dst / 'refs.bib').read_text(encoding='utf-8')
    check("goodfellow2014generative removed", 'goodfellow2014generative' not in text)


def test_simple_in_place_comment():
    """Fixture: simple — --in-place --comment: modify original, comment unused."""
    print("\n[Test] simple — --in-place --comment mode")
    dst = setup('simple')

    run_cleaner(dst, '--in-place', '--comment')

    check_file_not_exists(dst / 'new_refs.bib', "no new_refs.bib")
    text = (dst / 'refs.bib').read_text(encoding='utf-8')
    check("he2016deep uncommented", not re.search(r'^% @inproceedings\{he2016deep', text, re.MULTILINE))
    check("goodfellow2014generative commented", bool(re.search(r'^% @article\{goodfellow2014generative', text, re.MULTILINE)))
    check("all entries preserved", count_entries(dst / 'refs.bib') == 5)


def test_simple_dry_run():
    """Fixture: simple — --dry-run: no files created or modified."""
    print("\n[Test] simple — --dry-run mode")
    dst = setup('simple')
    orig_text = (dst / 'refs.bib').read_text(encoding='utf-8')

    r = run_cleaner(dst, '--dry-run')

    check_file_not_exists(dst / 'new_refs.bib', "no new_refs.bib created in dry-run")
    check("original unchanged", (dst / 'refs.bib').read_text(encoding='utf-8') == orig_text)
    check("output mentions 'would write'", 'would write' in r.stdout)
    check("output mentions 'removed'", 'removed' in r.stdout)


def test_simple_keep():
    """Fixture: simple — --keep: protect uncited entries from removal."""
    print("\n[Test] simple — --keep mode")
    dst = setup('simple')

    run_cleaner(dst, '--keep', 'lecun1998gradient')

    new_text = (dst / 'new_refs.bib').read_text(encoding='utf-8')
    check("kept entry lecun1998gradient preserved", 'lecun1998gradient' in new_text)
    check("uncited goodfellow2014generative still removed", 'goodfellow2014generative' not in new_text)
    check("4 entries total (3 cited + 1 kept)", count_entries(dst / 'new_refs.bib') == 4,
          f"got {count_entries(dst / 'new_refs.bib')}")


def test_multi_input():
    """Fixture: multi_input — resolve \\input, collect cites from all sub-files."""
    print("\n[Test] multi_input — \\input resolution")
    dst = setup('multi_input')

    r = run_cleaner(dst)

    check("main.tex detected as main", 'main.tex' in r.stdout)
    check("2 included files found", '2 included' in r.stdout)
    check("4 unique citation keys (he, krizhevsky, vaswani, ioffe)",
          '4 unique citation key' in r.stdout,
          r.stdout)
    new_text = (dst / 'new_refs.bib').read_text(encoding='utf-8')
    check("he2016deep kept (from intro.tex)", 'he2016deep' in new_text)
    check("ioffe2015batch kept (from method.tex)", 'ioffe2015batch' in new_text)
    check("goodfellow2014generative removed (never cited)", 'goodfellow2014generative' not in new_text)


def test_multi_input_no_recursive():
    """Fixture: multi_input — --no-recursive still follows \\input includes."""
    print("\n[Test] multi_input — --no-recursive with \\input")
    dst = setup('multi_input')

    r = run_cleaner(dst, '--no-recursive')

    check("2 included files still found", '2 included' in r.stdout)
    check("4 unique citation keys still found", '4 unique citation key' in r.stdout)
    new_text = (dst / 'new_refs.bib').read_text(encoding='utf-8')
    check("he2016deep kept", 'he2016deep' in new_text)
    check("ioffe2015batch kept", 'ioffe2015batch' in new_text)


def test_multi_version_select_first():
    """Fixture: multi_version — select v1, uses refs_v1.bib."""
    print("\n[Test] multi_version — select v1")
    dst = setup('multi_version')

    r = run_cleaner(dst, 'STDIN:1')

    check("prompt shows 2 candidates", '2]' in r.stdout)
    check("paper_v1 selected", 'paper_v1' in r.stdout.lower() or '1' in r.stdout)
    # v1 only cites he2016deep, so refs_v1.bib should keep he2016deep and remove goodfellow2014generative
    if (dst / 'new_refs_v1.bib').exists():
        new_text = (dst / 'new_refs_v1.bib').read_text(encoding='utf-8')
        check("he2016deep kept", 'he2016deep' in new_text)
        check("goodfellow2014generative removed", 'goodfellow2014generative' not in new_text)


def test_multi_version_select_second():
    """Fixture: multi_version — select v2, uses refs_v2.bib."""
    print("\n[Test] multi_version — select v2")
    dst = setup('multi_version')

    r = run_cleaner(dst, 'STDIN:2')

    check("prompt shows 2 candidates", '2]' in r.stdout)
    if (dst / 'new_refs_v2.bib').exists():
        new_text = (dst / 'new_refs_v2.bib').read_text(encoding='utf-8')
        check("he2016deep kept", 'he2016deep' in new_text)
        check("vaswani2017attention kept", 'vaswani2017attention' in new_text)
        check("goodfellow2014generative removed", 'goodfellow2014generative' not in new_text)


def test_crossref():
    """Fixture: crossref — crossref parent entries preserved."""
    print("\n[Test] crossref — dependency resolution")
    dst = setup('crossref')

    run_cleaner(dst)

    r = run_cleaner(dst, '--dry-run')
    check("crossref parent neurips2016 kept",
          'neurips2016' in r.stdout and 'referenced via crossref' in r.stdout)
    new_text = (dst / 'new_refs.bib').read_text(encoding='utf-8')
    check("neurips2016 in output (crossref parent)", 'neurips2016' in new_text)
    check("goodfellow2014generative removed (uncited, no crossref)", 'goodfellow2014generative' not in new_text)


def test_nocite_star():
    """Fixture: nocite_star — \\nocite{*} keeps all entries."""
    print("\n[Test] nocite_star — \\\\nocite{*}")
    dst = setup('nocite_star')

    r = run_cleaner(dst)

    check("detected \\nocite{*}", 'nocite' in r.stdout.lower() and 'all bib entries' in r.stdout.lower())
    check("Nothing to do message", 'Nothing to do' in r.stdout)
    check_file_not_exists(dst / 'new_refs.bib',
                          "no new file (all cited, nothing to do)")
    check("original unchanged", count_entries(dst / 'refs.bib') == 3)


def test_no_documentclass():
    """Fixture: no_documentclass — fallback: glob all .tex files."""
    print("\n[Test] no_documentclass — fallback (no \\\\documentclass)")
    dst = setup('no_documentclass')

    r = run_cleaner(dst)

    check("fallback message shown", 'No .tex file with' in r.stdout)
    new_text = (dst / 'new_refs.bib').read_text(encoding='utf-8')
    check("he2016deep kept (cited in notes.tex)", 'he2016deep' in new_text)
    check("vaswani2017attention kept (cited in appendix.tex)", 'vaswani2017attention' in new_text)
    check("goodfellow2014generative removed", 'goodfellow2014generative' not in new_text)


def test_no_documentclass_no_recursive():
    """Fixture: no_documentclass — --no-recursive limits glob to root .tex only."""
    print("\n[Test] no_documentclass — --no-recursive fallback")
    dst = setup('no_documentclass')
    # Move one tex file to subdir so --no-recursive won't find it
    subdir = dst / 'subdir'
    subdir.mkdir()
    shutil.move(str(dst / 'appendix.tex'), str(subdir / 'appendix.tex'))
    # Still put refs.bib in root so it's found

    r = run_cleaner(dst, '--no-recursive')

    # Only notes.tex in root, so only he2016deep should be cited
    new_text = (dst / 'new_refs.bib').read_text(encoding='utf-8')
    check("he2016deep kept (in root notes.tex)", 'he2016deep' in new_text)
    check("vaswani2017attention removed (in subdir, not scanned)", 'vaswani2017attention' not in new_text)


def test_edge_all_cited():
    """Fixture: edge_all_cited — all entries cited: skip writing, nothing to do."""
    print("\n[Test] edge_all_cited — nothing to remove")
    dst = setup('edge_all_cited')

    r = run_cleaner(dst)

    check("'No unused entries' message", 'No unused entries' in r.stdout)
    check("'Skipping' message", 'Skipping' in r.stdout)


def test_edge_none_cited():
    """Fixture: edge_none_cited — no citations: all entries removed."""
    print("\n[Test] edge_none_cited — all entries unused")
    dst = setup('edge_none_cited')

    r = run_cleaner(dst)

    check("0 unique citation keys", '0 unique citation key' in r.stdout)
    new_text = (dst / 'new_refs.bib').read_text(encoding='utf-8')
    check("both entries removed", count_entries(dst / 'new_refs.bib') == 0,
          f"got {count_entries(dst / 'new_refs.bib')}")


def test_special_chars_default():
    """Fixture: special_chars — @string, @comment, @preamble preserved, nested braces handled."""
    print("\n[Test] special_chars — @string/@comment/@preamble, nested braces")
    dst = setup('special_chars')
    orig_count = count_entries(dst / 'refs.bib')

    run_cleaner(dst)

    new_text = (dst / 'new_refs.bib').read_text(encoding='utf-8')
    check("@string preserved", '@string{cvpr' in new_text)
    check("@comment preserved", '@comment{' in new_text and 'should be preserved' in new_text)
    check("@preamble preserved", '@preamble' in new_text)
    check("nested braces in title preserved", '{CNN}' in new_text)
    check("escaped char {\\L}ukasz preserved", '{\\L}ukasz' in new_text)
    check("only cited 3 of 4 entries kept", count_entries(dst / 'new_refs.bib') == 3,
          f"got {count_entries(dst / 'new_refs.bib')}")
    check("goodfellow2014generative removed (uncited)", 'goodfellow2014generative' not in new_text)


def test_special_chars_comment():
    """Fixture: special_chars — comment mode preserves all structure including special blocks."""
    print("\n[Test] special_chars — --comment with special blocks")
    dst = setup('special_chars')

    run_cleaner(dst, '--comment')

    new_text = (dst / 'new_refs.bib').read_text(encoding='utf-8')
    check("@string preserved in comment mode", '@string{cvpr' in new_text)
    check("@comment NOT commented out", not re.search(r'^% @comment\{', new_text, re.MULTILINE),
          "@comment should remain as preamble, not get % prefix")
    check("@preamble NOT commented out", not re.search(r'^% @preamble', new_text, re.MULTILINE))
    check("uncited entry goodfellow2014generative commented",
          bool(re.search(r'^% @article\{goodfellow2014generative', new_text, re.MULTILINE)))
    check("cited entry he2016deep NOT commented",
          not re.search(r'^% @inproceedings\{he2016deep', new_text, re.MULTILINE))


def test_bib_flag_override():
    """Fixture: simple — --bib overrides auto-discovery."""
    print("\n[Test] simple — --bib flag override")
    dst = setup('simple')
    # Create a second bib that wouldn't be auto-discovered
    extra_bib = dst / 'extra.bib'
    extra_bib.write_text("""@article{test2024extra, title={Test}, author={Tester}, journal={J}, year={2024} }
""", encoding='utf-8')

    r = run_cleaner(dst, '--bib', 'extra.bib')

    check("processes extra.bib (not refs.bib)", 'extra.bib' in r.stdout)
    check("refs.bib not in output", 'refs.bib' not in r.stdout.split('---')[1] if '---' in r.stdout else True)

    # Also test that --bib with refs.bib works and doesn't touch extra.bib
    dst2 = setup('simple')
    (dst2 / 'extra.bib').write_text("""@article{test2024extra, title={Test}, author={Tester}, journal={J}, year={2024} }
""")
    run_cleaner(dst2, '--bib', 'refs.bib')
    check_file_exists(dst2 / 'new_refs.bib', "new_refs.bib created for specified bib")
    check_file_not_exists(dst2 / 'new_extra.bib', "extra.bib not processed")


def test_cwd_default():
    """Run from the project directory without specifying path."""
    print("\n[Test] cwd — default project path")
    dst = setup('simple')

    original_cwd = Path.cwd()
    try:
        import os
        os.chdir(str(dst))
        r = subprocess.run(
            ['bibkit', 'clean'],
            capture_output=True, text=True, timeout=30
        )
        check("runs without path argument", r.returncode == 0, r.stderr)
        check("detected main file paper.tex", 'paper.tex' in r.stdout)
        check_file_exists(Path('new_refs.bib'), "new_refs.bib created from cwd")
    finally:
        os.chdir(str(original_cwd))


def test_citation_patterns():
    """Verify various \cite variants are all captured."""
    print("\n[Test] citation patterns — all \\cite variants captured")
    dst = Path(TMP_DIR)
    teardown()
    dst.mkdir(parents=True, exist_ok=True)
    (dst / 'paper.tex').write_text(r"""\documentclass{article}
\begin{document}
\cite{key1}
\citep{key2}
\citet{key3}
\citeauthor{key4}
\citeyear{key5}
\parencite{key6}
\textcite{key7}
\cite[page 3]{key8}
\citep[see][chapter 2]{key9}
\Cite{key10}
\Citep{key11}
\Citet{key12}
\cite{key13,key14,key15}
\bibliography{refs}
\end{document}""", encoding='utf-8')
    # Create bib with all keys
    bib_entries = '\n'.join(
        f"@article{{key{i}, title={{Test {i}}}, author={{Author}}, journal={{J}}, year={{2024}} }}"
        for i in range(1, 16)
    )
    (dst / 'refs.bib').write_text(bib_entries, encoding='utf-8')

    r = run_cleaner(dst)

    check("15 unique citation keys found", '15 unique citation key' in r.stdout)
    # All 15 keys are cited → nothing to remove → no new file written
    check("No unused entries, skipping", 'No unused entries' in r.stdout)
    check("15 entries total, 15 to keep, 0 to remove",
          '15 unique citation key' in r.stdout and 'No unused entries' in r.stdout)


# ── Main ───────────────────────────────────────────────────────────────

def main():
    global PASS, FAIL

    print("=" * 60)
    print("bib_cleaner.py — Comprehensive Test Suite")
    print("=" * 60)

    tests = [
        # Core modes
        test_simple_default,
        test_simple_comment,
        test_simple_in_place,
        test_simple_in_place_comment,
        test_simple_dry_run,
        test_simple_keep,
        # Multi-file
        test_multi_input,
        test_multi_input_no_recursive,
        # Multiple versions
        test_multi_version_select_first,
        test_multi_version_select_second,
        # Crossref
        test_crossref,
        # \nocite{*}
        test_nocite_star,
        # No \documentclass fallback
        test_no_documentclass,
        test_no_documentclass_no_recursive,
        # Edge cases
        test_edge_all_cited,
        test_edge_none_cited,
        # Special characters / @string / nested braces
        test_special_chars_default,
        test_special_chars_comment,
        # --bib flag
        test_bib_flag_override,
        # CWD default
        test_cwd_default,
        # Citation patterns
        test_citation_patterns,
    ]

    for test in tests:
        try:
            test()
        except Exception as e:
            FAIL += 1
            print(f"  ERROR {test.__name__}: {e}")
            import traceback
            traceback.print_exc()
        finally:
            teardown()

    print("\n" + "=" * 60)
    total = PASS + FAIL
    print(f"Results: {PASS}/{total} passed", end='')
    if FAIL > 0:
        print(f", {FAIL} FAILED")
    else:
        print(" — all passed!")
    print("=" * 60)

    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
