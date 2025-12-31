# Requirements Document

## Introduction

This specification defines the requirements for unifying the vince CLI documentation with the current source code implementation. The documentation has drifted from the actual implementation and requires a complete overhaul to serve as a living framework that agents can utilize for essential data and context on the source code.

The unification must comply with the existing validation methods defined in `validate_docs.py` and ensure bidirectional traceability between documentation and source code.

## Glossary

- **Documentation_System**: The collection of markdown files in `docs/` that define the vince CLI specification
- **Source_Code**: The Python implementation in `vince/` directory
- **Validation_Script**: The `validate_docs.py` script that validates documentation against defined rules
- **Cross_Reference**: A link or reference between documentation files or between documentation and source code
- **EARS_Pattern**: Easy Approach to Requirements Syntax - structured requirement format
- **SID**: Short identifier (2-4 letter abbreviation) used in the ID system
- **RID**: Rule ID combining sid prefix with number (e.g., `PD01`, `VE101`)
- **Agent**: An AI system that consumes documentation for context and implementation guidance

## Requirements

### Requirement 1: Documentation-Source Code Synchronization

**User Story:** As a developer or agent, I want documentation that accurately reflects the current source code implementation, so that I can rely on documentation as the single source of truth.

#### Acceptance Criteria

1. WHEN a validation function exists in source code, THE Documentation_System SHALL document that function with matching signature, parameters, and return types
2. WHEN an error class is defined in `vince/errors.py`, THE Documentation_System SHALL include that error in `docs/errors.md` with matching code, message template, and recovery action
3. WHEN a state transition is implemented in `vince/state/`, THE Documentation_System SHALL document that transition in `docs/states.md` with matching from/to states and triggers
4. WHEN a configuration option is used in `vince/config.py`, THE Documentation_System SHALL document that option in `docs/config.md` with matching type, default, and description
5. FOR ALL supported extensions in `vince/validation/extension.py`, THE Documentation_System SHALL list them in `docs/tables.md` FILE_TYPES table

### Requirement 2: Validation Script Compliance

**User Story:** As a documentation maintainer, I want all documentation to pass the existing validation script, so that documentation quality is automatically enforced.

#### Acceptance Criteria

1. THE Documentation_System SHALL pass all heading hierarchy validations (Property 1 in validate_docs.py)
2. THE Documentation_System SHALL pass all table syntax validations (Property 2 in validate_docs.py)
3. THE Documentation_System SHALL pass all code block language identifier validations (Property 3 in validate_docs.py)
4. THE Documentation_System SHALL pass all entry field completeness validations (Property 4 in validate_docs.py)
5. THE Documentation_System SHALL pass all SID naming convention validations (Property 5 in validate_docs.py)
6. THE Documentation_System SHALL pass all cross-reference consistency validations (Property 6 in validate_docs.py)
7. THE Documentation_System SHALL pass all flag prefix convention validations (Property 7 in validate_docs.py)
8. THE Documentation_System SHALL pass all example coverage validations (Property 8 in validate_docs.py)

### Requirement 3: Cross-Reference Integrity

**User Story:** As an agent consuming documentation, I want all cross-references between documents to be valid and consistent, so that I can navigate the documentation reliably.

#### Acceptance Criteria

1. WHEN a document references another document, THE Documentation_System SHALL use valid relative paths that resolve correctly
2. WHEN a document references an identifier (command, error code, state), THE Documentation_System SHALL ensure that identifier is defined in `docs/tables.md`
3. WHEN `docs/tables.md` defines an identifier, THE Documentation_System SHALL ensure all other documents use that exact identifier
4. FOR ALL error codes referenced in any document, THE Documentation_System SHALL ensure they match entries in the ERRORS table
5. FOR ALL commands referenced in any document, THE Documentation_System SHALL ensure they match entries in the COMMANDS table

### Requirement 4: API Documentation Accuracy

**User Story:** As a developer implementing the CLI, I want API documentation that matches the actual function signatures, so that I can implement commands correctly.

#### Acceptance Criteria

1. WHEN a command function exists in `vince/commands/`, THE Documentation_System SHALL document it in `docs/api.md` with matching parameter names and types
2. WHEN a command accepts extension flags, THE Documentation_System SHALL list all supported extensions matching `SUPPORTED_EXTENSIONS` in source code
3. WHEN a command raises an exception, THE Documentation_System SHALL document that exception with the correct error code
4. FOR ALL Typer Option/Argument decorators in source code, THE Documentation_System SHALL document matching parameter definitions
5. WHEN a command has verbose output behavior, THE Documentation_System SHALL document the verbose output pattern

### Requirement 5: Schema Documentation Accuracy

