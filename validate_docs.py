#!/usr/bin/env python3
"""
Documentation Validation Script for vince CLI

This script validates the documentation files against the requirements
defined in the documentation-population spec.

Usage:
    python validate_docs.py --all
    python validate_docs.py --file tables.md
    python validate_docs.py --cross-refs
    python validate_docs.py --report
"""

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class ValidationError:
    """Represents a validation error."""

    file: str
    line: Optional[int]
    rule: str
    message: str
    severity: str = "error"  # error, warning


@dataclass
class ValidationResult:
    """Holds the results of validation."""

    errors: list[ValidationError] = field(default_factory=list)
    warnings: list[ValidationError] = field(default_factory=list)
    files_validated: set[str] = field(default_factory=set)
    properties_checked: set[str] = field(default_factory=set)

    def add_error(self, file: str, line: Optional[int], rule: str, message: str):
        self.errors.append(ValidationError(file, line, rule, message, "error"))

    def add_warning(self, file: str, line: Optional[int], rule: str, message: str):
        self.warnings.append(ValidationError(file, line, rule, message, "warning"))

    def mark_file_validated(self, filepath: str):
        """Mark a file as having been validated."""
        self.files_validated.add(filepath)

    def mark_property_checked(self, property_name: str):
        """Mark a property validator as having been run."""
        self.properties_checked.add(property_name)

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0

    def merge(self, other: "ValidationResult"):
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)
        self.files_validated.update(other.files_validated)
        self.properties_checked.update(other.properties_checked)


# =============================================================================
# Property 1: Heading Hierarchy Validator
# Validates: Requirements 1.1, 1.2
# =============================================================================


def validate_heading_hierarchy(content: str, filename: str) -> ValidationResult:
    """
    Validate that markdown heading hierarchy is correct.

    Rules:
    - H1 appears first as document title
    - H3 only appears after an H2 has been established
    - No heading level jumps (e.g., H1 -> H3 without H2)

    Property 1: For any markdown document, the heading hierarchy SHALL be valid:
    H1 appears first as document title, and H3 only appears after an H2 has been
    established in the document flow.
    """
    result = ValidationResult()
    lines = content.split("\n")

    # Track state
    found_h1 = False
    found_h2_after_last_h1 = False
    current_h2_section: Optional[str] = None  # Track current H2 for context in errors

    # Pattern to match headings (not in code blocks)
    heading_pattern = re.compile(r"^(#{1,6})\s+(.+)$")

    in_code_block = False

    for line_num, line in enumerate(lines, 1):
        # Track code blocks to ignore headings inside them
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            continue

        if in_code_block:
            continue

        match = heading_pattern.match(line)
        if not match:
            continue

        level = len(match.group(1))
        heading_text = match.group(2)

        if level == 1:
            if found_h1:
                result.add_warning(
                    filename,
                    line_num,
                    "1.1",
                    f"Multiple H1 headings found. Second H1: '{heading_text}'",
                )
            found_h1 = True
            found_h2_after_last_h1 = False

        elif level == 2:
            if not found_h1:
                result.add_error(
                    filename,
                    line_num,
                    "1.1",
                    f"H2 '{heading_text}' appears before any H1 heading",
                )
            found_h2_after_last_h1 = True
            current_h2_section = heading_text  # Track current section for context

        elif level == 3:
            if not found_h1:
                result.add_error(
                    filename,
                    line_num,
                    "1.2",
                    f"H3 '{heading_text}' appears before any H1 heading",
                )
            elif not found_h2_after_last_h1:
                section_context = (
                    " (no parent section)"
                    if not current_h2_section
                    else f" (expected under '{current_h2_section}')"
                )
                result.add_error(
                    filename,
                    line_num,
                    "1.2",
                    f"H3 '{heading_text}' appears without a preceding H2 heading{section_context}",
                )

    # Check that document starts with H1
    first_heading = None
    in_code_block = False
    for line_num, line in enumerate(lines, 1):
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue
        match = heading_pattern.match(line)
        if match:
            first_heading = (line_num, len(match.group(1)), match.group(2))
            break

    if first_heading and first_heading[1] != 1:
        result.add_error(
            filename,
            first_heading[0],
            "1.1",
            f"Document should start with H1, but starts with H{first_heading[1]}: '{first_heading[2]}'",
        )

    return result


# =============================================================================
# Property 2: Table Syntax Validator
# Validates: Requirements 1.3
# =============================================================================


def validate_table_syntax(content: str, filename: str) -> ValidationResult:
    """
    Validate that markdown tables have proper syntax.

    Rules:
    - Tables must have a header row
    - Tables must have a separator row with |---| pattern
    - Column counts must be consistent across all rows

    Property 2: For any table defined in the documentation, it SHALL have proper
    markdown table syntax including a header row, a separator row with |---|
    pattern, and consistent column counts across all rows.
    """
    result = ValidationResult()
    lines = content.split("\n")

    in_code_block = False
    table_start = None
    table_lines = []

    for line_num, line in enumerate(lines, 1):
        # Track code blocks
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            # If we were in a table, end it
            if table_start is not None:
                _validate_table_block(result, filename, table_start, table_lines)
                table_start = None
                table_lines = []
            continue

        if in_code_block:
            continue

        # Check if line is a table row
        stripped = line.strip()
        if stripped.startswith("|") and stripped.endswith("|"):
            if table_start is None:
                table_start = line_num
            table_lines.append((line_num, stripped))
        else:
            # End of table
            if table_start is not None:
                _validate_table_block(result, filename, table_start, table_lines)
                table_start = None
                table_lines = []

    # Handle table at end of file
    if table_start is not None:
        _validate_table_block(result, filename, table_start, table_lines)

    return result


def _validate_table_block(
    result: ValidationResult,
    filename: str,
    start_line: int,
    table_lines: list[tuple[int, str]],
):
    """Validate a single table block."""
    if len(table_lines) < 2:
        result.add_error(
            filename,
            start_line,
            "1.3",
            "Table must have at least a header row and separator row",
        )
        return

    # Check for separator row (second row should be separator)
    separator_pattern = re.compile(r"^\|(\s*[-:]+\s*\|)+$")

    if len(table_lines) >= 2:
        _, second_row = table_lines[1]
        if not separator_pattern.match(second_row):
            result.add_error(
                filename,
                table_lines[1][0],
                "1.3",
                f"Table separator row is malformed: '{second_row}'",
            )

    # Check column consistency
    def count_columns(row: str) -> int:
        # Count pipes minus 1 (accounting for leading/trailing pipes)
        return row.count("|") - 1

    header_cols = count_columns(table_lines[0][1])

    for line_num, row in table_lines[1:]:
        row_cols = count_columns(row)
        if row_cols != header_cols:
            result.add_error(
                filename,
                line_num,
                "1.3",
                f"Table row has {row_cols} columns, expected {header_cols}",
            )


# =============================================================================
# Property 3: Code Block Language Identifier Validator
# Validates: Requirements 1.4
# =============================================================================


