# TABLES

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
| `extension` | ex | ex01 | File type suffix (e.g., .md, .py) |
| `default` | dlt | dlt01 | The preferred application for a file type |
| `short_id` | sid | sid01 | Abbreviated identifier (2-4 characters) |
| `long_id` | lid | lid01 | Full-length identifier |
| `id` | id | id01 | Main identification of an object |
| `number` | num | num01 | Numerical identification variable |
| `rule_id` | rid | rid01 | Rule identifier combining sid + number |
| `command` | cm | cm01 | CLI action verb |
| `flag` | fl | fl01 | CLI modifier with - or -- prefix |
| `operator` | op | op01 | CLI symbol with special meaning |
| `offer` | ofr | ofr01 | Custom shortcut/alias for defaults |
| `path` | pa | pa01 | File system location of application |
| `step` | st | st01 | Sequential action in a workflow |

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

## FILE_TYPES

| id | full_id | ext | sid | flag_short | flag_long |
| --- | --- | --- | --- | --- | --- |
| `md` | markdown | .md | md | --md | --markdown |
| `py` | python | .py | py | --py | --python |
| `txt` | text | .txt | tx | --txt | --text |
| `js` | javascript | .js | js | --js | --javascript |
| `html` | html | .html | ht | --html | --html |
| `css` | css | .css | cs | --css | --css |
| `json` | json | .json | jn | --json | --json |
| `yml` | yaml | .yml | yl | --yml | --yaml |
| `yaml` | yaml | .yaml | ya | --yaml | --yaml |
| `xml` | xml | .xml | xm | --xml | --xml |
| `csv` | csv | .csv | cv | --csv | --csv |
| `sql` | sql | .sql | sq | --sql | --sql |

## UTILITY_FLAGS

| id | sid | short | long | description |
| --- | --- | --- | --- | --- |
| `help` | he | -h | --help | Display help information |
| `version` | ve | -v | --version | Display version information |
| `verbose` | vb | -vb | --verbose | Enable verbose output |
| `debug` | db | -db | --debug | Enable debug mode |
| `trace` | tr | -tr | --trace | Enable trace logging |

## QOL_FLAGS

| id | sid | short | description |
| --- | --- | --- | --- |
| `set` | se | -set | Set a file extension as default |
| `forget` | fo | -forget | Forget a file extension as default |
| `slap` | sl | -slap | Set a file extension as default |
| `chop` | ch | -chop | Forget a file extension as default |
| `offer` | of | -offer | Create a custom offer |
| `reject` | re | -reject | Remove a custom offer |

## LIST_FLAGS

| id | sid | short | description |
| --- | --- | --- | --- |
| `applications` | app | -app | List all tracked applications |
| `commands` | cmd | -cmd | List all available commands |
| `extensions` | ext | -ext | List all tracked extensions |
| `defaults` | def | -def | List all set defaults |
| `offers` | off | -off | List all custom offers |
| `all` | all | -all | List all subsections |

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

## RULES

| rid | category | description |
| --- | --- | --- |
| PD01 | Python Design | Commands must be modular and space-separated, not underscore-joined |
| UID01 | Universal ID | id/sid may use brackets or backticks contextually |
| TB01 | Table | Tables must have proper headers and separators |
| TB02 | Table | Use template [1] for variable definitions |
| TB03 | Table | Use template [2] for standard tables |
