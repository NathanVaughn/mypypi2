# MyPyPi2

## About

This is the next-generation of [MyPyPi](https://github.com/nathanvaughn/mypypi).
MyPyPi2 is a simple pull-through cache for Python package index servers.
This allows you to have a local cache of packages that you depend on.
This can help save bandwidth and handle upstream outages.

Compared to the original MyPyPi, MyPyPi2 is a complete rewrite with significant
performance improvements, and better adherence to the
[Python Simple Repository API Specification](https://packaging.python.org/en/latest/specifications/simple-repository-api).

This is NOT a way to distribute custom packages internally.
For that, I recommend more advanced solutions like Artifactory, Azure Artifacts, etc.

### Features

- Pull-through caching of Python packages
- Supports multiple upstream indexes
- S3 or local storage for package files
- PostgreSQL or MySQL for data storage
- Implements both the HTML and JSON APIs
- Supports metadata files
- Content Negotiation via [`Accept` header](https://packaging.python.org/en/latest/specifications/simple-repository-api/#content-types)
- Content Negotiation via [URL parameter](https://packaging.python.org/en/latest/specifications/simple-repository-api/#url-parameter)
- Legacy `data-dist-info-metadata` JSON keys and HTML attributes

## Setup

See [config.example.toml](config.example.toml) for configuration options.

A file named `config.toml`, `config.json` or `config.yaml` should be created
in the current working directory.

## Development

Use the provided [devcontainer](https://containers.dev/)
or run the following for local development:

```bash
python -m pip install pipx --upgrade
pipx ensurepath
pipx install poetry
pipx install vscode-task-runner
# (Optionally) Add pre-commit plugin
poetry self add poetry-pre-commit-plugin
```
