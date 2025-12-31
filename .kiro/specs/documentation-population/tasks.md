# Implementation Plan: Documentation Population

## Overview

This implementation plan populates and standardizes all `vince` CLI documentation files. The approach starts with tables.md as the Single Source of Truth, then propagates consistent definitions to all other documents.

## Tasks

- [x] 1. Populate tables.md as Single Source of Truth
  - [x] 1.1 Fix heading hierarchy (H1 → H2 → H3)
    - Change `### DEFINITIONS` to `## DEFINITIONS`
    - Ensure proper markdown structure
    - _Requirements: 1.1, 1.2_

  - [x] 1.2 Complete DEFINITIONS table with all id/sid pairs
    - Add missing definitions from overview.md
    - Add `rid` column to definitions
    - Ensure all system terms are defined
    - _Requirements: 2.1, 6.1_

  - [x] 1.3 Complete COMMANDS table with id, sid, rid, and description
    - Add `rid` and `description` columns
    - Include all 7 commands: slap, chop, set, forget, offer, reject, list
    - _Requirements: 2.1, 6.2_

  - [x] 1.4 Complete FILE_TYPES table with id, full_id, ext, sid, and flags
    - Add `sid` and flag columns
    - Ensure all 12 file types are documented
    - _Requirements: 2.2, 6.3_

  - [x] 1.5 Create FLAGS tables by category
    - Create UTILITY_FLAGS table (help, version, verbose, debug, trace)
    - Create QOL_FLAGS table (set, forget, slap, chop, offer, reject)
    - Create LIST_FLAGS table (app, cmd, ext, def, off, all)
    - _Requirements: 2.3, 4.1, 4.2, 4.4, 6.4_

  - [x] 1.6 Create OPERATORS table
    - Document `--`, `-`, `.` operators
    - Include symbol, name, and usage columns
    - _Requirements: 6.5_

  - [x] 1.7 Create ARGUMENTS table
    - Document path, file_extension, offer arguments
    - Include pattern and description columns
    - _Requirements: 6.6_

  - [x] 1.8 Create RULES table
    - Document PD01, UID01, TB01, TB02, TB03
    - Include rid, category, and description columns
    - _Requirements: 9.1, 9.3_

- [x] 2. Checkpoint - Verify tables.md completeness
  - Ensure all tables have proper headers and separators
  - Verify no duplicate sid values
  - Ensure all tests pass, ask the user if questions arise.

- [x] 3. Update overview.md for consistency
  - [x] 3.1 Align heading hierarchy
    - Ensure H1 → H2 → H3 structure
    - Fix any heading level jumps
    - _Requirements: 1.1, 1.2_

  - [x] 3.2 Update ID System documentation
    - Ensure id/sid/rid/num definitions match tables.md
    - Add cross-reference to tables.md for complete listings
    - _Requirements: 5.3, 5.5_

  - [x] 3.3 Update Commands section
    - Ensure all 7 commands are documented
    - Add `list` command documentation
    - Ensure descriptions match tables.md
    - _Requirements: 3.1, 5.1_

  - [x] 3.4 Update FLAGS sections
    - Organize into Utility, QOL, Extension, List categories
    - Ensure all flags have consistent `-` and `--` prefixes
    - Add missing list subsection flags documentation
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

  - [x] 3.5 Document command-QOL flag relationships
    - Explicitly state that QOL flags mirror commands
    - Document slap auto-creates offer behavior
    - _Requirements: 3.3, 3.4_

  - [x] 3.6 Document `.` operator usage per command
    - Add operator usage examples for each applicable command
    - _Requirements: 3.5_

  - [x] 3.7 Ensure [PD01] modular design principle is prominent
    - Move to top of document or highlight in introduction
    - _Requirements: 10.1, 10.4_

  - [x] 3.8 Add code block language identifiers
    - Ensure all code blocks have `sh` or appropriate language tag
    - _Requirements: 1.4_

  - [x] 3.9 Standardize note/callout syntax
    - Use `> [!NOTE]` format consistently
    - _Requirements: 1.5_

- [x] 4. Checkpoint - Verify overview.md consistency
  - Cross-reference all definitions with tables.md
  - Verify rule references use [rid] notation
  - Ensure all tests pass, ask the user if questions arise.

- [x] 5. Update examples.md for completeness
  - [x] 5.1 Complete `slap` examples
    - Ensure multi-step example is complete
    - Add flag combination examples
    - Document auto-offer creation behavior
    - _Requirements: 7.1, 7.2_

  - [x] 5.2 Complete `chop` examples
    - Add complete syntax examples
    - Add `.` operator usage example
    - _Requirements: 7.1, 7.3_

  - [x] 5.3 Complete `set` examples
    - Ensure examples are distinct from slap
    - Add flag combinations
    - _Requirements: 7.1, 7.2_

  - [x] 5.4 Complete `forget` examples
    - Add complete syntax examples
    - Add `.` operator usage example
    - _Requirements: 7.1, 7.3_

  - [x] 5.5 Add `offer` examples section
    - Create new section for offer command
    - Show offer creation syntax
    - _Requirements: 7.1_

  - [x] 5.6 Add `reject` examples section
    - Create new section for reject command
    - Show reject and complete-delete syntax
    - _Requirements: 7.1_

  - [x] 5.7 Complete `list` examples
    - Add examples for all subsection flags (-app, -cmd, -ext, -def, -off, -all)
    - _Requirements: 7.4_

  - [x] 5.8 Standardize step notation
    - Use consistent sid notation (S1, S2) for step references
    - _Requirements: 7.5_

  - [x] 5.9 Add code block language identifiers
    - Ensure all code blocks have `sh` language tag
    - _Requirements: 1.4_

