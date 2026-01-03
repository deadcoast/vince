# README.md

![vince-logo](https://github.com/deadcoast/vince/blob/master/assets/logo.png)

A Rich CLI for setting default applications to file extensions.

## Installation

```bash
pip install vince
```

Or with uv:

```bash
uv pip install vince
```

## Usage

```bash
# See all commands
vince --help

# Set VS Code as default for .md files
vince slap /Applications/Visual\ Studio\ Code.app --md -set

# List all defaults
vince list

# Remove a default
vince chop --md -forget

# Sync all defaults to OS
vince sync
```

## Commands

| Command | Description |
|---------|-------------|
| `slap` | Set application as default for extension |
| `chop` | Remove file extension association |
| `set` | Set a default for file extension |
| `forget` | Forget a default for file extension |
| `offer` | Create custom shortcut/alias |
| `reject` | Remove custom offer |
| `list` | Display tracked assets and offers |
| `sync` | Sync all defaults to OS |

## Documentation

- [Overview](docs/overview.md) - Commands, flags, and rules
- [API](docs/api.md) - Python interface documentation
- [Examples](docs/examples.md) - Usage examples
- [Errors](docs/errors.md) - Error codes and recovery
- [Config](docs/config.md) - Configuration options

## Development

```bash
# Clone and install
git clone https://github.com/deadcoast/vince.git
cd vince
uv sync

# Run tests
uv run pytest

# Type check
uv run mypy vince/
```
