# Requirements Document

## Introduction

This specification defines comprehensive end-to-end testing requirements for the vince CLI application. The testing strategy validates all 8 commands (slap, chop, set, forget, offer, reject, list, sync), all 21 error codes (VE101-VE606), all state machine transitions, and all command parameter combinations.

The testing approach combines:
- Unit tests for isolated component behavior
- Property-based tests (Hypothesis) for universal properties across generated inputs
- Integration tests for multi-command workflows
- Error condition tests for all documented error codes

## Glossary

- **CLI_Runner**: Typer's CliRunner for invoking commands programmatically in tests
- **Property_Test**: A test using Hypothesis to verify properties across many generated inputs (minimum 100 iterations)
- **Integration_Test**: A test that exercises multiple components working together
- **Fixture**: Pytest fixture providing test setup and teardown
- **Mock_Handler**: A mock platform handler for testing OS integration without actual OS changes
- **Dry_Run**: Command execution mode that previews changes without applying them
- **DefaultState**: Enum with values NONE, PENDING, ACTIVE, REMOVED
- **OfferState**: Enum with values NONE, CREATED, ACTIVE, REJECTED
- **VALID_TRANSITIONS**: Dictionary mapping current state to set of valid target states
- **Generator**: Hypothesis strategy for generating test data

## Requirements

### Requirement 1: Input Error Testing (VE1xx)

**User Story:** As a developer, I want comprehensive tests for all input validation errors, so that I can verify the CLI correctly rejects invalid inputs.

#### Acceptance Criteria

1. WHEN a non-existent path is provided to slap command, THE Test_Suite SHALL verify VE101 InvalidPathError is raised with message containing the path
2. WHEN a non-existent path is provided to set command, THE Test_Suite SHALL verify VE101 InvalidPathError is raised
3. WHEN a non-existent path is provided to offer command, THE Test_Suite SHALL verify VE101 InvalidPathError is raised
4. WHEN an unsupported extension is provided (e.g., .exe, .dll, .so), THE Test_Suite SHALL verify VE102 InvalidExtensionError is raised
5. WHEN no extension flag is provided to slap/set/chop/forget, THE Test_Suite SHALL verify VE102 InvalidExtensionError is raised
6. WHEN an offer_id starting with a number is provided, THE Test_Suite SHALL verify VE103 InvalidOfferIdError is raised
7. WHEN an offer_id starting with uppercase is provided, THE Test_Suite SHALL verify VE103 InvalidOfferIdError is raised
8. WHEN an offer_id containing spaces is provided, THE Test_Suite SHALL verify VE103 InvalidOfferIdError is raised
9. WHEN an offer_id longer than 32 characters is provided, THE Test_Suite SHALL verify VE103 InvalidOfferIdError is raised
10. WHEN a reserved name (help, version, list, all, none, default) is used as offer_id, THE Test_Suite SHALL verify VE103 InvalidOfferIdError is raised
11. WHEN reject is called with a non-existent offer_id, THE Test_Suite SHALL verify VE104 OfferNotFoundError is raised
12. WHEN list is called with an invalid subsection flag, THE Test_Suite SHALL verify VE105 InvalidSubsectionError is raised

### Requirement 2: File Error Testing (VE2xx)

**User Story:** As a developer, I want comprehensive tests for all file system errors, so that I can verify the CLI handles file errors gracefully.

#### Acceptance Criteria

1. WHEN defaults.json is missing and a read operation is attempted, THE Test_Suite SHALL verify the system creates a new file with default schema
2. WHEN offers.json is missing and a read operation is attempted, THE Test_Suite SHALL verify the system creates a new file with default schema
3. WHEN a file has insufficient permissions, THE Test_Suite SHALL verify VE202 PermissionDeniedError is raised
4. WHEN defaults.json contains invalid JSON syntax, THE Test_Suite SHALL verify VE203 DataCorruptedError is raised
5. WHEN defaults.json contains invalid schema (wrong state value), THE Test_Suite SHALL verify VE203 DataCorruptedError is raised
6. WHEN defaults.json contains invalid schema (missing required field), THE Test_Suite SHALL verify VE203 DataCorruptedError is raised
7. WHEN offers.json contains invalid JSON syntax, THE Test_Suite SHALL verify VE203 DataCorruptedError is raised
8. WHEN offers.json contains invalid schema (invalid offer_id pattern), THE Test_Suite SHALL verify VE203 DataCorruptedError is raised

