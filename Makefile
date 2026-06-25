#################################################################################
# SELF DOCUMENTING HELP                                                                       #
#################################################################################

.DEFAULT_GOAL := help
.PHONY: help
help:  ## Display this help
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

#################################################################################
# GLOBALS                                                                       #
#################################################################################

PROJECT_DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
PROJECT_NAME = {{ cookiecutter.project_name }}
PYTHON_INTERPRETER = python

#################################################################################
# COMMANDS                                                                      #
#################################################################################

##@ Formatting
.PHONY: sync
sync: ## install project dependencies
	@uv sync --all-extras --dev

.PHONY: format
format: ## format code
	@uv run ruff format pakkenellik tests
	@uv run ruff check --select I --fix pakkenellik tests

##@ Linting
.PHONY: lint-ruff
lint-ruff: ## ruff lint and format checks
	@uv run ruff format --check pakkenellik tests
	@uv run ruff check pakkenellik tests

.PHONY: lint-mypy
lint-mypy: ## mypy (static-type checker)
	@uv run mypy --config-file pyproject.toml pakkenellik

.PHONY: lint-mypy-report
lint-mypy-report: ## run mypy & create report
	@uv run mypy --config-file pyproject.toml pakkenellik --html-report ./mypy_html

lint: lint-ruff lint-mypy ## run all linters

##@ Tests
.PHONY: test
test: ## run tests
	@uv run pytest

.PHONY: check
check: lint test ## run all checks

##@ Releases
.PHONY: clean-dist
clean-dist: ## remove built package artifacts
	@rm -f dist/*.whl dist/*.tar.gz

.PHONY: bump-patch
bump-patch: clean-dist ## bump version patch
	@uv run bump2version patch --allow-dirty --verbose
	@uv build
	@git add .
	@git commit -m "updating package"
	@git push --tags
	@git push

.PHONY: bump-minor
bump-minor: clean-dist ## bump version minor
	@uv run bump2version minor --allow-dirty --verbose
	@uv build
	@git add .
	@git commit -m "updating package"
	@git push --tags
	@git push

.PHONY: bump-major
bump-major: clean-dist  ## bump version major
	@uv run bump2version major --allow-dirty --verbose
	@uv build
	@git add .
	@git commit -m "updating package"
	@git push --tags
	@git push

.PHONY: release
release: check clean-dist ## release package to pypi
	@uv build
	@uv publish
