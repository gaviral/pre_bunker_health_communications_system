# PRE-BUNKER Test Runner Scripts

This directory contains two test runner scripts that execute all test versions sequentially and store logs in timestamped folders.

## Scripts Available

### 1. Bash Script (Recommended) - `run_all_tests.sh`

**Simple, fast, and portable bash script**

```bash
# Make executable (first time only)
chmod +x run_all_tests.sh

# Run all tests
./run_all_tests.sh
```

**Features:**
- ✅ Fast execution
- ✅ Colored output for easy reading
- ✅ Works on macOS/Linux without dependencies
- ✅ Creates timestamped log folders automatically
- ✅ Generates both text logs and markdown summary
- ✅ Sequential execution of all test versions

### 2. Python Script - `run_all_tests.py`

**More detailed logging with Python**

```bash
# Run all tests
python3 run_all_tests.py
```

**Features:**
- ✅ Comprehensive logging and monitoring
- ✅ Detailed error handling and timeouts
- ✅ Rich markdown report generation
- ✅ Performance metrics tracking

## Test Execution Order

Both scripts run tests in chronological order:

1. `test_v1_1.py` - Health Domain Setup
2. `test_v1_2.py` - Claim Extraction
3. `test_v1_3.py` - Risk Scoring
4. `test_v1_4.py` - Persona Interpretation
5. `test_v1_5.py` - Evidence Validation
6. `test_v1_7.py` - Evidence Validator
7. `test_v1_9.py` - Pipeline Processing
8. `test_v1_11.py` - API Testing
9. `test_v1_15.py` - Persona Coverage
10. `test_v1_16.py` - AB Testing
11. `test_v2_0.py` - Complete Integration

## Output Structure

Each execution creates a timestamped folder:

```
test_logs_YYYYMMDD_HHMMSS/
├── test_runner.log       # Main execution log
├── test_summary.md       # Markdown summary report
├── test_v1_1.log        # Individual test logs
├── test_v1_2.log
├── test_v1_3.log
└── ... (one log per test)
```

## Log Contents

### Individual Test Logs
Each test log contains:
- Execution timestamp
- Command used
- Full stdout (test output)
- Full stderr (logging output with diagnostic details)
- Return code

### Main Runner Log
- Overall execution timeline
- Success/failure status for each test
- Summary statistics

### Markdown Summary
- Test execution overview
- Pass/fail statistics
- Links to individual log files
- Directory structure

## Example Usage

```bash
# Run tests and view results
./run_all_tests.sh

# Check latest results
ls -la test_logs_*/

# View summary
cat test_logs_*/test_summary.md

# Check specific test output
cat test_logs_*/test_v1_1.log
```

## Interpreting Results

### Exit Codes
- `0` = All tests passed
- `1` = Some tests failed
- `2` = Execution interrupted
- `3` = Script error

### Test Status
- ✅ **PASS** = Test completed successfully (return code 0)
- ❌ **FAIL** = Test failed or had errors (return code ≠ 0)
- ⚠️ **SKIP** = Test file not found

### Understanding Test Failures

Most tests are expected to have non-zero return codes because they contain:
- Simulated timeout errors
- Memory usage monitoring
- Resource constraint testing
- Integration failure simulation

The logging improvements we implemented are designed to capture diagnostic information about these simulated issues, which is why the tests may "fail" but still provide valuable logging output.

## Comprehensive Logging Features

Each test now includes enhanced monitoring:

- **v1.1**: Scope analysis, validation gaps, performance baseline
- **v1.2**: LLM utilization tracking, integration completeness
- **v1.3**: Confidence calibration, scoring inconsistency detection
- **v1.4**: Timeout patterns, concurrency tracking, resource monitoring
- **v1.5**: Failure pattern analysis, memory tracking, connection lifecycle
- **v1.7**: Validation failure detection, performance breakdown, caching analysis
- **v1.9**: Pipeline breakdown, memory growth tracking, error handling
- **v1.11**: API performance monitoring, timeout configuration
- **v1.15**: Coverage analysis, quality impact measurement
- **v1.16**: Regression analysis, timeout distribution tracking
- **v2.0**: Integration failure tracking, API contract validation

Check the `stderr` section of each test log to see the detailed diagnostic logging output.
