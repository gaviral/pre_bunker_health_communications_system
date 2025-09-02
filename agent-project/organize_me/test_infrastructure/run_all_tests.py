#!/usr/bin/env python3
"""
Sequential Test Runner for PRE-BUNKER Health Communications System
Runs all test versions chronologically and captures logs in timestamped folder
"""

import os
import sys
import subprocess
import datetime
import logging
from pathlib import Path


class TestRunner:
    def __init__(self):
        self.timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_dir = Path(f"test_logs_{self.timestamp}")
        self.log_dir.mkdir(exist_ok=True)
        
        # Configure main runner logging
        self.setup_runner_logging()
        
        # Test files in chronological order
        self.test_files = [
            "test_v1_1.py",
            "test_v1_2.py", 
            "test_v1_3.py",
            "test_v1_4.py",
            "test_v1_5.py",
            "test_v1_7.py",
            "test_v1_9.py",
            "test_v1_11.py",
            "test_v1_15.py",
            "test_v1_16.py",
            "test_v2_0.py"
        ]
    
    def setup_runner_logging(self):
        """Setup logging for the test runner itself"""
        log_file = self.log_dir / "test_runner.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        self.logger.info(f"Test Runner initialized - Timestamp: {self.timestamp}")
        self.logger.info(f"Log directory: {self.log_dir.absolute()}")
    
    def run_single_test(self, test_file):
        """Run a single test file and capture its output"""
        self.logger.info(f"Starting test: {test_file}")
        
        # Create individual log file for this test
        test_log_file = self.log_dir / f"{test_file.replace('.py', '')}.log"
        
        try:
            # Run the test and capture output
            result = subprocess.run(
                [sys.executable, test_file],
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout per test
                cwd=os.getcwd()
            )
            
            # Write captured output to log file
            with open(test_log_file, 'w') as f:
                f.write(f"=== TEST RUN: {test_file} ===\n")
                f.write(f"Timestamp: {datetime.datetime.now().isoformat()}\n")
                f.write(f"Return Code: {result.returncode}\n")
                f.write("\n=== STDOUT ===\n")
                f.write(result.stdout)
                f.write("\n=== STDERR ===\n")
                f.write(result.stderr)
                f.write("\n=== END ===\n")
            
            # Log results
            if result.returncode == 0:
                self.logger.info(f"✅ {test_file} completed successfully")
            else:
                self.logger.warning(f"⚠️  {test_file} completed with return code {result.returncode}")
            
            return {
                'test_file': test_file,
                'return_code': result.returncode,
                'success': result.returncode == 0,
                'log_file': test_log_file,
                'stdout_lines': len(result.stdout.splitlines()),
                'stderr_lines': len(result.stderr.splitlines())
            }
            
        except subprocess.TimeoutExpired:
            self.logger.error(f"❌ {test_file} timed out after 5 minutes")
            with open(test_log_file, 'w') as f:
                f.write(f"=== TEST RUN: {test_file} ===\n")
                f.write(f"Timestamp: {datetime.datetime.now().isoformat()}\n")
                f.write("Status: TIMEOUT (5 minutes)\n")
            
            return {
                'test_file': test_file,
                'return_code': -1,
                'success': False,
                'log_file': test_log_file,
                'error': 'timeout'
            }
            
        except Exception as e:
            self.logger.error(f"❌ {test_file} failed with exception: {e}")
            with open(test_log_file, 'w') as f:
                f.write(f"=== TEST RUN: {test_file} ===\n")
                f.write(f"Timestamp: {datetime.datetime.now().isoformat()}\n")
                f.write(f"Exception: {str(e)}\n")
            
            return {
                'test_file': test_file,
                'return_code': -2,
                'success': False,
                'log_file': test_log_file,
                'error': str(e)
            }
    
    def run_all_tests(self):
        """Run all tests sequentially and generate summary"""
        self.logger.info("=" * 60)
        self.logger.info("STARTING SEQUENTIAL TEST EXECUTION")
        self.logger.info(f"Total tests to run: {len(self.test_files)}")
        self.logger.info("=" * 60)
        
        results = []
        start_time = datetime.datetime.now()
        
        for i, test_file in enumerate(self.test_files, 1):
            self.logger.info(f"[{i}/{len(self.test_files)}] Running {test_file}")
            
            # Check if test file exists
            if not Path(test_file).exists():
                self.logger.warning(f"⚠️  Test file {test_file} not found, skipping")
                results.append({
                    'test_file': test_file,
                    'return_code': -3,
                    'success': False,
                    'error': 'file_not_found'
                })
                continue
            
            result = self.run_single_test(test_file)
            results.append(result)
        
        end_time = datetime.datetime.now()
        total_duration = end_time - start_time
        
        # Generate summary
        self.generate_summary(results, start_time, end_time, total_duration)
        
        return results
    
    def generate_summary(self, results, start_time, end_time, total_duration):
        """Generate comprehensive test summary"""
        summary_file = self.log_dir / "test_summary.md"
        
        successful_tests = [r for r in results if r['success']]
        failed_tests = [r for r in results if not r['success']]
        
        self.logger.info("=" * 60)
        self.logger.info("TEST EXECUTION SUMMARY")
        self.logger.info("=" * 60)
        self.logger.info(f"Total tests: {len(results)}")
        self.logger.info(f"Successful: {len(successful_tests)}")
        self.logger.info(f"Failed: {len(failed_tests)}")
        self.logger.info(f"Success rate: {len(successful_tests)/len(results)*100:.1f}%")
        self.logger.info(f"Total duration: {total_duration}")
        self.logger.info(f"Summary saved to: {summary_file}")
        
        # Write detailed summary to markdown file
        with open(summary_file, 'w') as f:
            f.write(f"# PRE-BUNKER Test Suite Execution Summary\n\n")
            f.write(f"**Execution Timestamp:** {self.timestamp}\n")
            f.write(f"**Start Time:** {start_time.isoformat()}\n")
            f.write(f"**End Time:** {end_time.isoformat()}\n")
            f.write(f"**Total Duration:** {total_duration}\n\n")
            
            f.write(f"## Summary Statistics\n\n")
            f.write(f"- **Total Tests:** {len(results)}\n")
            f.write(f"- **Successful:** {len(successful_tests)}\n")
            f.write(f"- **Failed:** {len(failed_tests)}\n")
            f.write(f"- **Success Rate:** {len(successful_tests)/len(results)*100:.1f}%\n\n")
            
            f.write(f"## Test Results\n\n")
            f.write(f"| Test File | Status | Return Code | Log File | Notes |\n")
            f.write(f"|-----------|--------|-------------|----------|-------|\n")
            
            for result in results:
                status = "✅ PASS" if result['success'] else "❌ FAIL"
                log_file = result.get('log_file', 'N/A')
                log_name = log_file.name if log_file != 'N/A' else 'N/A'
                error = result.get('error', '')
                
                f.write(f"| {result['test_file']} | {status} | {result['return_code']} | {log_name} | {error} |\n")
            
            if failed_tests:
                f.write(f"\n## Failed Tests Details\n\n")
                for result in failed_tests:
                    f.write(f"### {result['test_file']}\n")
                    f.write(f"- **Return Code:** {result['return_code']}\n")
                    if 'error' in result:
                        f.write(f"- **Error:** {result['error']}\n")
                    f.write(f"- **Log File:** {result.get('log_file', 'N/A')}\n\n")
            
            f.write(f"\n## Log Directory Structure\n\n")
            f.write(f"All logs are stored in: `{self.log_dir.absolute()}`\n\n")
            f.write(f"```\n")
            f.write(f"{self.log_dir.name}/\n")
            f.write(f"├── test_runner.log       # Main runner log\n")
            f.write(f"├── test_summary.md       # This summary file\n")
            for result in results:
                if 'log_file' in result and result['log_file'] != 'N/A':
                    f.write(f"├── {result['log_file'].name}\n")
            f.write(f"```\n")


def main():
    """Main execution function"""
    print("🚀 PRE-BUNKER Health Communications System - Test Runner")
    print("=" * 60)
    
    runner = TestRunner()
    
    try:
        results = runner.run_all_tests()
        
        successful = sum(1 for r in results if r['success'])
        total = len(results)
        
        print("\n" + "=" * 60)
        print(f"🎯 EXECUTION COMPLETE: {successful}/{total} tests passed")
        print(f"📁 Logs stored in: {runner.log_dir.absolute()}")
        print("=" * 60)
        
        # Exit with non-zero code if any tests failed
        if successful < total:
            sys.exit(1)
        else:
            sys.exit(0)
            
    except KeyboardInterrupt:
        print("\n❌ Test execution interrupted by user")
        sys.exit(2)
    except Exception as e:
        print(f"\n❌ Test execution failed with error: {e}")
        sys.exit(3)


if __name__ == "__main__":
    main()