- [x] 6. Checkpoint - Verify examples.md completeness
  - Verify all 7 commands have examples
  - Verify no underscore-joined commands in examples
  - Ensure all tests pass, ask the user if questions arise.

- [x] 7. Update README.md for professional presentation
  - [x] 7.1 Populate framework links
    - Replace XXXXXXX placeholders with actual URLs
    - _Requirements: 5.4, 8.1_

  - [x] 7.2 Verify installation structure
    - Ensure Quick Install, Step One, Step Two, Step Three sections exist
    - _Requirements: 8.2_

  - [x] 7.3 Verify troubleshooting section
    - Ensure troubleshooting section is complete
    - _Requirements: 8.3_

  - [x] 7.4 Add documentation references
    - Add links to overview.md, examples.md, tables.md
    - Create "Documentation" section
    - _Requirements: 8.4_

  - [x] 7.5 Add code block language identifiers
    - Ensure all code blocks have `sh` language tag
    - _Requirements: 1.4_

- [x] 8. Final Checkpoint - Cross-reference validation
  - Verify all commands in examples.md exist in overview.md
  - Verify all file types in overview.md exist in tables.md
  - Verify all sid values are defined in tables.md
  - Verify no placeholder links remain
  - Verify identical definitions across documents
  - Ensure all tests pass, ask the user if questions arise.

- [x] 9. Create validation script
  - [x] 9.1 Implement heading hierarchy validator
    - Parse markdown and validate H1 → H2 → H3 structure
    - **Property 1: Heading hierarchy validation**
    - **Validates: Requirements 1.1, 1.2**

  - [x] 9.2 Implement table syntax validator
    - Validate table headers and separators
    - **Property 2: Table syntax validation**
    - **Validates: Requirements 1.3**

  - [x] 9.3 Implement code block validator
    - Check for language identifiers
    - **Property 3: Code block language identifiers**
    - **Validates: Requirements 1.4**

  - [x] 9.4 Implement entry completeness validator
    - Verify all required fields present
    - **Property 4: Entry field completeness**
    - **Validates: Requirements 2.1, 2.2, 2.3**

  - [x] 9.5 Implement sid naming validator
    - Verify naming convention compliance
    - **Property 5: SID naming convention compliance**
    - **Validates: Requirements 2.4, 2.5**

  - [x] 9.6 Implement cross-reference validator
    - Verify all references resolve
    - **Property 6: Cross-reference consistency**
    - **Validates: Requirements 5.1, 5.2, 5.3, 5.5**

  - [x] 9.7 Implement flag prefix validator
    - Verify `-` and `--` conventions
    - **Property 7: Flag prefix convention**
    - **Validates: Requirements 4.5**

  - [x] 9.8 Implement example coverage validator
    - Verify all commands have examples
    - **Property 8: Example completeness per command**
    - **Validates: Requirements 3.1, 3.2, 7.1, 7.2**

  - [x] 9.9 Implement rule format validator
    - Verify rid format and bracket notation
    - **Property 9: Rule reference format consistency**
    - **Validates: Requirements 9.2, 9.4**

  - [x] 9.10 Implement modular syntax validator
    - Verify no underscore-joined commands
    - **Property 10: Modular command syntax**
    - **Validates: Requirements 10.2, 10.3**

- [x] 10. Fix validation errors in documentation
  - [x] 10.1 Resolve duplicate SID conflicts in tables.md
    - Change `application` sid from `app` to unique value (e.g., `ap`)
    - Change `extension` sid from `ext` to unique value (e.g., `ex`)
    - Change `command` sid from `cmd` to unique value (e.g., `cm`)
    - Change `offer` sid from `off` to unique value (e.g., `of`)
    - Ensure DEFINITIONS table sids don't conflict with LIST_FLAGS sids
    - _Requirements: 2.5, 6.1_

  - [x] 10.2 Fix overview.md table schemas
    - Update Commands table to not trigger COMMANDS schema validation (rename section or adjust validator)
    - Update Operators table to not trigger OPERATORS schema validation
    - Update Arguments table to not trigger ARGUMENTS schema validation
    - _Requirements: 2.1_

  - [x] 10.3 Fix Extension Flags table structure in overview.md
    - Change column headers from `Short | Long | Sets Default For` to proper flag format
    - Extension flags use `--` prefix for both short and long forms (they are long flags)
    - Update table to reflect that extension flags don't have single-dash short forms
    - _Requirements: 4.5_

- [x] 11. Final validation checkpoint
  - Run `python validate_docs.py --all` and verify 0 errors
  - Ensure all property-based tests pass
  - _Requirements: All_

## Notes

- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- tables.md must be completed first as it is the Single Source of Truth
- All other documents reference tables.md for canonical definitions
- Task 10 addresses validation errors discovered after initial implementation
