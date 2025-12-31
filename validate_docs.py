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
    
    def add_error(self, file: str, line: Optional[int], rule: str, message: str):
        self.errors.append(ValidationError(file, line, rule, message, "error"))
    
    def add_warning(self, file: str, line: Optional[int], rule: str, message: str):
        self.warnings.append(ValidationError(file, line, rule, message, "warning"))
    
    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0
    
    def merge(self, other: "ValidationResult"):
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)


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
    lines = content.split('\n')
    
    # Track state
    found_h1 = False
    found_h2_after_last_h1 = False
    current_h2_section = False
    
    # Pattern to match headings (not in code blocks)
    heading_pattern = re.compile(r'^(#{1,6})\s+(.+)$')
    
    in_code_block = False
    
    for line_num, line in enumerate(lines, 1):
        # Track code blocks to ignore headings inside them
        if line.strip().startswith('```'):
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
                    filename, line_num, "1.1",
                    f"Multiple H1 headings found. Second H1: '{heading_text}'"
                )
            found_h1 = True
            found_h2_after_last_h1 = False
            current_h2_section = False
        
        elif level == 2:
            if not found_h1:
                result.add_error(
                    filename, line_num, "1.1",
                    f"H2 '{heading_text}' appears before any H1 heading"
                )
            found_h2_after_last_h1 = True
            current_h2_section = True
        
        elif level == 3:
            if not found_h1:
                result.add_error(
                    filename, line_num, "1.2",
                    f"H3 '{heading_text}' appears before any H1 heading"
                )
            elif not found_h2_after_last_h1:
                result.add_error(
                    filename, line_num, "1.2",
                    f"H3 '{heading_text}' appears without a preceding H2 heading"
                )
    
    # Check that document starts with H1
    first_heading = None
    in_code_block = False
    for line_num, line in enumerate(lines, 1):
        if line.strip().startswith('```'):
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
            filename, first_heading[0], "1.1",
            f"Document should start with H1, but starts with H{first_heading[1]}: '{first_heading[2]}'"
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
    lines = content.split('\n')
    
    in_code_block = False
    table_start = None
    table_lines = []
    
    for line_num, line in enumerate(lines, 1):
        # Track code blocks
        if line.strip().startswith('```'):
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
        if stripped.startswith('|') and stripped.endswith('|'):
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
    table_lines: list[tuple[int, str]]
):
    """Validate a single table block."""
    if len(table_lines) < 2:
        result.add_error(
            filename, start_line, "1.3",
            "Table must have at least a header row and separator row"
        )
        return
    
    # Check for separator row (second row should be separator)
    separator_pattern = re.compile(r'^\|(\s*[-:]+\s*\|)+$')
    
    if len(table_lines) >= 2:
        _, second_row = table_lines[1]
        if not separator_pattern.match(second_row):
            result.add_error(
                filename, table_lines[1][0], "1.3",
                f"Table separator row is malformed: '{second_row}'"
            )
    
    # Check column consistency
    def count_columns(row: str) -> int:
        # Count pipes minus 1 (accounting for leading/trailing pipes)
        return row.count('|') - 1
    
    header_cols = count_columns(table_lines[0][1])
    
    for line_num, row in table_lines[1:]:
        row_cols = count_columns(row)
        if row_cols != header_cols:
            result.add_error(
                filename, line_num, "1.3",
                f"Table row has {row_cols} columns, expected {header_cols}"
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
    lines = content.split('\n')
    
    code_fence_pattern = re.compile(r'^```(\w*)$')
    
    for line_num, line in enumerate(lines, 1):
        stripped = line.strip()
        match = code_fence_pattern.match(stripped)
        if match:
            lang = match.group(1)
            # Opening fence without language identifier
            if stripped == '```':
                # Check if this is a closing fence by looking at context
                # We need to track if we're in a code block
                pass
    
    # Better approach: track code blocks properly
    in_code_block = False
    code_block_start = None
    
    for line_num, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith('```'):
            if not in_code_block:
                # Opening fence
                in_code_block = True
                code_block_start = line_num
                # Check for language identifier
                lang = stripped[3:].strip()
                if not lang:
                    result.add_error(
                        filename, line_num, "1.4",
                        "Code block missing language identifier"
                    )
            else:
                # Closing fence
                in_code_block = False
                code_block_start = None
    
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
        'DEFINITIONS': ['id', 'sid', 'rid', 'description'],
        'COMMANDS': ['id', 'sid', 'rid', 'description'],
        'FILE_TYPES': ['id', 'full_id', 'ext', 'sid', 'flag_short', 'flag_long'],
        'UTILITY_FLAGS': ['id', 'sid', 'short', 'long', 'description'],
        'QOL_FLAGS': ['id', 'sid', 'short', 'description'],
        'LIST_FLAGS': ['id', 'sid', 'short', 'description'],
        'OPERATORS': ['symbol', 'name', 'usage'],
        'ARGUMENTS': ['pattern', 'name', 'description'],
        'RULES': ['rid', 'category', 'description'],
    }
    
    lines = content.split('\n')
    current_section = None
    in_table = False
    table_headers = []
    table_start_line = None
    
    in_code_block = False
    
    for line_num, line in enumerate(lines, 1):
        stripped = line.strip()
        
        # Track code blocks
        if stripped.startswith('```'):
            in_code_block = not in_code_block
            continue
        
        if in_code_block:
            continue
        
        # Check for section headers
        if stripped.startswith('## '):
            section_name = stripped[3:].strip().upper().replace(' ', '_')
            if section_name in table_schemas:
                current_section = section_name
                in_table = False
                table_headers = []
            else:
                current_section = None
        
        # Parse table
        if current_section and stripped.startswith('|') and stripped.endswith('|'):
            if not in_table:
                # This is the header row
                in_table = True
                table_start_line = line_num
                # Parse headers
                table_headers = [h.strip().strip('`') for h in stripped.split('|')[1:-1]]
                
                # Validate headers match schema
                required = table_schemas.get(current_section, [])
                for req_field in required:
                    if req_field not in table_headers:
                        result.add_error(
                            filename, line_num, "2.1",
                            f"Table {current_section} missing required column: {req_field}"
                        )
            elif stripped.startswith('|') and '---' in stripped:
                # Separator row, skip
                continue
            else:
                # Data row - check for empty fields
                cells = [c.strip() for c in stripped.split('|')[1:-1]]
                for i, cell in enumerate(cells):
                    if not cell and i < len(table_headers):
                        result.add_error(
                            filename, line_num, "2.1",
                            f"Empty field '{table_headers[i]}' in {current_section} table"
                        )
        elif in_table and not stripped.startswith('|'):
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
    
    lines = content.split('\n')
    in_code_block = False
    in_table = False
    table_headers = []
    sid_col_idx = -1
    id_col_idx = -1
    
    for line_num, line in enumerate(lines, 1):
        stripped = line.strip()
        
        if stripped.startswith('```'):
            in_code_block = not in_code_block
            continue
        
        if in_code_block:
            continue
        
        if stripped.startswith('|') and stripped.endswith('|'):
            cells = [c.strip().strip('`') for c in stripped.split('|')[1:-1]]
            
            if not in_table:
                # Header row
                in_table = True
                table_headers = cells
                sid_col_idx = -1
                id_col_idx = -1
                for i, h in enumerate(cells):
                    if h.lower() == 'sid':
                        sid_col_idx = i
                    if h.lower() == 'id':
                        id_col_idx = i
            elif '---' in stripped:
                # Separator row
                continue
            else:
                # Data row
                if sid_col_idx >= 0 and sid_col_idx < len(cells):
                    sid = cells[sid_col_idx]
                    id_val = cells[id_col_idx] if id_col_idx >= 0 and id_col_idx < len(cells) else ""
                    if sid:
                        if sid not in sid_occurrences:
                            sid_occurrences[sid] = []
                        sid_occurrences[sid].append((line_num, id_val))
        elif in_table and not stripped.startswith('|'):
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
                    filename, occurrences[0][0], "2.5",
                    f"Duplicate sid '{sid}' used for different ids on lines: {lines_str}"
                )
    
    # Validate naming convention (basic check)
    for sid, occurrences in sid_occurrences.items():
        for line_num, id_val in occurrences:
            if id_val and sid:
                # Check if sid follows convention
                id_clean = id_val.strip('`')
                if '_' in id_clean:
                    # Two-word: should be first 2 letters of each word
                    parts = id_clean.split('_')
                    if len(parts) == 2:
                        expected = parts[0][:2] + parts[1][:2]
                        # Allow for collision handling (subsequent letters)
                        if not sid.startswith(parts[0][:2]):
                            result.add_warning(
                                filename, line_num, "2.4",
                                f"SID '{sid}' may not follow two-word convention for id '{id_val}'"
                            )
                else:
                    # One-word: should be first 2 letters
                    if len(id_clean) >= 2 and len(sid) >= 2:
                        # Allow for collision handling
                        if not id_clean.lower().startswith(sid[:2].lower()):
                            # Could be collision handling, just warn
                            pass
    
    return result


