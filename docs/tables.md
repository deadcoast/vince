# TABLES

## Overview

This document serves as the Single Source of Truth (SSOT) for all definitions, identifiers, and reference tables in the vince CLI documentation system. All other documentation files reference this document for canonical definitions of commands, errors, states, extensions, and configuration options.

## ID SYSTEM OVERVIEW

The `id`/`sid` relationship mirrors the familiar CLI flag pattern of `-h`/`--help`:

| CLI Pattern | ID System | Purpose |
| --- | --- | --- |
| `-h` | `sid` | Short form, quick to type/reference |
| `--help` | `id` | Long form, self-documenting |

Both follow the same principle: provide a concise shorthand for efficiency while maintaining a readable full form for clarity.

| Context | Short Form | Long Form | Usage |
| --- | --- | --- | --- |
| CLI flags | `-h` | `--help` | Interchangeable at runtime |
| ID system | `sid` | `id` | `sid` for tables/refs, `id` for human-readable |

## DEFINITIONS

| id | sid | rid | description |
| --- | --- | --- | --- |
| `example` | eg | eg01 | Sample or instance used for illustration |
| `application` | ap | ap01 | Program or executable to set as default |
| `extension` | xt | xt01 | File type suffix (e.g., .md, .py) |
| `default` | df | df01 | The preferred application for a file type |
| `short_id` | shid | shid01 | Abbreviated identifier (2-4 characters) |
| `long_id` | loid | loid01 | Full-length identifier |
| `id` | id | id01 | Main identification of an object |
| `number` | nu | nu01 | Numerical identification variable |
| `rule_id` | ruid | ruid01 | Rule identifier combining sid + number |
| `command` | cm | cm01 | CLI action verb |
| `flag` | fl | fl01 | CLI modifier with - or -- prefix |
| `operator` | op | op01 | CLI symbol with special meaning |
| `offer` | ofr | ofr01 | Custom shortcut/alias for defaults |
| `path` | pa | pa01 | File system location of application |
| `step` | stp | stp01 | Sequential action in a workflow |
| `error` | er | er01 | Error condition with code, message, and recovery |
| `error_code` | erco | erco01 | Unique identifier for error condition (VE###) |
| `state` | sta | sta01 | Lifecycle state of an entity (default or offer) |
| `transition` | trn | trn01 | State change triggered by a command |
| `config` | cfg | cfg01 | Configuration option for CLI behavior |
| `schema` | sc | sc01 | JSON schema defining data structure |
| `severity` | sv | sv01 | Error severity level (error, warning, info) |
| `recovery` | rc | rc01 | Recommended action to resolve an error |
| `validation` | vl | vl01 | Rule for checking data correctness |
| `persistence` | ps | ps01 | Data storage and retrieval mechanism |
| `backup` | bk | bk01 | Copy of data file for recovery purposes |
| `theme` | tm | tm01 | Console color scheme (default, dark, light) |

## COMMANDS

| id | sid | rid | description |
| --- | --- | --- | --- |
| `slap` | sl | sl01 | Set application as default for extension |
| `chop` | ch | ch01 | Remove/forget a file extension association |
| `set` | se | se01 | Set a default for a file extension |
| `forget` | fo | fo01 | Forget a default for a file extension |
| `offer` | of | of01 | Create a custom shortcut/alias |
| `reject` | re | re01 | Remove a custom offer |
| `list` | li | li01 | Display tracked assets and offers |
| `sync` | sy | sy01 | Sync all active defaults to the OS |

## FILE_TYPES

| id | full_id | ext | sid | flag_short | flag_long |
| --- | --- | --- | --- | --- | --- |
| `md` | markdown | .md | md | --md | --markdown |
| `py` | python | .py | py | --py | --python |
| `txt` | text | .txt | tx | --txt | --text |
| `js` | javascript | .js | js | --js | --javascript |
| `html` | html | .html | ht | --html | --html |
| `css` | css | .css | css | --css | --css |
| `json` | json | .json | jsn | --json | --json |
| `yml` | yaml | .yml | ym | --yml | --yaml |
| `yaml` | yaml | .yaml | ya | --yaml | --yaml |
| `xml` | xml | .xml | xm | --xml | --xml |
| `csv` | csv | .csv | csv | --csv | --csv |
| `sql` | sql | .sql | sq | --sql | --sql |

## UTILITY_FLAGS

| id | sid | short | long | description |
| --- | --- | --- | --- | --- |
| `help` | hlp | -h | --help | Display help information |
| `version` | ver | -v | --version | Display version information |
| `verbose` | vrb | -vb | --verbose | Enable verbose output |
| `debug` | dbg | -db | --debug | Enable debug mode |
| `trace` | trc | -tr | --trace | Enable trace logging |

## QOL_FLAGS

| id | sid | short | description |
| --- | --- | --- | --- |
| `set` | qset | -set | Set a file extension as default |
| `forget` | qfgt | -forget | Forget a file extension as default |
| `slap` | qslp | -slap | Set a file extension as default |
| `chop` | qchp | -chop | Forget a file extension as default |
| `offer` | qofr | -offer | Create a custom offer |
| `reject` | qrjt | -reject | Remove a custom offer |

## LIST_FLAGS

| id | sid | short | description |
| --- | --- | --- | --- |
| `applications` | lapp | -app | List all tracked applications |
| `commands` | lcmd | -cmd | List all available commands |
| `extensions` | lext | -ext | List all tracked extensions |
| `defaults` | ldef | -def | List all set defaults |
| `offers` | loff | -off | List all custom offers |
| `all` | lall | -all | List all subsections |

## OPERATORS

| symbol | name | usage |
| --- | --- | --- |
| `--` | flag_prefix | Prefix for long flags |
| `-` | short_prefix | Prefix for short flags |
| `.` | wildcard | Signifies 'all' or 'any' in context |

## ARGUMENTS

| pattern | name | description |
| --- | --- | --- |
| `<path/to/application/app.exe>` | path | File system path to the application executable |
| `<file_extension>` | file_extension | The file extension to target (e.g., .md, .py) |
| `<offer_id>` | offer | Custom shortcut/alias identifier |

## ERRORS

| code | sid | category | message | severity |
| --- | --- | --- | --- | --- |
| VE101 | ve101 | Input | Invalid path: {path} does not exist | error |
| VE102 | ve102 | Input | Invalid extension: {ext} is not supported | error |
| VE103 | ve103 | Input | Invalid offer_id: {id} does not match pattern | error |
| VE104 | ve104 | Input | Offer not found: {id} does not exist | error |
| VE105 | ve105 | Input | Invalid list subsection: {section} | error |
| VE201 | ve201 | File | File not found: {path} | error |
| VE202 | ve202 | File | Permission denied: cannot access {path} | error |
| VE203 | ve203 | File | Data file corrupted: {file} | error |
| VE301 | ve301 | State | Default already exists for {ext} | warning |
| VE302 | ve302 | State | No default set for {ext} | warning |
| VE303 | ve303 | State | Offer already exists: {id} | warning |
| VE304 | ve304 | State | Cannot reject: offer {id} is in use | error |
| VE401 | ve401 | Config | Invalid config option: {key} | error |
| VE402 | ve402 | Config | Config file malformed: {file} | error |
| VE501 | ve501 | System | Unexpected error: {message} | error |
| VE601 | ve601 | OS | Unsupported platform: {platform} | error |
| VE602 | ve602 | OS | Cannot determine bundle ID for: {app_path} | error |
| VE603 | ve603 | OS | Registry access denied: {operation} | error |
| VE604 | ve604 | OS | Application not found or invalid: {app_path} | error |
| VE605 | ve605 | OS | OS operation failed: {operation} - {details} | error |
| VE606 | ve606 | OS | Sync partially failed: {succeeded} succeeded, {failed} failed | error |

## STATES

| id | sid | entity | description |
| --- | --- | --- | --- |
| `none` | def-no | default | No default exists for the extension |
| `pending` | def-pe | default | Default identified but not yet set as active |
| `active` | def-ac | default | Default is set and actively used |
| `removed` | def-re | default | Default was removed but record retained |
| `none` | off-no | offer | No offer exists with the given ID |
| `created` | off-cr | offer | Offer created but not yet used |
| `active` | off-ac | offer | Offer has been used at least once |
| `rejected` | off-re | offer | Offer was rejected/removed |

## CONFIG_OPTIONS

| key | sid | type | default | description |
| --- | --- | --- | --- | --- |
| `version` | cver | string | Required | Schema version in semver format |
| `data_dir` | cdir | string | `~/.vince` | Data storage directory path |
| `verbose` | cvrb | boolean | `false` | Enable verbose output by default |
| `color_theme` | cthm | enum | `default` | Console color theme (default/dark/light) |
| `backup_enabled` | cbak | boolean | `true` | Enable automatic backups before writes |
| `max_backups` | cmax | integer | `5` | Maximum number of backup files to retain (0-100) |
| `confirm_destructive` | ccfm | boolean | `true` | Require confirmation for destructive operations |

## RULES

| rid | category | description |
| --- | --- | --- |
| PD01 | Python Design | Commands must be modular and space-separated, not underscore-joined |
| UID01 | Universal ID | id/sid may use brackets or backticks contextually |
| TB01 | Table | Tables must have proper headers and separators |
| TB02 | Table | Use template [1] for variable definitions |
| TB03 | Table | Use template [2] for standard tables |

## Cross-References

This document is the Single Source of Truth for the vince CLI documentation system. For related information, see:

| Document | Description |
| --- | --- |
| [README.md](README.md) | Documentation entry point and navigation |
| [overview.md](overview.md) | System design, commands, flags, and validation rules |
| [api.md](api.md) | Python function signatures and command interfaces |
| [schemas.md](schemas.md) | JSON schema definitions for data persistence |
| [errors.md](errors.md) | Complete error catalog with codes, messages, and recovery actions |
| [states.md](states.md) | State machine documentation for defaults and offers |
| [config.md](config.md) | Configuration options and hierarchy |
| [examples.md](examples.md) | Usage examples for all commands |
| [testing.md](testing.md) | Testing patterns and fixtures |
