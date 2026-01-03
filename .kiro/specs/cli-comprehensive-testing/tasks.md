# Implementation Plan: CLI Comprehensive Testing

## Overview

This implementation plan creates comprehensive tests for the vince CLI application, covering all 21 error codes (VE101-VE606), all state machine transitions, and all command parameter combinations using pytest and Hypothesis.

## Tasks

- [-] 1. Create shared test infrastructure
  - [x] 1.1 Create `tests/strategies.py` with Hypothesis generators
    - Implement valid_extensions, unsupported_extensions strategies
    - Implement valid_offer_ids, invalid_pattern_offer_ids strategies
    - Implement valid_default_transitions, invalid_default_transitions strategies
    - Implement valid_offer_transitions strategies
    - Implement valid_application_paths, valid_default_entries, valid_offer_entries strategies
    - _Requirements: 21.1, 21.2, 21.3, 21.4, 21.5, 21.6_

  - [x] 1.2 Create `tests/mock_platform_handler.py` with MockPlatformHandler
    - Implement PlatformHandler protocol
    - Track all method calls for verification
    - Support configurable failure modes
    - _Requirements: 20.1_

  - [-] 1.3 Update `tests/conftest.py` with additional fixtures
    - Add mock_platform_handler fixture
    - Add corrupted_defaults_json fixture
    - Add corrupted_offers_json fixture
    - Add invalid_config_json fixture
    - _Requirements: 2.4, 2.5, 2.6, 2.7, 2.8, 4.1, 4.2, 4.3, 4.4_

- [ ] 2. Checkpoint - Verify test infrastructure
  - Ensure all fixtures and strategies are importable
  - Run existing tests to verify no regressions

- [ ] 3. Create input error tests (VE1xx)
  - [ ] 3.1 Create `tests/test_input_error_coverage.py`
    - Test VE101 InvalidPathError for slap, set, offer commands
    - Test VE102 InvalidExtensionError for unsupported extensions
    - Test VE102 InvalidExtensionError for missing extension flag
    - Test VE103 InvalidOfferIdError for invalid patterns
    - Test VE103 InvalidOfferIdError for reserved names
    - Test VE104 OfferNotFoundError for reject with non-existent offer
    - Test VE105 InvalidSubsectionError for list with invalid flag
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 1.10, 1.11, 1.12_

  - [ ] 3.2 Write property test for invalid offer_id pattern rejection
    - **Property 1: Invalid Offer ID Pattern Rejection**
    - **Validates: Requirements 1.6, 1.7, 1.8, 1.9**

  - [ ] 3.3 Write property test for reserved name rejection
    - **Property 2: Reserved Name Rejection**
    - **Validates: Requirements 1.10**

  - [ ] 3.4 Write property test for unsupported extension rejection
    - **Property 3: Unsupported Extension Rejection**
    - **Validates: Requirements 1.4**

- [ ] 4. Create file error tests (VE2xx)
  - [ ] 4.1 Create `tests/test_file_error_coverage.py`
    - Test VE201 VinceFileNotFoundError (if applicable)
    - Test VE202 PermissionDeniedError for insufficient permissions
    - Test VE203 DataCorruptedError for invalid JSON syntax
    - Test VE203 DataCorruptedError for invalid schema (wrong state)
    - Test VE203 DataCorruptedError for invalid schema (missing field)
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8_

- [ ] 5. Create state error tests (VE3xx)
  - [ ] 5.1 Create `tests/test_state_error_coverage.py`
    - Test VE301 DefaultExistsError for slap on active default
    - Test VE301 DefaultExistsError for set on active default
    - Test VE302 NoDefaultError for chop on no default
    - Test VE302 NoDefaultError for forget on no default
    - Test VE303 OfferExistsError for offer with existing offer_id
    - Test VE304 OfferInUseError for reject on active offer in use
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6_

  - [ ] 5.2 Write property test for valid default state transitions
    - **Property 4: Valid Default State Transitions**
    - **Validates: Requirements 6.1**

  - [ ] 5.3 Write property test for invalid default state transitions
    - **Property 5: Invalid Default State Transitions**
    - **Validates: Requirements 6.2, 6.3, 6.4, 6.5, 6.6, 6.7**

  - [ ] 5.4 Write property test for valid offer state transitions
    - **Property 6: Valid Offer State Transitions**
    - **Validates: Requirements 7.1**

  - [ ] 5.5 Write property test for invalid offer state transitions
    - **Property 7: Invalid Offer State Transitions**
    - **Validates: Requirements 7.2, 7.3, 7.4, 7.5, 7.7, 7.8**

