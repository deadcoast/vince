# Configuration

This document provides comprehensive documentation for the vince CLI configuration system, including file hierarchy, configuration options, validation rules, precedence behavior, and example configurations.

> [!NOTE]
> For JSON schema definitions, see [schemas.md](schemas.md). For definition tables, see [tables.md](tables.md).

## File Hierarchy

The vince CLI uses a layered configuration system that allows settings to be defined at multiple levels. Configuration files are discovered and merged in a specific order to provide flexibility for both user-wide and project-specific settings.

### Configuration Levels

| Level | Location | Purpose | sid |
|-------|----------|---------|-----|
| Default | Built-in | Hardcoded defaults in application code | cfg-def |
| User | `~/.vince/config.json` | User-wide settings across all projects | cfg-usr |
| Project | `./.vince/config.json` | Project-specific overrides | cfg-prj |

### Discovery Order

Configuration files are discovered in the following order (lowest to highest priority):

```text
1. Default (built-in)     ← Base configuration
       ↓
2. User (~/.vince/)       ← User preferences
       ↓
3. Project (./.vince/)    ← Project overrides
```

### File Locations

| Location | Path | Description |
|----------|------|-------------|
| User config | `~/.vince/config.json` | User home directory configuration |
| Project config | `./.vince/config.json` | Current working directory configuration |
| Data directory | `{data_dir}/` | Configurable via `data_dir` option |

### Directory Structure

```text
~/.vince/                    # User-level data directory
├── config.json              # User configuration
├── defaults.json            # Default associations
├── offers.json              # Custom offers
└── backups/                 # Backup files

./.vince/                    # Project-level (optional)
└── config.json              # Project configuration overrides
```

## Config Options

All configuration options with their types, default values, and descriptions:

| Key | Type | Default | Description | sid |
|-----|------|---------|-------------|-----|
| `version` | string | Required | Schema version in semver format | cfg-ver |
| `data_dir` | string | `~/.vince` | Data storage directory path | cfg-dir |
| `verbose` | boolean | `false` | Enable verbose output by default | cfg-vb |
| `color_theme` | enum | `default` | Console color theme | cfg-thm |
| `backup_enabled` | boolean | `true` | Enable automatic backups before writes | cfg-bak |
| `max_backups` | integer | `5` | Maximum number of backup files to retain | cfg-max |
| `confirm_destructive` | boolean | `true` | Require confirmation for destructive operations | cfg-cfm |

### Option Details

#### version

- **Type:** `string`
- **Required:** Yes
- **Pattern:** `^\d+\.\d+\.\d+$`
- **Description:** Schema version in semantic versioning format. Used for migration detection.

#### data_dir

- **Type:** `string`
- **Default:** `~/.vince`
- **Description:** Directory path where vince stores data files (defaults.json, offers.json, backups). Supports tilde expansion for home directory.

#### verbose

- **Type:** `boolean`
- **Default:** `false`
- **Description:** When enabled, commands output additional diagnostic information. Can be overridden per-command with `-vb` flag.

#### color_theme

- **Type:** `enum`
- **Default:** `default`
- **Values:** `default`, `dark`, `light`
- **Description:** Console color theme for Rich output formatting.

#### backup_enabled

- **Type:** `boolean`
- **Default:** `true`
- **Description:** When enabled, vince creates backup copies of data files before each write operation.

#### max_backups

- **Type:** `integer`
- **Default:** `5`
- **Range:** `0` to `100`
- **Description:** Maximum number of backup files to retain per data file. Oldest backups are deleted when limit is exceeded. Set to `0` to disable backup retention.

#### confirm_destructive

- **Type:** `boolean`
- **Default:** `true`
- **Description:** When enabled, destructive operations (like `chop`, `forget`, `reject`) require user confirmation before proceeding.

## Validation

Configuration files are validated against the JSON schema when loaded. Validation ensures type correctness and constraint compliance.

### Type Validation

| Option | Type Check | Error Code |
|--------|------------|------------|
| `version` | Must be string | VE401 |
| `data_dir` | Must be string | VE401 |
| `verbose` | Must be boolean | VE401 |
| `color_theme` | Must be string | VE401 |
| `backup_enabled` | Must be boolean | VE401 |
| `max_backups` | Must be integer | VE401 |
| `confirm_destructive` | Must be boolean | VE401 |