### Requirement 3: State Error Testing (VE3xx)

**User Story:** As a developer, I want comprehensive tests for all state transition errors, so that I can verify the CLI enforces state machine rules.

#### Acceptance Criteria

1. WHEN slap is called for an extension with an active default, THE Test_Suite SHALL verify VE301 DefaultExistsError is raised
2. WHEN set is called for an extension with an active default, THE Test_Suite SHALL verify VE301 DefaultExistsError is raised
3. WHEN chop is called for an extension with no default, THE Test_Suite SHALL verify VE302 NoDefaultError is raised
4. WHEN forget is called for an extension with no default, THE Test_Suite SHALL verify VE302 NoDefaultError is raised
5. WHEN offer is called with an offer_id that already exists, THE Test_Suite SHALL verify VE303 OfferExistsError is raised
6. WHEN reject is called on an active offer that is in use, THE Test_Suite SHALL verify VE304 OfferInUseError is raised

### Requirement 4: Config Error Testing (VE4xx)

**User Story:** As a developer, I want comprehensive tests for all configuration errors, so that I can verify the CLI handles config errors correctly.

#### Acceptance Criteria

1. WHEN config.json contains an unknown option, THE Test_Suite SHALL verify VE401 InvalidConfigOptionError is raised
2. WHEN config.json contains an invalid color_theme value, THE Test_Suite SHALL verify VE401 InvalidConfigOptionError is raised
3. WHEN config.json contains max_backups outside range 0-100, THE Test_Suite SHALL verify VE401 InvalidConfigOptionError is raised
4. WHEN config.json contains invalid JSON syntax, THE Test_Suite SHALL verify VE402 ConfigMalformedError is raised

### Requirement 5: OS Integration Error Testing (VE6xx)

**User Story:** As a developer, I want comprehensive tests for all OS integration errors, so that I can verify the CLI handles platform errors correctly.

#### Acceptance Criteria

1. WHEN running on an unsupported platform (Linux), THE Test_Suite SHALL verify VE601 UnsupportedPlatformError is raised
2. WHEN a macOS app bundle has no CFBundleIdentifier, THE Test_Suite SHALL verify VE602 BundleIdNotFoundError is raised
3. WHEN Windows registry access is denied, THE Test_Suite SHALL verify VE603 RegistryAccessError is raised
4. WHEN an application path is invalid or not executable, THE Test_Suite SHALL verify VE604 ApplicationNotFoundError is raised
5. WHEN an OS operation fails for other reasons, THE Test_Suite SHALL verify VE605 OSOperationError is raised
6. WHEN sync completes with partial failures, THE Test_Suite SHALL verify VE606 SyncPartialError is raised with correct counts

### Requirement 6: Default State Machine Property Testing

**User Story:** As a developer, I want property-based tests for all default state transitions, so that I can verify the state machine is correct for all inputs.

#### Acceptance Criteria

1. FOR ALL valid transitions in VALID_TRANSITIONS (none→pending, none→active, pending→active, pending→none, active→removed, removed→active), THE Test_Suite SHALL verify validate_transition succeeds
2. FOR ALL extensions in SUPPORTED_EXTENSIONS, THE Test_Suite SHALL verify none→removed raises NoDefaultError (VE302)
3. FOR ALL extensions in SUPPORTED_EXTENSIONS, THE Test_Suite SHALL verify active→active raises DefaultExistsError (VE301)
4. FOR ALL extensions in SUPPORTED_EXTENSIONS, THE Test_Suite SHALL verify active→pending raises DefaultExistsError (VE301)
5. FOR ALL extensions in SUPPORTED_EXTENSIONS, THE Test_Suite SHALL verify pending→removed raises InvalidTransitionError
6. FOR ALL extensions in SUPPORTED_EXTENSIONS, THE Test_Suite SHALL verify removed→pending raises InvalidTransitionError
7. FOR ALL extensions in SUPPORTED_EXTENSIONS, THE Test_Suite SHALL verify removed→none raises InvalidTransitionError
8. THE Test_Suite SHALL use Hypothesis with minimum 100 examples per property test