def validate_code_blocks(content: str, filename: str) -> ValidationResult:
    """
    Validate that fenced code blocks have language identifiers.

    Property 3: For any fenced code block in the documentation, it SHALL include
    a language identifier immediately after the opening fence.
    """
    result = ValidationResult()
    lines = content.split("\n")

    code_fence_pattern = re.compile(r"^```(\w*)$")

    for line_num, line in enumerate(lines, 1):
        stripped = line.strip()
        match = code_fence_pattern.match(stripped)
        if match:
            lang = match.group(1)
            # Opening fence without language identifier
            if stripped == "```":
                # Check if this is a closing fence by looking at context
                # We need to track if we're in a code block
                pass

    # Better approach: track code blocks properly
    in_code_block = False
    code_block_start: Optional[int] = (
        None  # Track start line for unclosed block detection
    )

    for line_num, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("```"):
            if not in_code_block:
                # Opening fence
                in_code_block = True
                code_block_start = line_num
                # Check for language identifier
                lang = stripped[3:].strip()
                if not lang:
                    result.add_error(
                        filename,
                        line_num,
                        "1.4",
                        "Code block missing language identifier",
                    )
            else:
                # Closing fence
                in_code_block = False
                code_block_start = None

    # Check for unclosed code blocks
    if in_code_block and code_block_start:
        result.add_error(
            filename,
            code_block_start,
            "1.4",
            f"Code block opened at line {code_block_start} is never closed",
        )

    return result


# =============================================================================
# Property 4: Entry Field Completeness Validator
# Validates: Requirements 2.1, 2.2, 2.3
# =============================================================================


def validate_entry_completeness(content: str, filename: str) -> ValidationResult:
    """
    Validate that all entries in definition tables have required fields.

    Property 4: For any entry in a definition table (commands, flags, extensions,
    definitions), all required fields for that entry type SHALL be present and
    non-empty.
    """
    result = ValidationResult()

    # Define required fields for each table type
    table_schemas = {
        "DEFINITIONS": ["id", "sid", "rid", "description"],
        "COMMANDS": ["id", "sid", "rid", "description"],
        "FILE_TYPES": ["id", "full_id", "ext", "sid", "flag_short", "flag_long"],
        "UTILITY_FLAGS": ["id", "sid", "short", "long", "description"],
        "QOL_FLAGS": ["id", "sid", "short", "description"],
        "LIST_FLAGS": ["id", "sid", "short", "description"],
        "OPERATORS": ["symbol", "name", "usage"],
        "ARGUMENTS": ["pattern", "name", "description"],
        "RULES": ["rid", "category", "description"],
    }

    lines = content.split("\n")
    current_section = None
    in_table = False
    table_headers: list[str] = []
    table_start_line: Optional[int] = None  # Track where table starts for error context

    in_code_block = False

    for line_num, line in enumerate(lines, 1):
        stripped = line.strip()

        # Track code blocks
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue

        if in_code_block:
            continue

        # Check for section headers
        if stripped.startswith("## "):
            section_name = stripped[3:].strip().upper().replace(" ", "_")
            if section_name in table_schemas:
                current_section = section_name
                in_table = False
                table_headers = []
                table_start_line = None
            else:
                current_section = None

        # Parse table
        if current_section and stripped.startswith("|") and stripped.endswith("|"):
            if not in_table:
                # This is the header row
                in_table = True
                table_start_line = line_num
                # Parse headers
                table_headers = [
                    h.strip().strip("`") for h in stripped.split("|")[1:-1]
                ]

                # Validate headers match schema
                required = table_schemas.get(current_section, [])
                for req_field in required:
                    if req_field not in table_headers:
                        result.add_error(
                            filename,
                            line_num,
                            "2.1",
                            f"Table {current_section} (starting line {table_start_line}) missing required column: {req_field}",
                        )
            elif stripped.startswith("|") and "---" in stripped:
                # Separator row, skip
                continue
            else:
                # Data row - check for empty fields
                cells = [c.strip() for c in stripped.split("|")[1:-1]]
                for i, cell in enumerate(cells):
                    if not cell and i < len(table_headers):
                        result.add_error(
                            filename,
                            line_num,
                            "2.1",
                            f"Empty field '{table_headers[i]}' in {current_section} table",
                        )
        elif in_table and not stripped.startswith("|"):
            # End of table
            in_table = False
            table_headers = []

    return result


# =============================================================================
# Property 5: SID Naming Convention Validator
# Validates: Requirements 2.4, 2.5
# =============================================================================


def validate_sid_naming(content: str, filename: str) -> ValidationResult:
    """
    Validate SID naming conventions.

    Rules:
    - One-word identifiers: first two letters (e.g., step -> st)
    - Two-word identifiers: first two letters of each word (e.g., short_id -> sid)
    - No duplicate sid values

    Property 5: For any sid value in the documentation system, it SHALL follow
    the naming rules: one-word identifiers use first two letters, two-word
    identifiers use first two letters of each word, and no duplicate sid values
    exist.
    """
    result = ValidationResult()

    # Extract all sid values from tables
    sid_occurrences: dict[str, list[tuple[int, str]]] = {}  # sid -> [(line, id)]

    lines = content.split("\n")
    in_code_block = False
    in_table = False
    table_headers: list[str] = []  # Track headers to know column positions
    sid_col_idx = -1
    id_col_idx = -1

    for line_num, line in enumerate(lines, 1):
        stripped = line.strip()

        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue

        if in_code_block:
            continue

        if stripped.startswith("|") and stripped.endswith("|"):
            cells = [c.strip().strip("`") for c in stripped.split("|")[1:-1]]

            if not in_table:
                # Header row
                in_table = True
                table_headers = cells
                sid_col_idx = -1
                id_col_idx = -1
                for i, h in enumerate(table_headers):
                    if h.lower() == "sid":
                        sid_col_idx = i
                    if h.lower() == "id":
                        id_col_idx = i
            elif "---" in stripped:
                # Separator row
                continue
            else:
                # Data row
                if sid_col_idx >= 0 and sid_col_idx < len(cells):
                    sid = cells[sid_col_idx]
                    id_val = (
                        cells[id_col_idx]
                        if id_col_idx >= 0 and id_col_idx < len(cells)
                        else ""
                    )
                    if sid:
                        if sid not in sid_occurrences:
                            sid_occurrences[sid] = []
                        sid_occurrences[sid].append((line_num, id_val))
        elif in_table and not stripped.startswith("|"):
            in_table = False
            table_headers = []
            sid_col_idx = -1
            id_col_idx = -1

    # Check for duplicates
    for sid, occurrences in sid_occurrences.items():
        if len(occurrences) > 1:
            # Check if they're for different ids
            unique_ids = set(occ[1] for occ in occurrences)
            if len(unique_ids) > 1:
                lines_str = ", ".join(str(occ[0]) for occ in occurrences)
                result.add_error(
                    filename,
                    occurrences[0][0],
                    "2.5",
                    f"Duplicate sid '{sid}' used for different ids on lines: {lines_str}",
                )

    # Validate naming convention (basic check)
    for sid, occurrences in sid_occurrences.items():
        for line_num, id_val in occurrences:
            if id_val and sid:
                # Check if sid follows convention
                id_clean = id_val.strip("`")
                if "_" in id_clean:
                    # Two-word: should be first 2 letters of each word (e.g., short_id -> sid)
                    parts = id_clean.split("_")
                    if len(parts) == 2:
                        expected = parts[0][:2] + parts[1][:2]
                        # Check if sid matches expected or starts with first part (collision handling)
                        if sid != expected and not sid.startswith(parts[0][:2]):
                            result.add_warning(
                                filename,
                                line_num,
                                "2.4",
                                f"SID '{sid}' may not follow two-word convention for id '{id_val}' (expected '{expected}' or collision variant)",
                            )
                else:
                    # One-word: should be first 2 letters (e.g., step -> st)
                    if len(id_clean) >= 2 and len(sid) >= 2:
                        expected = id_clean[:2].lower()
                        # Allow for collision handling (subsequent letters)
                        if sid[:2].lower() != expected:
                            result.add_warning(
                                filename,
                                line_num,
                                "2.4",
                                f"SID '{sid}' may not follow one-word convention for id '{id_val}' (expected '{expected}' or collision variant)",
                            )

    return result


