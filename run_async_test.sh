#!/bin/bash

# Asynchronous Test Runner Script
# Usage: ./run_async_test.sh <test_name>
# Example: ./run_async_test.sh test_v1_1

set -e

# Configuration
TEST_NAME="$1"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_DIR="async_test_logs"
RESULT_FILE="${LOG_DIR}/${TEST_NAME}_${TIMESTAMP}.log"
STATUS_FILE="test_status.json"
TRACKER_FILE="TEST_STATUS_TRACKER.md"

# Validate input
if [ -z "$TEST_NAME" ]; then
    echo "Error: Test name required"
    echo "Usage: $0 <test_name>"
    echo "Example: $0 test_v1_1"
    exit 1
fi

# Create directories
mkdir -p "$LOG_DIR"

# Initialize status file if it doesn't exist
if [ ! -f "$STATUS_FILE" ]; then
    echo '{}' > "$STATUS_FILE"
fi

# Function to update status
update_status() {
    local status="$1"
    local duration="$2"
    
    python3 -c "
import json
import sys
from datetime import datetime

# Read current status
try:
    with open('$STATUS_FILE', 'r') as f:
        data = json.load(f)
except:
    data = {}

# Update test status
data['$TEST_NAME'] = {
    'status': '$status',
    'started': '$(date -Iseconds)',
    'duration': '$duration',
    'result_file': '$RESULT_FILE',
    'timestamp': '$TIMESTAMP'
}

# Write back
with open('$STATUS_FILE', 'w') as f:
    json.dump(data, f, indent=2)
"
}

# Function to update tracker markdown
update_tracker() {
    python3 -c "
import json
from datetime import datetime

# Read status
try:
    with open('$STATUS_FILE', 'r') as f:
        data = json.load(f)
except:
    data = {}

# Generate table rows
rows = []
for test_name, info in data.items():
    status_icon = {
        'running': '🔵',
        'passed': '✅', 
        'failed': '❌',
        'timeout': '⏸️',
        'queued': '🔄'
    }.get(info['status'], '⚪')
    
    rows.append(f\"| {test_name} | {test_name.replace('_', ' ').title()} | {status_icon} {info['status'].title()} | {info.get('started', 'N/A')} | {info.get('duration', 'N/A')} | {info.get('result_file', 'N/A')} | - |\")

if not rows:
    rows = ['| - | - | ⚪ Ready | - | - | - | No tests currently running |']

# Read current tracker
with open('$TRACKER_FILE', 'r') as f:
    content = f.read()

# Update table
lines = content.split('\n')
new_lines = []
in_table = False
for line in lines:
    if line.startswith('| Test ID'):
        new_lines.append(line)
        in_table = True
    elif line.startswith('|------'):
        new_lines.append(line)
    elif in_table and line.startswith('|'):
        continue  # Skip old table rows
    elif in_table and not line.startswith('|'):
        # End of table, add new rows
        new_lines.extend(rows)
        new_lines.append(line)
        in_table = False
    else:
        new_lines.append(line)

# Update timestamp
for i, line in enumerate(new_lines):
    if line.startswith('**Last Updated**'):
        new_lines[i] = f'**Last Updated**: {datetime.now().strftime(\"%Y-%m-%d %H:%M:%S\")}'

# Write back
with open('$TRACKER_FILE', 'w') as f:
    f.write('\n'.join(new_lines))
"
}

echo "🚀 Starting asynchronous test: $TEST_NAME"
echo "📁 Log file: $RESULT_FILE"

# Update status to running
update_status "running" ""
update_tracker

# Run test in background and capture everything
{
    START_TIME=$(date +%s)
    echo "=== ASYNC TEST EXECUTION LOG ===" > "$RESULT_FILE"
    echo "Test: $TEST_NAME" >> "$RESULT_FILE"
    echo "Started: $(date -Iseconds)" >> "$RESULT_FILE"
    echo "Log File: $RESULT_FILE" >> "$RESULT_FILE"
    echo "======================================" >> "$RESULT_FILE"
    echo "" >> "$RESULT_FILE"
    
    cd agent-project
    
    # Try to run the test with proper Python path and uv environment
    if PYTHONPATH=. uv run python "tests/${TEST_NAME}.py" >> "../$RESULT_FILE" 2>&1; then
        END_TIME=$(date +%s)
        DURATION=$((END_TIME - START_TIME))
        echo "" >> "../$RESULT_FILE"
        echo "======================================" >> "../$RESULT_FILE"
        echo "✅ TEST PASSED" >> "../$RESULT_FILE"
        echo "Duration: ${DURATION}s" >> "../$RESULT_FILE"
        echo "Completed: $(date -Iseconds)" >> "../$RESULT_FILE"
        
        cd ..
        update_status "passed" "${DURATION}s"
        echo "✅ Test $TEST_NAME completed successfully in ${DURATION}s"
    else
        END_TIME=$(date +%s)
        DURATION=$((END_TIME - START_TIME))
        echo "" >> "../$RESULT_FILE"
        echo "======================================" >> "../$RESULT_FILE"
        echo "❌ TEST FAILED" >> "../$RESULT_FILE"
        echo "Duration: ${DURATION}s" >> "../$RESULT_FILE"
        echo "Completed: $(date -Iseconds)" >> "../$RESULT_FILE"
        
        cd ..
        update_status "failed" "${DURATION}s"
        echo "❌ Test $TEST_NAME failed after ${DURATION}s"
    fi
    
    update_tracker
    
} &

# Get the background process ID
BG_PID=$!
echo "🔵 Test running in background (PID: $BG_PID)"
echo "📊 Track progress: cat $TRACKER_FILE"
echo "📝 View logs: tail -f $RESULT_FILE"

# Save PID for potential cleanup
echo "$BG_PID" > "${LOG_DIR}/${TEST_NAME}_${TIMESTAMP}.pid"

echo ""
echo "✨ Test started asynchronously!"
echo "   Status tracker: $TRACKER_FILE"
echo "   Result file: $RESULT_FILE"
echo "   Check status anytime with: ./check_test_status.sh"
