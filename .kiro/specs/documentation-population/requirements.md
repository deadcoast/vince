# Requirements Document

## Introduction

This specification defines the comprehensive analysis, cross-referencing, and population of the `vince` CLI documentation system. The goal is to ensure all existing documentation is consistent, accurate, professionally formatted, and fully populated according to the established modular design patterns and identification semantics.

## Glossary

- **Vince_CLI**: The main command-line interface application for setting default applications to file extensions
- **Documentation_System**: The collection of markdown files defining the CLI's structure, commands, and conventions
- **ID_System**: The three-tier identification scheme using `id`, `sid`, and `rid` for consistent naming (mirrors CLI `-h`/`--help` pattern)
- **id**: Main identification of an object in the document (full name) - analogous to `--help` in CLI
- **sid**: Short identification of an object (2-4 letter abbreviation) - analogous to `-h` in CLI
- **rid**: Rule ID tag combining `sid` prefix with numerical identifier
- **num**: Numerical identification variable for sequential ordering
- **Command**: A CLI action verb (slap, chop, set, forget, offer, reject)
- **Flag**: A CLI modifier prefixed with `-` (short) or `--` (long)
- **Operator**: A CLI symbol with special meaning (`.`, `--`, `-`)
- **Extension_Flag**: A flag representing a file type (e.g., `--md`, `--py`)
- **Utility_Flag**: A flag for CLI behavior control (e.g., `-h`, `-v`, `-db`)
- **QOL_Flag**: Quality-of-life flags mirroring command functionality
- **Offer**: A custom shortcut/alias created when setting defaults
- **Cross_Reference**: Validation that all IDs, commands, and definitions are consistent across documents

## Requirements

### Requirement 1: Document Structure Consistency

**User Story:** As a developer, I want all documentation files to follow consistent markdown structure, so that the documentation is professional and navigable.

#### Acceptance Criteria

1. THE Documentation_System SHALL use consistent heading hierarchy starting with H1 for document title
2. THE Documentation_System SHALL use H2 for major sections and H3 for subsections only after H2
3. WHEN tables are defined, THE Documentation_System SHALL include proper table headers with column separators
4. THE Documentation_System SHALL maintain consistent code block formatting with language identifiers
5. THE Documentation_System SHALL use consistent note/callout syntax (`> [!NOTE]`)

### Requirement 2: ID System Completeness

**User Story:** As a documentation maintainer, I want all identifiable objects to have complete id/sid/rid definitions, so that the naming system is fully populated and traceable.

#### Acceptance Criteria

1. FOR ALL commands defined in the system, THE Documentation_System SHALL provide `id`, `sid`, and `rid` values
2. FOR ALL file types/extensions, THE Documentation_System SHALL provide `id`, `full_id`, `ext`, and `sid` values
3. FOR ALL flags defined in the system, THE Documentation_System SHALL provide `id`, `sid`, and description
4. WHEN a new `sid` is created, THE Documentation_System SHALL follow the naming rules (first two letters for one-word, first two of each word for two-word)
5. WHEN an `sid` collision occurs, THE Documentation_System SHALL use subsequent letters as per the defined priority rules
6. THE Documentation_System SHALL maintain a master definitions table with all `id`/`sid` mappings

### Requirement 3: Command Documentation Completeness

**User Story:** As a CLI user, I want all commands to be fully documented with syntax, arguments, and examples, so that I can use the CLI effectively.

#### Acceptance Criteria

1. FOR ALL commands (slap, chop, set, forget, offer, reject), THE Documentation_System SHALL provide complete syntax documentation
2. FOR ALL commands, THE Documentation_System SHALL provide at least one working example
3. THE Documentation_System SHALL document the relationship between commands and their QOL flag equivalents
4. WHEN a command creates side effects (e.g., slap auto-creates offer), THE Documentation_System SHALL document this behavior
5. THE Documentation_System SHALL document the `.` operator usage for each applicable command

### Requirement 4: Flag Documentation Completeness

**User Story:** As a CLI user, I want all flags to be documented in consistent tables, so that I can quickly reference available options.

#### Acceptance Criteria