### Constraint Validation

| Option | Constraint | Rule | Error Code |
|--------|------------|------|------------|
| `version` | Pattern | Must match `^\d+\.\d+\.\d+$` | VE401 |
| `color_theme` | Enum | Must be one of: `default`, `dark`, `light` | VE401 |
| `max_backups` | Minimum | Must be >= 0 | VE401 |
| `max_backups` | Maximum | Must be <= 100 | VE401 |

### Path Validation

The `data_dir` option undergoes additional path validation:

| Check | Description | Error Code |
|-------|-------------|------------|
| Expansion | Tilde (`~`) is expanded to home directory | - |
| Existence | Directory must exist or be creatable | VE201 |
| Permissions | Directory must be readable and writable | VE202 |

### Validation Process

```text
┌─────────────────────┐
│ Load Config File    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐     ┌─────────────────────┐
│ Parse JSON          │────►│ VE402: Malformed    │
│                     │ err └─────────────────────┘
└──────────┬──────────┘
           │ ok
           ▼
┌─────────────────────┐     ┌─────────────────────┐
│ Validate Types      │────►│ VE401: Invalid type │
│                     │ err └─────────────────────┘
└──────────┬──────────┘
           │ ok
           ▼
┌─────────────────────┐     ┌─────────────────────┐
│ Validate Constraints│────►│ VE401: Invalid value│
│                     │ err └─────────────────────┘
└──────────┬──────────┘
           │ ok
           ▼
┌─────────────────────┐
│ Config Valid        │
└─────────────────────┘
```

## Precedence

Configuration values are merged using a layered precedence system where higher-priority sources override lower-priority ones.

### Precedence Order

```text
Priority (highest to lowest):
┌─────────────────────────────────────────┐
│ 1. Command-line flags (e.g., -vb)       │  ← Highest
├─────────────────────────────────────────┤
│ 2. Project config (./.vince/config.json)│
├─────────────────────────────────────────┤
│ 3. User config (~/.vince/config.json)   │
├─────────────────────────────────────────┤
│ 4. Built-in defaults                    │  ← Lowest
└─────────────────────────────────────────┘
```

### Merge Behavior

Configuration merging follows these rules:

1. **Shallow merge:** Only top-level keys are merged (no deep object merging)
2. **Override:** Higher-priority values completely replace lower-priority values
3. **Missing keys:** If a key is absent, the next lower priority value is used
4. **Type preservation:** Merged values retain their original types

### Precedence Examples

#### Example 1: User Overrides Default

**Built-in defaults:**
```json
{
  "verbose": false,
  "max_backups": 5
}
```

**User config (~/.vince/config.json):**
```json
{
  "version": "1.0.0",
  "verbose": true
}
```

**Effective configuration:**
```json
{
  "version": "1.0.0",
  "verbose": true,      // From user config
  "max_backups": 5      // From defaults
}
```

#### Example 2: Project Overrides User

**User config (~/.vince/config.json):**
```json
{
  "version": "1.0.0",
  "verbose": true,
  "color_theme": "dark",
  "max_backups": 10
}
```

**Project config (./.vince/config.json):**
```json
{
  "version": "1.0.0",
  "color_theme": "light",
  "confirm_destructive": false
}
```

**Effective configuration:**
```json
{
  "version": "1.0.0",
  "verbose": true,              // From user config
  "color_theme": "light",       // From project config (overrides user)
  "max_backups": 10,            // From user config
  "confirm_destructive": false  // From project config
}
```

#### Example 3: Command-Line Override

**Effective config (from files):**
```json
{
  "version": "1.0.0",
  "verbose": false
}
```

**Command executed:**
```bash
vince list -all -vb
```

**Runtime behavior:**
- `verbose` is `true` for this command (flag overrides config)
- Config file is not modified

### Precedence Table

| Option | CLI Flag | Project | User | Default |
|--------|----------|---------|------|---------|
| verbose | `-vb` | ✓ | ✓ | `false` |
| color_theme | - | ✓ | ✓ | `default` |
| backup_enabled | - | ✓ | ✓ | `true` |
| max_backups | - | ✓ | ✓ | `5` |
| confirm_destructive | - | ✓ | ✓ | `true` |
| data_dir | - | ✓ | ✓ | `~/.vince` |

## Examples

### Minimal Configuration

