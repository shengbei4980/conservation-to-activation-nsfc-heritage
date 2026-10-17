# Figure 9: Overall and stage-specific outcome pathways

[All figures](../README.md)

## Data and code

Run these commands from the repository root:

```text
python figures/figure9/code/plot_outcome_pathways_by_stage.py
python figures/figure9/code/plot_outcome_pathways_overall.py
```

| Script | Original archived filename |
| --- | --- |
| [plot_outcome_pathways_by_stage.py](code/plot_outcome_pathways_by_stage.py) | `figure_outcome_pathway_by_stage_small_multiples.py` |
| [plot_outcome_pathways_overall.py](code/plot_outcome_pathways_overall.py) | `figure_outcome_pathway_by_research_turn_stacked_bar.py` |

Directly supplied inputs:

- [data/inputs/analysis_dataset_in_scope.csv](data/inputs/analysis_dataset_in_scope.csv)

Original data values, Chinese coding labels and source prompt documents are preserved. Additional source tables and materials are in the figure's data subdirectories. Historical absolute paths inside source data are provenance, not current runtime paths.

## Outputs and reproduction

Submitted final artwork:

- [figure9.ai](outputs/final/figure9.ai)
- [figure9.pdf](outputs/final/figure9.pdf)
- [figure9_01.png](outputs/final/figure9_01.png)

Archived script output, where supplied, is in `outputs/script_reference/`. Running a script writes only to ignored `outputs/reproduced/`, keeping the archived artwork intact. Historical figure numbers in source-table/output filenames are preserved for traceability; this directory's figure number is the manuscript number.

The archived upstream program is [code/upstream/make_heritage_results.py](code/upstream/make_heritage_results.py). It reads the repository's original [coding table](../../data/heritage_llm_coding_results.csv) and [metadata table](../../data/nsfc_results_with_achievement_stat.csv) by default, and writes to this figure's `outputs/reproduced/upstream/`. `DATA_DIR` can override its input directory. Per-figure upstream copies were checked against the repository originals.

Python requirements and the tested runtime are documented in [the figure index](../README.md). Generated raster/vector appearance may depend on available fonts; the original font settings are preserved.

## Verification status

The earlier review matched all 252 cells (four panels by nine outcome types by seven research turns); stage totals equal overall totals. Overall counts are 141 journal papers, 133 researcher-training outcomes, 79 conference papers, 64 monographs, 61 policy/planning outcomes, 59 software/database outcomes, 3 awards, 28 standards/guidelines and 24 patent/software-copyright outcomes. The submitted artwork combines panels and shortens stage headings.

Source/destination names and SHA-256 values are recorded in [the file manifest](../../metadata/figure_file_manifest.csv). The adapted publication code changes file locations only; original analytical rules and plotting parameters are preserved. See [verification results](../verification.md) for the current offline checks.
