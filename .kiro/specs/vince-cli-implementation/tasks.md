# Implementation Plan: Vince CLI Implementation

## Overview

This implementation plan creates the vince CLI Python application following the design document. The approach builds components incrementally: project setup → errors → validation → persistence → state → config → output → commands → tests.

## Tasks

- [x] 1. Set up project structure and entry point
  - [x] 1.1 Create pyproject.toml with dependencies
    - Add typer>=0.9.0, rich>=13.0.0 as dependencies
    - Add pytest, hypothesis, pytest-cov as dev dependencies
    - Configure project scripts entry point
    - _Requirements: 1.1_

  - [x] 1.2 Create vince package structure
    - Create vince/__init__.py with __version__
    - Create vince/main.py with Typer app initialization
    - Create empty command, validation, persistence, state, output directories
    - _Requirements: 1.2, 1.3_

  - [x] 1.3 Implement basic CLI entry point
    - Initialize Typer app with name="vince" and rich_markup_mode="rich"
    - Add --help and --version support
    - _Requirements: 1.3, 1.4, 1.5_

- [x] 2. Checkpoint - Verify project setup
  - Run `uv run python -m vince --help` and verify output
  - Ensure all tests pass, ask the user if questions arise.

- [x] 3. Implement error system
  - [x] 3.1 Create VinceError base class
    - Create vince/errors.py with VinceError dataclass
    - Add code, message, recovery fields
    - Implement __str__ method
    - _Requirements: 2.1_

  - [x] 3.2 Implement Input errors (VE1xx)
    - Add InvalidPathError (VE101)
    - Add InvalidExtensionError (VE102)
    - Add InvalidOfferIdError (VE103)
    - Add OfferNotFoundError (VE104)
    - Add InvalidSubsectionError (VE105)
    - _Requirements: 2.3_

  - [x] 3.3 Implement File errors (VE2xx)
    - Add FileNotFoundError (VE201)
    - Add PermissionDeniedError (VE202)
    - Add DataCorruptedError (VE203)
    - _Requirements: 2.4_

  - [x] 3.4 Implement State errors (VE3xx)
    - Add DefaultExistsError (VE301)
    - Add NoDefaultError (VE302)
    - Add OfferExistsError (VE303)
    - Add OfferInUseError (VE304)
    - _Requirements: 2.5_

  - [x] 3.5 Implement Config and System errors (VE4xx, VE5xx)
    - Add InvalidConfigOptionError (VE401)
    - Add ConfigMalformedError (VE402)
    - Add UnexpectedError (VE501)
    - _Requirements: 2.6, 2.7_

  - [x] 3.6 Implement handle_error function
    - Display formatted error with Rich
    - Show recovery message if available
    - Exit with code 1
    - _Requirements: 2.8_

  - [x] 3.7 Write property test for error class completeness
    - **Property 12: Error Class Completeness**
    - Test all VinceError subclasses have required attributes
    - **Validates: Requirements 2.2**

- [x] 4. Checkpoint - Verify error system
  - Ensure all error classes are defined
  - Ensure all tests pass, ask the user if questions arise.

- [x] 5. Implement validation system
  - [x] 5.1 Implement path validator
    - Create vince/validation/path.py
    - Implement validate_path() with exists, is_file, executable checks
    - Raise InvalidPathError or PermissionDeniedError on failure
    - _Requirements: 3.1, 3.2, 3.3, 3.4_

  - [x] 5.2 Write property test for path validation
    - **Property 1: Path Validation Correctness**
    - Test valid paths pass, invalid paths raise correct errors
    - **Validates: Requirements 3.1, 3.2, 3.3, 3.4**

  - [x] 5.3 Implement extension validator
    - Create vince/validation/extension.py
    - Define EXTENSION_PATTERN and SUPPORTED_EXTENSIONS
    - Implement validate_extension() with pattern and support checks
    - Implement flag_to_extension() helper
    - _Requirements: 3.5, 3.6, 3.7_

  - [x] 5.4 Write property test for extension validation
    - **Property 2: Extension Validation Correctness**
    - Test valid extensions pass, invalid extensions raise errors
    - **Validates: Requirements 3.5, 3.6, 3.7**

  - [x] 5.5 Implement offer_id validator
    - Create vince/validation/offer_id.py
    - Define OFFER_ID_PATTERN and RESERVED_NAMES
    - Implement validate_offer_id() with pattern and reserved checks
    - _Requirements: 3.8, 3.9, 3.10_

  - [x] 5.6 Write property test for offer_id validation
    - **Property 3: Offer ID Validation Correctness**
    - Test valid offer_ids pass, invalid ones raise errors
    - **Validates: Requirements 3.8, 3.9, 3.10**

- [x] 6. Checkpoint - Verify validation system
  - Ensure all validators work correctly
  - Ensure all tests pass, ask the user if questions arise.