- [ ] 6. Checkpoint - Verify error coverage
  - Run all error tests
  - Verify all VE1xx, VE2xx, VE3xx errors are covered

- [ ] 7. Create config error tests (VE4xx)
  - [ ] 7.1 Create `tests/test_config_error_coverage.py`
    - Test VE401 InvalidConfigOptionError for unknown option
    - Test VE401 InvalidConfigOptionError for invalid color_theme
    - Test VE401 InvalidConfigOptionError for out-of-range max_backups
    - Test VE402 ConfigMalformedError for invalid JSON syntax
    - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [ ] 8. Create OS error tests (VE6xx)
  - [ ] 8.1 Create `tests/test_os_error_coverage.py`
    - Test VE601 UnsupportedPlatformError with mocked platform
    - Test VE602 BundleIdNotFoundError with mocked bundle info
    - Test VE603 RegistryAccessError with mocked registry
    - Test VE604 ApplicationNotFoundError for invalid app path
    - Test VE605 OSOperationError with mocked OS failure
    - Test VE606 SyncPartialError with partial sync failures
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6_

- [ ] 9. Create validation property tests
  - [ ] 9.1 Create `tests/test_validation_properties.py`
    - _Requirements: 21.1, 21.2, 21.3, 21.4, 21.5, 21.6_

  - [ ] 9.2 Write property test for valid extension validation
    - **Property 18: Valid Extension Validation**
    - **Validates: Requirements 21.2**

  - [ ] 9.3 Write property test for valid offer_id validation
    - **Property 19: Valid Offer ID Validation**
    - **Validates: Requirements 21.4**

- [ ] 10. Checkpoint - Verify all error codes covered
  - Run all error tests
  - Verify all 21 error codes (VE101-VE606) have at least one test

- [ ] 11. Create dry run property tests
  - [ ] 11.1 Enhance `tests/test_dry_run_idempotence.py`
    - Add tests for all commands supporting -dry flag
    - _Requirements: 8.4, 9.4, 10.3, 11.3, 15.5, 16.1, 16.2, 16.3_

  - [ ] 11.2 Write property test for dry run state preservation
    - **Property 8: Dry Run State Preservation**
    - **Validates: Requirements 8.4, 9.4, 10.3, 11.3, 15.5, 16.1, 16.2**

  - [ ] 11.3 Write property test for dry run idempotence
    - **Property 9: Dry Run Idempotence**
    - **Validates: Requirements 16.3**

- [ ] 12. Create persistence property tests
  - [ ] 12.1 Create `tests/test_persistence_roundtrip.py`
    - _Requirements: 17.1, 17.2, 17.3, 17.4_

  - [ ] 12.2 Write property test for persistence round-trip consistency
    - **Property 11: Persistence Round-Trip Consistency**
    - **Validates: Requirements 17.1, 17.2, 17.3, 17.4**

- [ ] 13. Create backup retention tests
  - [ ] 13.1 Create `tests/test_backup_retention.py`
    - _Requirements: 18.1, 18.2, 18.3_

  - [ ] 13.2 Write property test for backup retention limit
    - **Property 12: Backup Retention Limit**
    - **Validates: Requirements 18.1**

  - [ ] 13.3 Write property test for backup rotation order
    - **Property 13: Backup Rotation Order**
    - **Validates: Requirements 18.2**

  - [ ] 13.4 Write property test for backup disabled behavior
    - **Property 14: Backup Disabled Behavior**
    - **Validates: Requirements 18.3**

- [ ] 14. Checkpoint - Verify property tests
  - Run all property tests with 100 iterations
  - Verify all properties pass