### Requirement 7: Offer State Machine Property Testing

**User Story:** As a developer, I want property-based tests for all offer state transitions, so that I can verify the offer state machine is correct for all inputs.

#### Acceptance Criteria

1. FOR ALL valid transitions in OFFER_VALID_TRANSITIONS (none→created, created→active, created→rejected, active→rejected), THE Test_Suite SHALL verify validate_transition succeeds
2. FOR ALL valid offer_ids, THE Test_Suite SHALL verify none→rejected raises OfferNotFoundError (VE104)
3. FOR ALL valid offer_ids, THE Test_Suite SHALL verify created→created raises OfferExistsError (VE303)
4. FOR ALL valid offer_ids, THE Test_Suite SHALL verify active→created raises OfferExistsError (VE303)
5. FOR ALL valid offer_ids, THE Test_Suite SHALL verify active→rejected with in_use=True raises OfferInUseError (VE304)
6. FOR ALL valid offer_ids, THE Test_Suite SHALL verify active→rejected with in_use=False succeeds
7. FOR ALL target states, THE Test_Suite SHALL verify rejected→target raises InvalidOfferTransitionError (terminal state)
8. FOR ALL valid offer_ids, THE Test_Suite SHALL verify none→active raises InvalidOfferTransitionError
9. THE Test_Suite SHALL use Hypothesis with minimum 100 examples per property test

### Requirement 8: Slap Command Comprehensive Testing

**User Story:** As a developer, I want comprehensive tests for the slap command, so that I can verify all parameter combinations work correctly.

#### Acceptance Criteria

1. WHEN slap is called with valid path and --md flag, THE Test_Suite SHALL verify a pending default is created
2. WHEN slap is called with valid path and -set flag, THE Test_Suite SHALL verify an active default is created
3. WHEN slap is called with -set flag, THE Test_Suite SHALL verify an offer is auto-created with auto_created=True
4. WHEN slap is called with -dry flag, THE Test_Suite SHALL verify no changes are made to defaults.json
5. WHEN slap is called with -dry flag, THE Test_Suite SHALL verify no OS changes are made
6. WHEN slap is called with -vb flag, THE Test_Suite SHALL verify verbose output includes path and state information
7. FOR ALL 12 supported extensions (md, py, txt, js, html, css, json, yml, yaml, xml, csv, sql), THE Test_Suite SHALL verify slap creates correct default
8. WHEN slap is called with multiple extension flags, THE Test_Suite SHALL verify first flag wins
9. WHEN slap is called on a removed default, THE Test_Suite SHALL verify it can be re-activated with -set

### Requirement 9: Chop Command Comprehensive Testing

**User Story:** As a developer, I want comprehensive tests for the chop command, so that I can verify all parameter combinations work correctly.

#### Acceptance Criteria

1. WHEN chop is called with -forget flag on a pending default, THE Test_Suite SHALL verify the default is removed (state→none)
2. WHEN chop is called with -forget flag on an active default, THE Test_Suite SHALL verify the default is marked removed (state→removed)
3. WHEN chop is called without -forget flag, THE Test_Suite SHALL verify the default info is displayed without state change
4. WHEN chop is called with -dry flag, THE Test_Suite SHALL verify no changes are made to defaults.json
5. WHEN chop is called with -vb flag, THE Test_Suite SHALL verify verbose output includes extension and state information
6. FOR ALL 12 supported extensions, THE Test_Suite SHALL verify chop works correctly

### Requirement 10: Set Command Comprehensive Testing

