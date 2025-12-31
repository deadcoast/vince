# Requirements Document

## Introduction

This specification defines the requirements for implementing the vince CLI Python application. The vince CLI is a Rich-based command-line interface for setting default applications to file extensions. This implementation follows the comprehensive documentation suite created in the python-integration-preparation spec.

## Glossary

- **Vince_CLI**: The main command-line interface application built with Typer and Rich
- **Typer**: Python CLI framework used for command registration and argument parsing
- **Rich**: Python library for terminal formatting and styled output
- **DefaultsStore**: Persistence layer component for managing defaults.json
- **OffersStore**: Persistence layer component for managing offers.json
- **ConfigLoader**: Component for loading and merging configuration from multiple sources
- **StateManager**: Component for validating and executing state transitions
- **Validator**: Component for validating paths, extensions, and offer IDs
- **AtomicWrite**: File write pattern using temp file + rename for data integrity
- **VinceError**: Base exception class for all vince CLI errors

## Requirements

### Requirement 1: Project Structure and Entry Point

**User Story:** As a developer, I want a properly structured Python project with a working entry point, so that I can run the vince CLI.

#### Acceptance Criteria

1. THE Project SHALL have a pyproject.toml with dependencies (typer>=0.9.0, rich>=13.0.0)
2. THE Project SHALL have a vince/ package directory with __init__.py
3. THE Entry_Point SHALL initialize a Typer app with name "vince" and rich_markup_mode="rich"
4. WHEN the CLI is invoked with --help, THE System SHALL display help information
5. WHEN the CLI is invoked with --version, THE System SHALL display version information

### Requirement 2: Error System Implementation

**User Story:** As a developer, I want a comprehensive error system, so that errors are handled consistently with proper codes and recovery messages.

#### Acceptance Criteria

1. THE Error_System SHALL define a VinceError base class with code, message, and recovery fields
2. FOR ALL error categories (Input VE1xx, File VE2xx, State VE3xx, Config VE4xx, System VE5xx), THE Error_System SHALL provide specific exception classes
3. THE Error_System SHALL provide InvalidPathError (VE101), InvalidExtensionError (VE102), InvalidOfferIdError (VE103), OfferNotFoundError (VE104), InvalidSubsectionError (VE105)
4. THE Error_System SHALL provide FileNotFoundError (VE201), PermissionDeniedError (VE202), DataCorruptedError (VE203)
5. THE Error_System SHALL provide DefaultExistsError (VE301), NoDefaultError (VE302), OfferExistsError (VE303), OfferInUseError (VE304)
6. THE Error_System SHALL provide InvalidConfigOptionError (VE401), ConfigMalformedError (VE402)
7. THE Error_System SHALL provide UnexpectedError (VE501)
8. THE Error_System SHALL provide a handle_error function that displays formatted error with Rich and exits

### Requirement 3: Validation System Implementation

**User Story:** As a developer, I want input validation functions, so that all user input is validated before processing.

#### Acceptance Criteria

1. THE Path_Validator SHALL verify path exists using Path.exists()
2. THE Path_Validator SHALL verify path is a file using Path.is_file()
3. THE Path_Validator SHALL verify path is executable using os.access(path, os.X_OK)
4. IF path validation fails, THEN THE Path_Validator SHALL raise InvalidPathError (VE101) or PermissionDeniedError (VE202)
5. THE Extension_Validator SHALL verify extension matches pattern ^\.[a-z0-9]+$
6. THE Extension_Validator SHALL verify extension is in the supported list (.md, .py, .txt, .js, .html, .css, .json, .yml, .yaml, .xml, .csv, .sql)
7. IF extension validation fails, THEN THE Extension_Validator SHALL raise InvalidExtensionError (VE102)
8. THE OfferID_Validator SHALL verify offer_id matches pattern ^[a-z][a-z0-9_-]{0,31}$
9. THE OfferID_Validator SHALL verify offer_id is not a reserved name (help, version, list, all, none, default)
10. IF offer_id validation fails, THEN THE OfferID_Validator SHALL raise InvalidOfferIdError (VE103)

### Requirement 4: Persistence Layer Implementation

**User Story:** As a developer, I want a persistence layer for JSON data files, so that data is stored reliably with backup support.

