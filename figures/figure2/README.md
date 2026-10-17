# Figure 2: Project characteristics and research-dimension distributions

[All figures](../README.md)

## Data and code

Run these commands from the repository root:

```text
python figures/figure2/code/plot_basic_descriptive_statistics.py
python figures/figure2/code/plot_dimension_distributions.py
```

| Script | Original archived filename |
| --- | --- |
| [plot_basic_descriptive_statistics.py](code/plot_basic_descriptive_statistics.py) | `plot_basic_descriptive_statistics.py` |
| [plot_dimension_distributions.py](code/plot_dimension_distributions.py) | `figure1.py` |

Directly supplied inputs:

- [data/inputs/analysis_dataset_in_scope.csv](data/inputs/analysis_dataset_in_scope.csv)
- [data/inputs/discipline_code_counts.csv](data/inputs/discipline_code_counts.csv)
- [data/inputs/fig3_overall_agenda_structure/heritage_object_counts.csv](data/inputs/fig3_overall_agenda_structure/heritage_object_counts.csv)
- [data/inputs/fig3_overall_agenda_structure/method_orientation_counts.csv](data/inputs/fig3_overall_agenda_structure/method_orientation_counts.csv)
- [data/inputs/fig3_overall_agenda_structure/research_orientation_counts.csv](data/inputs/fig3_overall_agenda_structure/research_orientation_counts.csv)
- [data/inputs/heritage_object_counts.csv](data/inputs/heritage_object_counts.csv)
- [data/inputs/method_orientation_counts.csv](data/inputs/method_orientation_counts.csv)
- [data/inputs/project_type_counts.csv](data/inputs/project_type_counts.csv)
- [data/inputs/research_orientation_counts.csv](data/inputs/research_orientation_counts.csv)

Original data values, Chinese coding labels and source prompt documents are preserved. Additional source tables and materials are in the figure's data subdirectories. Historical absolute paths inside source data are provenance, not current runtime paths.

## Outputs and reproduction

Submitted final artwork:

- [figure2.ai](outputs/final/figure2.ai)
- [figure2.png](outputs/final/figure2.png)

Archived script output, where supplied, is in `outputs/script_reference/`. Running a script writes only to ignored `outputs/reproduced/`, keeping the archived artwork intact. Historical figure numbers in source-table/output filenames are preserved for traceability; this directory's figure number is the manuscript number.

The archived upstream program is [code/upstream/make_heritage_results.py](code/upstream/make_heritage_results.py). It reads the repository's original [coding table](../../data/heritage_llm_coding_results.csv) and [metadata table](../../data/nsfc_results_with_achievement_stat.csv) by default, and writes to this figure's `outputs/reproduced/upstream/`. `DATA_DIR` can override its input directory. Per-figure upstream copies were checked against the repository originals.

Python requirements and the tested runtime are documented in [the figure index](../README.md). Generated raster/vector appearance may depend on available fonts; the original font settings are preserved.

## Verification status

Five category distributions agree with the 142-project analysis table. The earlier review matched 12 bar-height proportions and 23 quantity/percentage labels. Four historical CSV files are isolated in data/archive; the current compact-statistics and dimension-distribution tables remain in data/source_data. The submitted artwork includes panel assembly and text edits.

Source/destination names and SHA-256 values are recorded in [the file manifest](../../metadata/figure_file_manifest.csv). The adapted publication code changes file locations only; original analytical rules and plotting parameters are preserved. See [verification results](../verification.md) for the current offline checks.
