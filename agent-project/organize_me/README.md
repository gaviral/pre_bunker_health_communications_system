# organize_me - Staging Area for Project Cleanup

This directory contains items that were moved out of the project root during reorganization. Each item needs investigation to determine its proper place or whether it should be kept.

## Directory Structure

### 📊 `logs_investigation/`
Contains multiple log directories that had overlapping purposes:

- **`current_logs/`** - Contains "detailed logs" from v1.1-v2.0 (26 files)
- **`legacy_logs/`** - Contains older "detailed logs" (12 files) 
- **`test_runner_outputs/`** - Timestamped test runner outputs (4 directories from Aug 26, 2025)

**Investigation needed:** Determine which logs are authoritative and consolidate or archive appropriately.

### 🧪 `test_infrastructure/`
Contains test runner scripts and documentation:

- `run_all_tests.py` - Python test runner
- `run_all_tests.sh` - Bash test runner  
- `TEST_RUNNER_README.md` - Documentation

**Investigation needed:** Determine if this is experimental tooling or production-ready infrastructure.

### 📋 `analysis_documents/`
Contains large analysis documents:

- `comprehensive_issues_analysis.md` - 512-line exhaustive analysis of all test issues

**Investigation needed:** Determine if this should be in `docs/` or is reference material.

## Resolution Process

For each item in `organize_me/`:

1. **Investigate** - Determine purpose and current relevance
2. **Decide** - Keep, move to proper location, or delete
3. **Act** - Move back to project or remove
4. **Document** - Update this README as items are resolved

## Goal

Clean up the `organize_me/` directory gradually until the main project structure is minimal, clear, and well-organized.
