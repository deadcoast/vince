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

## `sync`

Sync all active defaults to the operating system. This command applies all tracked defaults to the OS at once.

### Basic Usage

```sh
# Sync all active defaults to the OS
vince sync
```

### With Dry Run Flag

```sh
# Preview changes without applying them
vince sync -dry
```

### With Verbose Output

```sh
# Sync with verbose output
vince sync -vb

# Sync with long verbose flag
vince sync --verbose

# Dry run with verbose output
vince sync -dry -vb
```

### Multi-Step Workflow

```sh
# Step 1: Set up defaults
vince slap /path/to/app -set --md
vince slap /path/to/app -set --py

# Step 2: Preview what will be synced
vince sync -dry

# Step 3: Apply all defaults to OS
vince sync

# Step 4: Verify with list
vince list -def
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

## OS Integration Examples

The following examples demonstrate how vince integrates with the operating system to actually set file associations.

### Setting OS Defaults

When you use `-set` with `slap` or use the `set` command, vince configures the OS to use your chosen application:

```sh
# Set VS Code as default for markdown files (updates both JSON and OS)
vince slap /Applications/Visual\ Studio\ Code.app -set --md

# On Windows
vince slap "C:\Program Files\Microsoft VS Code\Code.exe" -set --md
```

### Dry Run Mode

Preview what OS changes would be made without actually applying them:

```sh
# Preview slap changes
vince slap /Applications/Sublime\ Text.app -set --py -dry

# Output shows:
# Would set com.sublimetext.4 as default for public.python-script
# Current OS default: com.apple.TextEdit
# Proposed new default: com.sublimetext.4
```

```sh
# Preview sync changes
vince sync -dry

# Output shows all pending OS changes:
# .md: Would set com.microsoft.VSCode as default
# .py: Already synced (no change needed)
# .json: Would set com.sublimetext.4 as default
```

### Sync Command

Apply all tracked defaults to the OS at once:

```sh
# Basic sync - apply all active defaults to OS
vince sync

# Preview what would be synced
vince sync -dry

# Sync with verbose output
vince sync -vb
```

### Sync Workflow Example

```sh
# Step 1: Set up multiple defaults (JSON only, no OS changes yet)
vince slap /Applications/Code.app --md
vince slap /Applications/Code.app --py
vince slap /Applications/Code.app --json

# Step 2: Activate them (still JSON only)
vince set /Applications/Code.app --md
vince set /Applications/Code.app --py
vince set /Applications/Code.app --json

# Step 3: Preview what will be synced to OS
vince sync -dry

# Step 4: Apply all defaults to OS at once
vince sync

# Step 5: Verify with list
vince list -def
```

### Removing OS Defaults

When you forget a default, vince also removes the OS association:

```sh
# Remove default for markdown files (updates both JSON and OS)
vince chop -forget --md

# Or using forget command
vince forget --md
```

### Dry Run with Remove

```sh
# Preview what would be removed from OS
vince chop -forget --md -dry

# Output shows:
# Would reset default for .md (UTI: net.daringfireball.markdown)
# Current OS default: com.microsoft.VSCode
# Will reset to: system default
```

### Handling OS Errors

If an OS operation fails, vince will warn you:

```sh
# If OS operation fails but JSON update succeeded
vince slap /Applications/Code.app -set --md

# Output might show:
# ✓ Default set for .md
# ⚠ OS operation failed: duti not installed
# ℹ Run 'vince sync' to retry OS changes
```

### macOS-Specific Examples

```sh
# Using duti (recommended - install with: brew install duti)
vince slap /Applications/Visual\ Studio\ Code.app -set --md

# Check current OS default
vince list -def
# Shows both vince default and actual OS default

# If duti is not installed, vince falls back to PyObjC
# Install duti for more reliable operation:
brew install duti
```

### Windows-Specific Examples

```sh
# Set default using full path to executable
vince slap "C:\Program Files\Microsoft VS Code\Code.exe" -set --md

# Or using a directory (vince finds the .exe)
vince slap "C:\Program Files\Microsoft VS Code" -set --md

# Check current OS default
vince list -def
```

### Verbose OS Operations

```sh
# See detailed OS operation output
vince slap /Applications/Code.app -set --md -vb

# Output shows:
# ℹ Processing slap command...
# ℹ Validating path: /Applications/Visual Studio Code.app
# ℹ Bundle ID: com.microsoft.VSCode
# ℹ UTI for .md: net.daringfireball.markdown
# ✓ Path validated
# ✓ Default set for .md
# ✓ OS default configured via duti
# ℹ Previous OS default: com.apple.TextEdit
```

### Rollback Example

If an OS operation fails partway through, vince attempts to rollback:

```sh
# If set_default fails after recording previous default
vince slap /Applications/Code.app -set --md

# Output might show:
# ✗ VE605: OS operation failed: Launch Services error
# ℹ Attempting rollback to previous default...
# ✓ Rollback successful: restored com.apple.TextEdit
```

### Checking OS Sync Status

```sh
# List defaults with OS status
vince list -def

# Output shows sync status:
# ╭─────────────────────────────────────────────────────────────╮
# │                         Defaults                            │
# ├───────────┬─────────────────────┬────────┬─────────────────┤
# │ Extension │ Application         │ State  │ OS Default      │
# ├───────────┼─────────────────────┼────────┼─────────────────┤
# │ .md       │ /Applications/Code  │ active │ ✓ synced        │
# │ .py       │ /Applications/Code  │ active │ ⚠ mismatch      │
# │ .json     │ /Applications/Code  │ active │ ✓ synced        │
# ╰───────────┴─────────────────────┴────────┴─────────────────╯
```

### Complete OS Integration Workflow

```sh
# 1. Set up defaults with OS integration
vince slap /Applications/Visual\ Studio\ Code.app -set --md
vince slap /Applications/Visual\ Studio\ Code.app -set --py
vince slap /Applications/Visual\ Studio\ Code.app -set --json

# 2. Verify OS defaults are set
vince list -def

# 3. Later, change one default
vince forget --py
vince slap /Applications/PyCharm.app -set --py

# 4. Sync any out-of-sync entries
vince sync

# 5. Remove all custom defaults (reset to system defaults)
vince forget --md
vince forget --py
vince forget --json
```
