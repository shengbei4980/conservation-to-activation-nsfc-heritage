# Data dictionary

All source values are preserved. The tables are UTF-8 CSV files and should be read with a CSV parser, not split on commas. Use `utf-8-sig` when reading them in Python. Treat `approval_no` as text. Each table has one row per approval number (144 unique records).

## Coding results

`data/heritage_llm_coding_results.csv` has 26 fields. Multiple labels are normally separated by semicolons in the supplied CSV. Category definitions and allowed labels are specified in the original Chinese coding tables and prompts embedded in `code/extract_heritage_coding.py`. Their wording is preserved.

| Original field | English description |
| --- | --- |
| `approval_no` | NSFC project approval number; primary join key, stored as text. |
| `scope` | Inclusion decision: in_scope or out_of_scope_non_heritage. |
| `exclusion_reason` | Reason for exclusion; empty for included records in the supplied table. |
| `project_title` | Project title recorded by the coding workflow. |
| `heritage_objects` | Primary heritage-object category. |
| `research_orientations` | Primary research orientation. |
| `primary_method_orientation` | Primary methodological orientation. |
| `spatial_scale` | Primary spatial scale. |
| `primary_stakeholder` | Primary stakeholder category. |
| `outcome_pathway` | Multiple outcome-pathway labels serialized in one CSV cell. |
| `heritage_object_tags` | Multiple heritage-object tags serialized in one CSV cell. |
| `research_theme_tags` | Multiple research-theme tags serialized in one CSV cell. |
| `method_tags` | Multiple method tags serialized in one CSV cell. |
| `stakeholder_tags` | Multiple stakeholder tags serialized in one CSV cell. |
| `agenda_turn_tags` | Multiple research-agenda turn tags serialized in one CSV cell. |
| `turn_type` | Dominant research-agenda turn category. |
| `turn_strength` | Strength of the coded research-agenda turn. |
| `proposal_to_outcome_alignment` | Coded alignment between proposal intent and completed outcomes. |
| `primary_knowledge_function` | Primary knowledge function of the project. |
| `confidence` | Model-reported coding confidence (high, medium, or low); not a calibrated probability. |
| `one_sentence_rationale` | Short textual rationale for the coding decision. |
| `evidence_phrases` | Evidence snippets from input text, serialized in one CSV cell. |
| `human_review_flags` | Review flags serialized in one CSV cell; empty values are retained. |
| `_source_file` | Historical absolute input-file path on the original coding machine; provenance only. |
| `_coded_at` | Original coding timestamp as recorded; timezone is not encoded. |
| `_model` | Original provider model identifier as recorded. |

## Project metadata and achievement statistics

`data/nsfc_results_with_achievement_stat.csv` has 27 fields. Original Chinese field names are schema identifiers and have not been renamed. Empty cells and textual missing-data markers are retained, rather than converted to zeros.

| Original field | English description |
| --- | --- |
| `search_year` | Search-year value retained from the source collection; use research_period_start for project start dates. |
| `search_category` | Funding/project category used in the source query. |
| `search_code` | Discipline/search code used in the source query. |
| `search_keyword` | Keyword used in the source query. |
| `search_keyword_field` | Field searched for the keyword. |
| `approval_no` | NSFC project approval number; primary join key, stored as text. |
| `apply_code` | Project application/discipline code. |
| `project_name` | Project title in the metadata source. |
| `pi_name` | Principal investigator name. |
| `pi_title` | Principal investigator professional title as supplied. |
| `org_name` | Host institution name. |
| `research_period_start` | Project research-period start date as supplied. |
| `research_period_end` | Project research-period end date as supplied. |
| `funding_amount` | Funding amount; interpret together with funding_unit. |
| `funding_unit` | Original funding unit; for example, 万元 means ten thousand yuan. |
| `participants` | Original participant listing, including names and affiliations where present. |
| `participants_count` | Participant-count field as supplied; not recomputed from the participant text. |
| `project_abstract_cn` | Chinese project/proposal abstract. |
| `project_abstract_en` | English project/proposal abstract, or the original missing-data placeholder. |
| `final_abstract_cn` | Chinese final/completion abstract. |
| `final_abstract_en` | English final/completion abstract, or the original missing-data placeholder. |
| `data_update_time` | Source metadata update date as recorded. |
| `期刊论文数量` | Number of journal papers recorded in the achievement statistics. |
| `会议论文数量` | Number of conference papers recorded in the achievement statistics. |
| `专著数量` | Number of monographs recorded in the achievement statistics. |
| `专利` | Patent count recorded in the achievement statistics. |
| `获奖` | Award count recorded in the achievement statistics. |

## Text corpus JSON

Each `data/text_corpus/<approval_no>_llm_ready.json` is an unchanged source JSON object:

| Field | English description |
| --- | --- |
| `report_id` | Project identifier corresponding to the NSFC approval number |
| `total_pages` | Original reported page-count metadata; not recalculated |
| `project_full_markdown` | Extracted report text in its original Markdown/OCR representation |

## Report image archive

PNG pages are stored at `final_report_images/<approval_no>/report_page_NNN.png`. Each project also has the original `index_progress.json` download record. Its fields describe successful and failed page indices, source URLs, historical local paths, page limits, completion status, errors and update time. They are operational download metadata rather than additional scientific variables. The preserved fields are `success_indexes`, `failed_indexes`, `index_to_url`, `index_to_file`, `max_index_tried`, `total_pages`, `api_index_start`, `is_complete`, `end_reason`, `consecutive_404`, `proxy_refresh_count`, `download404_indexes`, and `update_time`.

The three ZIP files contain disjoint complete project directories. Download all three to obtain the supplied full collection.

## Traceability metadata

- `project_index.csv`: links each approval number to its original scope decision and exclusion reason, title, corpus path, reported page count, available PNG count, release asset, and current image directory. Text values copied from the source remain in their original language.
- `file_manifest.csv`: records all 148 local source files, source byte counts and SHA-256 values, repository destinations and checksums, release-asset destinations, and the applied packaging change.
- `archive_manifest.csv`: maps all 6,521 source ZIP entries to English paths. `is_directory` distinguishes files and directories. Original byte counts, CRC32 and SHA-256 values are retained. `packaged_sha256` was computed by reading back each repacked payload. The common root directory is present in all three assets.
- `release_assets.csv`: records each ZIP filename, byte count, SHA-256 checksum, project/file counts, and GitHub download URL.

These manifests verify correspondence and copying integrity. They do not replace scientific review of the original data or model annotations.