- [x] 7. Implement persistence layer
  - [x] 7.1 Implement base persistence functions
    - Create vince/persistence/base.py
    - Implement atomic_write() with temp file + rename
    - Implement file_lock() context manager with fcntl
    - Implement create_backup() with timestamp naming
    - Implement load_json() with default fallback
    - _Requirements: 4.1, 4.2, 4.3, 4.4_

  - [x] 7.2 Implement DefaultsStore
    - Create vince/persistence/defaults.py
    - Implement load(), save() methods
    - Implement find_by_extension() method
    - Implement add() method with entry creation
    - Implement update_state() method
    - _Requirements: 4.5, 4.6_

  - [x] 7.3 Write property test for DefaultsStore
    - **Property 5: DefaultsStore Add-Find Consistency**
    - Test add then find returns the entry
    - **Validates: Requirements 4.6**

  - [x] 7.4 Implement OffersStore
    - Create vince/persistence/offers.py
    - Implement load(), save() methods
    - Implement find_by_id() method
    - Implement add() method with entry creation
    - Implement update_state() method
    - _Requirements: 4.7, 4.8_

  - [x] 7.5 Write property test for OffersStore
    - **Property 6: OffersStore Add-Find Consistency**
    - Test add then find returns the entry
    - **Validates: Requirements 4.8**

  - [x] 7.6 Write property test for persistence round-trip
    - **Property 4: Persistence Round-Trip Consistency**
    - Test save then load returns equivalent data
    - **Validates: Requirements 4.1, 4.5, 4.7**

  - [x] 7.7 Write property test for backup retention
    - **Property 7: Backup Retention Limit**
    - Test backup count never exceeds max_backups
    - **Validates: Requirements 4.9, 4.10**

- [x] 8. Checkpoint - Verify persistence layer
  - Ensure stores work correctly
  - Ensure all tests pass, ask the user if questions arise.

- [x] 9. Implement state machines
  - [x] 9.1 Implement default state machine
    - Create vince/state/default_state.py
    - Define DefaultState enum (none, pending, active, removed)
    - Define VALID_TRANSITIONS mapping
    - Implement validate_transition() function
    - _Requirements: 5.1, 5.2, 5.3_

  - [x] 9.2 Write property test for default state transitions
    - **Property 8: Default State Transition Validity**
    - Test valid transitions succeed, invalid raise errors
    - **Validates: Requirements 5.2, 5.3**

  - [x] 9.3 Implement offer state machine
    - Create vince/state/offer_state.py
    - Define OfferState enum (none, created, active, rejected)
    - Define VALID_TRANSITIONS mapping
    - Implement validate_transition() function
    - _Requirements: 5.4, 5.5, 5.6_

  - [x] 9.4 Write property test for offer state transitions
    - **Property 9: Offer State Transition Validity**
    - Test valid transitions succeed, invalid raise errors
    - **Validates: Requirements 5.5, 5.6**

- [x] 10. Checkpoint - Verify state machines
  - Ensure state transitions work correctly
  - Ensure all tests pass, ask the user if questions arise.

- [x] 11. Implement configuration system
  - [x] 11.1 Implement config loader
    - Create vince/config.py
    - Define DEFAULT_CONFIG with all options
    - Implement get_config() with hierarchy loading
    - Implement config merging with precedence
    - _Requirements: 6.1, 6.2, 6.3, 6.4_

  - [x] 11.2 Write property test for config precedence
    - **Property 10: Config Precedence Correctness**
    - Test project > user > default precedence
    - **Validates: Requirements 6.2, 6.3, 6.4**

  - [x] 11.3 Implement config validation
    - Add JSON parsing error handling
    - Add config option validation
    - Raise appropriate errors (VE401, VE402)
    - _Requirements: 6.5, 6.6_

  - [x] 11.4 Write property test for config error handling
    - **Property 11: Config Error Handling**
    - Test malformed JSON raises VE402, invalid options raise VE401
    - **Validates: Requirements 6.5, 6.6**

- [x] 12. Checkpoint - Verify configuration system
  - Ensure config loading works correctly
  - Ensure all tests pass, ask the user if questions arise.

- [x] 13. Implement output system
  - [x] 13.1 Implement Rich theme
    - Create vince/output/theme.py
    - Define VINCE_THEME with all styles
    - Create themed console instance
    - _Requirements: 7.1_

  - [x] 13.2 Implement message functions
    - Create vince/output/messages.py
    - Implement print_success(), print_warning(), print_error(), print_info()
    - Use correct Rich markup formats
    - _Requirements: 7.2, 7.3, 7.4, 7.5_

  - [x] 13.3 Implement table functions
    - Create vince/output/tables.py
    - Implement create_defaults_table()
    - Implement create_offers_table()
    - _Requirements: 7.6, 7.7_

