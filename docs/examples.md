# Examples

## `slap`

Set an application as the default for a file extension. When a slap is set, an `offer` is automatically created and added to the CLI list command (`list -off`).

> [!NOTE]
> The `slap` command auto-creates an `offer` for the default, making it available as a custom shortcut.

### Basic Usage

```sh
# S1: Set application as default for markdown files
vince slap <path/to/application/app.exe> --md

# S2: Set application as default for python files
vince slap <path/to/application/app.exe> --py
```

### With QOL Flag Combinations

```sh
# S1: Using -set flag with extension
vince slap <path/to/application/app.exe> -set --md

# S2: Using verbose output
vince slap <path/to/application/app.exe> --md -vb

# S3: Using debug mode
vince slap <path/to/application/app.exe> --md -db
```

### Multi-Step Workflow

```sh
# S1: Identify an application path to set as default
vince slap <path/to/application/app.exe>

# S2: Set S1 application as default for markdown extension
vince slap <path/to/application/app.exe> --md

# S3: Verify the offer was auto-created
vince list -off
```

## `chop`

Remove or forget a file extension association.

### Basic Usage

```sh
# S1: Remove the default for markdown files
vince chop --md

# S2: Remove the default for python files
vince chop --py
```

### With `.` Operator (All Extensions)

```sh
# S1: Remove all file extension associations
vince chop .
```

### With Flag Combinations

```sh
# S1: Remove default with verbose output
vince chop --md -vb

# S2: Remove default with debug mode
vince chop --py -db
```

## `set`

Set a default application for a file extension. Unlike `slap`, this is the direct command form without auto-offer creation.

### Basic Usage

```sh
# S1: Set application as default for markdown files
vince set <path/to/application/app.exe> --md

# S2: Set application as default for text files
vince set <path/to/application/app.exe> --txt
```

### With QOL Flag Combinations

```sh
# S1: Using -set flag explicitly
vince set <path/to/application/app.exe> -set --md

# S2: Using verbose output
vince set <path/to/application/app.exe> --md -vb

# S3: Using debug mode
vince set <path/to/application/app.exe> --md -db
```

### Multi-Step Workflow

```sh
# S1: Identify an application path
vince set <path/to/application/app.exe>

# S2: Set S1 application as default for json extension
vince set <path/to/application/app.exe> --json

# S3: Verify the default was set
vince list -def
```

## `forget`

Forget a default for a file extension.

### Basic Usage

```sh
# S1: Forget the default for markdown files
vince forget --md

# S2: Forget the default for python files
vince forget --py
```

### With `.` Operator (All Extensions)

```sh
# S1: Forget all file extension defaults
vince forget .
```

### With Flag Combinations

```sh
# S1: Forget default with verbose output
vince forget --md -vb

# S2: Forget default with debug mode
vince forget --py -db
```

## `offer`

Create a custom shortcut/alias for quick access.

### Basic Usage

```sh
# S1: Create an offer for a specific application
vince offer <offer_id> <path/to/application/app.exe>

# S2: Create an offer with extension association
vince offer <offer_id> <path/to/application/app.exe> --md
```

### With Flag Combinations

```sh
# S1: Create offer with verbose output
vince offer <offer_id> <path/to/application/app.exe> -vb

# S2: Create offer using -offer flag
vince offer <offer_id> <path/to/application/app.exe> -offer
```

## `reject`

Remove a custom offer/shortcut.

### Basic Usage

```sh
# S1: Remove a specific offer by ID
vince reject <offer_id>
```

### Complete Delete Workflow

```sh
# S1: List all offers to find the target
vince list -off

# S2: Reject the specific offer
vince reject <offer_id>

# S3: Verify the offer was removed
vince list -off
```

### With Flag Combinations

```sh
# S1: Reject offer with verbose output
vince reject <offer_id> -vb

# S2: Reject offer with debug mode
vince reject <offer_id> -db
```

## `list`

Display tracked assets and offers.

> [!NOTE]
> The `.` operator shows all subsections at once.

### Show All Lists

```sh
# S1: Show all lists using the wildcard operator
vince list .

# S2: Alternative using -all flag
vince list -all
```

### List Applications

```sh
# S1: List all tracked applications
vince list -app
```

### List Commands

```sh
# S1: List all available commands
vince list -cmd
```

### List Extensions

```sh
# S1: List all tracked extensions
vince list -ext
```

### List Defaults

```sh
# S1: List all set defaults
vince list -def
```

### List Offers

```sh
# S1: List all custom offers
vince list -off

# S2: List offers filtered by extension
vince list -off --md
```

### Combined Examples

```sh
# S1: List defaults with verbose output
vince list -def -vb

# S2: List offers with debug mode
vince list -off -db
```