1. THE Documentation_System SHALL provide a complete table of all Utility Flags with `id`, `sid`, and description
2. THE Documentation_System SHALL provide a complete table of all QOL Flags with `id`, `sid`, and description
3. THE Documentation_System SHALL provide a complete table of all Extension Flags with `id`, `full_id`, `ext`, and `sid`
4. THE Documentation_System SHALL document the `--list` flag subsections (`-app`, `-cmd`, `-ext`, `-def`, `-off`, `-all`)
5. FOR ALL flags, THE Documentation_System SHALL use consistent short (`-`) and long (`--`) prefix conventions

### Requirement 5: Cross-Reference Validation

**User Story:** As a documentation maintainer, I want all references between documents to be validated, so that there are no orphaned or inconsistent definitions.

#### Acceptance Criteria

1. FOR ALL commands referenced in examples.md, THE Documentation_System SHALL have matching definitions in overview.md
2. FOR ALL file types referenced in overview.md, THE Documentation_System SHALL have matching entries in tables.md
3. FOR ALL `sid` values used in any document, THE Documentation_System SHALL have a definition in the master tables
4. THE Documentation_System SHALL ensure README.md framework links are populated (not XXXXXXX placeholders)
5. WHEN a definition appears in multiple documents, THE Documentation_System SHALL ensure identical values

### Requirement 6: Tables Document Completeness

**User Story:** As a developer, I want tables.md to serve as the single source of truth for all definitions, so that other documents can reference it.

#### Acceptance Criteria

1. THE tables.md SHALL include a complete DEFINITIONS table with all `id`/`sid` pairs
2. THE tables.md SHALL include a complete COMMANDS table with `id`, `sid`, `rid`, and description
3. THE tables.md SHALL include a complete FILE_TYPES table with `id`, `full_id`, `ext`, `sid`, and flag
4. THE tables.md SHALL include a complete FLAGS table subdivided by category (Utility, QOL, Extension, List)
5. THE tables.md SHALL include an OPERATORS table with symbol, name, and usage description
6. THE tables.md SHALL include an ARGUMENTS table with argument patterns and descriptions

### Requirement 7: Examples Document Completeness

**User Story:** As a CLI user, I want examples.md to provide complete, working examples for all commands, so that I can learn by example.

#### Acceptance Criteria

1. FOR ALL commands, THE examples.md SHALL provide at least one complete example with explanation
2. THE examples.md SHALL demonstrate flag combinations for each command
3. THE examples.md SHALL demonstrate the `.` operator usage where applicable
4. THE examples.md SHALL include examples for the `--list` command with all subsection flags
5. WHEN examples reference step numbers (S1, S2), THE examples.md SHALL use consistent `sid` notation

### Requirement 8: README Professional Formatting

**User Story:** As a new user, I want README.md to provide a professional introduction and installation guide, so that I can get started quickly.

#### Acceptance Criteria

1. THE README.md SHALL include populated framework links (Python, Typer, Rich, UV)
2. THE README.md SHALL maintain the current installation structure with Quick Install, Step One, Step Two, Step Three
3. THE README.md SHALL include troubleshooting section with common issues
4. THE README.md SHALL reference the other documentation files for detailed information

### Requirement 9: Semantic Rule Documentation

**User Story:** As a documentation maintainer, I want all semantic rules (uid01, PD01, etc.) to be catalogued, so that future automation can reference them.

#### Acceptance Criteria

1. THE Documentation_System SHALL maintain a RULES table with all rule IDs and their descriptions
2. FOR ALL rules referenced in documents, THE Documentation_System SHALL use consistent `rid` format
3. THE Documentation_System SHALL document the rule ID generation pattern (prefix + number)
4. WHEN a rule is referenced, THE Documentation_System SHALL use the `[rid]` notation consistently

### Requirement 10: Modular Design Compliance

**User Story:** As a developer, I want the documentation to enforce the modular design principle, so that commands and flags remain independent.

#### Acceptance Criteria

1. THE Documentation_System SHALL document that commands are independent and composable
2. THE Documentation_System SHALL NOT show examples with underscore-joined subcommands (e.g., `sub_command`)
3. THE Documentation_System SHALL show examples with space-separated modular commands
4. THE Documentation_System SHALL document the design principle [PD01] prominently