**User Story:** As a developer, I want comprehensive tests for the set command, so that I can verify all parameter combinations work correctly.

#### Acceptance Criteria

1. WHEN set is called with valid path and extension, THE Test_Suite SHALL verify an active default is created
2. WHEN set is called on a removed default, THE Test_Suite SHALL verify the default is re-activated (removed→active)
3. WHEN set is called with -dry flag, THE Test_Suite SHALL verify no changes are made to defaults.json
4. WHEN set is called with -vb flag, THE Test_Suite SHALL verify verbose output includes path and state information
5. FOR ALL 12 supported extensions, THE Test_Suite SHALL verify set creates correct default

### Requirement 11: Forget Command Comprehensive Testing

**User Story:** As a developer, I want comprehensive tests for the forget command, so that I can verify all parameter combinations work correctly.

#### Acceptance Criteria

1. WHEN forget is called on an active default, THE Test_Suite SHALL verify the default is marked removed (active→removed)
2. WHEN forget is called on a pending default, THE Test_Suite SHALL verify the default is removed (pending→none)
3. WHEN forget is called with -dry flag, THE Test_Suite SHALL verify no changes are made to defaults.json
4. WHEN forget is called with -vb flag, THE Test_Suite SHALL verify verbose output includes extension and state information
5. FOR ALL 12 supported extensions, THE Test_Suite SHALL verify forget works correctly

### Requirement 12: Offer Command Comprehensive Testing

**User Story:** As a developer, I want comprehensive tests for the offer command, so that I can verify all parameter combinations work correctly.

#### Acceptance Criteria

1. WHEN offer is called with valid offer_id, path, and extension, THE Test_Suite SHALL verify an offer is created with state=created
2. WHEN offer is called, THE Test_Suite SHALL verify the offer references the correct default_id
3. WHEN offer is called with -vb flag, THE Test_Suite SHALL verify verbose output includes offer_id and default information
4. FOR ALL valid offer_id patterns (lowercase, with hyphens, with underscores, with numbers after first char), THE Test_Suite SHALL verify offer creation succeeds
5. FOR ALL 12 supported extensions, THE Test_Suite SHALL verify offer works correctly

### Requirement 13: Reject Command Comprehensive Testing

**User Story:** As a developer, I want comprehensive tests for the reject command, so that I can verify all parameter combinations work correctly.

#### Acceptance Criteria

1. WHEN reject is called on a created offer, THE Test_Suite SHALL verify the offer state changes to rejected
2. WHEN reject is called on an active offer (not in use), THE Test_Suite SHALL verify the offer state changes to rejected
3. WHEN reject is called with -. flag, THE Test_Suite SHALL verify the offer is completely removed from offers.json
4. WHEN reject is called with -vb flag, THE Test_Suite SHALL verify verbose output includes offer_id and state information
5. WHEN reject is called on one offer, THE Test_Suite SHALL verify other offers are not affected

### Requirement 14: List Command Comprehensive Testing

**User Story:** As a developer, I want comprehensive tests for the list command, so that I can verify all subsection flags work correctly.

#### Acceptance Criteria

1. WHEN list is called with -app flag, THE Test_Suite SHALL verify applications are displayed
2. WHEN list is called with -cmd flag, THE Test_Suite SHALL verify commands are displayed
3. WHEN list is called with -ext flag, THE Test_Suite SHALL verify extensions are displayed
4. WHEN list is called with -def flag, THE Test_Suite SHALL verify defaults are displayed with OS default comparison
5. WHEN list is called with -off flag, THE Test_Suite SHALL verify offers are displayed (excluding rejected)
6. WHEN list is called with -all flag, THE Test_Suite SHALL verify all sections are displayed
7. WHEN list is called with extension filter (--md, --py, etc.), THE Test_Suite SHALL verify only matching entries are shown
8. WHEN list is called with -vb flag, THE Test_Suite SHALL verify verbose output includes additional details
9. WHEN list -def is called with no defaults, THE Test_Suite SHALL verify "No defaults found" message is shown
10. WHEN list -off is called with no offers, THE Test_Suite SHALL verify "No offers found" message is shown

