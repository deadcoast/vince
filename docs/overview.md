# `vince` - A Rich CLI Application

Vince is a simple, sopthisticated CLI created with elevated visual ASCII UI delivery to quickly set default applications to file extensions. Its quick, intuitive and visually friendly design sets the new standard for user quality of life and visual CLI UI design.

- *Inspired by Infomercials of the Millennials Age*

## FRAMEWORK

### Python Design

> [!NOTE]
> [PD01] ALL VINCE PYTHON CLI COMMANDS, FLAGS, ARGUMENTS AND OPTIONS SHOULD BE INTEPENDANT AND MODULAR.
> ALL COMMANDS SHOULD WORK INTERDEPENDANTLY WITH EACHOTHER IN THE CLI.
> EXAMPLE: BAD PRACTICE
> `vince sub_command --flag`
> CORRECT: MODULAR PRACTICE
> `vince sub command --flag`

- [Python](XXXXXXXXXXXXXXXXXXXXXXX)
  - CLI:
    - [Typer](XXXXXXXXXXXXXXXXXXXXXXX)
    - [Rich](XXXXXXXXXXXXXXXXXXXXXXX)
  - PKG: [UV](XXXXXXXXXXXXXXXXXXXXXXX)
  - DATA: [JSON](XXXXXXXXXXXXXXXXXXXXXXX)
    - [!NOTE](PD01)

- [Docs]
  - ALL VINCE DOCS SHOULD FOLLOW A MODULAR, REGIMENTED FORMAT.
  - The docs Define its grammer for the CLI, document tagging, acronym and its functionality all in the same spaces.
    - This is to ensure that name_types and conventions are consistent and recognizable as per spec across the framework.

## DOCUMENT DICTIONARY

> [!NOTE]
> ALL DEFINITIONS ARE DESIGNED TO BE IDENTIFIED WITH THREE SEPERATE ID VARIANTS FOR THEIR CORRELATING PLATFORM.
> `id` is the main identification of an object in the document.
> `sid` is the short identification of an object in the document.
> `rid` is the ID RULE TAG that the documentation assignes based on the first letter of `id` and `sid` plus `number` for the numerical identification of an object in the document.
> > `number` is the numerical identification variable of an object in the document.

## Identification and their Alias

Identification definition is the main identification of an object in the document across three seperate platforms:

> UID
> [sid]
> [rid]
> [num]

### CLI Analogy

The `id`/`sid` relationship mirrors the familiar CLI flag pattern:

| CLI Pattern | ID System | Purpose |
| --- | --- | --- |
| `-h` | `sid` | Short form, quick to type/reference |
| `--help` | `id` | Long form, self-documenting |

This design makes the documentation system intuitive for CLI users who already understand the short/long duality. The key difference is context:
- **CLI flags**: `-h` and `--help` are interchangeable at runtime
- **ID system**: `sid` is for internal references/tables, `id` is the canonical human-readable name

### Universal Rules and Semantics

> [!NOTE]
> ALL RULES AND SEMANTICS ARE SET FORTH FOR FUTURE AUTOMATION, POPULATION AND DOCUMENTATION PURPOSES.
> THE CURRENT ID NAMING SCHEME MAY NOT COMPLY TO THE RULES BELOW. THE INITIAL DESIGN UTILIZED SUBJECTIVE, DESCRIPTION ACRONYMS FOR SOME WORDS THAT OTHERWISE HAVE VERY COMMON LETTERS OR VOWELS AT THE START.

---

- [uid01]: `id` and `sid` may or may not be using brackets or backticks depending on their contextual usage throughout the document.

#### `identification`

1. `id` is the main identification of an object in the document.
2. `sid` is the short identification of an object in the document.
3. `rid` is the ID RULE TAG that the documentation assignes based on the first letter of `id` and `sid` plus `number` for the numerical identification of an object in the document.
4. `number` is the numerical identification of an object in the document.

#### `sid`

`sid` are defined in order of cration

- All ONE-WORD `sid` are defined by the first two letters of its id.
- All TWO-WORD `sid` are defined by the first two letters of each word in its `sid`.

- IF
  - an `sid` has 'three' or 'four' letters, the `rid` will default to
  - a `sid` is already in use, utilize the second letter of the (first) word; if that is taken continue to the third, so on.
- Priority for `sid` naming schemes is `short_id` > `long_id` > `id`

#### `rid`

- `rid` are defined by the first two letters of its `sid` plus the first letter of its `number`.

- IF
  - an `rid` is already in use, utilize the second letter of the (first) word;
  - a `rid` is already in use, utilize the second letter of the (second) word;

