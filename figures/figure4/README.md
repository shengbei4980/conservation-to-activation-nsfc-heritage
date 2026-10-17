# Figure 4: Keyword-cluster networks

[All figures](../README.md)

## Data and code

Run these commands from the repository root:

```text
python figures/figure4/code/plot_keyword_clusters.py
```

| Script | Original archived filename |
| --- | --- |
| [plot_keyword_clusters.py](code/plot_keyword_clusters.py) | `figure3c_no_text_stroke_output_to_figure_cluster.py` |

Directly supplied inputs:

- [data/inputs/analysis_dataset_in_scope.csv](data/inputs/analysis_dataset_in_scope.csv)
- [data/inputs/base_analysis_dataset/analysis_dataset_in_scope.csv](data/inputs/base_analysis_dataset/analysis_dataset_in_scope.csv)

Original data values, Chinese coding labels and source prompt documents are preserved. Additional source tables and materials are in the figure's data subdirectories. Historical absolute paths inside source data are provenance, not current runtime paths.

## Outputs and reproduction

Submitted final artwork:

- [figure4.ai](outputs/final/figure4.ai)
- [figure4.png](outputs/final/figure4.png)

Archived script output, where supplied, is in `outputs/script_reference/`. Running a script writes only to ignored `outputs/reproduced/`, keeping the archived artwork intact. Historical figure numbers in source-table/output filenames are preserved for traceability; this directory's figure number is the manuscript number.

The archived upstream program is [code/upstream/make_heritage_results.py](code/upstream/make_heritage_results.py). It reads the repository's original [coding table](../../data/heritage_llm_coding_results.csv) and [metadata table](../../data/nsfc_results_with_achievement_stat.csv) by default, and writes to this figure's `outputs/reproduced/upstream/`. `DATA_DIR` can override its input directory. Per-figure upstream copies were checked against the repository originals.

Python requirements and the tested runtime are documented in [the figure index](../README.md). Generated raster/vector appearance may depend on available fonts; the original font settings are preserved.

## Verification status

The earlier review recomputed all nine node/edge tables and matched 64, 84 and 72 colored nodes in the three panels. The submitted artwork includes panel assembly, font-size and label-position edits.

Source/destination names and SHA-256 values are recorded in [the file manifest](../../metadata/figure_file_manifest.csv). The adapted publication code changes file locations only; original analytical rules and plotting parameters are preserved. See [verification results](../verification.md) for the current offline checks.