### Requirement 15: Sync Command Comprehensive Testing

**User Story:** As a developer, I want comprehensive tests for the sync command, so that I can verify bulk synchronization works correctly.

#### Acceptance Criteria

1. WHEN sync is called with no active defaults, THE Test_Suite SHALL verify "No active defaults to sync" message is shown
2. WHEN sync is called with already-synced entries, THE Test_Suite SHALL verify entries are skipped with appropriate message
3. WHEN sync is called with out-of-sync entries, THE Test_Suite SHALL verify OS handler is called for each entry
4. WHEN sync is called with partial failures, THE Test_Suite SHALL verify VE606 is raised with correct succeeded/failed counts
5. WHEN sync is called with -dry flag, THE Test_Suite SHALL verify no OS changes are made
6. WHEN sync is called with -dry flag, THE Test_Suite SHALL verify preview output shows what would be changed
7. WHEN sync is called with -vb flag, THE Test_Suite SHALL verify verbose output includes per-extension details
8. WHEN sync succeeds, THE Test_Suite SHALL verify os_synced field is updated in defaults.json

### Requirement 16: Dry Run Idempotence Property Testing

**User Story:** As a developer, I want property-based tests for dry run mode, so that I can verify dry run never modifies state.

#### Acceptance Criteria

1. FOR ALL commands supporting -dry flag (slap, chop, set, forget, sync), THE Test_Suite SHALL verify defaults.json is unchanged after dry run
2. FOR ALL commands supporting -dry flag, THE Test_Suite SHALL verify offers.json is unchanged after dry run
3. FOR ALL commands supporting -dry flag, THE Test_Suite SHALL verify running dry run twice produces identical output
4. THE Test_Suite SHALL use Hypothesis with minimum 100 examples per property test

### Requirement 17: Persistence Round-Trip Property Testing

**User Story:** As a developer, I want property-based tests for data persistence, so that I can verify data integrity across save/load cycles.

#### Acceptance Criteria

1. FOR ALL valid DefaultEntry objects, THE Test_Suite SHALL verify save then load returns equivalent data
2. FOR ALL valid OfferEntry objects, THE Test_Suite SHALL verify save then load returns equivalent data
3. FOR ALL valid extensions and application paths, THE Test_Suite SHALL verify DefaultsStore.add then find_by_extension returns the added entry
4. FOR ALL valid offer_ids, THE Test_Suite SHALL verify OffersStore.add then find_by_id returns the added entry
5. THE Test_Suite SHALL use Hypothesis with minimum 100 examples per property test

### Requirement 18: Backup Retention Property Testing

**User Story:** As a developer, I want property-based tests for backup retention, so that I can verify backup limits are enforced.

#### Acceptance Criteria

1. FOR ALL combinations of num_writes (1-10) and max_backups (1-5), THE Test_Suite SHALL verify backup count never exceeds max_backups
2. FOR ALL backup operations, THE Test_Suite SHALL verify oldest backups are deleted first when limit is exceeded
3. WHEN backup_enabled=False, THE Test_Suite SHALL verify no backups are created
4. THE Test_Suite SHALL use Hypothesis with minimum 100 examples per property test

### Requirement 19: Command Interaction Integration Testing

**User Story:** As a developer, I want integration tests for command sequences, so that I can verify commands work correctly together.

#### Acceptance Criteria

1. THE Test_Suite SHALL test slap → list -def → chop -forget workflow with state verification at each step
2. THE Test_Suite SHALL test slap -set → list -off → reject workflow with state verification at each step
3. THE Test_Suite SHALL test offer → list -off → reject workflow with state verification at each step
4. THE Test_Suite SHALL test set → forget → set workflow (re-activation) with state verification at each step
5. THE Test_Suite SHALL test slap → offer → reject → chop workflow with state verification at each step
6. THE Test_Suite SHALL test multiple slap -set → sync workflow with OS handler verification
7. WHEN a command modifies state, THE Test_Suite SHALL verify subsequent commands see the updated state

