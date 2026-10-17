# Figure 3: Heritage-object, research-orientation and method Sankey diagram

[All figures](../README.md)

## Data and code

Run these commands from the repository root:

```text
python figures/figure3/code/figure3_object_problem_method_sankey.py
```

| Script | Original archived filename |
| --- | --- |
| [figure3_object_problem_method_sankey.py](code/figure3_object_problem_method_sankey.py) | `figure3_object_problem_method_sankey.py` |

Directly supplied inputs:

- [data/inputs/analysis_dataset_in_scope.csv](data/inputs/analysis_dataset_in_scope.csv)
- [data/inputs/object_by_orientation_matrix.csv](data/inputs/object_by_orientation_matrix.csv)
- [data/inputs/orientation_by_method_matrix.csv](data/inputs/orientation_by_method_matrix.csv)

Original data values, Chinese coding labels and source prompt documents are preserved. Additional source tables and materials are in the figure's data subdirectories. Historical absolute paths inside source data are provenance, not current runtime paths.

## Outputs and reproduction

Submitted final artwork:

- [figure3.ai](outputs/final/figure3.ai)
- [figure3.pdf](outputs/final/figure3.pdf)
- [figure3_01.png](outputs/final/figure3_01.png)

Archived script output, where supplied, is in `outputs/script_reference/`. Running a script writes only to ignored `outputs/reproduced/`, keeping the archived artwork intact. Historical figure numbers in source-table/output filenames are preserved for traceability; this directory's figure number is the manuscript number.

The archived upstream program is [code/upstream/make_heritage_results.py](code/upstream/make_heritage_results.py). It reads the repository's original [coding table](../../data/heritage_llm_coding_results.csv) and [metadata table](../../data/nsfc_results_with_achievement_stat.csv) by default, and writes to this figure's `outputs/reproduced/upstream/`. `DATA_DIR` can override its input directory. Per-figure upstream copies were checked against the repository originals.

Python requirements and the tested runtime are documented in [the figure index](../README.md). Generated raster/vector appearance may depend on available fonts; the original font settings are preserved.

## Verification status

The two cross-tabulations, 23 nodes and 63 links agree with the 142-project data; each Sankey layer totals 142. Here flow_strength is normalized by each source node's outgoing total. The submitted artwork includes layout and explanatory-text edits.

Source/destination names and SHA-256 values are recorded in [the file manifest](../../metadata/figure_file_manifest.csv). The adapted publication code changes file locations only; original analytical rules and plotting parameters are preserved. See [verification results](../verification.md) for the current offline checks.