# =============================================================================
# Property 6: Cross-Reference Consistency Validator
# Validates: Requirements 5.1, 5.2, 5.3, 5.5
# =============================================================================


def extract_definitions_from_tables(tables_content: str) -> dict[str, set[str]]:
    """Extract all defined identifiers from tables.md."""
    definitions = {
        "commands": set(),
        "sids": set(),
        "ids": set(),
        "extensions": set(),
        "flags": set(),
    }

    lines = tables_content.split("\n")
    in_code_block = False
    current_section = None
    in_table = False
    table_headers = []

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue

        if in_code_block:
            continue

        if stripped.startswith("## "):
            section = stripped[3:].strip().upper()
            current_section = section
            in_table = False
            table_headers = []

        if stripped.startswith("|") and stripped.endswith("|"):
            cells = [c.strip().strip("`") for c in stripped.split("|")[1:-1]]

            if not in_table:
                in_table = True
                table_headers = [h.lower() for h in cells]
            elif "---" in stripped:
                continue
            else:
                # Data row
                cell_dict = dict(zip(table_headers, cells))

                if "sid" in cell_dict and cell_dict["sid"]:
                    definitions["sids"].add(cell_dict["sid"])
                if "id" in cell_dict and cell_dict["id"]:
                    definitions["ids"].add(cell_dict["id"])

                if current_section == "COMMANDS":
                    if "id" in cell_dict:
                        definitions["commands"].add(cell_dict["id"])
                elif current_section == "FILE_TYPES":
                    if "ext" in cell_dict:
                        definitions["extensions"].add(cell_dict["ext"])
                    if "flag_short" in cell_dict:
                        definitions["flags"].add(cell_dict["flag_short"])
                    if "flag_long" in cell_dict:
                        definitions["flags"].add(cell_dict["flag_long"])
        elif in_table and not stripped.startswith("|"):
            in_table = False

    return definitions


def validate_cross_references(
    content: str, filename: str, tables_definitions: dict[str, set[str]]
) -> ValidationResult:
    """
    Validate cross-references between documents.

    Property 6: For any identifier referenced in one document, if it is defined
    in another document, the definitions SHALL be identical. Additionally, all
    referenced identifiers SHALL have a definition in tables.md.
    """
    result = ValidationResult()

    # Extract commands mentioned in the document
    lines = content.split("\n")
    in_code_block = False

    # Pattern to find command references like `slap`, `chop`, etc.
    command_pattern = re.compile(r"`(slap|chop|set|forget|offer|reject|list)`")

    for line_num, line in enumerate(lines, 1):
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            continue

        if in_code_block:
            continue

        # Check for command references
        for match in command_pattern.finditer(line):
            cmd = match.group(1)
            if cmd not in tables_definitions["commands"]:
                result.add_error(
                    filename,
                    line_num,
                    "5.1",
                    f"Command '{cmd}' referenced but not defined in tables.md",
                )

    return result


# =============================================================================
# Property 7: Flag Prefix Convention Validator
# Validates: Requirements 4.5
# =============================================================================


def validate_flag_prefixes(content: str, filename: str) -> ValidationResult:
    """
    Validate flag prefix conventions.

    Rules:
    - Short flags use single dash prefix (-)
    - Long flags use double dash prefix (--)

    Property 7: For any flag defined in the documentation, short flags SHALL use
    single dash prefix (-) and long flags SHALL use double dash prefix (--).
    """
    result = ValidationResult()

    lines = content.split("\n")
    in_code_block = False
    in_table = False
    table_headers = []
    short_col_idx = -1
    long_col_idx = -1

    for line_num, line in enumerate(lines, 1):
        stripped = line.strip()

        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue

        if in_code_block:
            continue

        if stripped.startswith("|") and stripped.endswith("|"):
            cells = [c.strip().strip("`") for c in stripped.split("|")[1:-1]]

            if not in_table:
                in_table = True
                table_headers = [h.lower() for h in cells]
                short_col_idx = -1
                long_col_idx = -1
                for i, h in enumerate(table_headers):
                    if h == "short":
                        short_col_idx = i
                    if h == "long":
                        long_col_idx = i
            elif "---" in stripped:
                continue
            else:
                # Data row - validate flag prefixes
                if short_col_idx >= 0 and short_col_idx < len(cells):
                    short_flag = cells[short_col_idx]
                    if short_flag and not short_flag.startswith("-"):
                        result.add_error(
                            filename,
                            line_num,
                            "4.5",
                            f"Short flag '{short_flag}' should start with '-'",
                        )
                    # Short flags should NOT start with --
                    if short_flag and short_flag.startswith("--"):
                        result.add_error(
                            filename,
                            line_num,
                            "4.5",
                            f"Short flag '{short_flag}' should use single dash, not double",
                        )

                if long_col_idx >= 0 and long_col_idx < len(cells):
                    long_flag = cells[long_col_idx]
                    if long_flag and not long_flag.startswith("--"):
                        result.add_error(
                            filename,
                            line_num,
                            "4.5",
                            f"Long flag '{long_flag}' should start with '--'",
                        )
        elif in_table and not stripped.startswith("|"):
            in_table = False
            table_headers = []
            short_col_idx = -1
            long_col_idx = -1

    return result


# =============================================================================
# Property 8: Example Completeness Validator
# Validates: Requirements 3.1, 3.2, 7.1, 7.2
# =============================================================================


def validate_example_coverage(
    examples_content: str, filename: str, tables_definitions: dict[str, set[str]]
) -> ValidationResult:
    """
    Validate that all commands have examples.

    Property 8: For any command defined in the system, examples.md SHALL contain
    at least one complete example demonstrating that command with appropriate flags.
    """
    result = ValidationResult()

    # Find all command sections in examples.md
    documented_commands = set()

    lines = examples_content.split("\n")
    in_code_block = False

    # Pattern to match command section headers like ## `slap`
    section_pattern = re.compile(r"^##\s+`(\w+)`")

    for line_num, line in enumerate(lines, 1):
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            continue

        if in_code_block:
            continue

        match = section_pattern.match(line)
        if match:
            documented_commands.add(match.group(1))

    # Check that all commands from tables.md have examples
    required_commands = tables_definitions.get("commands", set())

    for cmd in required_commands:
        if cmd not in documented_commands:
            result.add_error(
                filename,
                None,
                "7.1",
                f"Command '{cmd}' has no example section in examples.md",
            )

    # Also check that each documented command has at least one code block
    current_section = None
    section_has_code = False
    section_start_line = None

    for line_num, line in enumerate(lines, 1):
        stripped = line.strip()

        match = section_pattern.match(line)
        if match:
            # Check previous section
            if current_section and not section_has_code:
                result.add_error(
                    filename,
                    section_start_line,
                    "7.2",
                    f"Command section '{current_section}' has no code examples",
                )
            current_section = match.group(1)
            section_has_code = False
            section_start_line = line_num

        if stripped.startswith("```") and current_section:
            section_has_code = True

    # Check last section
    if current_section and not section_has_code:
        result.add_error(
            filename,
            section_start_line,
            "7.2",
            f"Command section '{current_section}' has no code examples",
        )

    return result