### Requirement 20: Platform Handler Mock Testing

**User Story:** As a developer, I want tests using mock platform handlers, so that I can verify OS integration without actual OS changes.

#### Acceptance Criteria

1. THE Test_Suite SHALL provide a MockPlatformHandler implementing the PlatformHandler protocol
2. THE Test_Suite SHALL verify slap -set calls handler.set_default with correct extension and path
3. THE Test_Suite SHALL verify set calls handler.set_default with correct extension and path
4. THE Test_Suite SHALL verify chop -forget calls handler.remove_default with correct extension
5. THE Test_Suite SHALL verify forget calls handler.remove_default with correct extension
6. THE Test_Suite SHALL verify sync calls handler.set_default for each active default
7. WHEN handler.set_default returns failure, THE Test_Suite SHALL verify command warns but succeeds
8. THE Test_Suite SHALL verify list -def calls handler.get_current_default for OS comparison

### Requirement 21: Validation Function Property Testing

**User Story:** As a developer, I want property-based tests for validation functions, so that I can verify validation is correct for all inputs.

#### Acceptance Criteria

1. FOR ALL paths generated by valid_application_paths strategy, THE Test_Suite SHALL verify validate_path behavior
2. FOR ALL extensions in SUPPORTED_EXTENSIONS, THE Test_Suite SHALL verify validate_extension returns the extension
3. FOR ALL extensions generated by unsupported_extensions strategy, THE Test_Suite SHALL verify validate_extension raises VE102
4. FOR ALL offer_ids generated by valid_offer_ids strategy, THE Test_Suite SHALL verify validate_offer_id returns the offer_id
5. FOR ALL offer_ids generated by invalid_pattern_offer_ids strategy, THE Test_Suite SHALL verify validate_offer_id raises VE103
6. FOR ALL reserved names, THE Test_Suite SHALL verify validate_offer_id raises VE103
7. THE Test_Suite SHALL use Hypothesis with minimum 100 examples per property test

### Requirement 22: Error Message Consistency Testing

**User Story:** As a developer, I want tests verifying error messages match documentation, so that I can ensure consistent user experience.

#### Acceptance Criteria

1. FOR ALL error codes VE101-VE606, THE Test_Suite SHALL verify the error message matches the template in docs/errors.md
2. FOR ALL error codes, THE Test_Suite SHALL verify the recovery message is present and actionable
3. FOR ALL error codes, THE Test_Suite SHALL verify the error code format matches VE{category}{number} pattern
4. THE Test_Suite SHALL verify error codes are in correct category ranges (VE1xx=Input, VE2xx=File, VE3xx=State, VE4xx=Config, VE5xx=System, VE6xx=OS)

### Requirement 23: Verbose Output Consistency Testing

**User Story:** As a developer, I want tests verifying verbose output is consistent, so that I can ensure useful debugging information.

#### Acceptance Criteria

1. FOR ALL commands supporting -vb flag, THE Test_Suite SHALL verify additional output is produced when flag is set
2. FOR ALL commands supporting -vb flag, THE Test_Suite SHALL verify no verbose output when flag is not set
3. WHEN -vb flag is set, THE Test_Suite SHALL verify output includes operation details (path, extension, state)
4. WHEN -vb flag is set, THE Test_Suite SHALL verify output uses Rich formatting (colors, icons)

### Requirement 24: Schema Migration Testing

**User Story:** As a developer, I want tests for schema migration, so that I can verify data files are upgraded correctly.

#### Acceptance Criteria

1. WHEN defaults.json has version 1.0.0 and is missing os_synced field, THE Test_Suite SHALL verify migration adds the field
2. WHEN offers.json has version 1.0.0, THE Test_Suite SHALL verify migration to 1.1.0 succeeds
3. WHEN a data file has an unknown future version, THE Test_Suite SHALL verify appropriate error handling
4. THE Test_Suite SHALL verify migration preserves all existing data

