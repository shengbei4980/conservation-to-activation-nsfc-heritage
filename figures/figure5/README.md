# Figure 5: Annual research orientations and stage ellipses

[All figures](../README.md)

## Data and code

Run these commands from the repository root:

```text
python figures/figure5/code/plot_annual_research_orientations.py
python figures/figure5/code/plot_stage_orientation_ellipses.py
```

| Script | Original archived filename |
| --- | --- |
| [plot_annual_research_orientations.py](code/plot_annual_research_orientations.py) | `figure4_annual_research_orientation_stacked_bar.py` |
| [plot_stage_orientation_ellipses.py](code/plot_stage_orientation_ellipses.py) | `figure4b_stage_orientation_ellipse_map.py` |

Directly supplied inputs:

- [data/inputs/analysis_dataset_in_scope.csv](data/inputs/analysis_dataset_in_scope.csv)
- [data/inputs/stage_by_orientation_matrix.csv](data/inputs/stage_by_orientation_matrix.csv)

Original data values, Chinese coding labels and source prompt documents are preserved. Additional source tables and materials are in the figure's data subdirectories. Historical absolute paths inside source data are provenance, not current runtime paths.

## Outputs and reproduction

Submitted final artwork:

- [figure5.ai](outputs/final/figure5.ai)
- [figure5.png](outputs/final/figure5.png)

Archived script output, where supplied, is in `outputs/script_reference/`. Running a script writes only to ignored `outputs/reproduced/`, keeping the archived artwork intact. Historical figure numbers in source-table/output filenames are preserved for traceability; this directory's figure number is the manuscript number.

The archived upstream program is [code/upstream/make_heritage_results.py](code/upstream/make_heritage_results.py). It reads the repository's original [coding table](../../data/heritage_llm_coding_results.csv) and [metadata table](../../data/nsfc_results_with_achievement_stat.csv) by default, and writes to this figure's `outputs/reproduced/upstream/`. `DATA_DIR` can override its input directory. Per-figure upstream copies were checked against the repository originals.

Python requirements and the tested runtime are documented in [the figure index](../README.md). Generated raster/vector appearance may depend on available fonts; the original font settings are preserved.

## Verification status

The earlier review matched all 105 annual values (15 years by seven categories), totaling 142 projects. The three stage totals are 22, 61 and 59. The archived ellipse script labels the final stage through 2024, while the project data and submitted artwork end in 2022; this historical label difference is preserved and disclosed.

Source/destination names and SHA-256 values are recorded in [the file manifest](../../metadata/figure_file_manifest.csv). The adapted publication code changes file locations only; original analytical rules and plotting parameters are preserved. See [verification results](../verification.md) for the current offline checks.