# =============================================================================
# Property 9: Rule Format Validator
# Validates: Requirements 9.2, 9.4
# =============================================================================


def validate_rule_format(content: str, filename: str) -> ValidationResult:
    """
    Validate rule reference format.

    Rules:
    - Rule IDs use format: category prefix + number (e.g., PD01, UID01)
    - Rule references use bracket notation [rid]

    Property 9: For any rule referenced in the documentation, it SHALL use the
    rid format (category prefix + number) and bracket notation [rid] when
    referenced inline.
    """
    result = ValidationResult()

    lines = content.split("\n")
    in_code_block = False

    # Pattern for valid rid format (2-4 uppercase letters + 2 digits)
    rid_pattern = re.compile(r"\[([A-Z]{2,4}\d{2})\]")

    # Pattern for potentially malformed rule references (lowercase)
    malformed_pattern = re.compile(r"\[([a-z]{2,4}\d{2})\]")

    # Track all valid rule references found
    valid_rule_refs: set[str] = set()

    for line_num, line in enumerate(lines, 1):
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            continue

        if in_code_block:
            continue

        # Collect valid rule references
        for match in rid_pattern.finditer(line):
            valid_rule_refs.add(match.group(1))

        # Check for malformed (lowercase) rule references
        for match in malformed_pattern.finditer(line):
            rid = match.group(1)
            result.add_warning(
                filename,
                line_num,
                "9.2",
                f"Rule reference '[{rid}]' should use uppercase: '[{rid.upper()}]'",
            )

    # Validate that rule references follow the expected format categories
    known_prefixes = {"PD", "UID", "TB", "SL", "CH", "SE", "FO", "OF", "RE", "LI"}
    for rid in valid_rule_refs:
        prefix = "".join(c for c in rid if c.isalpha())
        if prefix not in known_prefixes:
            result.add_warning(
                filename,
                None,
                "9.4",
                f"Rule reference '[{rid}]' uses unknown prefix '{prefix}'",
            )

    return result


# =============================================================================
# Property 10: Modular Command Syntax Validator
# Validates: Requirements 10.2, 10.3
# =============================================================================


def validate_modular_syntax(content: str, filename: str) -> ValidationResult:
    """
    Validate modular command syntax.

    Rules:
    - No underscore-joined subcommands (e.g., sub_command)
    - Commands should use space-separated modular syntax

    Property 10: For any command example in the documentation, it SHALL NOT
    contain underscore-joined subcommands and SHALL use space-separated modular
    syntax.
    """
    result = ValidationResult()

    lines = content.split("\n")
    in_code_block = False

    # Pattern to detect underscore-joined commands after 'vince'
    # This looks for patterns like: vince word_word
    underscore_cmd_pattern = re.compile(r"vince\s+(\w+_\w+)")

    for line_num, line in enumerate(lines, 1):
        stripped = line.strip()

        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue

        # Only check inside code blocks (actual command examples)
        if in_code_block:
            match = underscore_cmd_pattern.search(line)
            if match:
                bad_cmd = match.group(1)
                result.add_error(
                    filename,
                    line_num,
                    "10.2",
                    f"Underscore-joined command '{bad_cmd}' violates modular design [PD01]",
                )

    # Also check for underscore commands in inline code
    inline_pattern = re.compile(r"`vince\s+(\w+_\w+)`")
    in_code_block = False

    for line_num, line in enumerate(lines, 1):
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            continue

        if not in_code_block:
            for match in inline_pattern.finditer(line):
                bad_cmd = match.group(1)
                result.add_error(
                    filename,
                    line_num,
                    "10.3",
                    f"Underscore-joined command '{bad_cmd}' in inline code violates modular design",
                )

    return result


# =============================================================================
# Property 11: API Documentation Completeness Validator
# Validates: Requirements 1.1, 1.2, 1.3, 1.4
# Feature: python-integration-preparation
# =============================================================================


def validate_api_completeness(content: str, filename: str) -> ValidationResult:
    """
    Validate that API documentation is complete for all commands.

    Rules:
    - All commands must have function signatures with type hints
    - All parameters must be documented with types and descriptions
    - Return types must be documented
    - Raised exceptions must be documented

    Property 1: For any command defined in the system, the api.md document SHALL
    contain a complete function specification including: function signature with
    type hints, all parameters with types and descriptions, return type
    documentation, and raised exceptions with conditions.
    """
    result = ValidationResult()

    # Expected commands from the vince CLI
    expected_commands = {"slap", "chop", "set", "forget", "offer", "reject", "list"}

    lines = content.split("\n")
    in_code_block = False
    code_block_lang = ""

    # Track documented commands and their completeness
    documented_commands: dict[str, dict[str, bool]] = {}
    current_command = None

    # Patterns for detecting command sections and documentation elements
    command_section_pattern = re.compile(r"^###\s+(\w+)\s*$")
    subsection_pattern = re.compile(r"^####\s+(.+)\s*$")
    function_sig_pattern = re.compile(r"def\s+cmd_(\w+)\s*\(")
    param_table_header = re.compile(r"\|\s*Parameter\s*\|")
    return_type_pattern = re.compile(r"####\s+Return\s+Type")
    exceptions_pattern = re.compile(r"####\s+Raised\s+Exceptions")

    for line_num, line in enumerate(lines, 1):
        stripped = line.strip()

        # Track code blocks
        if stripped.startswith("```"):
            if not in_code_block:
                in_code_block = True
                code_block_lang = stripped[3:].strip()
            else:
                in_code_block = False
                code_block_lang = ""
            continue

        # Check for command section headers (### slap, ### chop, etc.)
        match = command_section_pattern.match(stripped)
        if match:
            cmd_name = match.group(1).lower()
            if cmd_name in expected_commands:
                current_command = cmd_name
                if current_command not in documented_commands:
                    documented_commands[current_command] = {
                        "has_signature": False,
                        "has_parameters": False,
                        "has_return_type": False,
                        "has_exceptions": False,
                        "line": line_num,
                    }
            continue

        # Check for subsections within a command using precise pattern matching
        # Use return_type_pattern for more precise detection of return type sections
        if return_type_pattern.match(stripped):
            if current_command:
                documented_commands[current_command]["has_return_type"] = True
            continue

        # Use exceptions_pattern for more precise detection of raised exceptions sections
        if exceptions_pattern.match(stripped):
            if current_command:
                documented_commands[current_command]["has_exceptions"] = True
            continue

        # Check for other subsections within a command (for future extensibility)
        subsection_match = subsection_pattern.match(stripped)
        if subsection_match:
            # Subsection detected but not currently used for additional tracking
            continue

        # Check for function signature in code blocks
        if in_code_block and code_block_lang == "python" and current_command:
            sig_match = function_sig_pattern.search(line)
            if sig_match:
                documented_commands[current_command]["has_signature"] = True

        # Check for parameter table
        if current_command and param_table_header.search(line):
            documented_commands[current_command]["has_parameters"] = True

    # Validate completeness for each expected command
    for cmd in expected_commands:
        if cmd not in documented_commands:
            result.add_error(
                filename,
                None,
                "1.1",
                f"Command '{cmd}' is missing from API documentation",
            )
        else:
            cmd_info = documented_commands[cmd]
            if not cmd_info["has_signature"]:
                result.add_error(
                    filename,
                    cmd_info["line"],
                    "1.1",
                    f"Command '{cmd}' missing function signature with type hints",
                )
            if not cmd_info["has_parameters"]:
                result.add_error(
                    filename,
                    cmd_info["line"],
                    "1.2",
                    f"Command '{cmd}' missing parameter documentation table",
                )
            if not cmd_info["has_return_type"]:
                result.add_error(
                    filename,
                    cmd_info["line"],
                    "1.3",
                    f"Command '{cmd}' missing return type documentation",
                )
            if not cmd_info["has_exceptions"]:
                result.add_error(
                    filename,
                    cmd_info["line"],
                    "1.4",
                    f"Command '{cmd}' missing raised exceptions documentation",
                )

    return result


