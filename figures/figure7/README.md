# Figure 7: Annual research-turn distribution in 3D

[All figures](../README.md)

## Data and code

Run these commands from the repository root:

```text
python figures/figure7/code/plot_annual_research_turns_3d.py
```

| Script | Original archived filename |
| --- | --- |
| [plot_annual_research_turns_3d.py](code/plot_annual_research_turns_3d.py) | `figure9_research_turn_annual_distribution_3d.py` |

Directly supplied inputs:

- [data/inputs/analysis_dataset_in_scope.csv](data/inputs/analysis_dataset_in_scope.csv)

Original data values, Chinese coding labels and source prompt documents are preserved. Additional source tables and materials are in the figure's data subdirectories. Historical absolute paths inside source data are provenance, not current runtime paths.

## Outputs and reproduction

Submitted final artwork:

- [figure7.ai](outputs/final/figure7.ai)
- [figure7.pdf](outputs/final/figure7.pdf)
- [figure7_01.png](outputs/final/figure7_01.png)

Archived script output, where supplied, is in `outputs/script_reference/`. Running a script writes only to ignored `outputs/reproduced/`, keeping the archived artwork intact. Historical figure numbers in source-table/output filenames are preserved for traceability; this directory's figure number is the manuscript number.

The archived upstream program is [code/upstream/make_heritage_results.py](code/upstream/make_heritage_results.py). It reads the repository's original [coding table](../../data/heritage_llm_coding_results.csv) and [metadata table](../../data/nsfc_results_with_achievement_stat.csv) by default, and writes to this figure's `outputs/reproduced/upstream/`. `DATA_DIR` can override its input directory. Per-figure upstream copies were checked against the repository originals.

Python requirements and the tested runtime are documented in [the figure index](../README.md). Generated raster/vector appearance may depend on available fonts; the original font settings are preserved.

## Verification status

Known display-scope discrepancy. The original script and full annual tables contain seven categories and 142 projects. The submitted graphic displays six categories totaling 141, omitting one 2014 traditional-continuity project and changing category order/colors. The separate data/submission_view table preserves the six-category display. The script intentionally retains the full seven-category computation; it cannot directly generate the submitted six-category graphic without further changes.

Source/destination names and SHA-256 values are recorded in [the file manifest](../../metadata/figure_file_manifest.csv). The adapted publication code changes file locations only; original analytical rules and plotting parameters are preserved. See [verification results](../verification.md) for the current offline checks.
