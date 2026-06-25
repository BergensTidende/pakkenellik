# Pakkenellik: Bord4's swiss army knife for python projects

<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary><h2 style="display: inline-block">Table of Contents</h2></summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#requirements">Requirements</a></li>
        <li><a href="#structure">Structure</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->

## About The Project

Pakkenellik is german and used in Bergen as a synonym for small packages one carry around, especially when traveling. This package is a swiss army knife for Bord4's python projects. It contains a makefile with commands for linting and formatting. One day it will contain testing as well.

This package is used by the [cookiecutter-bord4-analysis](https://github.com/BergensTidende/cookiecutter-bord4-analysis) project and [bord4-analysis-templates](https://github.com/BergensTidende/bord4-analysis-templates)

Inspiration for the makefile and project setup is taken from Johannes Schmidt's series ["Setting up Python Projects"](https://johschmidt42.medium.com/setting-up-python-projects-part-i-408603868c08)


## Installation

Requires Python 3.10 or later.

```bash
pip install pakkenellik
```

or using pipenv:

```bash
pipenv install pakkenellik
```

or using uv:

```bash
uv add pakkenellik
```

Optional dependencies are split into extras:

```bash
uv add "pakkenellik[s3]"
uv add "pakkenellik[gspread]"
uv add "pakkenellik[nvdb]"
uv add "pakkenellik[viz]"
uv add "pakkenellik[datawrapper]"
```

## Usage

Clean dataframe column headers:

```python
import pandas as pd

from pakkenellik.dataframe.clean_column_headers import clean_column_headers

df = pd.DataFrame({"Første kolonne": [1]})
df = clean_column_headers(df)
```

Format numbers for publishing:

```python
from pakkenellik.dataframe.numbers import format_number

formatted = format_number(1234567.89)
```

Use common project paths:

```python
from pakkenellik.config import Config

config = Config("/path/to/project")
source_file = config.get_source_file("data.csv")
```

## Local development

### Requirements
---

- pyenv - manage python versions
- uv - manage python dependencies and packaging

To install on mac you can use homebrew:

```bash
brew upgrade
brew install pyenv
```

Install uv with homebrew or the way described in the [documentation](https://docs.astral.sh/uv/getting-started/installation/):

```bash
brew install uv
```

Install the project dependencies:

```bash
make sync
```


### Makefile commands

- `make lint`
  - lint the code with ruff. Mypy will check for correct typing.
- `make format`
  - format the code with ruff.
- `make test`
  - run tests with pytest.
- `make check`
  - run linting and tests.

### Structure

```
.
├── .editorconfig
├── pyproject.toml
├── README.md
└── pakkenellik
    ├── __init__.py
    ├── aws
    │   ├── __init__.py
    │   └── s3.py
    ├── config
    │   └── __init__.py
    ├── dataframe
    │   ├── __init__.py
    │   ├── clean_column_headers.py
    │   ├── datetime.py
    │   └── numbers.py
    ├── integration
    │   ├── __init__.py
    │   └── client.py
    ├── log
    │   ├── __init__.py
    │   └── ansi.py
    ├── regions
    │   ├── __init__.py
    │   └── norway.py
    ├── ssb
    │   ├── __init__.py
    │   ├── population.py
    │   └── rates.py
    ├── vegvesen
    │   ├── __init__.py
    │   └── visvegen.py
    └── viz
        ├── __init__.py
        └── pyplot.py
```

- `.editorconfig`
  - Configuration file for editorconfig.
- `pyproject.toml`
  - Project metadata and configuration for uv, ruff and mypy.
- `README.md`
  - This file.
- `pakkenellik`
  - The package. It has the following subpackages:
- `aws`
  - util functions for working with AWS
- `config`
  - configuration functions that helps with adhering to bord4's folder structure and help with common urls. 
- `dataframe`
  - util functions for working with dataframes
- `integration`
  - helper functions when working with Schibsted MM API
- `log`
  - better log functions
- `vegvesen`
  - Functions to work with Vegvesenet's VisVegen API

## Usage

To install the package in your project run

```bash
uv add pakkenellik
```

## Contributing

Do you have write permissions to the repo? Then you can clone this project to a folder on your computer.

```bash
git clone https://github.com/BergensTidende/pakkenellik.git
```

If not do the following:

- Create a personal fork of the project on Github.
- Clone the fork on your local machine. Your remote repo on Github is called `origin`.
- Add the original repository as a remote called `upstream`.
- If you created your fork a while ago be sure to pull upstream changes into your local repository.

This will clone the repo into `pakkenellik`. 

Create a branch for your changes

```bash
git checkout -b name-of-branch
```

Make your changes, rememeber to commit. And always write your commit messages in the present tense. Your commit message should describe what the commit, when applied, does to the code – not what you did to the code.

If you're working on a clone push the branch to github and make PR.

If your're working a fork:

- Squash your commits into a single commit with git's [interactive rebase](https://help.github.com/articles/interactive-rebase). Create a new branch if necessary.
- Push your branch to your fork on Github, the remote `origin`.
- From your fork open a pull request in the correct branch. Target the project's `develop` branch if there is one, else go for `master`!
- …
- If the maintainer requests further changes just push them to your branch. The PR will be updated automatically.
- Once the pull request is approved and merged you can pull the changes from `upstream` to your local repo and delete
  your extra branch(es).

 <!-- CONTACT -->

## Contact

Bord4 - bord4@bt.no