# =============================================================================
# Property 12: Schema Completeness Validator
# Validates: Requirements 2.4, 2.5, 2.7
# Feature: python-integration-preparation
# =============================================================================


def validate_schema_completeness(content: str, filename: str) -> ValidationResult:
    """
    Validate that JSON schemas are complete with all required elements.

    Rules:
    - Schemas must define required and optional fields with types
    - Schemas must define validation constraints (min/max, patterns, enums)
    - Schemas must include example JSON documents

    Property 2: For any JSON schema defined in schemas.md, it SHALL contain:
    all required and optional field definitions with types, validation
    constraints (min/max, patterns, enums), and at least one example JSON document.
    """
    result = ValidationResult()

    # Expected schemas
    expected_schemas = {"defaults", "offers", "config"}

    lines = content.split("\n")
    in_code_block = False
    code_block_lang = ""
    code_block_content = []

    # Track documented schemas
    documented_schemas: dict[str, dict[str, bool]] = {}
    current_schema = None
    in_example_section = False  # Track when parser enters example section

    # Patterns
    schema_section_pattern = re.compile(r"^##\s+(\w+)\s+Schema", re.IGNORECASE)
    example_section_pattern = re.compile(r"^###\s+Example", re.IGNORECASE)

    for line_num, line in enumerate(lines, 1):
        stripped = line.strip()

        # Track code blocks
        if stripped.startswith("```"):
            if not in_code_block:
                in_code_block = True
                code_block_lang = stripped[3:].strip()
                code_block_content = []
            else:
                # End of code block - analyze content
                if current_schema and code_block_lang == "json":
                    block_text = "\n".join(code_block_content)

                    # Check if it's a schema definition
                    if '"$schema"' in block_text:
                        documented_schemas[current_schema]["has_schema_def"] = True

                        # Check for type definitions
                        if '"type"' in block_text:
                            documented_schemas[current_schema]["has_types"] = True

                        # Check for constraints
                        if any(
                            c in block_text
                            for c in [
                                '"pattern"',
                                '"enum"',
                                '"minimum"',
                                '"maximum"',
                                '"minLength"',
                                '"maxLength"',
                            ]
                        ):
                            documented_schemas[current_schema]["has_constraints"] = True

                        # Check for required fields definition
                        if '"required"' in block_text:
                            documented_schemas[current_schema]["has_required"] = True

                    # Check if it's an example - use example_section_pattern context
                    # or fallback to content-based detection
                    elif in_example_section or (
                        '"version"' in block_text and '"$schema"' not in block_text
                    ):
                        documented_schemas[current_schema]["has_example"] = True

                in_code_block = False
                code_block_lang = ""
            continue

        if in_code_block:
            code_block_content.append(line)
            continue

        # Use example_section_pattern to detect example sections
        if example_section_pattern.match(stripped):
            if current_schema:
                in_example_section = True
            continue

        # Check for schema section headers
        match = schema_section_pattern.match(stripped)
        if match:
            schema_name = match.group(1).lower()
            if schema_name in expected_schemas:
                current_schema = schema_name
                in_example_section = False  # Reset example section flag for new schema
                if current_schema not in documented_schemas:
                    documented_schemas[current_schema] = {
                        "has_schema_def": False,
                        "has_types": False,
                        "has_constraints": False,
                        "has_required": False,
                        "has_example": False,
                        "line": line_num,
                    }

    # Validate completeness for each expected schema
    for schema in expected_schemas:
        if schema not in documented_schemas:
            result.add_error(
                filename,
                None,
                "2.4",
                f"Schema '{schema}' is missing from schemas documentation",
            )
        else:
            schema_info = documented_schemas[schema]
            if not schema_info["has_schema_def"]:
                result.add_error(
                    filename,
                    schema_info["line"],
                    "2.4",
                    f"Schema '{schema}' missing JSON schema definition",
                )
            if not schema_info["has_types"]:
                result.add_error(
                    filename,
                    schema_info["line"],
                    "2.4",
                    f"Schema '{schema}' missing field type definitions",
                )
            if not schema_info["has_constraints"]:
                result.add_error(
                    filename,
                    schema_info["line"],
                    "2.5",
                    f"Schema '{schema}' missing validation constraints",
                )
            if not schema_info["has_example"]:
                result.add_error(
                    filename,
                    schema_info["line"],
                    "2.7",
                    f"Schema '{schema}' missing example JSON document",
                )

    return result


# =============================================================================
# Property 13: Error Catalog Completeness Validator
# Validates: Requirements 3.1, 3.3, 3.4, 3.5
# Feature: python-integration-preparation
# =============================================================================


