# Examples

## Overview

This document provides usage examples for all vince CLI commands. Each example demonstrates correct flag syntax and common workflows.

## `slap`

Set an application as the default for a file extension. When used with `-set`, an `offer` is automatically created and added to the CLI list command (`list -off`).

> [!NOTE]
> The `slap` command auto-creates an `offer` for the default when using `-set`, making it available as a custom shortcut.

### Basic Usage

```sh
# Set application as default for markdown files (pending state)
vince slap /path/to/app --md

# Set application as default for python files (pending state)
vince slap /path/to/app --py
```

### With -set Flag (Active State)

```sh
# Set as active default immediately (also creates offer)
vince slap /path/to/app -set --md

# Set as active default for text files
vince slap /path/to/app -set --txt
```

### With Verbose Output

```sh
# Using verbose output with short flag
vince slap /path/to/app --md -vb

# Using verbose output with long flag
vince slap /path/to/app --md --verbose
```

### Multi-Step Workflow

```sh
# Step 1: Set application as pending default for markdown
vince slap /path/to/app --md

# Step 2: Verify the default was created
vince list -def

# Step 3: Set as active with offer creation
vince slap /path/to/app -set --md

# Step 4: Verify the offer was auto-created
vince list -off
```

## `chop`

Remove or forget a file extension association.

### Basic Usage

```sh
# Show current default for markdown files (no state change)
vince chop --md

# Show current default for python files
vince chop --py
```

### With -forget Flag (Remove Default)

```sh
# Remove the default for markdown files
vince chop -forget --md

# Remove the default for python files
vince chop -forget --py
```

### With Verbose Output

```sh
# Remove default with verbose output
vince chop -forget --md -vb

# Remove default with long verbose flag
vince chop -forget --py --verbose
```

## `set`

Set a default application for a file extension. Creates an active default entry immediately.

### Basic Usage

```sh
# Set application as active default for markdown files
vince set /path/to/app --md

# Set application as active default for text files
vince set /path/to/app --txt
```

### With Verbose Output

```sh
# Set default with verbose output
vince set /path/to/app --md -vb

# Set default with long verbose flag
vince set /path/to/app --json --verbose
```

### Multi-Step Workflow

```sh
# Step 1: Set application as default for json extension
vince set /path/to/app --json

# Step 2: Verify the default was set
vince list -def

# Step 3: Create an offer for quick access
vince offer my-json-editor /path/to/app --json
```

## `forget`

Forget a default for a file extension. Transitions the default state to removed.

### Basic Usage

```sh
# Forget the default for markdown files
vince forget --md

# Forget the default for python files
vince forget --py
```

### With Verbose Output

```sh
# Forget default with verbose output
vince forget --md -vb

# Forget default with long verbose flag
vince forget --py --verbose
```

## `offer`

Create a custom shortcut/alias for quick access.

### Basic Usage

```sh
# Create an offer for a specific application
vince offer my-editor /path/to/app --md

# Create an offer with extension association
vince offer code-py /path/to/vscode --py
```

### With Verbose Output

```sh
# Create offer with verbose output
vince offer my-editor /path/to/app --md -vb

# Create offer with long verbose flag
vince offer my-editor /path/to/app --txt --verbose
```

## `reject`

Remove a custom offer/shortcut.

### Basic Usage

```sh
# Remove a specific offer by ID
vince reject my-editor
```

### Complete Delete Workflow

```sh
# Step 1: List all offers to find the target
vince list -off

# Step 2: Reject the specific offer (transitions to rejected state)
vince reject my-editor

# Step 3: Verify the offer was removed
vince list -off
```

### With Complete Delete Flag

```sh
# Permanently remove offer from data file
vince reject my-editor -.
```

### With Verbose Output

```sh
# Reject offer with verbose output
vince reject my-editor -vb

# Reject offer with long verbose flag
vince reject my-editor --verbose
```

## `list`

Display tracked assets and offers.

> [!NOTE]
> When no subsection flag is specified, `-all` is used by default.

### Show All Lists

```sh
# Show all lists using -all flag
vince list -all

# Show all lists (default behavior)
vince list
```

### List Applications

```sh
# List all tracked applications
vince list -app
```

### List Commands

```sh
# List all available commands/offers
vince list -cmd
```

### List Extensions

```sh
# List all tracked extensions
vince list -ext
```

### List Defaults

```sh
# List all set defaults
vince list -def
```

### List Offers

```sh
# List all custom offers
vince list -off

# List offers filtered by extension
vince list -off --md
```

### Combined Examples

```sh
# List defaults with verbose output
vince list -def -vb

# List offers with verbose output
vince list -off --verbose
```

## Extension Flag Examples

All 12 supported extensions with their flags:

### Markdown (.md)

```sh
vince slap /path/to/app --md
vince set /path/to/app --md
vince forget --md
vince list -def --md
```

### Python (.py)

```sh
vince slap /path/to/app --py
vince set /path/to/app --py
vince forget --py
vince list -def --py
```

### Text (.txt)

```sh
vince slap /path/to/app --txt
vince set /path/to/app --txt
vince forget --txt
vince list -def --txt
```

### JavaScript (.js)

```sh
vince slap /path/to/app --js
vince set /path/to/app --js
vince forget --js
vince list -def --js
```

### HTML (.html)

```sh
vince slap /path/to/app --html
vince set /path/to/app --html
vince forget --html
vince list -def --html
```

### CSS (.css)

```sh
vince slap /path/to/app --css
vince set /path/to/app --css
vince forget --css
vince list -def --css
```

### JSON (.json)

```sh
vince slap /path/to/app --json
vince set /path/to/app --json
vince forget --json
vince list -def --json
```

### YAML (.yml)

```sh
vince slap /path/to/app --yml
vince set /path/to/app --yml
vince forget --yml
vince list -def --yml
```

### YAML (.yaml)

```sh
vince slap /path/to/app --yaml
vince set /path/to/app --yaml
vince forget --yaml
vince list -def --yaml
```

### XML (.xml)

```sh
vince slap /path/to/app --xml
vince set /path/to/app --xml
vince forget --xml
vince list -def --xml
```

### CSV (.csv)

```sh
vince slap /path/to/app --csv
vince set /path/to/app --csv
vince forget --csv
vince list -def --csv
```

### SQL (.sql)

```sh
vince slap /path/to/app --sql
vince set /path/to/app --sql
vince forget --sql
vince list -def --sql
```

## QOL Flag Examples

Quality of Life flags that mirror command behavior:

### -set Flag (with slap)

```sh
# Set as active default immediately
vince slap /path/to/app -set --md

# Equivalent to running slap then set
vince slap /path/to/app --md
vince set /path/to/app --md
```

### -forget Flag (with chop)

```sh
# Remove the default for an extension
vince chop -forget --md

# Equivalent to running forget
vince forget --md
```

## Cross-References

- [API Documentation](api.md) - Command function signatures and parameters
- [Tables Reference](tables.md) - Complete flag and command definitions
- [Errors Reference](errors.md) - Error codes that may be raised
- [States Reference](states.md) - State transitions for defaults and offers