The simplest valid configuration file with only the required `version` field:

```json
{
  "version": "1.0.0"
}
```

All other options use their default values.

### Full Configuration

A complete configuration file with all options explicitly set:

```json
{
  "version": "1.0.0",
  "data_dir": "~/.vince",
  "verbose": false,
  "color_theme": "default",
  "backup_enabled": true,
  "max_backups": 5,
  "confirm_destructive": true
}
```

### Development Configuration

A configuration optimized for development with verbose output and no confirmations:

```json
{
  "version": "1.0.0",
  "verbose": true,
  "color_theme": "dark",
  "confirm_destructive": false,
  "max_backups": 10
}
```

### Project-Specific Configuration

A project configuration that uses a local data directory and light theme:

```json
{
  "version": "1.0.0",
  "data_dir": "./.vince-data",
  "color_theme": "light",
  "backup_enabled": true,
  "max_backups": 3
}
```

### CI/CD Configuration

A configuration for automated environments with minimal interaction:

```json
{
  "version": "1.0.0",
  "verbose": false,
  "confirm_destructive": false,
  "backup_enabled": false,
  "max_backups": 0
}
```

### High-Reliability Configuration

A configuration prioritizing data safety with maximum backups:

```json
{
  "version": "1.0.0",
  "backup_enabled": true,
  "max_backups": 100,
  "confirm_destructive": true
}
```

## Error Handling

When configuration errors occur, vince provides clear error messages with recovery guidance.

### Error Codes

| Code | Condition | Message Template | Recovery |
|------|-----------|------------------|----------|
| VE401 | Invalid option | Invalid config option: {key} | Check config.md for valid options |
| VE402 | Malformed JSON | Config file malformed: {file} | Fix JSON syntax or restore default |

### Invalid Option Errors (VE401)

Triggered when a configuration option has an invalid type or value:

**Example: Invalid type**
```json
{
  "version": "1.0.0",
  "verbose": "yes"  // Should be boolean
}
```

**Error output:**
```text
✗ VE401: Invalid config option: verbose
  Expected: boolean
  Received: string ("yes")
  
ℹ Check docs/config.md for valid configuration options
```

**Example: Invalid enum value**
```json
{
  "version": "1.0.0",
  "color_theme": "blue"  // Not a valid theme
}
```

**Error output:**
```text
✗ VE401: Invalid config option: color_theme
  Expected: one of [default, dark, light]
  Received: "blue"
  
ℹ Valid themes: default, dark, light
```

**Example: Out of range**
```json
{
  "version": "1.0.0",
  "max_backups": 500  // Exceeds maximum
}
```

**Error output:**
```text
✗ VE401: Invalid config option: max_backups
  Expected: integer between 0 and 100
  Received: 500
  
ℹ Set max_backups to a value between 0 and 100
```

### Malformed Config Errors (VE402)

Triggered when the configuration file contains invalid JSON:

**Example: Syntax error**
```json
{
  "version": "1.0.0",
  "verbose": true,  // Trailing comma
}
```

**Error output:**
```text
✗ VE402: Config file malformed: ~/.vince/config.json
  JSON parse error at line 4: Unexpected token '}'
  
ℹ Fix JSON syntax errors or delete the file to use defaults
```

### Recovery Procedures

| Error | Recovery Steps |
|-------|----------------|
| VE401 | 1. Open config file<br>2. Fix the invalid option value<br>3. Save and retry |
| VE402 | 1. Validate JSON syntax (use a JSON linter)<br>2. Fix syntax errors<br>3. Or delete file to reset to defaults |

### Fallback Behavior

When a configuration file cannot be loaded:

1. **User config invalid:** Fall back to built-in defaults, show warning
2. **Project config invalid:** Fall back to user config (if valid) or defaults, show warning
3. **Both invalid:** Use built-in defaults, show error for each invalid file

**Warning output example:**
```text
⚠ Could not load user config: ~/.vince/config.json
  Reason: VE402 - JSON parse error
  Using built-in defaults
  
ℹ Run 'vince config --reset' to create a fresh config file
```

## Cross-References

- See [schemas.md](schemas.md) for the complete JSON schema definition
- See [errors.md](errors.md) for detailed error code documentation
- See [tables.md](tables.md) for the CONFIG_OPTIONS table
- See [api.md](api.md) for programmatic configuration access
