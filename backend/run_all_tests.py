#!/usr/bin/env python3
"""
Master Test Runner for AI Stock Trading Application
Executes all test suites and provides comprehensive reporting
"""

import subprocess
import sys
import time
import json
from datetime import datetime
from typing import Dict, List, Any

class MasterTestRunner:
    def __init__(self):
        self.test_suites = [
            {
                'name': 'Comprehensive API Tests',
                'script': 'test_comprehensive_api.py',
                'description': 'Tests all API endpoints and functionality'
            },
            {
                'name': 'Frontend Integration Tests',
                'script': 'test_frontend_integration.py',
                'description': 'Tests frontend-backend integration'
            },
            {
                'name': 'Stress Load Tests',
                'script': 'test_stress_load.py',
                'description': 'Tests system performance under load'
            }
        ]
        self.results = {
            'start_time': None,
            'end_time': None,
            'total_duration': 0,
            'suites': [],
            'summary': {
                'total_tests': 0,
                'passed': 0,
                'failed': 0,
                'success_rate': 0
            }
        }
    
    def run_test_suite(self, suite: Dict) -> Dict:
        """Run a single test suite"""
        print(f"\n🚀 Running {suite['name']}...")
        print(f"   Description: {suite['description']}")
        print("   " + "=" * 50)
        
        start_time = time.time()
        
        try:
            # Run the test script
            result = subprocess.run(
                [sys.executable, suite['script']],
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout per suite
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            suite_result = {
                'name': suite['name'],
                'script': suite['script'],
                'duration': duration,
                'return_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'success': result.returncode == 0
            }
            
            if result.returncode == 0:
                print(f"✅ {suite['name']} completed successfully in {duration:.2f}s")
            else:
                print(f"❌ {suite['name']} failed with return code {result.returncode}")
                if result.stderr:
                    print(f"   Error: {result.stderr[:200]}...")
            
            return suite_result
            
        except subprocess.TimeoutExpired:
            end_time = time.time()
            duration = end_time - start_time
            
            suite_result = {
                'name': suite['name'],
                'script': suite['script'],
                'duration': duration,
                'return_code': -1,
                'stdout': '',
                'stderr': 'Test suite timed out after 10 minutes',
                'success': False
            }
            
            print(f"⏰ {suite['name']} timed out after {duration:.2f}s")
            return suite_result
            
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            
            suite_result = {
                'name': suite['name'],
                'script': suite['script'],
                'duration': duration,
                'return_code': -2,
                'stdout': '',
                'stderr': str(e),
                'success': False
            }
            
            print(f"💥 {suite['name']} crashed: {str(e)}")
            return suite_result
    
    def parse_test_output(self, stdout: str) -> Dict:
        """Parse test output to extract statistics"""
        stats = {
            'passed': 0,
            'failed': 0,
            'total': 0
        }
        
        lines = stdout.split('\n')
        for line in lines:
            if '✅ Passed:' in line:
                try:
                    stats['passed'] = int(line.split(':')[1].strip())
                except:
                    pass
            elif '❌ Failed:' in line:
                try:
                    stats['failed'] = int(line.split(':')[1].strip())
                except:
                    pass
            elif 'Success Rate:' in line:
                try:
                    stats['success_rate'] = float(line.split(':')[1].strip().replace('%', ''))
                except:
                    pass
        
        stats['total'] = stats['passed'] + stats['failed']
        return stats
    
    def run_all_tests(self):
        """Run all test suites"""
        print("🧪 AI Stock Trading - Master Test Runner")
        print("=" * 60)
        print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🔧 Running {len(self.test_suites)} test suites...")
        print("=" * 60)
        
        self.results['start_time'] = datetime.now()
        
        for suite in self.test_suites:
            suite_result = self.run_test_suite(suite)
            self.results['suites'].append(suite_result)
            
            # Parse output for statistics
            if suite_result['stdout']:
                stats = self.parse_test_output(suite_result['stdout'])
                suite_result['stats'] = stats
                self.results['summary']['total_tests'] += stats['total']
                self.results['summary']['passed'] += stats['passed']
                self.results['summary']['failed'] += stats['failed']
        
        self.results['end_time'] = datetime.now()
        self.results['total_duration'] = (self.results['end_time'] - self.results['start_time']).total_seconds()
        
        # Calculate overall success rate
        if self.results['summary']['total_tests'] > 0:
            self.results['summary']['success_rate'] = (
                self.results['summary']['passed'] / self.results['summary']['total_tests'] * 100
            )
        
        self.print_summary()
        self.save_results()
        
        return self.results
    
    def print_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE TEST SUMMARY")
        print("=" * 60)
        
        print(f"⏱️  Total Duration: {self.results['total_duration']:.2f}s")
        print(f"🧪 Total Test Suites: {len(self.test_suites)}")
        print(f"📈 Total Tests: {self.results['summary']['total_tests']}")
        print(f"✅ Passed: {self.results['summary']['passed']}")
        print(f"❌ Failed: {self.results['summary']['failed']}")
        print(f"📊 Success Rate: {self.results['summary']['success_rate']:.1f}%")
        
        print(f"\n📋 Test Suite Results:")
        for suite in self.results['suites']:
            status = "✅ PASS" if suite['success'] else "❌ FAIL"
            duration = suite['duration']
            stats = suite.get('stats', {})
            
            print(f"   {status} {suite['name']} ({duration:.2f}s)")
            if stats:
                print(f"      Tests: {stats.get('total', 0)}, Passed: {stats.get('passed', 0)}, Failed: {stats.get('failed', 0)}")
        
        # Overall assessment
        if self.results['summary']['success_rate'] >= 90:
            print(f"\n🎉 EXCELLENT! System is performing very well.")
        elif self.results['summary']['success_rate'] >= 75:
            print(f"\n👍 GOOD! System is working well with minor issues.")
        elif self.results['summary']['success_rate'] >= 50:
            print(f"\n⚠️  FAIR! System has some issues that need attention.")
        else:
            print(f"\n🚨 POOR! System has significant issues that need immediate attention.")
        
        # Recommendations
        print(f"\n💡 Recommendations:")
        if self.results['summary']['success_rate'] < 100:
            print("   - Review failed tests and fix identified issues")
            print("   - Check error logs for detailed failure information")
            print("   - Consider performance optimizations if response times are high")
        
        if self.results['summary']['success_rate'] >= 90:
            print("   - System is ready for production use")
            print("   - Consider implementing monitoring and alerting")
            print("   - Regular testing is recommended to maintain quality")
    
    def save_results(self):
        """Save test results to file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"test_results_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(self.results, f, indent=2, default=str)
            print(f"\n💾 Test results saved to: {filename}")
        except Exception as e:
            print(f"\n⚠️  Failed to save results: {str(e)}")
    
    def generate_report(self):
        """Generate a detailed HTML report"""
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>AI Stock Trading - Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .summary {{ background-color: #e8f5e8; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .suite {{ border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 5px; }}
        .pass {{ background-color: #d4edda; }}
        .fail {{ background-color: #f8d7da; }}
        .stats {{ display: flex; justify-content: space-around; margin: 20px 0; }}
        .stat {{ text-align: center; padding: 10px; background-color: #f8f9fa; border-radius: 5px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🧪 AI Stock Trading - Test Report</h1>
        <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>Total Duration: {self.results['total_duration']:.2f}s</p>
    </div>
    
    <div class="summary">
        <h2>📊 Summary</h2>
        <div class="stats">
            <div class="stat">
                <h3>{self.results['summary']['total_tests']}</h3>
                <p>Total Tests</p>
            </div>
            <div class="stat">
                <h3>{self.results['summary']['passed']}</h3>
                <p>Passed</p>
            </div>
            <div class="stat">
                <h3>{self.results['summary']['failed']}</h3>
                <p>Failed</p>
            </div>
            <div class="stat">
                <h3>{self.results['summary']['success_rate']:.1f}%</h3>
                <p>Success Rate</p>
            </div>
        </div>
    </div>
    
    <h2>📋 Test Suite Details</h2>
"""
        
        for suite in self.results['suites']:
            status_class = "pass" if suite['success'] else "fail"
            status_icon = "✅" if suite['success'] else "❌"
            
            html_content += f"""
    <div class="suite {status_class}">
        <h3>{status_icon} {suite['name']}</h3>
        <p><strong>Duration:</strong> {suite['duration']:.2f}s</p>
        <p><strong>Return Code:</strong> {suite['return_code']}</p>
"""
            
            if 'stats' in suite:
                stats = suite['stats']
                html_content += f"""
        <p><strong>Tests:</strong> {stats.get('total', 0)} | 
           <strong>Passed:</strong> {stats.get('passed', 0)} | 
           <strong>Failed:</strong> {stats.get('failed', 0)}</p>
"""
            
            if suite['stderr']:
                html_content += f"""
        <p><strong>Errors:</strong></p>
        <pre>{suite['stderr']}</pre>
"""
            
            html_content += "    </div>\n"
        
        html_content += """
</body>
</html>
"""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"test_report_{timestamp}.html"
        
        try:
            with open(filename, 'w') as f:
                f.write(html_content)
            print(f"📄 HTML report generated: {filename}")
        except Exception as e:
            print(f"⚠️  Failed to generate HTML report: {str(e)}")

def main():
    """Main test runner"""
    runner = MasterTestRunner()
    results = runner.run_all_tests()
    runner.generate_report()
    
    # Exit with appropriate code
    overall_success = results['summary']['success_rate'] >= 75
    sys.exit(0 if overall_success else 1)

if __name__ == "__main__":
    main()