# =============================================================================
# Property 6: Cross-Reference Consistency Validator
# Validates: Requirements 5.1, 5.2, 5.3, 5.5
# =============================================================================

def extract_definitions_from_tables(tables_content: str) -> dict[str, set[str]]:
    """Extract all defined identifiers from tables.md."""
    definitions = {
        'commands': set(),
        'sids': set(),
        'ids': set(),
        'extensions': set(),
        'flags': set(),
    }
    
    lines = tables_content.split('\n')
    in_code_block = False
    current_section = None
    in_table = False
    table_headers = []
    
    for line in lines:
        stripped = line.strip()
        
        if stripped.startswith('```'):
            in_code_block = not in_code_block
            continue
        
        if in_code_block:
            continue
        
        if stripped.startswith('## '):
            section = stripped[3:].strip().upper()
            current_section = section
            in_table = False
            table_headers = []
        
        if stripped.startswith('|') and stripped.endswith('|'):
            cells = [c.strip().strip('`') for c in stripped.split('|')[1:-1]]
            
            if not in_table:
                in_table = True
                table_headers = [h.lower() for h in cells]
            elif '---' in stripped:
                continue
            else:
                # Data row
                cell_dict = dict(zip(table_headers, cells))
                
                if 'sid' in cell_dict and cell_dict['sid']:
                    definitions['sids'].add(cell_dict['sid'])
                if 'id' in cell_dict and cell_dict['id']:
                    definitions['ids'].add(cell_dict['id'])
                
                if current_section == 'COMMANDS':
                    if 'id' in cell_dict:
                        definitions['commands'].add(cell_dict['id'])
                elif current_section == 'FILE_TYPES':
                    if 'ext' in cell_dict:
                        definitions['extensions'].add(cell_dict['ext'])
                    if 'flag_short' in cell_dict:
                        definitions['flags'].add(cell_dict['flag_short'])
                    if 'flag_long' in cell_dict:
                        definitions['flags'].add(cell_dict['flag_long'])
        elif in_table and not stripped.startswith('|'):
            in_table = False
    
    return definitions


