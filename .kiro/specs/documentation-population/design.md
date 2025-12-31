# Design Document: Documentation Population

## Overview

This design specifies the comprehensive population and standardization of the `vince` CLI documentation system. The approach treats `tables.md` as the single source of truth (SSOT) for all definitions, with other documents referencing and expanding upon these canonical definitions.

The design follows a modular architecture where each document has a specific responsibility:
- **tables.md**: Master definition tables (SSOT)
- **overview.md**: System design, rules, and detailed explanations
- **examples.md**: Practical usage examples for all commands
- **README.md**: User-facing introduction and installation

## Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                    DOCUMENTATION SYSTEM                        │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌─────────────┐    references    ┌─────────────────────────┐  │
│  │  README.md  │ ───────────────► │      overview.md        │  │
│  │  (Entry)    │                  │  (Design & Rules)       │  │
│  └─────────────┘                  └───────────┬─────────────┘  │
│         │                                     │                │
│         │ references                          │ references     │
│         ▼                                     ▼                │
│  ┌─────────────┐                  ┌─────────────────────────┐  │
│  │ examples.md │ ◄───────────────►│      tables.md          │  │
│  │  (Usage)    │    references    │  (SSOT - Definitions)   │  │
│  └─────────────┘                  └─────────────────────────┘  │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

### Document Responsibilities

| Document | Responsibility | Contains |
|----------|---------------|----------|
| tables.md | Single Source of Truth | All ID/SID/RID definitions, complete tables |
| overview.md | Design Specification | Rules, semantics, command descriptions, flag docs |
| examples.md | Practical Usage | Working examples for all commands |
| README.md | User Entry Point | Introduction, installation, quick start |

## Components and Interfaces

### Component 1: ID System Schema

The identification system uses a three-tier naming convention that mirrors the familiar CLI flag pattern of `-h`/`--help`:

| CLI Pattern | ID System | Purpose |
|-------------|-----------|---------|
| `-h` | `sid` | Short form, quick to type/reference |
| `--help` | `id` | Long form, self-documenting |

This design makes the documentation system intuitive for CLI users who already understand the short/long duality:
- **CLI flags**: `-h` and `--help` are interchangeable at runtime
- **ID system**: `sid` is for internal references/tables, `id` is the canonical human-readable name

