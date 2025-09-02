# Test Infrastructure Investigation

This directory contains test runner scripts that were recently added to automate test execution.

## Contents

### `run_all_tests.py`
- Python script for running all test versions sequentially
- Creates timestamped log directories
- Provides detailed logging and summary generation
- More complex but feature-rich

### `run_all_tests.sh` 
- Bash script for running all test versions sequentially
- Simpler, faster execution
- Colored output for readability
- Platform-independent (macOS/Linux)

### `TEST_RUNNER_README.md`
- Documentation explaining both test runners
- Usage instructions and feature comparisons
- Indicates this was meant to be production tooling

## Investigation Questions

1. **Are these production-ready or experimental?** - Documentation suggests production-ready
2. **Do we need both Python and Bash versions?** - Redundant functionality
3. **Should this be in the main project or separate tooling?** - Depends on usage frequency
4. **Are the generated logs valuable?** - Test runner outputs were moved to logs_investigation

## Recommendation

- **If actively used**: Move back to project root, keep both scripts for flexibility
- **If experimental**: Keep in organize_me until proven valuable  
- **If obsolete**: Delete if not being used

The comprehensive documentation suggests these were intended as production tooling, but the fact that they were creating log pollution suggests they might need refinement.
