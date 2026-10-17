# Figure 6: Knowledge-function timeline network

[All figures](../README.md)

## Data and code

Run these commands from the repository root:

```text
python figures/figure6/code/plot_knowledge_function_timeline.py
```

| Script | Original archived filename |
| --- | --- |
| [plot_knowledge_function_timeline.py](code/plot_knowledge_function_timeline.py) | `figure5_knowledge_function_timeline_map_EN_adjusted.py` |

Directly supplied inputs:

- [data/inputs/analysis_dataset_in_scope.csv](data/inputs/analysis_dataset_in_scope.csv)

Original data values, Chinese coding labels and source prompt documents are preserved. Additional source tables and materials are in the figure's data subdirectories. Historical absolute paths inside source data are provenance, not current runtime paths.

## Outputs and reproduction

Submitted final artwork:

- [figure6.ai](outputs/final/figure6.ai)
- [figure6.pdf](outputs/final/figure6.pdf)
- [figure6_01.png](outputs/final/figure6_01.png)

Archived script output, where supplied, is in `outputs/script_reference/`. Running a script writes only to ignored `outputs/reproduced/`, keeping the archived artwork intact. Historical figure numbers in source-table/output filenames are preserved for traceability; this directory's figure number is the manuscript number.

The archived upstream program is [code/upstream/make_heritage_results.py](code/upstream/make_heritage_results.py). It reads the repository's original [coding table](../../data/heritage_llm_coding_results.csv) and [metadata table](../../data/nsfc_results_with_achievement_stat.csv) by default, and writes to this figure's `outputs/reproduced/upstream/`. `DATA_DIR` can override its input directory. Per-figure upstream copies were checked against the repository originals.

Python requirements and the tested runtime are documented in [the figure index](../README.md). Generated raster/vector appearance may depend on available fonts; the original font settings are preserved.

## Verification status

Known legend/unit discrepancy. The source assignment and recomputed 1,861 project-tag rows, 470 nodes and 760 edges were confirmed. The submitted legend uses 1/3/6/>=7, whereas the script uses 1/7/17/67. Some merged-node visual_count values are tag-hit totals rather than counts of distinct projects: 67 mechanism-explanation tag hits in 2021 correspond to 15 distinct projects. The archived time-axis/stage labeling also extends to 2024 while project data end in 2022. This package does not classify the submitted legend and units as a complete reproduction pass.

Source/destination names and SHA-256 values are recorded in [the file manifest](../../metadata/figure_file_manifest.csv). The adapted publication code changes file locations only; original analytical rules and plotting parameters are preserved. See [verification results](../verification.md) for the current offline checks.
