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
For that, I recommend more advanced solutions like Artifactory,
Azure Artifacts, Sonatype Nexus, etc.

## Caveats

This is always going to be slower than using the actual upstream index.
Since the upstream index knows when updates occur, it can cache content far more
aggressively. Additionally, whenever MyPyPi2 needs to fetch data from the upstream
index, it needs to download the content, parse it, and insert it into its own
database, and then return a response. Therefore, expect the first time a package
is requested to be significantly slower than incremental or cached requests.

However, in my experience, the performance still  tends to be better than other
Python index servers like Azure Artifacts or Sonatype Nexus.
This is because MyPyPi2 also supports
[`.metadata`](https://packaging.python.org/en/latest/specifications/simple-repository-api/#serve-distribution-metadata-in-the-simple-repository-api)
files from the upstream package server that allow `pip` and other tools
to download a small separate file to determine package dependencies and other
metadata. Most other index servers don't support this and force package managers
to download full copies of possible package versions to figure out this information.
Additionally, since MyPyPi2 supports the JSON API, it can be faster
to parse than the HTML API.

When cached data is available though, MyPyPi2 should be pretty performant.
When files are served from S3, by default the redirect is served with a `308`
status code so clients should cache this redirect and not need to re-fetch it
directly from MyPyPi2.

## Features

- Pull-through caching of Python packages
- Supports multiple upstream indexes
- S3 or local storage for package files
- PostgreSQL for data storage
- Implements both the HTML and JSON APIs
- Supports metadata files
- Automatic [name normalization](https://packaging.python.org/en/latest/specifications/simple-repository-api/#base-html-api)
- Automatic [trailing slash redirection](https://packaging.python.org/en/latest/specifications/simple-repository-api/#base-html-api)
- Content Negotiation via [`Accept` header](https://packaging.python.org/en/latest/specifications/simple-repository-api/#content-types)
- Content Negotiation via [URL parameter](https://packaging.python.org/en/latest/specifications/simple-repository-api/#url-parameter)
- Content Negotiation via [URL path](https://packaging.python.org/en/latest/specifications/simple-repository-api/#endpoint-configuration)
- Legacy `data-dist-info-metadata` JSON keys and HTML attributes
- `pip`, `poetry`, and `uv` compatible

## Setup

See [config.example.toml](https://github.com/NathanVaughn/mypypi2/blob/main/config.example.toml)
for configuration options.

A file named `config.toml`, `config.json` or `config.yaml` should be created
in the application's working directory. The Docker container working directory
is `/app/`.

## Development

Use the provided [devcontainer](https://containers.dev/)
or run the following for local development:

```bash
# Install uv
# https://docs.astral.sh/uv/getting-started/installation/
uv tool install vscode-task-runner
vtr install
```
