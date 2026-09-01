# qhld-extract-topics

This project extracts topics from Google Sheets (one topic, one Sheet) and saves the content
into a JSON file ready to import into a MongoDB database. It also evaluates all the regular
expressions each topic has.

## Layout

```
.
├── pyproject.toml              # project metadata and dependencies (managed by uv)
├── uv.lock                     # pinned resolution — commit it
└── qhld_extract_topics/
    ├── app.py                  # entry point
    ├── test_app.py
    ├── credentials.json        # your Google service account (git-ignored)
    └── data/
        ├── data.json.example   # data reference template
        └── <name>.json         # one data reference file per knowledge base
```

`credentials.json` and `data/<name>.json` are package resources: `app.py` resolves them
relative to its own location, so the commands below work from any directory. Only the
generated `topics.json` is written relative to the current working directory.

## Requirements

* [uv](https://docs.astral.sh/uv/) (the Python toolchain is handled by uv; see `.python-version`)

## Configuration

1. Create a Google Drive service account. You can follow
   [this guide](https://pygsheets.readthedocs.io/en/latest/authorization.html).
2. Save it as `qhld_extract_topics/credentials.json`.
3. Create a data reference file in `qhld_extract_topics/data/`, using
   `data/data.json.example` as a template.
4. Share every Sheet you want to extract with your service account (it is an email address).

Installing dependencies is not a separate step: `uv run` syncs the environment from
`uv.lock` before running. To create the virtualenv up front anyway:

```
uv sync
```

## Run

```
cd qhld_extract_topics
uv run app.py qhld.json
```

From anywhere else, point uv at the project:

```
uv run --project /path/to/qhld-extract-topics \
  python /path/to/qhld-extract-topics/qhld_extract_topics/app.py qhld.json
```

The argument is the **file name** of a data reference inside `data/`, not a path. Running it
with no argument lists the available ones.

Note that `uv run <file>` only treats the file as a Python script when it ends in `.py`;
passing the JSON directly (`uv run qhld_extract_topics/data/qhld.json`) makes uv try to
execute it as a program and fails with `Failed to spawn: Permission denied (os error 13)`.

The result is written to `topics.json` in the current working directory; the script prints
its absolute path when it finishes. A full run contacts the
Google Sheets API once per entry in the data reference file, so it can take several minutes
for the larger knowledge bases.

## Test

```
uv run pytest
```

`uv run python -m unittest` works too, from inside `qhld_extract_topics/`.

The test suite authenticates against Google and reads real Sheets, so it needs a valid
`credentials.json` and takes about a minute.

## Dependencies

Runtime dependencies live in `[project.dependencies]` and development-only ones in the `dev`
dependency group in `pyproject.toml`. To add one:

```
uv add <package>            # runtime
uv add --dev <package>      # development
```
