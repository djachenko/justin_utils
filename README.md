# justin_utils

Shared utility library for the Justin Python ecosystem. Provides reusable building blocks for filesystem operations, CLI tooling, functional sequences, EXIF handling, and more — designed to be installed as a lightweight dependency across multiple projects.

## Requirements

Python 3.11+

## Installation

```bash
pip install justin_utils
```

To install only specific modules and their dependencies, use extras:

```bash
pip install "justin_utils[filesystem]"
pip install "justin_utils[exif,sources]"
```

For development:

```bash
pip install -e ".[test]"
```

## Modules

### `filesystem`
`File` and `Folder` wrappers over `pathlib.Path` with move/copy/rename operations, cross-drive detection, and recursive tree handling. `RelativeFileset` preserves relative paths when moving groups of files.

### `util`
General-purpose functions: sequence operations (`distinct`, `flatten_lazy`, `group_by`, `stride`, `first`), date/time parsing, BFS traversal, user prompts (`ask_for_permission`, `ask_for_choice`), and `keydefaultdict` — a dict subclass with a key-dependent default factory.

### `pylinq`
Lazy `Sequence` wrapper with a LINQ-style API: `filter`, `map`, `flat_map`, `group_by`, `distinct`, `take`, `skip`, `reduce`, `any`, and terminal operations like `to_list`, `to_dict`, `to_set`.

### `joins`
SQL-style join operations over arbitrary iterables: `inner`, `left`, `right`, `full_outer`.

### `exif`
EXIF metadata extraction from image files via Pillow and the `exif` library. `parse_exif` auto-selects the parser by file extension. `exif_sorted` sorts a sequence of paths by date taken.

### `sources`
Photo source abstraction: groups raw files (NEF, RAF, ARW) with their XMP sidecar metadata, and JPEG/TIFF/DNG/HEIC files with embedded metadata. `parse_sources` returns a flat list of `Source` objects ready for sorting or moving.

### `transfer`
`TransferSpeedMeter` tracks a rolling transfer speed over recent history. `TransferTimeEstimator` estimates remaining time given current speed and remaining size.

### `data`
`DataSize` and `DataSpeed` with human-readable formatting (B/KB/MB/GB and per-second variants).

### `time_formatter`
`format_time(delta)` — formats a `timedelta` as a human-readable string (`"X h"`, `"Y m"`, `"Z s"`).

### `singleton`
`Singleton` abstract base class. Subclasses get a single cached instance via `.instance()`.

### `json_migration`
`JsonMigrator` applies versioned migrations to JSON objects in order, updating the stored version key after each step.

### `cli`
Lightweight argparse wrapper: `App`, `Command`, `Action`, `Parameter`. Supports multi-action commands and typed parameters.

## CLI tools

Two command-line utilities are installed as entry points:

**`parts`** — manages numbered folder structures (`01.name`, `02.name`, …):
```
parts make <count>       create N numbered folders
parts renumber           renumber existing parts sequentially
parts offset <n>         shift all part indices by n
```

**`sf`** — moves files into a named subfolder:
```
sf <subfolder>
```
