You are the change-semantics implementation agent for RWX. Build and measure one candidate; do not repeat basic AST-applicator work.

Root: `/Users/srujansai/Desktop/RWX - Blast Radius`. Read `src/change_analysis.py`, `src/patch_parser.py`, `src/coverage_selector.py`, their tests, and `docs/RE0_EXECUTION_MEMO.md`.

Already implemented and tested: original-coordinate multi-hunk application, old/new count checks, overlap/order checks, no-newline markers, pre/post parsing, post-range added-line mapping, pre-range removed-line mapping, AST-identical no-op suppression, and full fallback on uncertainty. Do not report these as proposals.

Choose one new semantic mechanism: branch-condition mutation impacts, class/module variable-use mapping, decorator/signature dependencies, docstring/source-inspection distinctions, or another concrete source-derived relation. Implement the smallest complete version with conservative fallback. It must be generic and derived from pinned source plus the patch, never from commit outcomes.

Required proof:

1. Tests for shifted multi-hunk edits, true syntax errors, no-newline input, nested functions/classes, and unchanged shifted symbols remain green.
2. Add focused tests for the new relation and its fallback.
3. Run the real Docker sample; promote only if zero official and independent misses and lower cost than 167.612 seconds.
4. Exercise a real patched suite that distinguishes the new relation from baseline line coverage.
5. Record results and revert on any miss or non-improvement.

Return implementation and evidence, not a design-only document.
