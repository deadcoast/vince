# Examples

## `slap`

- **NOTE**: TO ENSURE USER QOL, WHEN A SLAP IS SET AS DEFAULT, AN `offer` IS AUTOMATICALLY CREATED FOR IT, AND ADDED TO THE CLI COMMANDS LIST COMMAND (`--list`)

```sh
# STEP1: Identify an `application` path to set as Default
vince slap <path/to/application/app.exe>
# STEP2: Set [S1] as (ext)
vince slap <path/to/application/app.exe> --md
# STEP3: Set [S1] as [(dlt):(ext)]
vince slap <path/to/application/app.exe> -set --md
```

## `chop`

```sh
# STEP1: Identify an `app
vince chop <file_extension>
```

## `set`

```sh
# STEP1: Identify an `application` path to set as Default
vince set <path/to/application/app.exe>
# STEP2: Set [S1] as (ext)
vince set <path/to/application/app.exe> --md
# STEP3: Set [S1] as [(dlt):(ext)]
vince set <path/to/application/app.exe> -set --md
```

## `forget`

```sh

```

## `list`

> provides a list of all tracked assets, and their respective `offers`

```sh
# Show All Lists - No flag option, so this requires the 'any or all' operator `.`)
vince list .
# list all offers
vince list -offers
# lists all offers attached to the markdown format flag
vince list -offers --md
```
