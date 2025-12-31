# Design Document: Documentation Unification

## Overview

This design document specifies the architecture and implementation approach for unifying the vince CLI documentation with the current source code implementation. The goal is to create a living documentation framework that serves as the authoritative reference for both human developers and AI agents.

The unification process involves:
1. Auditing current documentation against source code
2. Updating documentation to match implementation
3. Ensuring all validation rules pass
4. Establishing bidirectional traceability

## Architecture

### Documentation Structure

The documentation system follows a hierarchical structure with `docs/tables.md` as the Single Source of Truth (SSOT):

```
docs/
├── README.md          # Entry point, links to all docs
├── tables.md          # SSOT: All definitions, identifiers, tables
├── overview.md        # System design, commands, flags, rules
├── api.md             # Python interface specifications
├── schemas.md         # JSON schema definitions
├── errors.md          # Error catalog with codes and recovery
├── states.md          # State machine documentation
├── config.md          # Configuration options and hierarchy
├── testing.md         # Testing patterns and fixtures
└── examples.md        # Usage examples for all commands
```

### Validation Pipeline

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Source Code    │────►│  Extraction     │────►│  Comparison     │
│  (vince/)       │     │  Scripts        │     │  Engine         │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                        │
                                                        ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Documentation  │◄────│  Update         │◄────│  Gap Analysis   │
│  (docs/)        │     │  Generator      │     │  Report         │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

### Cross-Reference System

All identifiers follow the ID system convention:

| Type | Format | Example | Usage |
|------|--------|---------|-------|
| `id` | Full name | `application` | Human-readable documentation |
| `sid` | 2-4 chars | `app` | Tables, internal references |
| `rid` | `{sid}{num}` | `app01` | Rule identifiers |

## Components and Interfaces

### Source Code Extractors

#### Error Extractor

Extracts error classes from `vince/errors.py`:

```python
def extract_errors(source_path: Path) -> list[ErrorDefinition]:
    """Extract all VinceError subclasses with their codes and messages.
    
    Returns:
        List of ErrorDefinition with code, message_template, recovery
    """
```

#### State Extractor

Extracts state machines from `vince/state/`:

```python
def extract_states(state_module: Path) -> StateDefinition:
    """Extract state enum and valid transitions.
    
    Returns:
        StateDefinition with states list and transitions dict
    """
```

#### Validation Pattern Extractor

Extracts validation patterns from `vince/validation/`:

```python
def extract_validation_patterns(validation_path: Path) -> dict[str, str]:
    """Extract regex patterns and constants.
    
    Returns:
        Dict mapping pattern name to regex string
    """
```

### Documentation Parsers

#### Table Parser

Parses markdown tables from documentation:

```python
def parse_table(content: str, table_name: str) -> list[dict[str, str]]:
    """Parse a named table from markdown content.
    
    Returns:
        List of row dictionaries with column headers as keys
    """
```

#### Cross-Reference Parser

Extracts cross-references from documentation:

```python
def extract_references(content: str) -> list[Reference]:
    """Extract all cross-references from markdown.
    
    Returns:
        List of Reference objects with type, target, line_number
    """
```

### Comparison Engine

#### Synchronization Checker

```python
def check_sync(source_data: SourceData, doc_data: DocData) -> SyncReport:
    """Compare source code data against documentation.
    
    Returns:
        SyncReport with matches, mismatches, missing items
    """
```

## Data Models

### ErrorDefinition

```python
@dataclass
class ErrorDefinition:
    code: str           # e.g., "VE101"
    class_name: str     # e.g., "InvalidPathError"
    message_template: str
    recovery: Optional[str]
    category: str       # Derived from code range
```

### StateDefinition

```python
@dataclass
class StateDefinition:
    entity: str         # "default" or "offer"
    states: list[str]   # ["none", "pending", "active", "removed"]
    transitions: dict[str, set[str]]  # from_state -> to_states
```

### SyncReport