**User Story:** As a developer working with data persistence, I want schema documentation that matches the actual JSON structures, so that I can correctly read and write data files.

#### Acceptance Criteria

1. WHEN `DefaultsStore` defines a field, THE Documentation_System SHALL document that field in `docs/schemas.md` DefaultEntry schema
2. WHEN `OffersStore` defines a field, THE Documentation_System SHALL document that field in `docs/schemas.md` OfferEntry schema
3. FOR ALL state values used in persistence code, THE Documentation_System SHALL document them as valid enum values in schemas
4. WHEN a timestamp field is used in persistence, THE Documentation_System SHALL document it with ISO 8601 format specification
5. FOR ALL required fields in persistence code, THE Documentation_System SHALL mark them as required in schema documentation

### Requirement 6: State Machine Documentation Accuracy

**User Story:** As a developer implementing state transitions, I want state machine documentation that matches the actual transition logic, so that I can implement correct state handling.

#### Acceptance Criteria

1. FOR ALL states in `DefaultState` enum, THE Documentation_System SHALL document them in `docs/states.md` with matching names and descriptions
2. FOR ALL states in `OfferState` enum, THE Documentation_System SHALL document them in `docs/states.md` with matching names and descriptions
3. FOR ALL valid transitions in `VALID_TRANSITIONS` dictionaries, THE Documentation_System SHALL document them with matching from/to states
4. WHEN a transition raises a specific error, THE Documentation_System SHALL document that error code for the invalid transition
5. FOR ALL state diagrams in documentation, THE Documentation_System SHALL ensure they match the `VALID_TRANSITIONS` definitions

### Requirement 7: Example Documentation Completeness

**User Story:** As a user learning the CLI, I want examples for all commands that demonstrate actual working usage, so that I can learn by example.

#### Acceptance Criteria

1. FOR ALL commands in the COMMANDS table, THE Documentation_System SHALL provide at least one example in `docs/examples.md`
2. WHEN an example uses a flag, THE Documentation_System SHALL use the correct flag syntax matching the source code
3. WHEN an example shows output, THE Documentation_System SHALL show output matching the actual Rich console formatting
4. FOR ALL QOL flags, THE Documentation_System SHALL provide examples showing their usage with commands
5. FOR ALL extension flags, THE Documentation_System SHALL provide at least one example per extension type

### Requirement 8: Tables.md as Single Source of Truth

**User Story:** As an agent, I want `docs/tables.md` to be the authoritative reference for all identifiers, so that I have one place to look up definitions.

#### Acceptance Criteria

1. THE Documentation_System SHALL define all commands in the COMMANDS table with id, sid, rid, and description
2. THE Documentation_System SHALL define all file types in the FILE_TYPES table with id, full_id, ext, sid, flag_short, and flag_long
3. THE Documentation_System SHALL define all error codes in the ERRORS table with code, sid, category, message, and severity
4. THE Documentation_System SHALL define all states in the STATES table with id, sid, entity, and description
5. THE Documentation_System SHALL define all config options in the CONFIG_OPTIONS table with key, sid, type, default, and description
6. FOR ALL tables, THE Documentation_System SHALL ensure no duplicate sid values exist

### Requirement 9: Validation Pattern Documentation

**User Story:** As a developer implementing validation, I want validation documentation that matches the actual regex patterns and rules, so that I can implement correct validation.

#### Acceptance Criteria

1. WHEN `EXTENSION_PATTERN` is defined in source code, THE Documentation_System SHALL document the exact regex pattern
2. WHEN `OFFER_ID_PATTERN` is defined in source code, THE Documentation_System SHALL document the exact regex pattern
3. FOR ALL reserved names in `RESERVED_NAMES`, THE Documentation_System SHALL list them in the validation documentation
4. WHEN path validation checks are performed, THE Documentation_System SHALL document each check with its corresponding error code
5. FOR ALL validation functions, THE Documentation_System SHALL document the error codes they can raise

### Requirement 10: Agent-Optimized Documentation Structure

**User Story:** As an agent consuming documentation, I want documentation structured for efficient context retrieval, so that I can quickly find relevant information.

#### Acceptance Criteria

1. THE Documentation_System SHALL use consistent heading hierarchy (H1 → H2 → H3) across all documents
2. THE Documentation_System SHALL include cross-reference sections at the end of each document linking to related documents
3. THE Documentation_System SHALL use code blocks with language identifiers for all code examples
4. THE Documentation_System SHALL use tables for structured data that agents can parse
5. THE Documentation_System SHALL include NOTE callouts for important contextual information
6. FOR ALL documents, THE Documentation_System SHALL include an Overview section explaining the document's purpose

