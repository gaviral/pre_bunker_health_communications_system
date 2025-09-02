#!/bin/bash

# Test Status Checker Script
# Usage: ./check_test_status.sh

STATUS_FILE="test_status.json"
TRACKER_FILE="TEST_STATUS_TRACKER.md"

echo "🔍 Checking test status..."
echo ""

# Check if any tests are running
if [ -f "$STATUS_FILE" ] && [ -s "$STATUS_FILE" ]; then
    python3 -c "
import json
from datetime import datetime

try:
    with open('$STATUS_FILE', 'r') as f:
        data = json.load(f)
except:
    print('No test status data found.')
    exit()

if not data:
    print('No tests have been run yet.')
    exit()

print('📊 Current Test Status:')
print('=' * 50)

running_count = 0
passed_count = 0
failed_count = 0

for test_name, info in data.items():
    status = info.get('status', 'unknown')
    duration = info.get('duration', 'N/A')
    result_file = info.get('result_file', 'N/A')
    
    status_icon = {
        'running': '🔵',
        'passed': '✅', 
        'failed': '❌',
        'timeout': '⏸️',
        'queued': '🔄'
    }.get(status, '⚪')
    
    print(f'{status_icon} {test_name}: {status.upper()}')
    print(f'   Duration: {duration}')
    print(f'   Log: {result_file}')
    print()
    
    if status == 'running':
        running_count += 1
    elif status == 'passed':
        passed_count += 1
    elif status == 'failed':
        failed_count += 1

print('📈 Summary:')
print(f'   🔵 Running: {running_count}')
print(f'   ✅ Passed: {passed_count}') 
print(f'   ❌ Failed: {failed_count}')
print(f'   📝 Total: {len(data)}')

if running_count > 0:
    print()
    print('💡 Tip: Use \"tail -f <log_file>\" to watch running tests')
"
else
    echo "No tests have been started yet."
    echo ""
    echo "💡 Start a test with: ./run_async_test.sh <test_name>"
    echo "   Example: ./run_async_test.sh test_v1_1"
fi

echo ""
echo "📋 Full status tracker: $TRACKER_FILE"
