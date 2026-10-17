# Figure 1: Corpus preparation and LLM-assisted coding workflow

[All figures](../README.md)

## Data and code

Run these commands from the repository root:

```text
node figures/figure1/code/build_figure1.mjs
```

| Script | Original archived filename |
| --- | --- |
| [build_figure1.mjs](code/build_figure1.mjs) | `build_figure1.mjs` |

Directly supplied inputs:

- [data/inputs/analysis_dataset_in_scope.csv](data/inputs/analysis_dataset_in_scope.csv)

Original data values, Chinese coding labels and source prompt documents are preserved. Additional source tables and materials are in the figure's data subdirectories. Historical absolute paths inside source data are provenance, not current runtime paths.

## Outputs and reproduction

Submitted final artwork:

- [figure1.pdf](outputs/final/figure1.pdf)
- [figure1_redrawn_editable.pptx](outputs/final/figure1_redrawn_editable.pptx)
- [figure1_redrawn_editable_01.png](outputs/final/figure1_redrawn_editable_01.png)

Archived script output, where supplied, is in `outputs/script_reference/`. Running a script writes only to ignored `outputs/reproduced/`, keeping the archived artwork intact. Historical figure numbers in source-table/output filenames are preserved for traceability; this directory's figure number is the manuscript number.

The archived upstream program is [code/upstream/make_heritage_results.py](code/upstream/make_heritage_results.py). It reads the repository's original [coding table](../../data/heritage_llm_coding_results.csv) and [metadata table](../../data/nsfc_results_with_achievement_stat.csv) by default, and writes to this figure's `outputs/reproduced/upstream/`. `DATA_DIR` can override its input directory. Per-figure upstream copies were checked against the repository originals.

The drawing program requires Node.js with `@oai/artifact-tool` available to its module resolver (tested version 2.8.99). The supplied package.json is a private ES-module marker and does not install that runtime. In an environment without this package, use the preserved editable PPTX; do not assume that a standard Node installation alone can run the program. The DOCX files in `data/methods/` are original Chinese research prompts and remain unchanged.

## Verification status

The earlier review matched 79 text boxes after normalizing whitespace and case. This package retains 34 original redraw assets and 32 assets embedded in the final PPTX. The final PPTX includes manual material and layout edits, so the script is not a byte-identical generator of the submitted artwork.

Source/destination names and SHA-256 values are recorded in [the file manifest](../../metadata/figure_file_manifest.csv). The adapted publication code changes file locations only; original analytical rules and plotting parameters are preserved. See [verification results](../verification.md) for the current offline checks.
