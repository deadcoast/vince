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

- [ ] 3. Update overview.md for consistency
  - [ ] 3.1 Align heading hierarchy
    - Ensure H1 → H2 → H3 structure
    - Fix any heading level jumps
    - _Requirements: 1.1, 1.2_

  - [ ] 3.2 Update ID System documentation
    - Ensure id/sid/rid/num definitions match tables.md
    - Add cross-reference to tables.md for complete listings
    - _Requirements: 5.3, 5.5_

  - [ ] 3.3 Update Commands section
    - Ensure all 7 commands are documented
    - Add `list` command documentation
    - Ensure descriptions match tables.md
    - _Requirements: 3.1, 5.1_

  - [ ] 3.4 Update FLAGS sections
    - Organize into Utility, QOL, Extension, List categories
    - Ensure all flags have consistent `-` and `--` prefixes
    - Add missing list subsection flags documentation
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

  - [ ] 3.5 Document command-QOL flag relationships
    - Explicitly state that QOL flags mirror commands
    - Document slap auto-creates offer behavior
    - _Requirements: 3.3, 3.4_

  - [ ] 3.6 Document `.` operator usage per command
    - Add operator usage examples for each applicable command
    - _Requirements: 3.5_

  - [ ] 3.7 Ensure [PD01] modular design principle is prominent
    - Move to top of document or highlight in introduction
    - _Requirements: 10.1, 10.4_

  - [ ] 3.8 Add code block language identifiers
    - Ensure all code blocks have `sh` or appropriate language tag
    - _Requirements: 1.4_

  - [ ] 3.9 Standardize note/callout syntax
    - Use `> [!NOTE]` format consistently
    - _Requirements: 1.5_

- [ ] 4. Checkpoint - Verify overview.md consistency
  - Cross-reference all definitions with tables.md
  - Verify rule references use [rid] notation
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 5. Update examples.md for completeness
  - [ ] 5.1 Complete `slap` examples
    - Ensure multi-step example is complete
    - Add flag combination examples
    - Document auto-offer creation behavior
    - _Requirements: 7.1, 7.2_

  - [ ] 5.2 Complete `chop` examples
    - Add complete syntax examples
    - Add `.` operator usage example
    - _Requirements: 7.1, 7.3_

  - [ ] 5.3 Complete `set` examples
    - Ensure examples are distinct from slap
    - Add flag combinations
    - _Requirements: 7.1, 7.2_

  - [ ] 5.4 Complete `forget` examples
    - Add complete syntax examples
    - Add `.` operator usage example
    - _Requirements: 7.1, 7.3_

  - [ ] 5.5 Add `offer` examples section
    - Create new section for offer command
    - Show offer creation syntax
    - _Requirements: 7.1_

  - [ ] 5.6 Add `reject` examples section
    - Create new section for reject command
    - Show reject and complete-delete syntax
    - _Requirements: 7.1_

  - [ ] 5.7 Complete `list` examples
    - Add examples for all subsection flags (-app, -cmd, -ext, -def, -off, -all)
    - _Requirements: 7.4_

  - [ ] 5.8 Standardize step notation
    - Use consistent sid notation (S1, S2) for step references
    - _Requirements: 7.5_

  - [ ] 5.9 Add code block language identifiers
    - Ensure all code blocks have `sh` language tag
    - _Requirements: 1.4_

- [ ] 6. Checkpoint - Verify examples.md completeness
  - Verify all 7 commands have examples
  - Verify no underscore-joined commands in examples
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 7. Update README.md for professional presentation
  - [ ] 7.1 Populate framework links
    - Replace XXXXXXX placeholders with actual URLs
    - Python: https://www.python.org/
    - Typer: https://typer.tiangolo.com/
    - Rich: https://rich.readthedocs.io/
    - UV: https://docs.astral.sh/uv/
    - _Requirements: 5.4, 8.1_

  - [ ] 7.2 Verify installation structure
    - Ensure Quick Install, Step One, Step Two, Step Three sections exist
    - _Requirements: 8.2_

  - [ ] 7.3 Verify troubleshooting section
    - Ensure troubleshooting section is complete
    - _Requirements: 8.3_

  - [ ] 7.4 Add documentation references
    - Add links to overview.md, examples.md, tables.md
    - Create "Documentation" section
    - _Requirements: 8.4_

  - [ ] 7.5 Add code block language identifiers
    - Ensure all code blocks have `sh` language tag
    - _Requirements: 1.4_

- [ ] 8. Final Checkpoint - Cross-reference validation
  - Verify all commands in examples.md exist in overview.md
  - Verify all file types in overview.md exist in tables.md
  - Verify all sid values are defined in tables.md
  - Verify no placeholder links remain
  - Verify identical definitions across documents
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 9. Create validation script
  - [ ] 9.1 Implement heading hierarchy validator
    - Parse markdown and validate H1 → H2 → H3 structure
    - **Property 1: Heading hierarchy validation**
    - **Validates: Requirements 1.1, 1.2**

  - [ ] 9.2 Implement table syntax validator
    - Validate table headers and separators
    - **Property 2: Table syntax validation**
    - **Validates: Requirements 1.3**

  - [ ] 9.3 Implement code block validator
    - Check for language identifiers
    - **Property 3: Code block language identifiers**
    - **Validates: Requirements 1.4**

  - [ ] 9.4 Implement entry completeness validator
    - Verify all required fields present
    - **Property 4: Entry field completeness**
    - **Validates: Requirements 2.1, 2.2, 2.3**

  - [ ] 9.5 Implement sid naming validator
    - Verify naming convention compliance
    - **Property 5: SID naming convention compliance**
    - **Validates: Requirements 2.4, 2.5**

  - [ ] 9.6 Implement cross-reference validator
    - Verify all references resolve
    - **Property 6: Cross-reference consistency**
    - **Validates: Requirements 5.1, 5.2, 5.3, 5.5**

  - [ ] 9.7 Implement flag prefix validator
    - Verify `-` and `--` conventions
    - **Property 7: Flag prefix convention**
    - **Validates: Requirements 4.5**

  - [ ] 9.8 Implement example coverage validator
    - Verify all commands have examples
    - **Property 8: Example completeness per command**
    - **Validates: Requirements 3.1, 3.2, 7.1, 7.2**

  - [ ] 9.9 Implement rule format validator
    - Verify rid format and bracket notation
    - **Property 9: Rule reference format consistency**
    - **Validates: Requirements 9.2, 9.4**

  - [ ] 9.10 Implement modular syntax validator
    - Verify no underscore-joined commands
    - **Property 10: Modular command syntax**
    - **Validates: Requirements 10.2, 10.3**

## Notes
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- tables.md must be completed first as it is the Single Source of Truth
- All other documents reference tables.md for canonical definitions
