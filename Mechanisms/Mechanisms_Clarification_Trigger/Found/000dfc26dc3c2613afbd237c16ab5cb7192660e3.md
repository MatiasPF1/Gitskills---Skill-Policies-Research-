---
name: robust-latex-formula-extraction
description: "Use this when extracting display equations from PDFs into $$...$$ LaTeX lines with exact rendering, while avoiding tool timeouts, hallucinated content, and syntax/quoting errors."
---

# Robust LaTeX Formula Extraction from PDFs

A resilient workflow to extract only standalone (display) equations from PDFs and write them as raw LaTeX, with fallbacks and validations that prevent common failure modes such as tool timeouts, hallucinated formulas, or broken LaTeX/quoting.

## When to Use

Activate this skill when a task asks you to:
- identify all equations that appear on their own line (display equations) in a PDF
- write them exactly as LaTeX using $$...$$ delimiters
- remove trailing tags and punctuation from the end of formulas
- append fixed versions only for syntax/typo corrections (not semantic changes)

## Core Workflow

1) Clarify scope and output format
- Only extract display equations (on their own line). Do not include inline math.
- Output each formula as a single line: `$$<formula>$$`.
- Remove trailing commas/periods/tags at the END of the formula only.
- If you fix a syntax error (e.g., unmatched braces), append the fixed version as additional lines after the originals.

2) Tool selection with bounded, test-first execution
- Inventory available tools before committing:
  - If a heavy converter that may preserve LaTeX (e.g., a PDF→Markdown/LaTeX converter) is available, run `--help` to confirm install.
  - Run a 1-page smoke test with a short timeout and capture logs. Confirm expected output (e.g., presence of math blocks) before scaling up.
- If heavy tools are unavailable, hang, or time out during the smoke test, stop and switch to lightweight, reliable fallbacks:
  - Use text and layout extractors (e.g., `pdftotext -layout`, `pdftohtml -xml`) to locate display-equation lines and their bounding boxes.
  - Optionally use a PDF library (e.g., PyMuPDF) to read page text and positions if available.
- Never leave long-running processes unattended. Always set timeouts and check for actual output artifacts before continuing.

3) Locating display equations (without guesswork)
- Prefer signals that indicate stand-alone equations:
  - Centered or isolated lines with high left/right margins in `-layout` text.
  - Equation numbers aligned near the right margin in the same y-band.
  - In XML (from `pdftohtml -xml`), clusters of glyphs on the same baseline spanning the page width with no surrounding paragraph text at that y-position.
- Merge wrapped lines that belong to the same display equation (based on proximity and alignment). Do not assume math content; confirm via layout signals.
- Do not infer or invent missing parts. If the text extraction drops special symbols and you cannot recover them reliably, mark the formula as problematic and avoid hallucinating replacements.

4) Transcription discipline (preserve exact display)
- Transcribe exactly what you can verify from extracted text/layout. Do not change the mathematical structure (e.g., do not turn a denominator into an exponent or vice versa).
- Only perform the minimal transformations required for LaTeX renderability, such as:
  - escaping special characters where needed
  - converting clearly recognized Unicode math symbols to their LaTeX equivalents (e.g., ×→\times, ±→\pm, ≤→\le, ≥→\ge) when they appear
- Do not “improve” stylistic choices (e.g., turning a plain operator name into \mathrm{}) unless the source unambiguously uses a roman operator and the change is necessary for correct LaTeX rendering.

5) Output assembly and safe writing
- Build the formula list in memory first. For each:
  - strip surrounding $$ if present
  - remove only trailing punctuation at the very end (commas/periods and obvious trailing equation-number tags like a final "(number)")
  - ensure it’s a single line and wrap as `$$<formula>$$`
- Write the file using a language-native file writer (e.g., Python), not shell here-docs, to avoid quoting/escaping corruption.

6) Validation before finalizing
- Run structural checks on each formula:
  - balanced (), [], {}
  - equal counts of \left and \right
  - absence of stray quotes/backticks/shell artifacts
- If a formula has a syntax issue you can safely fix without changing meaning (e.g., remove a trailing comma, add a missing \right that is obviously paired), append a corrected version as additional lines after all originals. Keep originals intact at the top section.
- If unsure about a fix, do not guess. Leave the original and flag the issue in your notes (not in the output file unless the task demands).

## Verification

Use these checks before delivering the file:
- Content checks
  - Only display equations included; no inline equations.
  - Each line strictly uses `$$...$$` with no extra text around.
  - Trailing punctuation removed only at the end of the formula; original math structure preserved.
- Syntax checks
  - Parentheses/brackets/braces balanced.
  - \left/\right pairs balanced.
  - No shell quoting artifacts (e.g., stray ' or \" or backticks) in formulas.
- Provenance checks
  - Each extracted formula can be pointed to a specific page and position if asked (keep private notes; not required in the output file).

Success criteria:
- The output file contains one formula per line, wrapped in `$$...$$`, matching the PDF’s display rendering (structure, ordering, and visible symbols).
- No hallucinated symbols or speculative rewrites.
- Fixed versions are appended only for syntax/typo corrections, clearly derived from actual issues.

## Common Pitfalls and How to Avoid Them

- Long-running converter hangs or timeouts
  - Always smoke-test with `--help` and a 1-page run + timeout. If it doesn’t produce verifiable math output, switch tools.
- Hallucinating formulas from memory or visual guesses
  - Only transcribe what you can extract from text/layout. If a piece is unreadable, don’t invent it.
- Silent background processes
  - Avoid running converters in the background without streaming logs. Use explicit timeouts and check for actual output files before proceeding.
- Altering math structure
  - Do not change denominators to exponents, add/removes sums/products, or normalize operators unless clearly required for LaTeX syntax.
- Broken LaTeX from shell quoting
  - Use a safe writer (Python/Open file APIs). Don’t pipe complex TeX through shell here-docs with nested quotes.
- Missing multi-line merges
  - Use layout signals (similar y and alignment) to join wrapped lines belonging to one display equation.

## Optional Script Usage

Use `scripts/math_formula_guard.py` to sanitize and validate formulas before writing the final file.

Examples:
- Validate and write formulas read from stdin:
  - cat formulas.txt | python3 scripts/math_formula_guard.py --stdin --output /path/to/latex_formula_extraction.md
- Validate a file of formulas (one per line), stripping trailing punctuation and wrapping in $$...$$:
  - python3 scripts/math_formula_guard.py --input formulas_raw.txt --output /path/to/latex_formula_extraction.md

The script reports bracket and \left/\right balance issues and removes trailing punctuation/tags at line ends. It does not invent content or change math structure.
