# vince - A Rich CLI Application

Vince is a simple, sophisticated CLI created with elevated visual ASCII UI delivery to quickly set default applications to file extensions. Its quick, intuitive and visually friendly design sets the new standard for user quality of life and visual CLI UI design.

— *Inspired by Infomercials of the Millennials Age*

> [!NOTE]
> **[PD01] Modular Design Principle**: All vince CLI commands, flags, arguments and options are independent and modular. Commands work interdependently with each other in the CLI. This means space-separated syntax, not underscore-joined subcommands.
>
> **Bad Practice**: `vince sub_command --flag`
>
> **Correct Practice**: `vince sub command --flag`

## Framework

### Python Design

The vince CLI is built on the following technologies:

- [Python](https://www.python.org/) - Core language
  - CLI Framework:
    - [Typer](https://typer.tiangolo.com/) - Command-line interface
    - [Rich](https://rich.readthedocs.io/) - Terminal formatting
  - Package Manager: [UV](https://docs.astral.sh/uv/)
  - Data Format: [JSON](https://www.json.org/)

### Documentation Design

All vince documentation follows a modular, regimented format. The docs define the grammar for the CLI, document tagging, acronyms and functionality in consistent spaces. This ensures that naming conventions are consistent and recognizable as per spec across the framework.

> [!NOTE]
> For complete definition tables and the Single Source of Truth, see [tables.md](tables.md).

## ID System

The identification system uses a three-tier naming convention that mirrors the familiar CLI flag pattern of `-h`/`--help`:

| CLI Pattern | ID System | Purpose |
| --- | --- | --- |
| `-h` | `sid` | Short form, quick to type/reference |
| `--help` | `id` | Long form, self-documenting |

This design makes the documentation system intuitive for CLI users who already understand the short/long duality:

- **CLI flags**: `-h` and `--help` are interchangeable at runtime
- **ID system**: `sid` is for internal references/tables, `id` is the canonical human-readable name

### Identification Types

| Type | Description | Example |
| --- | --- | --- |
| `id` | Main identification of an object (full name) | `application` |
| `sid` | Short identification (2-4 letter abbreviation) | `app` |
| `rid` | Rule ID tag combining sid prefix with number | `app01` |
| `num` | Numerical identification variable | `01` |

> [!NOTE]
> [UID01] `id` and `sid` may use brackets or backticks depending on contextual usage throughout the document.

### SID Naming Rules

- **One-word identifiers**: Use first two letters of the id (e.g., `step` → `st`)
- **Two-word identifiers**: Use first two letters of each word (e.g., `short_id` → `sid`)
- **Collision handling**: If an sid is already in use, use subsequent letters in sequence
- **Priority**: `short_id` > `long_id` > `id`

### RID Format

Rule IDs combine the `sid` with a zero-padded number:

- Format: `{sid}{num}` (e.g., `PD01`, `sl01`, `app01`)
- If collision occurs, use subsequent letters from the sid

> [!NOTE]
> For complete id/sid/rid listings, see the DEFINITIONS table in [tables.md](tables.md).

## CLI Commands

The vince CLI provides 7 commands for managing file extension defaults:

| Command | SID | Description |
| --- | --- | --- |
| `slap` | sl | Set application as default for extension |
| `chop` | ch | Remove/forget a file extension association |
| `set` | se | Set a default for a file extension |
| `forget` | fo | Forget a default for a file extension |
| `offer` | of | Create a custom shortcut/alias |
| `reject` | re | Remove a custom offer |
| `list` | li | Display tracked assets and offers |

> [!NOTE]
> For complete command definitions including rid values, see the COMMANDS table in [tables.md](tables.md).

### Command: slap

Set an application as the default for a file extension.

```sh
# STEP1: Identify an application path to set as default
vince slap <path/to/application/app.exe>

# STEP2: Set S1 as extension
vince slap <path/to/application/app.exe> --md

# STEP3: Set S1 as default for extension
vince slap <path/to/application/app.exe> -set --md
```

> [!NOTE]
> When using `slap` with `-set`, an offer is automatically created for the application-extension pairing.

### Command: chop

Remove or forget a file extension association.

```sh
# Remove an application as a default
vince chop <path/to/application/app.exe> -forget --md

# Use `.` operator to remove default without specifying path
vince chop . -forget --md
```

### Command: set

Set a default for a file extension (used as flag with other commands).

```sh
vince slap <path/to/application/app.exe> -set --md
```

### Command: forget

Forget a default for a file extension (used as flag with other commands).

```sh
vince chop <path/to/application/app.exe> -forget --md
```

### Command: offer

Create a custom shortcut/alias for a file extension default.

```sh
# Create an offer with application path, offer_id, and target extension
vince offer <path/to/application/app.exe> <offer_id> --md
```

### Command: reject

Remove a custom offer.

```sh
# Remove a specific offer
vince reject <path/to/application/app.exe> <offer_id> --md

# Complete-Delete: remove offer, its id, and all connections using `.` operator
vince reject <offer_id> .
```

### Command: list

Display tracked assets and offers.

```sh
# List all tracked applications
vince list -app

# List all available commands
vince list -cmd

# List all tracked extensions
vince list -ext

# List all set defaults
vince list -def

# List all custom offers
vince list -off

# List all subsections
vince list -all
```

## Flags

Flags are organized into four categories: Utility, QOL (Quality of Life), List, and Extension.

### Utility Flags

Control CLI behavior and output.

| Short | Long | Description |
| --- | --- | --- |
| `-h` | `--help` | Display help information |
| `-v` | `--version` | Display version information |
| `-vb` | `--verbose` | Enable verbose output |
| `-db` | `--debug` | Enable debug mode |
| `-tr` | `--trace` | Enable trace logging |

### QOL Flags

Quality-of-life flags that mirror command functionality. These provide shorthand access to command behaviors when used with other commands.

| Short | Description | Mirrors Command |
| --- | --- | --- |
| `-set` | Set a file extension as default | `set` |
| `-forget` | Forget a file extension as default | `forget` |
| `-slap` | Set a file extension as default | `slap` |
| `-chop` | Forget a file extension as default | `chop` |
| `-offer` | Create a custom offer | `offer` |
| `-reject` | Remove a custom offer | `reject` |

> [!NOTE]
> QOL flags mirror their corresponding commands. For example, `-set` provides the same functionality as the `set` command when used as a modifier.

### List Flags

Subsection flags for the `list` command. These provide cheatsheet-style table views.

| Short | Description |
| --- | --- |
| `-app` | List all tracked applications |
| `-cmd` | List all available commands |
| `-ext` | List all tracked extensions |
| `-def` | List all set defaults |
| `-off` | List all custom offers |
| `-all` | List all subsections |

```sh
# Example: List all applications
vince list -app
```

### Extension Flags

Set file type defaults. Extension flags use the `--` prefix (long flag format).

| Flag | Alias | Sets Default For |
| --- | --- | --- |
| `--md` | `--markdown` | Markdown files (.md) |
| `--py` | `--python` | Python files (.py) |
| `--txt` | `--text` | Text files (.txt) |
| `--js` | `--javascript` | JavaScript files (.js) |
| `--html` | `--html` | HTML files (.html) |
| `--css` | `--css` | CSS files (.css) |
| `--json` | `--json` | JSON files (.json) |
| `--yml` | `--yaml` | YAML files (.yml) |
| `--yaml` | `--yaml` | YAML files (.yaml) |
| `--xml` | `--xml` | XML files (.xml) |
| `--csv` | `--csv` | CSV files (.csv) |
| `--sql` | `--sql` | SQL files (.sql) |

> [!NOTE]
> Extension flags use the double-dash (`--`) prefix for both short and long forms. They do not have single-dash short forms like utility flags.

## CLI Operators

Special symbols with contextual meaning in the CLI.

| Symbol | Name | Usage |
| --- | --- | --- |
| `--` | flag_prefix | Prefix for long flags |
| `-` | short_prefix | Prefix for short flags |
| `.` | wildcard | Signifies 'all' or 'any' in context |

> [!NOTE]
> For complete operator definitions, see the OPERATORS table in [tables.md](tables.md).

### The `.` Operator

The `.` (wildcard) operator is used to signify "all" or "any" in the context of a command:

**With `chop`**: Remove default without specifying the application path

```sh
vince chop . -forget --md
```

**With `reject`**: Complete-delete an offer and all its connections

```sh
vince reject <offer_id> .
```

## CLI Arguments

| Pattern | Name | Description |
| --- | --- | --- |
| `<path/to/application/app.exe>` | path | File system path to the application executable |
| `<file_extension>` | file_extension | The file extension to target (e.g., .md, .py) |
| `<offer_id>` | offer | Custom shortcut/alias identifier |

> [!NOTE]
> For complete argument definitions, see the ARGUMENTS table in [tables.md](tables.md).