def validate_error_catalog(content: str, filename: str) -> ValidationResult:
    """
    Validate that error catalog is complete and follows conventions.

    Rules:
    - Error codes must follow VE### format
    - Error codes must fall within category ranges
    - All errors must have message, severity, and recovery action

    Property 3: For any error code defined in errors.md, it SHALL: follow the
    VE### format, include a message template and severity level, include a
    recovery action, and fall within its category's code range.
    """
    result = ValidationResult()

    # Expected error code ranges by category
    category_ranges = {
        "Input": (100, 199),
        "File": (200, 299),
        "State": (300, 399),
        "Config": (400, 499),
        "System": (500, 599),
    }

    lines = content.split("\n")
    in_code_block = False
    in_table = False
    table_headers: list[str] = []

    # Track documented errors
    documented_errors: dict[str, dict] = {}
    current_category = None

    # Patterns
    error_code_pattern = re.compile(r"^VE(\d{3})$")
    category_section_pattern = re.compile(r"^###\s+(\w+)\s+Errors", re.IGNORECASE)

    for line_num, line in enumerate(lines, 1):
        stripped = line.strip()

        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue

        if in_code_block:
            continue

        # Check for category section headers
        cat_match = category_section_pattern.match(stripped)
        if cat_match:
            current_category = cat_match.group(1)
            in_table = False
            table_headers = []
            continue

        # Parse error tables
        if stripped.startswith("|") and stripped.endswith("|"):
            cells = [c.strip() for c in stripped.split("|")[1:-1]]

            if not in_table:
                # Header row
                in_table = True
                table_headers = [h.lower() for h in cells]
            elif "---" in stripped:
                # Separator row
                continue
            else:
                # Data row
                if len(cells) >= len(table_headers):
                    row_data = dict(zip(table_headers, cells))

                    # Extract error code
                    code = row_data.get("code", "")
                    code_match = error_code_pattern.match(code)

                    if code_match:
                        error_num = int(code_match.group(1))
                        documented_errors[code] = {
                            "code": code,
                            "number": error_num,
                            "category": current_category,
                            "has_message": bool(
                                row_data.get(
                                    "message template", row_data.get("message", "")
                                )
                            ),
                            "has_severity": bool(row_data.get("severity", "")),
                            "has_recovery": bool(
                                row_data.get(
                                    "recovery action", row_data.get("recovery", "")
                                )
                            ),
                            "line": line_num,
                        }
        elif in_table and not stripped.startswith("|"):
            in_table = False
            table_headers = []

    # Validate each documented error
    for code, error_info in documented_errors.items():
        # Validate format
        if not error_code_pattern.match(code):
            result.add_error(
                filename,
                error_info["line"],
                "3.1",
                f"Error code '{code}' does not follow VE### format",
            )

        # Validate category range
        if error_info["category"] and error_info["category"] in category_ranges:
            min_val, max_val = category_ranges[error_info["category"]]
            if not (min_val <= error_info["number"] <= max_val):
                result.add_error(
                    filename,
                    error_info["line"],
                    "3.5",
                    f"Error code '{code}' ({error_info['number']}) outside {error_info['category']} range ({min_val}-{max_val})",
                )

        # Validate required fields
        if not error_info["has_message"]:
            result.add_error(
                filename,
                error_info["line"],
                "3.3",
                f"Error code '{code}' missing message template",
            )
        if not error_info["has_severity"]:
            result.add_error(
                filename,
                error_info["line"],
                "3.3",
                f"Error code '{code}' missing severity level",
            )
        if not error_info["has_recovery"]:
            result.add_error(
                filename,
                error_info["line"],
                "3.4",
                f"Error code '{code}' missing recovery action",
            )

    return result


# =============================================================================
# Property 14: State Transition Completeness Validator
# Validates: Requirements 5.3, 5.4
# Feature: python-integration-preparation
# =============================================================================


def validate_state_transitions(content: str, filename: str) -> ValidationResult:
    """
    Validate that state transitions are completely documented.

    Rules:
    - Transitions must have triggering command documented
    - Transitions must have conditions documented
    - Transitions must have resulting state documented
    - Transitions must have side effects documented

    Property 4: For any state transition documented in states.md, it SHALL
    include: the triggering command, transition conditions, resulting state,
    and any side effects.
    """
    result = ValidationResult()

    lines = content.split("\n")
    in_code_block = False
    in_table = False
    table_headers: list[str] = []

    # Track documented transitions
    documented_transitions: list[dict] = []
    current_entity = None
    current_transition_section = None  # Track current transition section for context

    # Patterns
    transition_section_pattern = re.compile(
        r"^###\s+(\w+)\s+State\s+Transitions", re.IGNORECASE
    )
    entity_section_pattern = re.compile(r"^##\s+(\w+)\s+Lifecycle", re.IGNORECASE)

    for line_num, line in enumerate(lines, 1):
        stripped = line.strip()

        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue

        if in_code_block:
            continue

        # Check for entity lifecycle sections
        entity_match = entity_section_pattern.match(stripped)
        if entity_match:
            current_entity = entity_match.group(1).lower()
            current_transition_section = None  # Reset transition section
            continue

        # Use transition_section_pattern to detect transition sections
        trans_match = transition_section_pattern.match(stripped)
        if trans_match:
            current_transition_section = trans_match.group(1).lower()
            in_table = False  # Reset table state for new section
            continue

        # Parse transition tables
        if stripped.startswith("|") and stripped.endswith("|"):
            cells = [c.strip() for c in stripped.split("|")[1:-1]]

            if not in_table:
                # Check if this is a transition table by looking at headers
                header_text = " ".join(cells).lower()
                if "from" in header_text and "to" in header_text:
                    in_table = True
                    table_headers = [h.lower() for h in cells]
            elif "---" in stripped:
                # Separator row
                continue
            else:
                # Data row
                if len(cells) >= len(table_headers):
                    row_data = dict(zip(table_headers, cells))

                    documented_transitions.append(
                        {
                            "from": row_data.get("from", ""),
                            "to": row_data.get("to", ""),
                            "trigger": row_data.get("trigger", ""),
                            "conditions": row_data.get("conditions", ""),
                            "side_effects": row_data.get(
                                "side effects", row_data.get("side_effects", "")
                            ),
                            "entity": current_entity,
                            "transition_section": current_transition_section,
                            "line": line_num,
                        }
                    )
        elif in_table and not stripped.startswith("|"):
            in_table = False
            table_headers = []

    # Validate each documented transition
    for trans in documented_transitions:
        # Build context string for error messages
        section_context = (
            f" in '{trans['transition_section']}' section"
            if trans.get("transition_section")
            else ""
        )

        if not trans["from"]:
            result.add_error(
                filename,
                trans["line"],
                "5.3",
                f"State transition missing 'from' state{section_context}",
            )
        if not trans["to"]:
            result.add_error(
                filename,
                trans["line"],
                "5.3",
                f"State transition missing 'to' state{section_context}",
            )
        if not trans["trigger"]:
            result.add_error(
                filename,
                trans["line"],
                "5.3",
                f"State transition from '{trans['from']}' to '{trans['to']}' missing trigger command{section_context}",
            )
        if not trans["conditions"]:
            result.add_error(
                filename,
                trans["line"],
                "5.3",
                f"State transition from '{trans['from']}' to '{trans['to']}' missing conditions{section_context}",
            )
        if not trans["side_effects"]:
            result.add_error(
                filename,
                trans["line"],
                "5.4",
                f"State transition from '{trans['from']}' to '{trans['to']}' missing side effects{section_context}",
            )

    return result


# =============================================================================
# Property 15: Cross-Reference Completeness for New Tables
# Validates: Requirements 10.1, 10.2, 10.3, 10.4, 10.5
# Feature: python-integration-preparation
# =============================================================================


def extract_errors_from_tables(tables_content: str) -> set[str]:
    """Extract all error codes from the ERRORS table in tables.md."""
    errors = set()
    lines = tables_content.split("\n")
    in_errors_section = False
    in_table = False

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("## ERRORS"):
            in_errors_section = True
            continue
        elif stripped.startswith("## ") and in_errors_section:
            in_errors_section = False
            continue

        if in_errors_section and stripped.startswith("|") and stripped.endswith("|"):
            if "---" in stripped:
                in_table = True
                continue
            if in_table:
                cells = [c.strip() for c in stripped.split("|")[1:-1]]
                if cells and cells[0].startswith("VE"):
                    errors.add(cells[0])

    return errors