#### Acceptance Criteria

1. THE Persistence_Layer SHALL implement atomic_write using temp file + rename pattern
2. THE Persistence_Layer SHALL implement file_lock using fcntl for exclusive access
3. THE Persistence_Layer SHALL implement create_backup with timestamped backup files
4. THE Persistence_Layer SHALL implement load_json with fallback to default schema
5. THE DefaultsStore SHALL load and save defaults.json with schema version 1.0.0
6. THE DefaultsStore SHALL provide find_by_extension, add, and update_state methods
7. THE OffersStore SHALL load and save offers.json with schema version 1.0.0
8. THE OffersStore SHALL provide find_by_id, add, and update_state methods
9. WHEN backup_enabled is true, THE Persistence_Layer SHALL create backup before each write
10. THE Persistence_Layer SHALL retain up to max_backups backup files, deleting oldest when exceeded

### Requirement 5: State Machine Implementation

**User Story:** As a developer, I want state machine validation, so that state transitions follow the defined lifecycle rules.

#### Acceptance Criteria

1. THE Default_State_Machine SHALL define states: none, pending, active, removed
2. THE Default_State_Machine SHALL allow transitions: none→pending, none→active, pending→active, pending→none, active→removed, removed→active
3. IF an invalid default transition is attempted, THEN THE State_Machine SHALL raise appropriate error (VE301 or VE302)
4. THE Offer_State_Machine SHALL define states: none, created, active, rejected
5. THE Offer_State_Machine SHALL allow transitions: none→created, created→active, created→rejected, active→rejected
6. IF an invalid offer transition is attempted, THEN THE State_Machine SHALL raise appropriate error (VE303 or VE304)

### Requirement 6: Configuration System Implementation

**User Story:** As a developer, I want a configuration system with hierarchy support, so that settings can be customized at user and project levels.

#### Acceptance Criteria

1. THE Config_System SHALL load default configuration with data_dir=~/.vince, verbose=false, color_theme=default, backup_enabled=true, max_backups=5, confirm_destructive=true
2. THE Config_System SHALL load user config from ~/.vince/config.json if it exists
3. THE Config_System SHALL load project config from ./.vince/config.json if it exists
4. THE Config_System SHALL merge configs with precedence: project > user > default
5. IF config file has invalid JSON, THEN THE Config_System SHALL raise ConfigMalformedError (VE402)
6. IF config option is invalid, THEN THE Config_System SHALL raise InvalidConfigOptionError (VE401)

### Requirement 7: Output Formatting Implementation

**User Story:** As a developer, I want Rich-based output formatting, so that CLI output is visually consistent and appealing.

#### Acceptance Criteria

1. THE Output_System SHALL define VINCE_THEME with styles: info=cyan, success=green, warning=yellow, error=red bold, command=magenta, path=blue underline, extension=cyan bold
2. THE Output_System SHALL provide print_success function with format "[success]✓[/] {message}"
3. THE Output_System SHALL provide print_warning function with format "[warning]⚠[/] {message}"
4. THE Output_System SHALL provide print_error function with format "[error]✗ {code}:[/] {message}"
5. THE Output_System SHALL provide print_info function with format "[info]ℹ[/] {message}"
6. THE Output_System SHALL provide create_defaults_table for displaying defaults in Rich table format
7. THE Output_System SHALL provide create_offers_table for displaying offers in Rich table format

### Requirement 8: Command Implementation - slap

**User Story:** As a user, I want to use the slap command to set an application as default for a file extension.

#### Acceptance Criteria

1. THE slap_Command SHALL accept path argument (required, must exist, must be file)
2. THE slap_Command SHALL accept extension option (--md, --py, --txt, --js, --html, --css, --json, --yml, --yaml, --xml, --csv, --sql)
3. THE slap_Command SHALL accept -set flag to set as default immediately
4. THE slap_Command SHALL accept -vb/--verbose flag for verbose output
5. WHEN slap is called without -set, THE System SHALL create a pending default entry
6. WHEN slap is called with -set, THE System SHALL create an active default entry and auto-create an offer
7. IF default already exists for extension, THEN THE System SHALL raise DefaultExistsError (VE301)

