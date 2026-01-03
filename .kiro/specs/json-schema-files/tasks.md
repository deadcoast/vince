# Implementation Plan: JSON Schema Files

## Overview

Extract JSON schemas from `docs/schemas.md` into actual `.json` files in `schemas/` directory and integrate schema validation into the persistence layer.

## Tasks

- [x] 1. Create schema files from docs/schemas.md
  - [x] 1.1 Create `schemas/defaults.schema.json` with DefaultEntry definition
    - Extract verbatim from docs/schemas.md "Defaults Schema" section
    - Include all fields: id, extension, application_path, application_name, state, os_synced, os_synced_at, previous_os_default, created_at, updated_at
    - *Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8*
  - [x] 1.2 Create `schemas/offers.schema.json` with OfferEntry definition
    - Extract verbatim from docs/schemas.md "Offers Schema" section
    - Include all fields: offer_id, default_id, state, auto_created, description, created_at, used_at
    - *Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8*
  - [x] 1.3 Create `schemas/config.schema.json` with config options
    - Extract verbatim from docs/schemas.md "Config Schema" section
    - Include all fields: version, data_dir, verbose, color_theme, backup_enabled, max_backups, confirm_destructive
    - *Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9*

- [x] 2. Create schema validation module
  - [x] 2.1 Create `vince/validation/schema.py` with load_schema() function
    - Load schema from `schemas/` directory by name
    - *Requirements: 4.1*
  - [x] 2.2 Add validate_against_schema() function
    - Use jsonschema library for validation
    - Raise DataCorruptedError (VE203) for defaults/offers failures
    - Raise InvalidConfigOptionError (VE401) for config failures
    - *Requirements: 4.5, 4.6*
  - [x] 2.3 Add convenience functions validate_defaults(), validate_offers(), validate_config()
    - *Requirements: 4.2, 4.3, 4.4*
  - [x] 2.4 Add graceful ImportError handling for missing jsonschema
    - Skip validation without error when jsonschema not installed
    - *Requirements: 4.7, 6.2, 6.3*

- [x] 3. Integrate validation into persistence layer
  - [x] 3.1 Modify `vince/persistence/base.py` load_json() to accept schema_name parameter
    - Add optional schema_name parameter
    - Call validate_against_schema() when schema_name provided
    - *Requirements: 5.1*
  - [x] 3.2 Modify `vince/persistence/defaults.py` to pass schema_name="defaults"
    - Update load() method to use schema validation
    - *Requirements: 5.2*
  - [x] 3.3 Modify `vince/persistence/offers.py` to pass schema_name="offers"
    - Update load() method to use schema validation
    - *Requirements: 5.3*
  - [x] 3.4 Modify `vince/config.py` to validate config on load
    - Add schema validation to get_config()
    - *Requirements: 5.4, 5.5*

- [x] 4. Add jsonschema dependency
  - [x] 4.1 Add `jsonschema>=4.0.0` to pyproject.toml optional-dependencies
    - Add under dev or validation optional group
    - *Requirements: 6.1*

- [x] 5. Checkpoint - Verify schema files and validation work
  - Ensure all tests pass, ask the user if questions arise.

- [x] 6. Write tests for schema validation
  - [x] 6.1 Write unit tests for schema file loading
    - Test each schema loads as valid JSON
    - Test schema structure matches docs/schemas.md
    - *Requirements: 1.1, 2.1, 3.1*
  - [x] 6.2 Write property test for version pattern validation
    - **Property 1: Version pattern validation**
    - *For any* string, validation passes iff it matches `^\d+\.\d+\.\d+$`
    - **Validates: Requirements 1.2, 2.2**
  - [x] 6.3 Write property test for required fields rejection
    - **Property 2: Required fields enforcement**
    - *For any* entry missing a required field, validation SHALL fail
    - **Validates: Requirements 1.4, 2.4**
  - [x] 6.4 Write property test for enum validation
    - **Property 3: Enum value enforcement**
    - *For any* entry with invalid enum value, validation SHALL fail
    - **Validates: Requirements 1.5, 2.5, 3.5**
  - [x] 6.5 Write property test for additionalProperties rejection
    - **Property 4: Unknown field rejection**
    - *For any* data with unknown fields, validation SHALL fail
    - **Validates: Requirements 1.8, 2.8, 3.9**
  - [x] 6.6 Write unit test for graceful degradation without jsonschema
    - Mock ImportError and verify no crash
    - **Validates: Requirements 4.7, 6.2, 6.3**

- [x] 7. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 8. Document schema validation module
  - [x] 8.1 Add schema validation section to docs/schemas.md
    - Document `vince/validation/schema.py` module
    - Document `load_schema()`, `validate_defaults()`, `validate_offers()`, `validate_config()` functions
    - Document graceful degradation when jsonschema not installed
    - *Requirements: 4.1, 4.2, 4.3, 4.4, 4.7*
  - [x] 8.2 Update docs/errors.md with schema validation errors
    - Document VE203 (DataCorruptedError) for schema validation failures
    - Document VE401 (InvalidConfigOptionError) for config validation failures
    - *Requirements: 4.5, 4.6*
  - [x] 8.3 Add jsonschema to installation docs
    - Document that jsonschema is optional dependency
    - Show how to install: `pip install vince[dev]` or `pip install jsonschema`
    - *Requirements: 6.1, 6.2, 6.3*

## Notes

- Schema files are extracted verbatim from docs/schemas.md to ensure consistency
- jsonschema is optional - validation is skipped gracefully when not installed
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
