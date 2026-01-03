# Implementation Plan: Coverage Completion

## Overview

This implementation plan addresses the remaining gaps to achieve production readiness: 85% test coverage, zero mypy errors, and complete task tracking. Tasks are organized to maximize coverage impact with minimal changes.

## Tasks

- [x] 1. Fix type annotation errors
  - [x] 1.1 Fix mypy error in `vince/platform/macos.py`
    - Change line 72: `app_bundle: Path` to `app_bundle: Optional[Path]`
    - Add `Optional` import if not present
    - *Requirements: 6.1, 6.3*
  - [x] 1.2 Fix mypy error in `vince/platform/windows.py`
    - Change line 91: `exe_path: Path` to `exe_path: Optional[Path]`
    - Add `Optional` import if not present
    - *Requirements: 6.2, 6.3*

- [x] 2. Checkpoint - Verify mypy passes
  - Run `uv run mypy vince/ --ignore-missing-imports`
  - Ensure zero errors reported
  - Ask the user if questions arise

- [x] 3. Create shared test fixtures
  - [x] 3.1 Create `tests/conftest.py` with core fixtures
    - Add `cli_runner` fixture returning CliRunner
    - Add `mock_executable` fixture creating executable file
    - Add `isolated_data_dir` fixture with empty JSON files
    - Add `populated_data_dir` fixture with sample data
    - *Requirements: 5.1, 5.2, 5.3, 5.4*
  - [x] 3.2 Add platform mock fixtures to conftest.py
    - Add `mock_platform_handler` fixture
    - Add `mock_get_handler` fixture for patching
    - Add `mock_unsupported_platform` fixture
    - *Requirements: 5.5*

- [x] 4. Add entry point tests
  - [x] 4.1 Create `tests/test_main_entry.py`
    - Test `__main__.py` module import
    - Test CLI --help invocation
    - Test CLI --version invocation
    - *Requirements: 1.1, 1.2*
  - [x] 4.2 Write property test for CLI initialization
    - Verify CLI always initializes without error
    - *Requirements: 1.1*

- [x] 5. Checkpoint - Verify entry point coverage
  - Run `uv run pytest tests/test_main_entry.py -v`
  - Ensure tests pass
  - Ask the user if questions arise

- [x] 6. Enhance Windows handler tests
  - [x] 6.1 Add registry operation mock tests
    - Test `set_default()` creates correct ProgID entries
    - Test `remove_default()` cleans up registry entries
    - Test `get_current_default()` queries correct keys
    - *Requirements: 2.2, 2.3, 2.4*
  - [x] 6.2 Add shell notification tests
    - Test SHChangeNotify is called after set_default
    - Test SHChangeNotify is called after remove_default
    - *Requirements: 2.5*
  - [x] 6.3 Write property test for Windows handler operations
    - **Property 1: Windows Handler Registry Operations**
    - **Validates: Requirements 2.2, 2.3, 2.4, 2.5**

- [x] 7. Enhance sync command tests
  - [x] 7.1 Add edge case tests
    - Test sync with no active defaults (empty result)
    - Test sync with all entries already synced (skip all)
    - Test sync with verbose flag (detailed output)
    - *Requirements: 3.1, 3.5*
  - [x] 7.2 Add error handling tests
    - Test sync with partial failures (error collection)
    - Test sync continues after individual failures
    - *Requirements: 3.3*
  - [x] 7.3 Write property test for sync skip and error handling
    - **Property 2: Sync Skip and Error Handling**
    - **Validates: Requirements 3.2, 3.3**
  - [x] 7.4 Enhance property test for dry run idempotence
    - **Property 3: Dry Run Idempotence**
    - **Validates: Requirements 3.4**

- [x] 8. Checkpoint - Verify sync command coverage
  - Run `uv run pytest tests/test_sync_command.py -v --cov=vince/commands/sync`
  - Ensure coverage >= 80%
  - Ask the user if questions arise

- [x] 9. Enhance list command tests
  - [x] 9.1 Add subsection flag tests
    - Test list with `-app` flag
    - Test list with `-cmd` flag
    - Test list with `-ext` flag
    - *Requirements: 4.1, 4.2, 4.3*
  - [x] 9.2 Add OS integration tests
    - Test list with OS default mismatch (warning indicator)
    - Test list with OS query failure ("unknown" fallback)
    - *Requirements: 4.4, 4.5*
  - [x] 9.3 Write property test for mismatch detection
    - **Property 4: List Mismatch Detection**
    - **Validates: Requirements 4.4**

- [ ] 10. Checkpoint - Verify list command coverage
  - Run `uv run pytest tests/test_list_command.py -v --cov=vince/commands/list_cmd`
  - Ensure coverage >= 80%
  - Ask the user if questions arise

- [ ] 11. Add schema migration tests
  - [ ] 11.1 Add migration unit tests
    - Test v1.0.0 to v1.1.0 migration adds os_synced field
    - Test v1.0.0 to v1.1.0 migration updates version
    - Test v1.1.0 files skip migration
    - *Requirements: 8.4*
  - [ ] 11.2 Write property test for schema migration
    - **Property 5: Schema Migration Correctness**
    - **Validates: Requirements 8.4**

- [ ] 12. Checkpoint - Verify overall coverage
  - Run `uv run pytest --cov=vince --cov-report=term-missing`
  - Ensure overall coverage >= 85%
  - Ask the user if questions arise

- [ ] 13. Update os-integration task tracking
  - [ ] 13.1 Mark checkpoint 5 as complete
    - Update `.kiro/specs/os-integration/tasks.md`
    - Change `- [ ] 5.` to `- [x] 5.`
    - *Requirements: 9.1*
  - [ ] 13.2 Mark task 11.2 as complete
    - Schema migration is already implemented
    - Change `- [-] 11.2` to `- [x] 11.2`
    - *Requirements: 9.2*
  - [ ] 13.3 Mark parent task 11 as complete
    - Change `- [-] 11.` to `- [x] 11.`
    - *Requirements: 9.3*

- [ ] 14. Final validation checkpoint
  - Run `uv run mypy vince/ --ignore-missing-imports` (0 errors)
  - Run `uv run pytest --cov=vince` (85%+ coverage, all tests pass)
  - Run `uv run ruff check vince/` (no errors)
  - Verify os-integration tasks.md shows all complete
  - *Requirements: All*

## Notes

- All tasks are required for comprehensive testing
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- The conftest.py consolidates duplicate fixtures from existing test files