def extract_states_from_tables(tables_content: str) -> set[str]:
    """Extract all state IDs from the STATES table in tables.md."""
    states = set()
    lines = tables_content.split("\n")
    in_states_section = False
    in_table = False

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("## STATES"):
            in_states_section = True
            continue
        elif stripped.startswith("## ") and in_states_section:
            in_states_section = False
            continue

        if in_states_section and stripped.startswith("|") and stripped.endswith("|"):
            if "---" in stripped:
                in_table = True
                continue
            if in_table:
                cells = [c.strip() for c in stripped.split("|")[1:-1]]
                if cells and len(cells) >= 2:
                    # sid is typically second column
                    states.add(cells[1])

    return states


def extract_config_options_from_tables(tables_content: str) -> set[str]:
    """Extract all config option keys from the CONFIG_OPTIONS table in tables.md."""
    options = set()
    lines = tables_content.split("\n")
    in_config_section = False
    in_table = False

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("## CONFIG_OPTIONS"):
            in_config_section = True
            continue
        elif stripped.startswith("## ") and in_config_section:
            in_config_section = False
            continue

        if in_config_section and stripped.startswith("|") and stripped.endswith("|"):
            if "---" in stripped:
                in_table = True
                continue
            if in_table:
                cells = [c.strip().strip("`") for c in stripped.split("|")[1:-1]]
                if cells:
                    options.add(cells[0])

    return options


# =============================================================================
# Cross-Reference Validation: Documentation-Code Sync
# Validates: Requirements 3.1, 6.3
# Feature: integration-validation
# =============================================================================


def extract_commands_from_api(api_path: Path) -> set[str]:
    """
    Extract all documented command names from api.md.

    Parses the api.md file to find command sections (### command_name)
    and returns a set of command identifiers.

    Args:
        api_path: Path to the api.md file

    Returns:
        Set of command names documented in api.md
    """
    commands = set()

    if not api_path.exists():
        return commands

    content = api_path.read_text()
    lines = content.split("\n")

    # Pattern to match command section headers like ### slap, ### chop, etc.
    # These are the main command documentation sections
    command_section_pattern = re.compile(r"^###\s+(\w+)\s*$")

    # Known vince commands to filter out non-command sections
    known_commands = {"slap", "chop", "set", "forget", "offer", "reject", "list"}

    in_code_block = False

    for line in lines:
        stripped = line.strip()

        # Track code blocks to avoid matching headers inside them
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue

        if in_code_block:
            continue

        match = command_section_pattern.match(stripped)
        if match:
            cmd_name = match.group(1).lower()
            # Only include if it's a known command (to filter out other H3 sections)
            if cmd_name in known_commands:
                commands.add(cmd_name)

    return commands


def extract_commands_from_source(commands_dir: Path) -> set[str]:
    """
    Extract all implemented command names from vince/commands/ directory.

    Scans the commands directory for Python files and extracts command
    identifiers based on file names and function definitions.

    Args:
        commands_dir: Path to the vince/commands/ directory

    Returns:
        Set of command names implemented in source code
    """
    commands = set()

    if not commands_dir.exists() or not commands_dir.is_dir():
        return commands

    # Map file names to command names
    # Some files have _cmd suffix to avoid Python keyword conflicts
    file_to_command = {
        "slap.py": "slap",
        "chop.py": "chop",
        "set_cmd.py": "set",
        "forget.py": "forget",
        "offer.py": "offer",
        "reject.py": "reject",
        "list_cmd.py": "list",
    }

    for py_file in commands_dir.glob("*.py"):
        if py_file.name == "__init__.py":
            continue

        # Check if file maps to a known command
        if py_file.name in file_to_command:
            commands.add(file_to_command[py_file.name])
        else:
            # For unknown files, try to extract command from function definition
            content = py_file.read_text()
            # Look for cmd_* function definitions
            cmd_pattern = re.compile(r"def\s+cmd_(\w+)\s*\(")
            for match in cmd_pattern.finditer(content):
                commands.add(match.group(1).lower())

    return commands


def validate_code_documentation_sync(
    docs_dir: Path,
    src_dir: Path,
) -> ValidationResult:
    """
    Validate bidirectional consistency between docs and source code.

    Checks:
    1. All documented commands have implementations
    2. All implemented commands are documented

    Args:
        docs_dir: Path to the docs/ directory
        src_dir: Path to the vince/ source directory

    Returns:
        ValidationResult with any sync errors found
    """
    result = ValidationResult()

    # Extract commands from documentation
    api_path = docs_dir / "api.md"
    doc_commands = extract_commands_from_api(api_path)

    # Extract commands from source code
    commands_dir = src_dir / "commands"
    src_commands = extract_commands_from_source(commands_dir)

    # Check for documented but not implemented commands
    for cmd in doc_commands - src_commands:
        result.add_error(
            "sync",
            None,
            "DOC-CODE",
            f"Command '{cmd}' documented in api.md but not implemented in vince/commands/",
        )

    # Check for implemented but not documented commands
    for cmd in src_commands - doc_commands:
        result.add_error(
            "sync",
            None,
            "CODE-DOC",
            f"Command '{cmd}' implemented in vince/commands/ but not documented in api.md",
        )

    return result


def validate_new_table_cross_references(
    errors_content: str,
    states_content: str,
    config_content: str,
    tables_content: str,
    filename: str,
) -> ValidationResult:
    """
    Validate cross-references between new documents and tables.md.

    Property 6: For any new definition introduced in the expanded documentation
    (errors, states, config options), there SHALL be a corresponding entry in
    the appropriate table in tables.md.
    """
    result = ValidationResult()

    # Extract definitions from tables.md
    table_errors = extract_errors_from_tables(tables_content)
    table_states = extract_states_from_tables(tables_content)
    table_config = extract_config_options_from_tables(tables_content)

    # Extract error codes from errors.md
    error_code_pattern = re.compile(r"VE\d{3}")
    doc_errors = set(error_code_pattern.findall(errors_content))

    # Check errors cross-reference
    for error in doc_errors:
        if error not in table_errors:
            result.add_error(
                filename,
                None,
                "10.2",
                f"Error code '{error}' in errors.md not found in tables.md ERRORS table",
            )

    # Extract state sids from states.md
    state_sid_pattern = re.compile(r"(def-\w+|off-\w+)")
    doc_states = set(state_sid_pattern.findall(states_content))

    # Check states cross-reference
    for state in doc_states:
        if state not in table_states:
            result.add_error(
                filename,
                None,
                "10.4",
                f"State '{state}' in states.md not found in tables.md STATES table",
            )

    # Extract config keys from config.md (look for keys in tables)
    config_key_pattern = re.compile(r"`(\w+)`\s*\|")
    doc_config = set()
    for match in config_key_pattern.finditer(config_content):
        key = match.group(1)
        if key not in [
            "Option",
            "Type",
            "Default",
            "Description",
            "key",
            "type",
            "default",
        ]:
            doc_config.add(key)

    # Check config cross-reference
    for option in doc_config:
        if option not in table_config and option not in ["version"]:
            result.add_warning(
                filename,
                None,
                "10.3",
                f"Config option '{option}' in config.md may not be in tables.md CONFIG_OPTIONS table",
            )

    return result


