![Pakkenellik](./docs/assets/github-header-banner-pakkenellik.png)

Pakkenellik is a collection of shared Python utilities for Bord4's data-analysis
projects. It includes helpers for dataframes, project paths, publishing,
integrations, Norwegian regions and Statistics Norway (SSB).

The package is used by
[bord4-analysis-templates](https://github.com/BergensTidende/bord4-analysis-templates).

## Requirements

- Python 3.10 or later

## Installation

Install the core package with pip:

```bash
pip install pakkenellik
```

Or add it to a project managed by uv:

```bash
uv add pakkenellik
```

Optional dependencies are grouped by feature:

```bash
uv add "pakkenellik[s3]"          # Amazon S3
uv add "pakkenellik[gspread]"     # Google Sheets
uv add "pakkenellik[nvdb]"        # Norwegian Public Roads Administration
uv add "pakkenellik[gis]"         # Geospatial dataframes
uv add "pakkenellik[viz]"         # Matplotlib visualizations
uv add "pakkenellik[datawrapper]" # Datawrapper
uv add "pakkenellik[ssb]"         # SSB helpers (no additional dependencies)
```

## Usage

Clean dataframe column names:

```python
import pandas as pd

from pakkenellik.dataframe.clean_column_headers import clean_column_headers

df = pd.DataFrame({"Første kolonne": [1]})
df = clean_column_headers(df)
# df.columns: ["forste_kolonne"]
```

Format numbers with Norwegian separators:

```python
from pakkenellik.dataframe.numbers import format_number

formatted = format_number(1234567.89)
# "1.234.567,89"
```

Use common project paths:

```python
from pakkenellik.config import Config

config = Config("/path/to/project")
source_file = config.get_source_file("data.csv")
# "/path/to/project/data/source/data.csv"
```

## Features

- `aws`: publishing files and data to Amazon S3
- `config`: common paths and URLs for Bord4 projects
- `dataframe`: cleaning columns, date/time helpers and number formatting
- `datawrapper`: low-level Datawrapper client helpers
- `google`: reading from and writing to Google Sheets
- `integration`: Schibsted MM and Datawrapper integration helpers
- `regions`: Norwegian municipality and county data, including historical changes
- `ssb`: population data, rates and ranking helpers
- `vegvesen`: routes and road data from the Norwegian Public Roads Administration
- `viz`: shared Matplotlib styling and plotting helpers

## Local development

[Install uv](https://docs.astral.sh/uv/getting-started/installation/), clone the
repository and install all development and optional dependencies:

```bash
git clone https://github.com/BergensTidende/pakkenellik.git
cd pakkenellik
make sync
```

The Makefile provides these common commands:

| Command | Description |
| --- | --- |
| `make format` | Format and sort imports with Ruff |
| `make lint` | Check formatting, linting and types with Ruff and mypy |
| `make test` | Run the pytest test suite |
| `make check` | Run all linting and tests |

## Contributing

Create a branch from `main`, make your changes and verify them before opening a
pull request:

```bash
git switch -c name-of-branch
make check
git push -u origin name-of-branch
```

Use present-tense commit messages that describe what the commit does. If you do
not have write access to the repository, create a personal fork and open the pull
request from your fork against the repository's `main` branch.

## License

Pakkenellik is distributed under the [MIT License](./LICENSE).

## Contact

Bord4 — bord4@bt.no
