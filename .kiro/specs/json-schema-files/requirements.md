# Requirements Document

## Introduction

This feature extracts the JSON schema definitions from `docs/schemas.md` into actual `.json` schema files in the `schemas/` directory and integrates schema validation into the persistence layer. The schemas follow JSON Schema Draft-07 and define the structure for `defaults.json`, `offers.json`, and `config.json` data files.

Reference: #[[file:docs/schemas.md]]

## Glossary

- **Schema_Validator**: Module at `vince/validation/schema.py` that validates JSON data against JSON Schema Draft-07
- **Persistence_Layer**: The `vince/persistence/` modules (base.py, defaults.py, offers.py) that handle data file I/O
- **Data_File**: JSON files storing vince data (defaults.json, offers.json, config.json) in `{data_dir}/`
- **DefaultEntry**: A single default application association with fields: id, extension, application_path, application_name, state, os_synced, os_synced_at, previous_os_default, created_at, updated_at
- **OfferEntry**: A single offer/alias definition with fields: offer_id, default_id, state, auto_created, description, created_at, used_at

## Requirements

### Requirement 1: Create Defaults Schema File

**User Story:** As a developer, I want `schemas/defaults.schema.json` extracted from docs/schemas.md, so that I can validate defaults.json programmatically.

#### Acceptance Criteria

1. THE Schema_Validator SHALL provide `schemas/defaults.schema.json` using JSON Schema Draft-07
2. THE defaults schema SHALL define `version` as required string matching pattern `^\d+\.\d+\.\d+$`
3. THE defaults schema SHALL define `defaults` as required array of DefaultEntry objects
4. THE DefaultEntry definition SHALL require fields: `id`, `extension`, `application_path`, `state`, `created_at`
5. THE DefaultEntry definition SHALL define `state` as enum with values: `pending`, `active`, `removed`
6. THE DefaultEntry definition SHALL define `extension` pattern as `^\.[a-z0-9]+$`
7. THE DefaultEntry definition SHALL define `os_synced` as optional boolean defaulting to false
8. THE defaults schema SHALL set `additionalProperties: false` to reject unknown fields

### Requirement 2: Create Offers Schema File

**User Story:** As a developer, I want `schemas/offers.schema.json` extracted from docs/schemas.md, so that I can validate offers.json programmatically.

#### Acceptance Criteria

1. THE Schema_Validator SHALL provide `schemas/offers.schema.json` using JSON Schema Draft-07
2. THE offers schema SHALL define `version` as required string matching pattern `^\d+\.\d+\.\d+$`
3. THE offers schema SHALL define `offers` as required array of OfferEntry objects
4. THE OfferEntry definition SHALL require fields: `offer_id`, `default_id`, `state`, `created_at`
5. THE OfferEntry definition SHALL define `state` as enum with values: `created`, `active`, `rejected`
6. THE OfferEntry definition SHALL define `offer_id` pattern as `^[a-z][a-z0-9_-]{0,31}$`
7. THE OfferEntry definition SHALL define `description` with maxLength 256
8. THE offers schema SHALL set `additionalProperties: false` to reject unknown fields

### Requirement 3: Create Config Schema File

**User Story:** As a developer, I want `schemas/config.schema.json` extracted from docs/schemas.md, so that I can validate config.json programmatically.

#### Acceptance Criteria

1. THE Schema_Validator SHALL provide `schemas/config.schema.json` using JSON Schema Draft-07
2. THE config schema SHALL define `version` as the only required field
3. THE config schema SHALL define `data_dir` as optional string with default `~/.vince`
4. THE config schema SHALL define `verbose` as optional boolean with default false
5. THE config schema SHALL define `color_theme` as enum with values: `default`, `dark`, `light`
6. THE config schema SHALL define `backup_enabled` as optional boolean with default true
7. THE config schema SHALL define `max_backups` as integer with minimum 0 and maximum 100
8. THE config schema SHALL define `confirm_destructive` as optional boolean with default true
9. THE config schema SHALL set `additionalProperties: false` to reject unknown fields

### Requirement 4: Schema Validation Module

**User Story:** As a developer, I want a validation module at `vince/validation/schema.py` that uses the schema files, so that I can validate data at runtime.

#### Acceptance Criteria

1. THE Schema_Validator SHALL provide `load_schema(schema_name)` function to load schema from `schemas/` directory
2. THE Schema_Validator SHALL provide `validate_defaults(data)` function that validates against defaults schema
3. THE Schema_Validator SHALL provide `validate_offers(data)` function that validates against offers schema
4. THE Schema_Validator SHALL provide `validate_config(data)` function that validates against config schema
5. WHEN validation fails for defaults or offers, THE Schema_Validator SHALL raise DataCorruptedError (VE203)
6. WHEN validation fails for config, THE Schema_Validator SHALL raise InvalidConfigOptionError (VE401)
7. IF jsonschema library is not installed, THEN THE Schema_Validator SHALL skip validation without error

### Requirement 5: Persistence Layer Integration

**User Story:** As a developer, I want the persistence layer to validate data on load, so that corrupted or invalid data is caught early.

#### Acceptance Criteria

1. WHEN `load_json()` is called with a schema_name parameter, THE Persistence_Layer SHALL validate loaded data
2. WHEN DefaultsStore.load() is called, THE Persistence_Layer SHALL validate against defaults schema
3. WHEN OffersStore.load() is called, THE Persistence_Layer SHALL validate against offers schema
4. WHEN get_config() loads config, THE Persistence_Layer SHALL validate against config schema
5. WHEN schema validation fails, THE Persistence_Layer SHALL raise the appropriate VinceError

### Requirement 6: Add jsonschema Dependency

**User Story:** As a developer, I want jsonschema as an optional dependency, so that validation works when installed but doesn't break the app when missing.

#### Acceptance Criteria

1. THE project SHALL list `jsonschema>=4.0.0` in optional-dependencies under `[project.optional-dependencies]` in pyproject.toml
2. WHEN jsonschema is not installed, THE Schema_Validator SHALL catch ImportError and skip validation
3. THE Schema_Validator SHALL NOT crash the application when jsonschema is missing