```
┌──────────────────────────────────────────────────────────────┐
│                     ID SYSTEM SCHEMA                         │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  id (full identifier)                                        │
│    └── "application"                                         │
│                                                              │
│  sid (short identifier) - 2-4 chars                          │
│    └── "app"                                                 │
│    Rules:                                                    │
│      • ONE-WORD: first 2 letters (eg: "step" → "st")         │
│      • TWO-WORD: first 2 of each word (eg: "short_id"→"sid") │
│      • Collision: use next letter in sequence                │
│                                                              │
│  rid (rule identifier) - sid + number                        │
│    └── "app01"                                               │
│    Format: {sid}{num} where num is zero-padded               │
│                                                              │
│  num (numerical identifier)                                  │
│    └── "01", "02", etc.                                      │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### Component 2: Command System

Commands are the primary CLI verbs. Each command has:
- `id`: Full command name
- `sid`: Short identifier with numerical suffix
- `rid`: Rule identifier for documentation references
- `description`: What the command does
- `syntax`: How to use it
- `flags`: Compatible flags
- `operators`: Compatible operators

**Command Registry:**

| id | sid | rid | description |
|----|-----|-----|-------------|
| slap | sl | sl01 | Set application as default for extension |
| chop | ch | ch01 | Remove/forget a file extension association |
| set | se | se01 | Set a default for a file extension |
| forget | fo | fo01 | Forget a default for a file extension |
| offer | of | of01 | Create a custom shortcut/alias |
| reject | re | re01 | Remove a custom offer |
| list | li | li01 | Display tracked assets and offers |

### Component 3: Flag System

Flags are organized into four categories:

**3.1 Utility Flags**

| id | sid | short | long | description |
|----|-----|-------|------|-------------|
| help | he | -h | --help | Display help information |
| version | ve | -v | --version | Display version information |
| verbose | vb | -vb | --verbose | Enable verbose output |
| debug | db | -db | --debug | Enable debug mode |
| trace | tr | -tr | --trace | Enable trace logging |

**3.2 QOL (Quality of Life) Flags**

| id | sid | short | description |
|----|-----|-------|-------------|
| set | se | -set | Set a file extension as default |
| forget | fo | -forget | Forget a file extension as default |
| slap | sl | -slap | Set a file extension as default |
| chop | ch | -chop | Forget a file extension as default |
| offer | of | -offer | Create a custom offer |
| reject | re | -reject | Remove a custom offer |

**3.3 Extension Flags**

| id | full_id | ext | short | long |
|----|---------|-----|-------|------|
| md | markdown | .md | --md | --markdown |
| py | python | .py | --py | --python |
| txt | text | .txt | --txt | --text |
| js | javascript | .js | --js | --javascript |
| html | html | .html | --html | --html |
| css | css | .css | --css | --css |
| json | json | .json | --json | --json |
| yml | yaml | .yml | --yml | --yaml |
| yaml | yaml | .yaml | --yaml | --yaml |
| xml | xml | .xml | --xml | --xml |
| csv | csv | .csv | --csv | --csv |
| sql | sql | .sql | --sql | --sql |

**3.4 List Subsection Flags**

| id | sid | short | description |
|----|-----|-------|-------------|
| applications | app | -app | List all tracked applications |
| commands | cmd | -cmd | List all available commands |
| extensions | ext | -ext | List all tracked extensions |
| defaults | def | -def | List all set defaults |
| offers | off | -off | List all custom offers |
| all | all | -all | List all subsections |

### Component 4: Operator System

| symbol | name | usage |
|--------|------|-------|
| `--` | flag_prefix | Prefix for long flags |
| `-` | short_prefix | Prefix for short flags |
| `.` | wildcard | Signifies 'all' or 'any' in context |

### Component 5: Rule System

Documentation rules are tagged with `rid` format for traceability:

| rid | category | description |
|-----|----------|-------------|
| PD01 | Python Design | Commands must be modular and space-separated |
| UID01 | Universal ID | id/sid may use brackets or backticks contextually |
| TB01 | Table | Tables must have proper headers and separators |
| TB02 | Table | Use template [1] for variable definitions |
| TB03 | Table | Use template [2] for standard tables |

## Data Models

### Definition Entry Model

```python
@dataclass
class Definition:
    id: str           # Full identifier (e.g., "application")
    sid: str          # Short identifier (e.g., "app")
    rid: Optional[str] # Rule identifier (e.g., "app01")
    description: str  # Human-readable description
```

### Command Entry Model

```python
@dataclass
class Command:
    id: str                    # Command name (e.g., "slap")
    sid: str                   # Short ID (e.g., "sl")
    rid: str                   # Rule ID (e.g., "sl01")
    description: str           # What it does
    syntax: List[str]          # Usage patterns
    compatible_flags: List[str] # Flags that work with this command
    compatible_operators: List[str] # Operators that work with this command
    auto_creates: Optional[str] # Side effects (e.g., slap auto-creates offer)
```

### Flag Entry Model

```python
@dataclass
class Flag:
    id: str           # Full name (e.g., "help")
    sid: str          # Short ID (e.g., "he")
    short: str        # Short form (e.g., "-h")
    long: str         # Long form (e.g., "--help")
    category: str     # utility | qol | extension | list
    description: str  # What it does
```

### Extension Entry Model

```python
@dataclass
class Extension:
    id: str           # Short name (e.g., "md")
    full_id: str      # Full name (e.g., "markdown")
    ext: str          # File extension (e.g., ".md")
    sid: str          # Short ID (e.g., "md")
    flag_short: str   # Short flag (e.g., "--md")
    flag_long: str    # Long flag (e.g., "--markdown")
```

### Rule Entry Model

```python
@dataclass
class Rule:
    rid: str          # Rule ID (e.g., "PD01")
    category: str     # Category (e.g., "Python Design")
    description: str  # Full rule text
    applies_to: List[str] # What this rule applies to
