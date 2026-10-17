# Conservation to Activation: NSFC Heritage Research Data and Coding

Data and LLM-assisted coding accompanying the manuscript **From Conservation to Activation: How Research Funding Reorganizes Heritage Knowledge in China** by Qian Ji, Shengbei Zhou, Lei Wang, and Kaiting Yang.

The source collection contains **144 project records**. The supplied coding table marks **142 as `in_scope`** and **2 as `out_of_scope_non_heritage`**. The manuscript analyzes the 142 included completed NSFC-funded heritage projects initiated in China during 2008-2022. All 144 source records are retained for traceability.

## Contents

| Path | Content |
| --- | --- |
| `code/extract_heritage_coding.py` | Original LLM-assisted coding program with portable default paths |
| `data/heritage_llm_coding_results.csv` | 144 coding records; 26 original columns |
| `data/nsfc_results_with_achievement_stat.csv` | 144 metadata and achievement records; 27 original columns |
| `data/text_corpus/` | 144 report-text JSON files |
| `docs/data_dictionary.md` | English descriptions of all original fields |
| `metadata/project_index.csv` | Project IDs, inclusion decisions, corpus paths, and image-asset mapping |
| `metadata/file_manifest.csv` | Original file names, new destinations, and SHA-256 checksums |
| `metadata/archive_manifest.csv` | All 6,521 original archive entries, renamed member paths, and payload checksums |
| `metadata/release_assets.csv` | Download URLs, sizes, checksums, and counts for the three image archives |

## Report-page images

Download the three ZIP assets from [Release v1.0.0](https://github.com/shengbei4980/conservation-to-activation-nsfc-heritage/releases/tag/v1.0.0). Each is independently extractable and contains complete project directories. Extract all three into the same directory to obtain `final_report_images/<approval_no>/`.

| Asset | Projects | Files | Size in bytes |
| --- | ---: | ---: | ---: |
| [nsfc_final_report_images_part_01.zip](https://github.com/shengbei4980/conservation-to-activation-nsfc-heritage/releases/download/v1.0.0/nsfc_final_report_images_part_01.zip) | 82 | 3392 | 914288908 |
| [nsfc_final_report_images_part_02.zip](https://github.com/shengbei4980/conservation-to-activation-nsfc-heritage/releases/download/v1.0.0/nsfc_final_report_images_part_02.zip) | 35 | 1674 | 922383707 |
| [nsfc_final_report_images_part_03.zip](https://github.com/shengbei4980/conservation-to-activation-nsfc-heritage/releases/download/v1.0.0/nsfc_final_report_images_part_03.zip) | 27 | 1310 | 751591134 |

Together the assets contain **6,232 PNG report pages** and **144 JSON download records** (6,376 files). The English directory names use stable NSFC approval numbers. The source payload of every archive member is unchanged; only ZIP member paths and ZIP packaging were changed. These counts describe the supplied archive, not an independent guarantee that every source report page was downloaded.

## Language and provenance

File and directory names and this repository's documentation use English. Original CSV/JSON data values, Chinese column names, report text, code comments, prompts, and categorical labels are preserved. The CSV files and all corpus JSON files are byte-for-byte copies. The code's four default input/output paths were adapted to this repository, and its usage examples use the English script path. Its executable processing logic and prompts are unchanged.

Historical paths in `_source_file` and in download-record JSON values are provenance from the original machine. They are not runnable paths on a new computer. Use `metadata/project_index.csv` and `metadata/archive_manifest.csv` to find the current files. Original Chinese filenames also appear as provenance values in the manifests.

## Run the coding program

Python 3.10 or later is required. The program uses only the Python standard library. No package installation is required.

From the repository root, inspect the command-line options or preview one prompt offline (PowerShell):

```powershell
$env:NEWAPI_API_KEY = "offline-placeholder"
python code/extract_heritage_coding.py --help
python code/extract_heritage_coding.py --limit 1 --dry-run
```

The original program checks that `NEWAPI_API_KEY` is nonempty at startup, including for `--help` and `--dry-run`. The placeholder above permits those offline commands; `--dry-run` returns before any API request.

For actual LLM coding, supply your own key for the endpoint you intend to use:

```powershell
$env:NEWAPI_API_KEY = "YOUR_OWN_API_KEY"
$env:NEWAPI_BASE_URL = "https://YOUR_COMPATIBLE_ENDPOINT"
python code/extract_heritage_coding.py --resume
```

Actual coding sends report text and metadata to the configured API and may incur provider charges. The preserved historical defaults are `https://api.zetatechs.com` and model identifier `gpt-5.5-xhigh`; the latter is a provider-specific recorded identifier, not a statement of current model availability. Both metadata loaders read the supplied integrated metadata CSV by default. Generated outputs go to the ignored `outputs/llm_coding/` directory. Environment variables and command-line flags can override the data/output paths. `.env.example` documents the variables; the script does not automatically load `.env` files.

## Verification and reuse

The publication copy was checked for matching project IDs across both tables, the corpus, and the image archives; 142/2 inclusion counts; English paths and path uniqueness; unchanged data-file hashes; unchanged archive-member payload hashes; and offline code execution. These checks establish packaging integrity and correspondence. LLM outputs are model-assisted annotations and may require human review. Rerunning an external model may produce different labels. This repository contains the supplied raw-data collection and coding program; it does not include the manuscript's complete downstream figure-generation pipeline.

Use `CITATION.cff` when citing this repository. The source reports and project information originate from the NSFC Knowledge Discovery platform (`kd.nsfc.cn`). Original source and third-party rights remain applicable; this repository does not grant a new blanket license to third-party reports.