```python
@dataclass
class SyncReport:
    matches: list[str]      # Items that match
    mismatches: list[Mismatch]  # Items with differences
    missing_in_docs: list[str]  # In source, not in docs
    missing_in_source: list[str]  # In docs, not in source
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Source-Documentation Synchronization

*For any* validation function, error class, state, or configuration option defined in source code, the documentation system SHALL contain a corresponding entry with matching attributes.

**Validates: Requirements 1.1, 1.2, 1.3, 1.4, 1.5**

### Property 2: Validation Script Compliance

*For any* documentation file in the docs/ directory, running the complete validation script SHALL produce zero errors.

**Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8**

### Property 3: Cross-Reference Integrity

*For any* cross-reference in the documentation (document links, identifier references, error codes, commands), the referenced target SHALL exist and match the definition in tables.md.

**Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5**

### Property 4: API Documentation Completeness

*For any* command function in vince/commands/, the api.md documentation SHALL contain matching parameter definitions with correct names, types, and supported extensions.

**Validates: Requirements 4.1, 4.2, 4.4**

### Property 5: Schema Documentation Accuracy

*For any* field defined in DefaultsStore or OffersStore, the schemas.md documentation SHALL contain that field with matching type, required status, and format specification.

**Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5**

### Property 6: State Machine Documentation Accuracy

*For any* state in DefaultState or OfferState enums, and *for any* valid transition in VALID_TRANSITIONS, the states.md documentation SHALL contain matching state definitions and transition diagrams.

**Validates: Requirements 6.1, 6.2, 6.3, 6.5**

### Property 7: Example Coverage

*For any* command in the COMMANDS table, examples.md SHALL contain at least one example demonstrating that command with correct flag syntax.

**Validates: Requirements 7.1, 7.2, 7.4, 7.5**

### Property 8: Tables.md Completeness

*For any* table in tables.md (COMMANDS, FILE_TYPES, ERRORS, STATES, CONFIG_OPTIONS), all required columns SHALL be present, all entries SHALL have non-empty values, and no duplicate sid values SHALL exist.

**Validates: Requirements 8.1, 8.2, 8.3, 8.4, 8.5, 8.6**

### Property 9: Validation Pattern Documentation

*For any* regex pattern constant (EXTENSION_PATTERN, OFFER_ID_PATTERN) or reserved name set (RESERVED_NAMES) in source code, the documentation SHALL contain the exact matching value.

**Validates: Requirements 9.1, 9.2, 9.3, 9.4, 9.5**

### Property 10: Document Structure Consistency

*For any* document in docs/, it SHALL have an Overview section and a Cross-References section linking to related documents.

**Validates: Requirements 10.2, 10.6**

## Error Handling

### Documentation Update Errors

| Error Condition | Handling Strategy |
|-----------------|-------------------|
| Source file not found | Skip with warning, continue processing |
| Parse error in source | Log error with line number, skip file |
| Invalid markdown syntax | Report via validation script |
| Missing required field | Add placeholder with TODO marker |

### Validation Errors

All validation errors are reported through the existing `validate_docs.py` framework:

```python
@dataclass
class ValidationError:
    file: str
    line: Optional[int]
    rule: str
    message: str
    severity: str  # "error" or "warning"
```

## Testing Strategy

### Unit Tests

Unit tests verify specific extraction and parsing functions:

- Error class extraction from Python source
- State enum and transition extraction
- Markdown table parsing
- Cross-reference extraction

### Property-Based Tests

Property-based tests using Hypothesis verify universal properties:

| Property | Generator | Iterations |
|----------|-----------|------------|
| Source-Doc Sync | Source code extractors | 100 |
| Validation Compliance | All doc files | 100 |
| Cross-Reference Integrity | All references | 100 |
| Tables Completeness | All table rows | 100 |

### Integration Tests

Integration tests verify end-to-end documentation validation:

1. Run full validation script on docs/
2. Verify zero errors returned
3. Verify all properties checked

### Test Configuration

```python
# pytest configuration for property tests
@settings(max_examples=100, deadline=None)
@given(doc_file=st.sampled_from(DOC_FILES))
def test_validation_compliance(doc_file):
    """Property 2: All docs pass validation."""
    result = validate_file(doc_file)
    assert result.is_valid
```

## Implementation Phases

### Phase 1: Gap Analysis

1. Run existing validation script to identify current errors
2. Extract all definitions from source code
3. Compare against documentation
4. Generate gap report

### Phase 2: Tables.md Update

1. Update COMMANDS table with all 7 commands
2. Update FILE_TYPES table with all 12 extensions
3. Update ERRORS table with all 15 error codes
4. Update STATES table with all 8 states
5. Update CONFIG_OPTIONS table with all 7 options
6. Verify no duplicate sids

### Phase 3: Core Documentation Update

1. Update api.md with accurate function signatures
2. Update schemas.md with accurate field definitions
3. Update states.md with accurate transitions
4. Update errors.md with accurate error catalog
5. Update config.md with accurate options

### Phase 4: Supporting Documentation Update

1. Update overview.md with accurate validation patterns
2. Update examples.md with examples for all commands
3. Update testing.md with current test patterns
4. Update README.md with accurate links

### Phase 5: Validation and Verification

1. Run full validation script
2. Run property-based tests
3. Fix any remaining issues
4. Final review

## Cross-References

- See [requirements.md](requirements.md) for detailed acceptance criteria
- See [tasks.md](tasks.md) for implementation task list
- See `validate_docs.py` for validation implementation
- See `docs/tables.md` for Single Source of Truth