```



## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Heading Hierarchy Validation

*For any* markdown document in the documentation system, the heading hierarchy SHALL be valid: H1 appears first as document title, and H3 only appears after an H2 has been established in the document flow.

**Validates: Requirements 1.1, 1.2**

### Property 2: Table Syntax Validation

*For any* table defined in the documentation, it SHALL have proper markdown table syntax including a header row, a separator row with `|---|` pattern, and consistent column counts across all rows.

**Validates: Requirements 1.3**

### Property 3: Code Block Language Identifiers

*For any* fenced code block in the documentation, it SHALL include a language identifier immediately after the opening fence (e.g., ```sh, ```python).

**Validates: Requirements 1.4**

### Property 4: Entry Field Completeness

*For any* entry in a definition table (commands, flags, extensions, definitions), all required fields for that entry type SHALL be present and non-empty.

**Validates: Requirements 2.1, 2.2, 2.3**

### Property 5: SID Naming Convention Compliance

*For any* `sid` value in the documentation system, it SHALL follow the naming rules: one-word identifiers use first two letters, two-word identifiers use first two letters of each word, and no duplicate `sid` values exist.

**Validates: Requirements 2.4, 2.5**

### Property 6: Cross-Reference Consistency

*For any* identifier (command, flag, extension, sid) referenced in one document, if it is defined in another document, the definitions SHALL be identical. Additionally, all referenced identifiers SHALL have a definition in tables.md.

**Validates: Requirements 5.1, 5.2, 5.3, 5.5**

### Property 7: Flag Prefix Convention

*For any* flag defined in the documentation, short flags SHALL use single dash prefix (`-`) and long flags SHALL use double dash prefix (`--`).

**Validates: Requirements 4.5**

### Property 8: Example Completeness Per Command

*For any* command defined in the system, examples.md SHALL contain at least one complete example demonstrating that command with appropriate flags.

**Validates: Requirements 3.1, 3.2, 7.1, 7.2**

### Property 9: Rule Reference Format Consistency

*For any* rule referenced in the documentation, it SHALL use the `rid` format (category prefix + number, e.g., PD01, UID01) and bracket notation `[rid]` when referenced inline.

**Validates: Requirements 9.2, 9.4**

### Property 10: Modular Command Syntax

*For any* command example in the documentation, it SHALL NOT contain underscore-joined subcommands (e.g., `sub_command`) and SHALL use space-separated modular syntax.

**Validates: Requirements 10.2, 10.3**

## Error Handling

### Document Parsing Errors

| Error Type | Detection | Resolution |
|------------|-----------|------------|
| Invalid heading hierarchy | H3 before H2 | Restructure with proper H2 parent |
| Malformed table | Missing separators or inconsistent columns | Fix table syntax |
| Missing language identifier | Code block without lang | Add appropriate language tag |
| Placeholder links | XXXXXXX pattern detected | Replace with actual URLs |

### Cross-Reference Errors

| Error Type | Detection | Resolution |
|------------|-----------|------------|
| Orphaned reference | ID used but not defined in tables.md | Add definition to tables.md |
| Duplicate sid | Same sid used for different ids | Apply collision rules |
| Inconsistent definition | Same id with different values across docs | Sync to tables.md SSOT |
| Missing example | Command without example in examples.md | Add example section |

### Validation Workflow

```
┌─────────────────┐
│ Parse Document  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌─────────────────┐
│ Validate        │────►│ Report Errors   │
│ Structure       │ err └─────────────────┘
└────────┬────────┘
         │ ok
         ▼
┌─────────────────┐     ┌─────────────────┐
│ Validate        │────►│ Report Errors   │
│ Cross-Refs      │ err └─────────────────┘
└────────┬────────┘
         │ ok
         ▼
┌─────────────────┐
│ Document Valid  │
└─────────────────┘
```

## Testing Strategy

### Dual Testing Approach

This documentation system will be validated using both unit tests and property-based tests:

**Unit Tests**: Verify specific examples and edge cases
- Specific table format validation
- Known placeholder detection
- Specific cross-reference checks

**Property-Based Tests**: Verify universal properties across all inputs
- Heading hierarchy for any markdown content
- Table syntax for any table definition
- SID naming rules for any identifier

### Property-Based Testing Framework

For this documentation validation system, we will use **Hypothesis** (Python) as the property-based testing library.

**Configuration:**
- Minimum 100 iterations per property test
- Each test tagged with: **Feature: documentation-population, Property {number}: {property_text}**

### Test Categories

| Category | Type | Coverage |
|----------|------|----------|
| Structure Validation | Property | Properties 1, 2, 3 |
| Field Completeness | Property | Property 4 |
| Naming Convention | Property | Property 5 |
| Cross-Reference | Property | Property 6 |
| Flag Convention | Property | Property 7 |
| Example Coverage | Property | Property 8 |
| Rule Format | Property | Property 9 |
| Modular Syntax | Property | Property 10 |

### Validation Scripts

The implementation will include validation scripts that can be run to verify documentation compliance:

```sh
# Validate all documents
python validate_docs.py --all

# Validate specific document
python validate_docs.py --file tables.md

# Check cross-references only
python validate_docs.py --cross-refs

# Generate compliance report
python validate_docs.py --report
```
