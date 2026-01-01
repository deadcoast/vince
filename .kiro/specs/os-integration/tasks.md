# Implementation Plan: OS Integration Layer

## Overview

This plan implements cross-platform OS integration for vince, adding the ability to actually set file associations at the operating system level on macOS and Windows. The implementation follows the Strategy pattern with platform-specific handlers.

## Tasks

- [x] 1. Create platform module structure and base interfaces
  - [x] 1.1 Create `vince/platform/__init__.py` with factory function and platform detection
    - Implement `get_platform()` returning Platform enum
    - Implement `get_handler()` singleton factory
    - _Requirements: 1.1, 1.2, 1.3_
  - [x] 1.2 Create `vince/platform/base.py` with Protocol and data classes
    - Define `Platform` enum (MACOS, WINDOWS, UNSUPPORTED)
    - Define `AppInfo` dataclass
    - Define `OperationResult` dataclass
    - Define `PlatformHandler` Protocol
    - _Requirements: 1.1_
  - [x] 1.3 Create `vince/platform/errors.py` with OS-specific error classes
    - Implement VE601 UnsupportedPlatformError
    - Implement VE602 BundleIdNotFoundError
    - Implement VE603 RegistryAccessError
    - Implement VE604 ApplicationNotFoundError
    - Implement VE605 OSOperationError
    - Implement VE606 SyncPartialError
    - _Requirements: 8.1, 8.2, 8.3_
  - [x] 1.4 Write unit tests for platform detection and error classes
    - Test get_platform() returns correct enum for each platform
    - Test error classes have correct codes and messages
    - _Requirements: 1.1, 1.2, 8.3_

- [x] 2. Implement UTI mapping for macOS
  - [x] 2.1 Create `vince/platform/uti_map.py` with extension-to-UTI mapping
    - Define UTI_MAP dictionary for all 12 supported extensions
    - Implement `extension_to_uti()` function
    - Implement `uti_to_extension()` reverse lookup
    - _Requirements: 2.2, 2.5_
  - [x] 2.2 Write property test for UTI mapping completeness
    - **Property 2: UTI Mapping Completeness**
    - **Validates: Requirements 2.2, 2.5**

- [x] 3. Implement macOS handler
  - [x] 3.1 Create `vince/platform/macos.py` with MacOSHandler class
    - Implement `platform` property
    - Implement `verify_application()` for .app bundle validation
    - Implement `_get_bundle_id()` using defaults command
    - Implement `_find_app_bundle()` for executable-to-bundle resolution
    - _Requirements: 2.1, 2.3_
  - [x] 3.2 Implement `get_current_default()` for macOS
    - Try duti first, fall back to Launch Services query
    - Handle duti not installed gracefully
    - _Requirements: 4.1_
  - [x] 3.3 Implement `set_default()` for macOS
    - Record previous default before change
    - Try duti first, fall back to PyObjC
    - Support dry_run mode
    - _Requirements: 2.1, 2.4, 7.1, 7.2, 9.1_
  - [x] 3.4 Implement `remove_default()` for macOS
    - Reset Launch Services for UTI
    - Rebuild Launch Services database
    - _Requirements: 5.1, 5.2_
  - [x] 3.5 Write property test for macOS set-query round trip
    - **Property 3: Set-Query Round Trip (macOS)**
    - **Validates: Requirements 2.1, 2.4**

- [ ] 4. Implement Windows handler
  - [ ] 4.1 Create `vince/platform/windows.py` with WindowsHandler class
    - Implement `platform` property
    - Implement `verify_application()` for .exe validation
    - Implement `_find_executable()` for directory scanning
    - _Requirements: 3.1_
  - [ ] 4.2 Implement `get_current_default()` for Windows
    - Query UserChoice registry key first
    - Fall back to HKEY_CLASSES_ROOT
    - Resolve ProgID to application path
    - _Requirements: 4.1_
  - [ ] 4.3 Implement `set_default()` for Windows
    - Record previous default before change
    - Create ProgID entries
    - Associate extension with ProgID
    - Call SHChangeNotify
    - Support dry_run mode
    - _Requirements: 3.1, 3.2, 3.3, 3.5, 7.1, 7.2, 9.1_
  - [ ] 4.4 Implement `remove_default()` for Windows
    - Delete ProgID entries recursively
    - Remove extension association
    - Notify shell
    - _Requirements: 5.1, 5.3_
  - [ ] 4.5 Write property test for Windows set-query round trip
    - **Property 3: Set-Query Round Trip (Windows)**
    - **Validates: Requirements 3.1, 3.5**

- [ ] 5. Checkpoint - Verify platform handlers work independently
  - Ensure all tests pass, ask the user if questions arise.
  - Test macOS handler on macOS (or with mocks)
  - Test Windows handler on Windows (or with mocks)

