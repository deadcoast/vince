# vince

A Rich CLI for setting default applications to file extensions.

## Overview

**vince** is a sophisticated command-line interface application built with Python, Typer, and Rich. It provides an intuitive way to manage default application associations for file extensions with elevated visual ASCII UI delivery.

The CLI offers:
- Quick default application assignment with `slap` and `set` commands
- Easy removal of associations with `chop` and `forget` commands
- Custom shortcut creation via `offer` and `reject` commands
- Comprehensive listing with the `list` command

## Documentation

For detailed documentation, see the [docs/](docs/) directory:

- [Overview](docs/overview.md) - System design, commands, flags, and rules
- [API](docs/api.md) - Python interface documentation for all CLI commands
- [Schemas](docs/schemas.md) - JSON schemas for defaults, offers, and configuration
- [Errors](docs/errors.md) - Error catalog with codes, messages, and recovery actions
- [States](docs/states.md) - State machine documentation for defaults and offers
- [Config](docs/config.md) - Configuration options, hierarchy, and precedence
- [Tables](docs/tables.md) - Complete reference tables for all definitions
- [Examples](docs/examples.md) - Practical usage examples for all commands
- [Testing](docs/testing.md) - Testing patterns, fixtures, and examples

## Quick Start

```bash
# Install dependencies
uv sync

# Run the CLI
uv run python -m vince --help

# Example: Set VS Code as default for .md files
uv run python -m vince slap /usr/bin/code --md -set
```

## Installation

See [docs/README.md](docs/README.md) for detailed installation instructions.

## Development

```bash
# Run tests
uv run pytest

# Run validation
uv run python validate_docs.py --all
```

## Cross-References

- [Documentation Index](docs/README.md) - Full documentation index
- [Tables Reference](docs/tables.md) - Single Source of Truth for all definitions
