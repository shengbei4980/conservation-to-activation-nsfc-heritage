# Figure 8: Research-turn and application-context co-occurrence network

[All figures](../README.md)

## Data and code

Run these commands from the repository root:

```text
python figures/figure8/code/plot_research_turn_context_network.py
```

| Script | Original archived filename |
| --- | --- |
| [plot_research_turn_context_network.py](code/plot_research_turn_context_network.py) | `figure7_8_layout_adjustable.py` |

Directly supplied inputs:

- [data/inputs/analysis_dataset_in_scope.csv](data/inputs/analysis_dataset_in_scope.csv)
- [data/inputs/heritage_llm_coding_results.csv](data/inputs/heritage_llm_coding_results.csv)

Original data values, Chinese coding labels and source prompt documents are preserved. Additional source tables and materials are in the figure's data subdirectories. Historical absolute paths inside source data are provenance, not current runtime paths.

## Outputs and reproduction

Submitted final artwork:

- [figure8.ai](outputs/final/figure8.ai)
- [figure8.pdf](outputs/final/figure8.pdf)
- [figure8_01.png](outputs/final/figure8_01.png)

Archived script output, where supplied, is in `outputs/script_reference/`. Running a script writes only to ignored `outputs/reproduced/`, keeping the archived artwork intact. Historical figure numbers in source-table/output filenames are preserved for traceability; this directory's figure number is the manuscript number.

The archived upstream program is [code/upstream/make_heritage_results.py](code/upstream/make_heritage_results.py). It reads the repository's original [coding table](../../data/heritage_llm_coding_results.csv) and [metadata table](../../data/nsfc_results_with_achievement_stat.csv) by default, and writes to this figure's `outputs/reproduced/upstream/`. `DATA_DIR` can override its input directory. Per-figure upstream copies were checked against the repository originals.

Python requirements and the tested runtime are documented in [the figure index](../README.md). Generated raster/vector appearance may depend on available fonts; the original font settings are preserved.

## Verification status

The earlier review recomputed 38 nodes, 189 edges and 142 project-level records after filtering 144 original coding records. The seven application-context totals are 128, 105, 80, 135, 114, 112 and 55. The final artwork includes node-label and heading edits.

Source/destination names and SHA-256 values are recorded in [the file manifest](../../metadata/figure_file_manifest.csv). The adapted publication code changes file locations only; original analytical rules and plotting parameters are preserved. See [verification results](../verification.md) for the current offline checks.
