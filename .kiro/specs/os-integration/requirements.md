# Requirements Document

## Introduction

This document specifies requirements for adding cross-platform OS integration to the vince CLI. Currently, vince tracks application-to-extension mappings in JSON files but does not actually configure the operating system to use these defaults. This feature adds the "last mile" integration to make vince fulfill its core purpose: actually setting default applications for file extensions at the OS level.

The implementation targets macOS and Windows platforms, with an abstraction layer that allows future Linux support.

## Glossary

- **OS_Integration_Layer**: The abstraction module that provides a unified interface for platform-specific file association operations
- **Platform_Handler**: A platform-specific implementation (macOS or Windows) that performs actual OS-level file association changes
- **UTI**: Uniform Type Identifier - macOS's system for identifying file types (e.g., `public.plain-text` for `.txt`)
- **Launch_Services**: macOS framework that manages application-to-file-type associations
- **Registry**: Windows system database that stores file association settings
- **HKEY_CURRENT_USER**: Windows registry hive for user-specific settings including file associations
- **ProgID**: Programmatic Identifier - Windows registry key that defines how a file type is handled
- **duti**: Third-party macOS command-line tool for managing default applications (optional dependency)
- **Rollback**: The ability to restore previous file association state if an operation fails

## Requirements

### Requirement 1: Platform Detection

**User Story:** As a user, I want vince to automatically detect my operating system, so that it uses the correct method to set file associations.

#### Acceptance Criteria

1. WHEN vince starts, THE OS_Integration_Layer SHALL detect the current platform (macOS, Windows, or unsupported)
2. WHEN running on an unsupported platform, THE OS_Integration_Layer SHALL raise a clear error with code VE601
3. THE OS_Integration_Layer SHALL expose a `get_platform()` function returning the detected platform identifier

### Requirement 2: macOS File Association

**User Story:** As a macOS user, I want vince to actually set my default applications, so that double-clicking a file opens it in my chosen application.

#### Acceptance Criteria

1. WHEN a user runs `slap -set` on macOS, THE Platform_Handler SHALL configure Launch Services to use the specified application for the extension
2. WHEN setting a default on macOS, THE Platform_Handler SHALL map the file extension to its corresponding UTI
3. IF the application bundle ID cannot be determined, THEN THE Platform_Handler SHALL raise error VE602
4. WHEN a default is set successfully on macOS, THE Platform_Handler SHALL verify the change took effect
5. THE Platform_Handler SHALL support common extensions: .md, .py, .txt, .js, .html, .css, .json, .yml, .yaml, .xml, .csv, .sql

### Requirement 3: Windows File Association

**User Story:** As a Windows user, I want vince to actually set my default applications, so that double-clicking a file opens it in my chosen application.

#### Acceptance Criteria

1. WHEN a user runs `slap -set` on Windows, THE Platform_Handler SHALL modify the Windows Registry to associate the extension with the application
2. WHEN setting a default on Windows, THE Platform_Handler SHALL create or update the appropriate ProgID entries
3. WHEN setting a default on Windows, THE Platform_Handler SHALL update HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\FileExts
4. IF registry modification fails due to permissions, THEN THE Platform_Handler SHALL raise error VE603
5. WHEN a default is set successfully on Windows, THE Platform_Handler SHALL notify the shell of the change (SHChangeNotify)

### Requirement 4: Query Current Defaults

**User Story:** As a user, I want to see what application is currently set as the OS default for an extension, so that I can compare it with my vince configuration.

#### Acceptance Criteria

1. WHEN a user runs `list -def`, THE OS_Integration_Layer SHALL query the OS for current default applications
2. THE list output SHALL show both the vince-tracked default AND the actual OS default side-by-side
3. WHEN the vince default differs from the OS default, THE list output SHALL indicate the mismatch with a warning indicator
4. IF querying the OS default fails, THEN THE OS_Integration_Layer SHALL display "unknown" for the OS default

### Requirement 5: Remove/Reset File Association

**User Story:** As a user, I want to remove a file association I set with vince, so that the OS reverts to its previous or system default.

#### Acceptance Criteria

1. WHEN a user runs `chop -forget` with an active default, THE Platform_Handler SHALL remove the custom association from the OS
2. WHEN removing an association on macOS, THE Platform_Handler SHALL reset Launch Services for that UTI
3. WHEN removing an association on Windows, THE Platform_Handler SHALL remove the custom ProgID entries
4. IF the original default was tracked, THEN THE Platform_Handler SHALL restore it; otherwise, THE Platform_Handler SHALL reset to system default

### Requirement 6: Sync Command

**User Story:** As a user, I want to sync my vince configuration to the OS, so that I can apply all my tracked defaults at once.

#### Acceptance Criteria

1. WHEN a user runs `vince sync`, THE OS_Integration_Layer SHALL apply all active defaults to the OS
2. WHEN syncing, THE OS_Integration_Layer SHALL skip entries that are already correctly configured
3. WHEN syncing, THE OS_Integration_Layer SHALL report success/failure for each extension
4. IF any sync operation fails, THEN THE OS_Integration_Layer SHALL continue with remaining entries and report all failures at the end

### Requirement 7: Dry Run Mode

**User Story:** As a user, I want to preview what changes vince will make to my OS, so that I can verify before committing.

#### Acceptance Criteria

1. WHEN a user provides the `-dry` flag with any command, THE OS_Integration_Layer SHALL NOT make actual OS changes
2. WHEN in dry run mode, THE OS_Integration_Layer SHALL display what changes WOULD be made
3. THE dry run output SHALL show: extension, current OS default, proposed new default, and required OS operations

### Requirement 8: Error Handling for OS Operations

**User Story:** As a user, I want clear error messages when OS operations fail, so that I can troubleshoot and resolve issues.

#### Acceptance Criteria

1. WHEN an OS operation fails, THE OS_Integration_Layer SHALL provide a specific error code (VE6xx series)
2. WHEN an OS operation fails, THE error message SHALL include the platform-specific reason
3. THE OS_Integration_Layer SHALL define these error codes:
   - VE601: Unsupported platform
   - VE602: Cannot determine application bundle ID (macOS)
   - VE603: Registry access denied (Windows)
   - VE604: Application not found or invalid
   - VE605: OS operation failed (generic)
   - VE606: Sync partially failed

### Requirement 9: Rollback Support

**User Story:** As a user, I want vince to restore my previous settings if something goes wrong, so that I don't end up with broken file associations.

#### Acceptance Criteria

1. BEFORE making OS changes, THE OS_Integration_Layer SHALL record the current OS default for the extension
2. IF an OS operation fails after partial changes, THEN THE OS_Integration_Layer SHALL attempt to rollback to the previous state
3. WHEN rollback is attempted, THE OS_Integration_Layer SHALL log the rollback action
4. IF rollback fails, THEN THE OS_Integration_Layer SHALL report both the original error and the rollback failure

### Requirement 10: Integration with Existing Commands

**User Story:** As a user, I want the existing vince commands to automatically apply OS changes, so that I don't need to learn new commands.

#### Acceptance Criteria

1. WHEN `slap -set` succeeds in updating the JSON store, THE command SHALL also apply the change to the OS
2. WHEN `chop -forget` succeeds in updating the JSON store, THE command SHALL also remove the OS association
3. WHEN `set` command succeeds, THE command SHALL also apply the change to the OS
4. WHEN `forget` command succeeds, THE command SHALL also remove the OS association
5. IF the OS operation fails but JSON update succeeded, THEN THE command SHALL warn the user and suggest running `sync`