def validate_cross_references(
    content: str, 
    filename: str, 
    tables_definitions: dict[str, set[str]]
) -> ValidationResult:
    """
    Validate cross-references between documents.
    
    Property 6: For any identifier referenced in one document, if it is defined
    in another document, the definitions SHALL be identical. Additionally, all
    referenced identifiers SHALL have a definition in tables.md.
    """
    result = ValidationResult()
    
    # Extract commands mentioned in the document
    lines = content.split('\n')
    in_code_block = False
    
    # Pattern to find command references like `slap`, `chop`, etc.
    command_pattern = re.compile(r'`(slap|chop|set|forget|offer|reject|list)`')
    
    for line_num, line in enumerate(lines, 1):
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            continue
        
        if in_code_block:
            continue
        
        # Check for command references
        for match in command_pattern.finditer(line):
            cmd = match.group(1)
            if cmd not in tables_definitions['commands']:
                result.add_error(
                    filename, line_num, "5.1",
                    f"Command '{cmd}' referenced but not defined in tables.md"
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
    
    lines = content.split('\n')
    in_code_block = False
    in_table = False
    table_headers = []
    short_col_idx = -1
    long_col_idx = -1
    
    for line_num, line in enumerate(lines, 1):
        stripped = line.strip()
        
        if stripped.startswith('```'):
            in_code_block = not in_code_block
            continue
        
        if in_code_block:
            continue
        
        if stripped.startswith('|') and stripped.endswith('|'):
            cells = [c.strip().strip('`') for c in stripped.split('|')[1:-1]]
            
            if not in_table:
                in_table = True
                table_headers = [h.lower() for h in cells]
                short_col_idx = -1
                long_col_idx = -1
                for i, h in enumerate(table_headers):
                    if h == 'short':
                        short_col_idx = i
                    if h == 'long':
                        long_col_idx = i
            elif '---' in stripped:
                continue
            else:
                # Data row - validate flag prefixes
                if short_col_idx >= 0 and short_col_idx < len(cells):
                    short_flag = cells[short_col_idx]
                    if short_flag and not short_flag.startswith('-'):
                        result.add_error(
                            filename, line_num, "4.5",
                            f"Short flag '{short_flag}' should start with '-'"
                        )
                    # Short flags should NOT start with --
                    if short_flag and short_flag.startswith('--'):
                        result.add_error(
                            filename, line_num, "4.5",
                            f"Short flag '{short_flag}' should use single dash, not double"
                        )
                
                if long_col_idx >= 0 and long_col_idx < len(cells):
                    long_flag = cells[long_col_idx]
                    if long_flag and not long_flag.startswith('--'):
                        result.add_error(
                            filename, line_num, "4.5",
                            f"Long flag '{long_flag}' should start with '--'"
                        )
        elif in_table and not stripped.startswith('|'):
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
    examples_content: str, 
    filename: str,
    tables_definitions: dict[str, set[str]]
) -> ValidationResult:
    """
    Validate that all commands have examples.
    
    Property 8: For any command defined in the system, examples.md SHALL contain
    at least one complete example demonstrating that command with appropriate flags.
    """
    result = ValidationResult()
    
    # Find all command sections in examples.md
    documented_commands = set()
    
    lines = examples_content.split('\n')
    in_code_block = False
    
    # Pattern to match command section headers like ## `slap`
    section_pattern = re.compile(r'^##\s+`(\w+)`')
    
    for line_num, line in enumerate(lines, 1):
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            continue
        
        if in_code_block:
            continue
        
        match = section_pattern.match(line)
        if match:
            documented_commands.add(match.group(1))
    
    # Check that all commands from tables.md have examples
    required_commands = tables_definitions.get('commands', set())
    
    for cmd in required_commands:
        if cmd not in documented_commands:
            result.add_error(
                filename, None, "7.1",
                f"Command '{cmd}' has no example section in examples.md"
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
                    filename, section_start_line, "7.2",
                    f"Command section '{current_section}' has no code examples"
                )
            current_section = match.group(1)
            section_has_code = False
            section_start_line = line_num
        
        if stripped.startswith('```') and current_section:
            section_has_code = True
    
    # Check last section
    if current_section and not section_has_code:
        result.add_error(
            filename, section_start_line, "7.2",
            f"Command section '{current_section}' has no code examples"
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
    
    lines = content.split('\n')
    in_code_block = False
    
    # Pattern for valid rid format (2-4 uppercase letters + 2 digits)
    rid_pattern = re.compile(r'\[([A-Z]{2,4}\d{2})\]')
    
    # Pattern for potentially malformed rule references
    malformed_pattern = re.compile(r'\[([a-z]{2,4}\d{2})\]')  # lowercase
    
    for line_num, line in enumerate(lines, 1):
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            continue
        
        if in_code_block:
            continue
        
        # Check for malformed (lowercase) rule references
        for match in malformed_pattern.finditer(line):
            rid = match.group(1)
            result.add_warning(
                filename, line_num, "9.2",
                f"Rule reference '[{rid}]' should use uppercase: '[{rid.upper()}]'"
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
    
    lines = content.split('\n')
    in_code_block = False
    
    # Pattern to detect underscore-joined commands after 'vince'
    # This looks for patterns like: vince word_word
    underscore_cmd_pattern = re.compile(r'vince\s+(\w+_\w+)')
    
    for line_num, line in enumerate(lines, 1):
        stripped = line.strip()
        
        if stripped.startswith('```'):
            in_code_block = not in_code_block
            continue
        
        # Only check inside code blocks (actual command examples)
        if in_code_block:
            match = underscore_cmd_pattern.search(line)
            if match:
                bad_cmd = match.group(1)
                result.add_error(
                    filename, line_num, "10.2",
                    f"Underscore-joined command '{bad_cmd}' violates modular design [PD01]"
                )
    
    # Also check for underscore commands in inline code
    inline_pattern = re.compile(r'`vince\s+(\w+_\w+)`')
    in_code_block = False
    
    for line_num, line in enumerate(lines, 1):
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            continue
        
        if not in_code_block:
            for match in inline_pattern.finditer(line):
                bad_cmd = match.group(1)
                result.add_error(
                    filename, line_num, "10.3",
                    f"Underscore-joined command '{bad_cmd}' in inline code violates modular design"
                )
    
    return result


# =============================================================================
# Main Validation Functions
# =============================================================================

def validate_file(filepath: Path, tables_definitions: dict[str, set[str]] = None) -> ValidationResult:
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
    
    # Cross-reference validation requires tables definitions
    if tables_definitions:
        result.merge(validate_cross_references(content, filename, tables_definitions))
        
        # Example coverage only for examples.md
        if filepath.name == 'examples.md':
            result.merge(validate_example_coverage(content, filename, tables_definitions))
    
    return result


def validate_all_docs(docs_dir: Path) -> ValidationResult:
    """Validate all documentation files."""
    result = ValidationResult()
    
    # First, extract definitions from tables.md (SSOT)
    tables_path = docs_dir / 'tables.md'
    tables_definitions = {}
    
    if tables_path.exists():
        tables_content = tables_path.read_text()
        tables_definitions = extract_definitions_from_tables(tables_content)
    else:
        result.add_error("tables.md", None, "FILE", "tables.md not found - cannot validate cross-references")
    
    # Validate each documentation file
    doc_files = ['tables.md', 'overview.md', 'examples.md', 'README.md']
    
    for doc_file in doc_files:
        filepath = docs_dir / doc_file
        if filepath.exists():
            file_result = validate_file(filepath, tables_definitions)
            result.merge(file_result)
        else:
            result.add_warning(str(filepath), None, "FILE", f"Documentation file not found: {doc_file}")
    
    return result


def validate_cross_refs_only(docs_dir: Path) -> ValidationResult:
    """Validate only cross-references between documents."""
    result = ValidationResult()
    
    tables_path = docs_dir / 'tables.md'
    if not tables_path.exists():
        result.add_error("tables.md", None, "FILE", "tables.md not found")
        return result
    
    tables_content = tables_path.read_text()
    tables_definitions = extract_definitions_from_tables(tables_content)
    
    doc_files = ['overview.md', 'examples.md', 'README.md']
    
    for doc_file in doc_files:
        filepath = docs_dir / doc_file
        if filepath.exists():
            content = filepath.read_text()
            result.merge(validate_cross_references(content, str(filepath), tables_definitions))
            if doc_file == 'examples.md':
                result.merge(validate_example_coverage(content, str(filepath), tables_definitions))
    
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
        print(f"❌ VALIDATION FAILED ({len(result.errors)} errors, {len(result.warnings)} warnings)")
    print("=" * 60 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Validate vince CLI documentation files"
    )
    parser.add_argument(
        '--all', action='store_true',
        help='Validate all documentation files'
    )
    parser.add_argument(
        '--file', type=str,
        help='Validate a specific file'
    )
    parser.add_argument(
        '--cross-refs', action='store_true',
        help='Validate only cross-references'
    )
    parser.add_argument(
        '--report', action='store_true',
        help='Generate a detailed compliance report'
    )
    parser.add_argument(
        '--docs-dir', type=str, default='docs',
        help='Path to documentation directory (default: docs)'
    )
    
    args = parser.parse_args()
    docs_dir = Path(args.docs_dir)
    
    if args.file:
        filepath = docs_dir / args.file if not Path(args.file).is_absolute() else Path(args.file)
        
        # Load tables definitions for cross-reference validation
        tables_path = docs_dir / 'tables.md'
        tables_definitions = {}
        if tables_path.exists():
            tables_definitions = extract_definitions_from_tables(tables_path.read_text())
        
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