- [ ] 15. Create verbose output tests
  - [ ] 15.1 Create `tests/test_verbose_output.py`
    - Test verbose output for all commands supporting -vb flag
    - Test no verbose output when flag is not set
    - Test verbose output includes operation details
    - _Requirements: 23.1, 23.2, 23.3, 23.4_

  - [ ] 15.2 Write property test for verbose flag controls output
    - **Property 16: Verbose Flag Controls Output**
    - **Validates: Requirements 23.1, 23.2**

- [ ] 16. Create command extension coverage tests
  - [ ] 16.1 Enhance command tests for all 12 extensions
    - Add tests for slap with all extensions
    - Add tests for chop with all extensions
    - Add tests for set with all extensions
    - Add tests for forget with all extensions
    - Add tests for offer with all extensions
    - _Requirements: 8.7, 9.6, 10.5, 11.5, 12.5_

  - [ ] 16.2 Write property test for commands work for all extensions
    - **Property 10: Commands Work for All Extensions**
    - **Validates: Requirements 8.7, 9.6, 10.5, 11.5, 12.5**

- [ ] 17. Create list command filter tests
  - [ ] 17.1 Enhance `tests/test_list_command.py`
    - Test list -app, -cmd, -ext, -def, -off, -all
    - Test extension filtering with all flags
    - Test empty state messages
    - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.5, 14.6, 14.7, 14.8, 14.9, 14.10_

  - [ ] 17.2 Write property test for list extension filtering
    - **Property 20: List Extension Filtering**
    - **Validates: Requirements 14.7**

- [ ] 18. Checkpoint - Verify command tests
  - Run all command tests
  - Verify all 8 commands have comprehensive coverage

- [ ] 19. Create platform handler integration tests
  - [ ] 19.1 Enhance `tests/test_command_handler_integration.py`
    - Test slap -set calls handler.set_default
    - Test set calls handler.set_default
    - Test chop -forget calls handler.remove_default
    - Test forget calls handler.remove_default
    - Test sync calls handler.set_default for each active default
    - Test handler failure warning behavior
    - Test list -def calls handler.get_current_default
    - _Requirements: 20.2, 20.3, 20.4, 20.5, 20.6, 20.7, 20.8_

- [ ] 20. Create integration workflow tests
  - [ ] 20.1 Enhance `tests/test_integration.py`
    - Test slap → list -def → chop -forget workflow
    - Test slap -set → list -off → reject workflow
    - Test offer → list -off → reject workflow
    - Test set → forget → set workflow (re-activation)
    - Test slap → offer → reject → chop workflow
    - Test multiple slap -set → sync workflow
    - _Requirements: 19.1, 19.2, 19.3, 19.4, 19.5, 19.6_

  - [ ] 20.2 Write property test for state persistence across commands
    - **Property 17: State Persistence Across Commands**
    - **Validates: Requirements 19.7**

- [ ] 21. Create error class completeness tests
  - [ ] 21.1 Enhance `tests/test_errors.py`
    - Verify all error classes have code, message, recovery
    - Verify error codes follow VE### format
    - Verify error codes are in correct category ranges
    - _Requirements: 22.1, 22.2, 22.3, 22.4_

  - [ ] 21.2 Write property test for error class completeness
    - **Property 15: Error Class Completeness**
    - **Validates: Requirements 22.1, 22.2, 22.3, 22.4**

- [ ] 22. Create schema migration tests
  - [ ] 22.1 Enhance `tests/test_schema_migration.py`
    - Test migration adds os_synced field
    - Test migration to v1.1.0 succeeds
    - Test unknown future version handling
    - _Requirements: 24.1, 24.2, 24.3_

  - [ ] 22.2 Write property test for schema migration data preservation
    - **Property 21: Schema Migration Data Preservation**
    - **Validates: Requirements 24.4**

- [ ] 23. Final checkpoint - Verify all tests pass
  - Run full test suite with coverage
  - Verify coverage meets 85% target
  - Verify all 21 correctness properties pass

## Notes

- All tasks are required for comprehensive test coverage
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties with minimum 100 iterations
- Unit tests validate specific examples and edge cases

