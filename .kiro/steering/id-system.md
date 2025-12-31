# ID System Conventions

## CLI Analogy Pattern

The `id`/`sid` relationship in the vince documentation system mirrors the familiar CLI flag pattern of `-h`/`--help`:

| CLI Pattern | ID System | Purpose |
|-------------|-----------|---------|
| `-h` | `sid` | Short form, quick to type/reference |
| `--help` | `id` | Long form, self-documenting |

## Key Principles

1. **Short/Long Duality**: Both CLI flags and the ID system provide a concise shorthand for efficiency while maintaining a readable full form for clarity.

2. **Context Differences**:
   - **CLI flags**: `-h` and `--help` are interchangeable at runtime
   - **ID system**: `sid` is for internal references/tables, `id` is the canonical human-readable name

3. **Familiarity**: This design makes the documentation system intuitive for CLI users who already understand the short/long duality.

## Usage Guidelines

When documenting vince CLI components:

- Use `id` (long form) for human-readable documentation and explanations
- Use `sid` (short form) for table references, internal cross-references, and compact displays
- Use `rid` (rule ID) for referencing specific rules: `{sid}{num}` format (e.g., `PD01`, `sl01`)

## Examples

| id | sid | rid | Analogy |
|----|-----|-----|---------|
| `help` | `he` | `he01` | Like `-h` / `--help` |
| `slap` | `sl` | `sl01` | Like `-sl` / `--slap` |
| `application` | `app` | `app01` | Like `-app` / `--application` |
