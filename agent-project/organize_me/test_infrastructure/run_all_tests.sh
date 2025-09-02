#!/bin/bash

# PRE-BUNKER Health Communications System - Sequential Test Runner
# Runs all test versions chronologically and captures logs in timestamped folder

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Create timestamped log directory
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_DIR="test_logs_${TIMESTAMP}"
mkdir -p "${LOG_DIR}"

# Test files in chronological order
TEST_FILES=(
    "test_v1_1.py"
    "test_v1_2.py"
    "test_v1_3.py"
    "test_v1_4.py"
    "test_v1_5.py"
    "test_v1_7.py"
    "test_v1_9.py"
    "test_v1_11.py"
    "test_v1_15.py"
    "test_v1_16.py"
    "test_v2_0.py"
)

# Initialize counters
TOTAL_TESTS=${#TEST_FILES[@]}
PASSED_TESTS=0
FAILED_TESTS=0
START_TIME=$(date)
START_EPOCH=$(date +%s)

echo -e "${BLUE}🚀 PRE-BUNKER Health Communications System - Test Runner${NC}"
echo "============================================================"
echo "Timestamp: ${TIMESTAMP}"
echo "Log Directory: ${LOG_DIR}"
echo "Total Tests: ${TOTAL_TESTS}"
echo "============================================================"

# Create main log file
MAIN_LOG="${LOG_DIR}/test_runner.log"
echo "Test Runner Started: ${START_TIME}" > "${MAIN_LOG}"
echo "Log Directory: ${LOG_DIR}" >> "${MAIN_LOG}"
echo "Total Tests: ${TOTAL_TESTS}" >> "${MAIN_LOG}"
echo "============================================================" >> "${MAIN_LOG}"

# Function to run a single test
run_test() {
    local test_file="$1"
    local test_num="$2"
    
    echo -e "\n${BLUE}[${test_num}/${TOTAL_TESTS}] Running ${test_file}${NC}"
    echo "[${test_num}/${TOTAL_TESTS}] Running ${test_file}" >> "${MAIN_LOG}"
    
    # Check if test file exists
    if [[ ! -f "${test_file}" ]]; then
        echo -e "${YELLOW}⚠️  Test file ${test_file} not found, skipping${NC}"
        echo "WARNING: Test file ${test_file} not found, skipping" >> "${MAIN_LOG}"
        return 1
    fi
    
    # Create individual log file
    local test_log="${LOG_DIR}/${test_file%.py}.log"
    
    # Run the test and capture output
    echo "=== TEST RUN: ${test_file} ===" > "${test_log}"
    echo "Timestamp: $(date -Iseconds)" >> "${test_log}"
    echo "Command: python3 ${test_file}" >> "${test_log}"
    echo "" >> "${test_log}"
    
    # Run test (without timeout for macOS compatibility)
    if python3 "${test_file}" >> "${test_log}" 2>&1; then
        local return_code=$?
        echo "Return Code: ${return_code}" >> "${test_log}"
        echo -e "${GREEN}✅ ${test_file} completed successfully${NC}"
        echo "SUCCESS: ${test_file} completed successfully" >> "${MAIN_LOG}"
        ((PASSED_TESTS++))
        return 0
    else
        local return_code=$?
        echo "Return Code: ${return_code}" >> "${test_log}"
        echo -e "${YELLOW}⚠️  ${test_file} completed with return code ${return_code}${NC}"
        echo "FAILED: ${test_file} completed with return code ${return_code}" >> "${MAIN_LOG}"
        ((FAILED_TESTS++))
        return 1
    fi
}

# Run all tests sequentially
echo -e "\n${BLUE}STARTING SEQUENTIAL TEST EXECUTION${NC}"
echo "" >> "${MAIN_LOG}"
echo "STARTING SEQUENTIAL TEST EXECUTION" >> "${MAIN_LOG}"

for i in "${!TEST_FILES[@]}"; do
    test_num=$((i + 1))
    run_test "${TEST_FILES[$i]}" "${test_num}"
done

# Calculate execution time
END_TIME=$(date)
END_EPOCH=$(date +%s)
DURATION=$((END_EPOCH - START_EPOCH))
DURATION_FORMATTED=$(printf '%02d:%02d:%02d' $((DURATION/3600)) $((DURATION%3600/60)) $((DURATION%60)))

# Calculate success rate
if [[ $TOTAL_TESTS -gt 0 ]]; then
    SUCCESS_RATE=$(( (PASSED_TESTS * 100) / TOTAL_TESTS ))
else
    SUCCESS_RATE=0
fi

# Generate summary
echo -e "\n============================================================"
echo -e "${BLUE}TEST EXECUTION SUMMARY${NC}"
echo "============================================================"
echo "Total Tests: ${TOTAL_TESTS}"
echo -e "Successful: ${GREEN}${PASSED_TESTS}${NC}"
echo -e "Failed: ${RED}${FAILED_TESTS}${NC}"
echo "Success Rate: ${SUCCESS_RATE}%"
echo "Start Time: ${START_TIME}"
echo "End Time: ${END_TIME}"
echo "Duration: ${DURATION_FORMATTED}"
echo "============================================================"

# Write summary to log
echo "" >> "${MAIN_LOG}"
echo "============================================================" >> "${MAIN_LOG}"
echo "TEST EXECUTION SUMMARY" >> "${MAIN_LOG}"
echo "============================================================" >> "${MAIN_LOG}"
echo "Total Tests: ${TOTAL_TESTS}" >> "${MAIN_LOG}"
echo "Successful: ${PASSED_TESTS}" >> "${MAIN_LOG}"
echo "Failed: ${FAILED_TESTS}" >> "${MAIN_LOG}"
echo "Success Rate: ${SUCCESS_RATE}%" >> "${MAIN_LOG}"
echo "Start Time: ${START_TIME}" >> "${MAIN_LOG}"
echo "End Time: ${END_TIME}" >> "${MAIN_LOG}"
echo "Duration: ${DURATION_FORMATTED}" >> "${MAIN_LOG}"
echo "============================================================" >> "${MAIN_LOG}"

# Generate markdown summary
SUMMARY_FILE="${LOG_DIR}/test_summary.md"
cat > "${SUMMARY_FILE}" << EOF
# PRE-BUNKER Test Suite Execution Summary

**Execution Timestamp:** ${TIMESTAMP}  
**Start Time:** ${START_TIME}  
**End Time:** ${END_TIME}  
**Duration:** ${DURATION_FORMATTED}  

## Summary Statistics

- **Total Tests:** ${TOTAL_TESTS}
- **Successful:** ${PASSED_TESTS}
- **Failed:** ${FAILED_TESTS}
- **Success Rate:** ${SUCCESS_RATE}%

## Test Results

| Test File | Status | Log File |
|-----------|--------|----------|
EOF

# Add test results to markdown
for test_file in "${TEST_FILES[@]}"; do
    test_log="${test_file%.py}.log"
    if [[ -f "${LOG_DIR}/${test_log}" ]]; then
        # Check if test passed by looking for SUCCESS in main log
        if grep -q "SUCCESS: ${test_file}" "${MAIN_LOG}"; then
            echo "| ${test_file} | ✅ PASS | ${test_log} |" >> "${SUMMARY_FILE}"
        else
            echo "| ${test_file} | ❌ FAIL | ${test_log} |" >> "${SUMMARY_FILE}"
        fi
    else
        echo "| ${test_file} | ⚠️ SKIP | N/A |" >> "${SUMMARY_FILE}"
    fi
done

# Add log directory structure to markdown
cat >> "${SUMMARY_FILE}" << EOF

## Log Directory Structure

All logs are stored in: \`$(pwd)/${LOG_DIR}\`

\`\`\`
${LOG_DIR}/
├── test_runner.log       # Main runner log
├── test_summary.md       # This summary file
EOF

# List all log files
for test_file in "${TEST_FILES[@]}"; do
    test_log="${test_file%.py}.log"
    if [[ -f "${LOG_DIR}/${test_log}" ]]; then
        echo "├── ${test_log}" >> "${SUMMARY_FILE}"
    fi
done

echo '```' >> "${SUMMARY_FILE}"

# Final output
echo -e "\n${GREEN}🎯 EXECUTION COMPLETE: ${PASSED_TESTS}/${TOTAL_TESTS} tests passed${NC}"
echo -e "${BLUE}📁 Logs stored in: $(pwd)/${LOG_DIR}${NC}"
echo -e "${BLUE}📊 Summary report: ${LOG_DIR}/test_summary.md${NC}"

# Exit with appropriate code
if [[ $FAILED_TESTS -gt 0 ]]; then
    echo -e "${RED}❌ Some tests failed${NC}"
    exit 1
else
    echo -e "${GREEN}✅ All tests passed${NC}"
    exit 0
fi