# =============================================================================
# Main Validation Functions
# =============================================================================


def validate_file(
    filepath: Path, tables_definitions: dict[str, set[str]] = None
) -> ValidationResult:
    """Validate a single documentation file."""
    result = ValidationResult()

    if not filepath.exists():
        result.add_error(str(filepath), None, "FILE", f"File not found: {filepath}")
        return result

    content = filepath.read_text()
    filename = str(filepath)

    # Run all validators
    result.merge(validate_heading_hierarchy(content, filename))
    result.merge(validate_table_syntax(content, filename))
    result.merge(validate_code_blocks(content, filename))
    result.merge(validate_entry_completeness(content, filename))
    result.merge(validate_sid_naming(content, filename))
    result.merge(validate_flag_prefixes(content, filename))
    result.merge(validate_rule_format(content, filename))
    result.merge(validate_modular_syntax(content, filename))

    # New validators for expanded documentation
    if filepath.name == "api.md":
        result.merge(validate_api_completeness(content, filename))
    elif filepath.name == "schemas.md":
        result.merge(validate_schema_completeness(content, filename))
    elif filepath.name == "errors.md":
        result.merge(validate_error_catalog(content, filename))
    elif filepath.name == "states.md":
        result.merge(validate_state_transitions(content, filename))

    # Cross-reference validation requires tables definitions
    if tables_definitions:
        result.merge(validate_cross_references(content, filename, tables_definitions))

        # Example coverage only for examples.md
        if filepath.name == "examples.md":
            result.merge(
                validate_example_coverage(content, filename, tables_definitions)
            )

    # Mark file as validated after processing
    result.mark_file_validated(filename)

    return result


def validate_all_docs(docs_dir: Path) -> ValidationResult:
    """Validate all documentation files."""
    result = ValidationResult()

    # First, extract definitions from tables.md (SSOT)
    tables_path = docs_dir / "tables.md"
    tables_definitions = {}
    tables_content = ""

    if tables_path.exists():
        tables_content = tables_path.read_text()
        tables_definitions = extract_definitions_from_tables(tables_content)
    else:
        result.add_error(
            "tables.md",
            None,
            "FILE",
            "tables.md not found - cannot validate cross-references",
        )

    # Validate each documentation file (original + new)
    doc_files = [
        "tables.md",
        "overview.md",
        "examples.md",
        "README.md",
        "api.md",
        "schemas.md",
        "errors.md",
        "config.md",
        "states.md",
        "testing.md",
    ]

    for doc_file in doc_files:
        filepath = docs_dir / doc_file
        if filepath.exists():
            file_result = validate_file(filepath, tables_definitions)
            result.merge(file_result)
        else:
            result.add_warning(
                str(filepath), None, "FILE", f"Documentation file not found: {doc_file}"
            )

    # Validate cross-references between new documents and tables.md
    if tables_content:
        errors_path = docs_dir / "errors.md"
        states_path = docs_dir / "states.md"
        config_path = docs_dir / "config.md"

        errors_content = errors_path.read_text() if errors_path.exists() else ""
        states_content = states_path.read_text() if states_path.exists() else ""
        config_content = config_path.read_text() if config_path.exists() else ""

        if errors_content or states_content or config_content:
            result.merge(
                validate_new_table_cross_references(
                    errors_content,
                    states_content,
                    config_content,
                    tables_content,
                    "cross-refs",
                )
            )

    # Validate documentation-to-code sync
    # Assumes source is in vince/ relative to docs parent directory
    src_dir = docs_dir.parent / "vince"
    if src_dir.exists():
        result.merge(validate_code_documentation_sync(docs_dir, src_dir))

    return result


def validate_cross_refs_only(docs_dir: Path) -> ValidationResult:
    """Validate only cross-references between documents."""
    result = ValidationResult()

    tables_path = docs_dir / "tables.md"
    if not tables_path.exists():
        result.add_error("tables.md", None, "FILE", "tables.md not found")
        return result

    tables_content = tables_path.read_text()
    tables_definitions = extract_definitions_from_tables(tables_content)

    doc_files = ["overview.md", "examples.md", "README.md"]

    for doc_file in doc_files:
        filepath = docs_dir / doc_file
        if filepath.exists():
            content = filepath.read_text()
            result.merge(
                validate_cross_references(content, str(filepath), tables_definitions)
            )
            if doc_file == "examples.md":
                result.merge(
                    validate_example_coverage(
                        content, str(filepath), tables_definitions
                    )
                )

    return result


def print_report(result: ValidationResult):
    """Print a formatted validation report."""
    print("\n" + "=" * 60)
    print("DOCUMENTATION VALIDATION REPORT")
    print("=" * 60)

    if result.errors:
        print(f"\n❌ ERRORS ({len(result.errors)}):")
        print("-" * 40)
        for err in result.errors:
            line_info = f":{err.line}" if err.line else ""
            print(f"  [{err.rule}] {err.file}{line_info}")
            print(f"         {err.message}")

    if result.warnings:
        print(f"\n⚠️  WARNINGS ({len(result.warnings)}):")
        print("-" * 40)
        for warn in result.warnings:
            line_info = f":{warn.line}" if warn.line else ""
            print(f"  [{warn.rule}] {warn.file}{line_info}")
            print(f"         {warn.message}")

    print("\n" + "=" * 60)
    if result.is_valid:
        print("✅ VALIDATION PASSED")
    else:
        print(
            f"❌ VALIDATION FAILED ({len(result.errors)} errors, {len(result.warnings)} warnings)"
        )
    print("=" * 60 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Validate vince CLI documentation files"
    )
    parser.add_argument(
        "--all", action="store_true", help="Validate all documentation files"
    )
    parser.add_argument("--file", type=str, help="Validate a specific file")
    parser.add_argument(
        "--cross-refs", action="store_true", help="Validate only cross-references"
    )
    parser.add_argument(
        "--report", action="store_true", help="Generate a detailed compliance report"
    )
    parser.add_argument(
        "--docs-dir",
        type=str,
        default="docs",
        help="Path to documentation directory (default: docs)",
    )

    args = parser.parse_args()
    docs_dir = Path(args.docs_dir)

    if args.file:
        filepath = (
            docs_dir / args.file
            if not Path(args.file).is_absolute()
            else Path(args.file)
        )

        # Load tables definitions for cross-reference validation
        tables_path = docs_dir / "tables.md"
        tables_definitions = {}
        if tables_path.exists():
            tables_definitions = extract_definitions_from_tables(
                tables_path.read_text()
            )

        result = validate_file(filepath, tables_definitions)
    elif args.cross_refs:
        result = validate_cross_refs_only(docs_dir)
    else:
        # Default: validate all
        result = validate_all_docs(docs_dir)

    print_report(result)

    sys.exit(0 if result.is_valid else 1)


if __name__ == "__main__":
    main()