### Requirement 9: Command Implementation - chop

**User Story:** As a user, I want to use the chop command to remove a file extension association.

#### Acceptance Criteria

1. THE chop_Command SHALL accept extension option (--md, --py, etc.)
2. THE chop_Command SHALL accept -forget flag to forget the default
3. THE chop_Command SHALL accept -vb/--verbose flag for verbose output
4. WHEN chop is called with -forget, THE System SHALL transition default state to removed
5. IF no default exists for extension, THEN THE System SHALL raise NoDefaultError (VE302)

### Requirement 10: Command Implementation - set

**User Story:** As a user, I want to use the set command to directly set a default for a file extension.

#### Acceptance Criteria

1. THE set_Command SHALL accept path argument (required, must exist, must be file)
2. THE set_Command SHALL accept extension option (--md, --py, etc.)
3. THE set_Command SHALL accept -vb/--verbose flag for verbose output
4. WHEN set is called, THE System SHALL create an active default entry
5. IF default already exists for extension, THEN THE System SHALL raise DefaultExistsError (VE301)

### Requirement 11: Command Implementation - forget

**User Story:** As a user, I want to use the forget command to forget a default for a file extension.

#### Acceptance Criteria

1. THE forget_Command SHALL accept extension option (--md, --py, etc.)
2. THE forget_Command SHALL accept -vb/--verbose flag for verbose output
3. WHEN forget is called, THE System SHALL transition default state to removed
4. IF no default exists for extension, THEN THE System SHALL raise NoDefaultError (VE302)

### Requirement 12: Command Implementation - offer

**User Story:** As a user, I want to use the offer command to create a custom shortcut/alias.

#### Acceptance Criteria

1. THE offer_Command SHALL accept offer_id argument (required, must match pattern)
2. THE offer_Command SHALL accept path argument (required, must exist, must be file)
3. THE offer_Command SHALL accept extension option (--md, --py, etc.)
4. THE offer_Command SHALL accept -vb/--verbose flag for verbose output
5. WHEN offer is called, THE System SHALL create an offer entry in created state
6. IF offer_id already exists, THEN THE System SHALL raise OfferExistsError (VE303)
7. IF offer_id is invalid format, THEN THE System SHALL raise InvalidOfferIdError (VE103)

### Requirement 13: Command Implementation - reject

**User Story:** As a user, I want to use the reject command to remove a custom offer.

#### Acceptance Criteria

1. THE reject_Command SHALL accept offer_id argument (required)
2. THE reject_Command SHALL accept "." flag for complete-delete
3. THE reject_Command SHALL accept -vb/--verbose flag for verbose output
4. WHEN reject is called, THE System SHALL transition offer state to rejected
5. IF offer_id does not exist, THEN THE System SHALL raise OfferNotFoundError (VE104)

### Requirement 14: Command Implementation - list

**User Story:** As a user, I want to use the list command to display tracked assets and offers.

#### Acceptance Criteria

1. THE list_Command SHALL accept subsection option (-app, -cmd, -ext, -def, -off, -all)
2. THE list_Command SHALL accept extension option for filtering (--md, --py, etc.)
3. THE list_Command SHALL accept -vb/--verbose flag for verbose output
4. WHEN list -def is called, THE System SHALL display defaults table
5. WHEN list -off is called, THE System SHALL display offers table
6. WHEN list -all is called, THE System SHALL display all subsections
7. IF invalid subsection is provided, THEN THE System SHALL raise InvalidSubsectionError (VE105)

### Requirement 15: Testing Infrastructure

**User Story:** As a developer, I want comprehensive tests, so that the CLI is reliable and correct.

#### Acceptance Criteria

1. THE Test_Suite SHALL use pytest as the testing framework
2. THE Test_Suite SHALL use Hypothesis for property-based testing
3. THE Test_Suite SHALL provide fixtures for isolated CLI testing (CliRunner, mock_executable, isolated_data_dir)
4. THE Test_Suite SHALL achieve minimum 85% code coverage
5. FOR ALL validation functions, THE Test_Suite SHALL include property-based tests with minimum 100 iterations
6. FOR ALL commands, THE Test_Suite SHALL include unit tests for success and error cases
