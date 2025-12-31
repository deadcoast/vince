# `vince` - A Rich CLI Application

## Overview

Vince is a sophisticated CLI created with elevated visual ASCII UI delivery to quickly set default applications to file extensions. Its quick, intuitive and visually friendly design sets the new standard for user quality of life and visual CLI UI design.

This documentation serves as the comprehensive reference for the vince CLI, covering all commands, data schemas, error handling, state management, and configuration options.

*Inspired by Infomercials of the Millennials Age*

## FRAMEWORK

- [Python](https://www.python.org/)
  CLI: [Typer](https://typer.tiangolo.com/)
  CLI: [Rich](https://rich.readthedocs.io/)
  PKG: [UV](https://docs.astral.sh/uv/)

## DOCUMENTATION

For detailed information about the `vince` CLI, see the following documentation:

### Core Documentation

- [Overview](overview.md) - System design, commands, flags, and rules
- [Examples](examples.md) - Practical usage examples for all commands
- [Tables](tables.md) - Complete reference tables for all definitions

### API & Data Models

- [API](api.md) - Python interface documentation for all CLI commands
- [Schemas](schemas.md) - JSON schemas for defaults, offers, and configuration files

### System Behavior

- [Errors](errors.md) - Error catalog with codes, messages, and recovery actions
- [Config](config.md) - Configuration options, hierarchy, and precedence rules
- [States](states.md) - State machine documentation for defaults and offers lifecycle

### Development

- [Testing](testing.md) - Testing patterns, fixtures, mocks, and example test cases

## INSTALLATION

### Quick Install

```sh
# For Linux & macOS (using curl)
curl -LsSf https://astral.sh/uv/install.sh | sh

# For Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

#### Additional Options

> MacOS

```sh
# Install uv
pip install uv
# MacOS
brew install uv
# curl
curl -LsSf https://astral.sh/uv/install.sh | sh
```

> Windows

```sh
# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
# Via choclatey
choco install uv
```

### Step One: `venv`

- After you have uv installed, use it to create the venv and activavte it.

> Create the Venv

```sh
# Create a virtual environment
uv venv
```

> Activate it

```sh
# Activate the virtual environment
source .venv/bin/activate
```

### Step Two: `init`, `sync`

```sh
# Initiate and create a project pyproject.toml file
uv init
# Installs the exact versions from the lockfile
uv sync
```

### Step Three: `lock`

- Install the uv dependencies and lock the versions of the dependencies.

```sh
# Resolves and locks dependencies to compatible versions
uv lock 
```

### Troubleshooting

- If something failed in installation or building, try the uatomated uv commands to debug dependencies

#### Manually adding to PATH

- If uv is not in PATH, try manually adding it to PATH

> utilizing pip

```sh
uv pip install --user
# MacOS
uv pip install --user --platform darwin
# Windows
uv pip install --user --platform win32
```

#### Update uv lock file

- Initiate the uv lock file and upgrade its compatible dependencies to the latest versions.
  - This will create a `uv.lock` file that contains the exact versions of the dependencies that are compatible with the current version of uv.

```sh
# Resolves and locks dependencies to compatible versions
uv lock 
# Upgrades all dependencies to latest compatible versions
uv lock --upgrade 
# Upgrades specific package(s) only
uv lock --upgrade-package <package> 
```


## Cross-References

- [Project README](../README.md) - Project root documentation
- [Tables](tables.md) - Single Source of Truth for all definitions
- [API](api.md) - Command function signatures and parameters
- [Schemas](schemas.md) - Data structure definitions
- [Errors](errors.md) - Error codes and recovery actions