- [ ] 6. Integrate with existing commands
  - [ ] 6.1 Update `vince/commands/slap.py` to call platform handler
    - Import and call `get_handler().set_default()` after JSON update
    - Handle OS operation failure with warning
    - Add `-dry` flag support
    - Update `os_synced` and `previous_os_default` fields
    - _Requirements: 10.1, 10.5_
  - [ ] 6.2 Update `vince/commands/set_cmd.py` to call platform handler
    - Same integration pattern as slap
    - _Requirements: 10.3_
  - [ ] 6.3 Update `vince/commands/chop.py` to call platform handler
    - Call `get_handler().remove_default()` after JSON update
    - Handle OS operation failure with warning
    - _Requirements: 10.2_
  - [ ] 6.4 Update `vince/commands/forget.py` to call platform handler
    - Same integration pattern as chop
    - _Requirements: 10.4_
  - [ ] 6.5 Write property test for command-handler integration
    - **Property 7: Command Integration Calls Handler**
    - **Validates: Requirements 10.1, 10.2, 10.3, 10.4, 10.5**

- [ ] 7. Implement sync command
  - [ ] 7.1 Create `vince/commands/sync.py` with cmd_sync function
    - Load all active defaults from JSON store
    - For each, check if OS default matches
    - Skip already-synced entries
    - Apply changes for out-of-sync entries
    - Collect and report failures
    - Support dry_run mode
    - _Requirements: 6.1, 6.2, 6.3, 6.4_
  - [ ] 7.2 Register sync command in `vince/main.py`
    - Add `app.command(name="sync")(sync.cmd_sync)`
    - _Requirements: 6.1_
  - [ ] 7.3 Write property test for sync completeness
    - **Property 6: Sync Applies All Active Defaults**
    - **Validates: Requirements 6.1, 6.2, 6.3, 6.4**

- [ ] 8. Update list command to show OS defaults
  - [ ] 8.1 Update `vince/commands/list_cmd.py` to query OS defaults
    - For `-def` flag, call `get_handler().get_current_default()` for each entry
    - Add "OS Default" column to table
    - Add mismatch indicator when vince != OS
    - Handle query failures gracefully (show "unknown")
    - _Requirements: 4.1, 4.2, 4.3, 4.4_
  - [ ] 8.2 Update `vince/output/tables.py` with new column
    - Add "OS Default" column to defaults table
    - Add warning style for mismatches
    - _Requirements: 4.2, 4.3_
  - [ ] 8.3 Write property test for mismatch detection
    - **Property 10: Mismatch Detection in List**
    - **Validates: Requirements 4.1, 4.3**

- [ ] 9. Implement rollback support
  - [ ] 9.1 Add rollback logic to platform handlers
    - In `set_default()`, if operation fails after partial change, attempt restore
    - Log rollback attempts
    - Return compound error if rollback also fails
    - _Requirements: 9.1, 9.2, 9.3, 9.4_
  - [ ] 9.2 Write property test for rollback restoration
    - **Property 5: Rollback on Failure**
    - **Validates: Requirements 9.1, 9.2**

- [ ] 10. Checkpoint - Full integration testing
  - Ensure all tests pass, ask the user if questions arise.
  - Run full test suite on both platforms (or with mocks)
  - Verify sync command works end-to-end

- [ ] 11. Update persistence layer for OS sync tracking
  - [ ] 11.1 Update `vince/persistence/defaults.py` schema
    - Add `os_synced` boolean field
    - Add `os_synced_at` timestamp field
    - Add `previous_os_default` string field
    - Update `add()` and `update_state()` to handle new fields
    - _Requirements: 9.1_
  - [ ] 11.2 Update schema version to 1.1.0
    - Add migration from 1.0.0 to 1.1.0
    - Set default values for new fields
    - _Requirements: 9.1_

- [ ] 12. Add dry run flag to all commands
  - [ ] 12.1 Add `-dry` option to slap, set, chop, forget, sync commands
    - Pass dry_run parameter to platform handler
    - Display planned changes without executing
    - _Requirements: 7.1, 7.2, 7.3_
  - [ ] 12.2 Write property test for dry run idempotence
    - **Property 4: Dry Run No Side Effects**
    - **Validates: Requirements 7.1, 7.2**

- [ ] 13. Update documentation
  - [ ] 13.1 Update `docs/overview.md` with OS integration section
    - Document platform support (macOS, Windows)
    - Document sync command
    - Document dry run mode
    - Document new error codes VE601-VE606
    - _Requirements: All_
  - [ ] 13.2 Update `docs/errors.md` with new error codes
    - Add VE6xx section for OS errors
    - Document each error with recovery actions
    - _Requirements: 8.3_
  - [ ] 13.3 Update `docs/api.md` with new functions
    - Document platform module API
    - Document sync command
    - _Requirements: All_
  - [ ] 13.4 Update `docs/examples.md` with OS integration examples
    - Add examples showing actual OS changes
    - Add sync command examples
    - Add dry run examples
    - _Requirements: All_

- [ ] 14. Final checkpoint - Complete validation
  - Ensure all tests pass, ask the user if questions arise.
  - Run full test suite
  - Verify documentation is complete
  - Test on actual macOS and Windows systems if available

## Notes

- All tasks including property-based tests are required for comprehensive coverage
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- macOS implementation prefers `duti` (brew install duti) but falls back to PyObjC
- Windows implementation uses built-in `winreg` module
