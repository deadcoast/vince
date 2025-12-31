# Error Catalog

This document provides a comprehensive catalog of all error codes used in the Vince CLI application. Each error is documented with its code, message template, severity level, and recommended recovery action.

## Error Code Format

Vince uses a structured error code format to categorize and identify errors consistently:

**Format:** `VE{category}{number}`

- **VE** - Vince Error prefix (all error codes start with this)
- **{category}** - Single digit (1-5) indicating the error category
- **{number}** - Two-digit number (01-99) identifying the specific error within the category

**Example:** `VE101` = Vince Error, Category 1 (Input), Error 01

## Error Categories

Errors are organized into five categories based on their source and nature:

| Range | Category | sid | Description |
|-------|----------|-----|-------------|
| VE1xx | Input | inp | Invalid user input errors - malformed arguments, invalid values |
| VE2xx | File | fil | File system operation errors - missing files, permission issues |
| VE3xx | State | sta | Invalid state transition errors - lifecycle violations |
| VE4xx | Config | cfg | Configuration errors - invalid options, malformed config files |
| VE5xx | System | sys | System-level errors - unexpected failures, resource issues |

## Error Registry

### Input Errors (VE1xx)

| Code | Message Template | Severity | Recovery Action |
|------|-----------------|----------|-----------------|
| VE101 | Invalid path: {path} does not exist | error | Verify the application path exists and is accessible |
| VE102 | Invalid extension: {ext} is not supported | error | Use a supported extension (--md, --py, etc.) |
| VE103 | Invalid offer_id: {id} does not match pattern | error | Use lowercase alphanumeric with hyphens/underscores (max 32 chars) |
| VE104 | Offer not found: {id} does not exist | error | Use `list -off` to see available offers |
| VE105 | Invalid list subsection: {section} | error | Use -app, -cmd, -ext, -def, -off, or -all |

### File Errors (VE2xx)

| Code | Message Template | Severity | Recovery Action |
|------|-----------------|----------|-----------------|
| VE201 | File not found: {path} | error | Check file path and ensure the file exists |
| VE202 | Permission denied: cannot access {path} | error | Check file permissions and ownership |
| VE203 | Data file corrupted: {file} | error | Restore from backup or delete and recreate the data file |

### State Errors (VE3xx)

| Code | Message Template | Severity | Recovery Action |
|------|-----------------|----------|-----------------|
| VE301 | Default already exists for {ext} | warning | Use `chop` to remove existing default first |
| VE302 | No default set for {ext} | warning | Use `slap` or `set` to create a default |
| VE303 | Offer already exists: {id} | warning | Use a different offer_id or reject existing offer |
| VE304 | Cannot reject: offer {id} is in use | error | Remove dependencies before rejecting |

### Config Errors (VE4xx)

| Code | Message Template | Severity | Recovery Action |
|------|-----------------|----------|-----------------|
| VE401 | Invalid config option: {key} | error | Check config.md for valid configuration options |
| VE402 | Config file malformed: {file} | error | Fix JSON syntax errors or restore default config |

### System Errors (VE5xx)

| Code | Message Template | Severity | Recovery Action |
|------|-----------------|----------|-----------------|
| VE501 | Unexpected error: {message} | error | Report issue with full error details to maintainers |

## Formatting Guidelines

Vince uses the Rich library for console output formatting. Error messages follow consistent formatting patterns for visual clarity.

### Rich Theme Colors

Error messages use the following color scheme:

```python
VINCE_THEME = Theme({
    "error": "red bold",
    "warning": "yellow",
    "info": "cyan",
    "success": "green",
    "code": "magenta",
    "path": "blue underline",
})
```

### Message Format Patterns

| Severity | Format | Rich Markup | Example Output |
|----------|--------|-------------|----------------|
| error | `[error]✗[/] {code}: {message}` | `[error]✗[/] VE101: Invalid path` | ✗ VE101: Invalid path |
| warning | `[warning]⚠[/] {code}: {message}` | `[warning]⚠[/] VE301: Default exists` | ⚠ VE301: Default exists |
| info | `[info]ℹ[/] {message}` | `[info]ℹ[/] Use -vb for details` | ℹ Use -vb for details |

### Rich Markup Examples

**Error with path highlighting:**

```python
console.print("[error]✗[/] VE101: Invalid path: [path]/usr/bin/missing[/] does not exist")
```

**Warning with extension highlighting:**

```python
console.print("[warning]⚠[/] VE301: Default already exists for [code].md[/]")
```

**Error with recovery suggestion:**

```python
console.print("[error]✗[/] VE104: Offer not found: [code]my-offer[/] does not exist")
console.print("[info]ℹ[/] Use [code]list -off[/] to see available offers")
```

### Structured Error Output

For verbose mode (`-vb`), errors include additional context:

```python
from rich.panel import Panel

error_panel = Panel(
    "[error]VE203: Data file corrupted[/]\n\n"
    "File: [path]~/.vince/defaults.json[/]\n"
    "Details: JSON decode error at line 15\n\n"
    "[info]Recovery:[/] Restore from backup or delete and recreate",
    title="Error",
    border_style="red"
)
console.print(error_panel)
```

## Cross-References

- See [tables.md](tables.md) for the ERRORS table with all error codes
- See [api.md](api.md) for command-specific exception documentation
- See [config.md](config.md) for configuration error handling