- [x] 14. Checkpoint - Verify output system
  - Ensure output formatting works correctly
  - Ensure all tests pass, ask the user if questions arise.

- [-] 15. Implement slap command
  - [ ] 15.1 Implement cmd_slap function
    - Create vince/commands/slap.py
    - Add path argument with Typer validation
    - Add extension option with all supported flags
    - Add -set and -vb flags
    - Implement command logic with validation, state check, persistence
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7_

  - [ ] 15.2 Register slap command
    - Import and register in main.py
    - _Requirements: 8.1_

  - [ ] 15.3 Write unit tests for slap command
    - Test successful slap without -set (pending state)
    - Test successful slap with -set (active state + offer)
    - Test error cases (invalid path, existing default)
    - _Requirements: 8.5, 8.6, 8.7_

- [ ] 16. Implement chop command
  - [ ] 16.1 Implement cmd_chop function
    - Create vince/commands/chop.py
    - Add extension option
    - Add -forget and -vb flags
    - Implement command logic
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

  - [ ] 16.2 Register chop command
    - Import and register in main.py
    - _Requirements: 9.1_

  - [ ] 16.3 Write unit tests for chop command
    - Test successful chop with -forget
    - Test error case (no default exists)
    - _Requirements: 9.4, 9.5_

- [ ] 17. Implement set command
  - [ ] 17.1 Implement cmd_set function
    - Create vince/commands/set_cmd.py
    - Add path argument and extension option
    - Add -vb flag
    - Implement command logic
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

  - [ ] 17.2 Register set command
    - Import and register in main.py
    - _Requirements: 10.1_

  - [ ] 17.3 Write unit tests for set command
    - Test successful set (active state)
    - Test error case (default exists)
    - _Requirements: 10.4, 10.5_

- [ ] 18. Implement forget command
  - [ ] 18.1 Implement cmd_forget function
    - Create vince/commands/forget.py
    - Add extension option and -vb flag
    - Implement command logic
    - _Requirements: 11.1, 11.2, 11.3, 11.4_

  - [ ] 18.2 Register forget command
    - Import and register in main.py
    - _Requirements: 11.1_

  - [ ] 18.3 Write unit tests for forget command
    - Test successful forget
    - Test error case (no default)
    - _Requirements: 11.3, 11.4_

- [ ] 19. Implement offer command
  - [ ] 19.1 Implement cmd_offer function
    - Create vince/commands/offer.py
    - Add offer_id and path arguments
    - Add extension option and -vb flag
    - Implement command logic with offer_id validation
    - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5, 12.6, 12.7_

  - [ ] 19.2 Register offer command
    - Import and register in main.py
    - _Requirements: 12.1_

  - [ ] 19.3 Write unit tests for offer command
    - Test successful offer creation
    - Test error cases (invalid offer_id, offer exists)
    - _Requirements: 12.5, 12.6, 12.7_

- [ ] 20. Implement reject command
  - [ ] 20.1 Implement cmd_reject function
    - Create vince/commands/reject.py
    - Add offer_id argument
    - Add "." flag for complete-delete and -vb flag
    - Implement command logic
    - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5_

  - [ ] 20.2 Register reject command
    - Import and register in main.py
    - _Requirements: 13.1_

  - [ ] 20.3 Write unit tests for reject command
    - Test successful reject
    - Test error case (offer not found)
    - _Requirements: 13.4, 13.5_

- [ ] 21. Implement list command
  - [ ] 21.1 Implement cmd_list function
    - Create vince/commands/list_cmd.py
    - Add subsection option (-app, -cmd, -ext, -def, -off, -all)
    - Add extension filter option and -vb flag
    - Implement display logic with Rich tables
    - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.5, 14.6, 14.7_

  - [ ] 21.2 Register list command
    - Import and register in main.py
    - _Requirements: 14.1_

  - [ ] 21.3 Write unit tests for list command
    - Test list -def, list -off, list -all
    - Test error case (invalid subsection)
    - _Requirements: 14.4, 14.5, 14.6, 14.7_

- [ ] 22. Checkpoint - Verify all commands
  - Run all commands manually to verify behavior
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 23. Integration tests and coverage
  - [ ] 23.1 Write integration tests for command flows
    - Test slap → list → chop flow
    - Test slap -set → offer auto-creation
    - Test offer → reject flow
    - _Requirements: 15.4_

  - [ ] 23.2 Verify coverage targets
    - Run pytest with coverage
    - Ensure minimum 85% overall coverage
    - _Requirements: 15.4_

- [ ] 24. Final validation checkpoint
  - Run full test suite with `pytest --cov=vince`
  - Verify all property-based tests pass
  - Verify all commands work end-to-end
  - _Requirements: All_

## Notes

- All tasks are required for comprehensive testing from the start
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- The implementation follows the steering files in `.kiro/steering/`