| id            | sid   |
| `example`     | (eg)  |
| `application` | (app) |
| `extension`   | (ext) |
| `default`     | (dlt) |
| `short_id`    | (sid) |
| `long_id`     | (lid) |
| `id`          | (id)  |
| `number`      | (num) |

### Numerical Dictionary

- FORMAT: `id{number}`, (`sid{num}`)
  - ACTUAL_USE: `step{1}` = (S1)

| id       | sid     |
| `step`   | (st0)   |
| `chop`   | (ch0)   |
| `slap`   | (sl0)   |
| `set`    | (se0)   |
| `forget` | (fo0)   |
| `offer`  | (ofr0)  |
| `reject` | (rejR0) |

> TABLE TEMPLATE

<!--  [1] For definitions that require variables:
```
- FORMAT:
  - ACTUAL_USE: `` = (S1)
```
-->
<!-- [2] For all other tables use:
```
> Table Title

| id      | sid     |
| ``      | ()      |
```
-->

- FORMAT: `id{number}`, (`sid{num}`)
  - ACTUAL_USE: `step{1}` = (S1)

| id       | sid     |
| `step`   | (st0)   |
| `chop`   | (ch0)   |
| `slap`   | (sl0)   |
| `set`    | (se0)   |
| `forget` | (fo0)   |
| `offer`  | (ofr0)  |
| `reject` | (rejR0) |

## Commands

- `vince`: the main command line call
- `slap`: identifies setting file `extension`
- `chop`: identifies forgetting a `file_extension`
- `set`: identifies setting a `default` for a `file_extension`
- `forget`: identifies forgetting a `default` for a `file_extension`
- `offer`: identifies setting a `custom_offer` for a `file_extension`
- `reject`: identifies removing a `custom_offer` for a `file_extension`

```sh
# STEP1: Identify an `application` path to set as Default
vince slap <path/to/application/app.exe>
# STEP2: Set [S1] as (ext)
vince slap <path/to/application/app.exe> --md
# STEP3: Set [S1] as [(dlt):(ext)]
vince slap <path/to/application/app.exe> -set --md
```

```sh
# Identify an application to remove as a default
vince chop <path/to/application/app.exe> -forget --md
# ALTERNATIVELY: utilize the `.` operator to signal the removal of a default without the specific applications path
vince chop . -forget --md
```

```sh
# [1] create an offer with the application path the offer_id and the file extension it is targetting
vince offer <path/to/application/app.exe> <offer_id> --md
# [2] replace offer with 'reject' to delete the same offer id
vince reject <path/to/application/app.exe> <offer_id> --md
# [3] Complete-Delete: deletes the offer, its id, and its correction to any applications or extensions using operator `.`
vince reject <offer_id> .
```

## FLAGS

## UTILITY FLAGS

> `-h`: Help, `--help`: Help
> `-v`: Version, `--version`: Version
> `-vb`: Verbose, --verbose`: Verbose
> `-db`: Debug,`--debug`: Debug
> `-tr`: Trace,`--trace`: Trace

### QOL FLAGS

>`-set`: Set a file extension as default
> `-forget`: Forget a file extension as default
> `-slap`: Set a file extension as default
> `-chop`: Forget a file extension as default
> `-offer`: Create a custom offer for a file extension
> `-reject`: Remove a custom offer for a file extension

#### `--list` flag subsections

- The list flag provides a seperate subsection than the help(`-h`, `--help`) flag. This subsection is designed specifically to provide cheatsheets in a table view.
  - Descriptions must be ABSOLUTE MINIMUM, TO ENSURE THEY DO NOT FOLD ANY LINES IN THE TABLE VIEW.

> `--list`: identifies the `list` subsection

```sh
vince --list -app
```

> `-app`: identifies the `applications` subsection
> `-cmd`: identifies the `commands` subsection
> `-ext`: identifies the `extensions` subsection
> `-def`: identifies the `defaults` subsection
> `-off`: identifies the `offers` subsection
> `-all`: identifies all subsections

### EXTENSION FLAGS

> `--md`: Set `markdown` as default
> `--py`: Set `python` as default
> `--txt`: Set `text` as default
> `--js`: Set `javascript` as default
> `--html`: Set `html` as default
> `--css`: Set `css` as default
> `--json`: Set `json` as default
> `--yml`: Set `yaml` as default
> `--yaml`: Set `yaml` as default
> `--xml`: Set `xml` as default
> `--csv`: Set `csv` as default
> `--sql`: Set `sql` as default

## ARGUMENTS

| ARGUMENT | DESCRIPTION |
| `path/to/application/app.exe` | The path to the application to set as default. |
| `file_extension` | The file extension to set as default. |
|  `offer` | The custom offer to set for a file extension. |

## OPERATORS

`--`: Flag
`-`: Short flag
`.`: signifies 'all' or 'any' in the context of the command
