import subprocess
import sys
import argparse
import time
from datetime import datetime

class OdooLoadTestRunner:
    """Automated test runner for different scenarios"""

    scenarios = {
        "light": {
            "users": 10,
            "spawn_rate": 2,
            "duration": "5m",
            "description": "Light load - 10 users, basic operations"
        },
        "medium": {
            "users": 50,
            "spawn_rate": 5,
            "duration": "15m",
            "description": "Medium load - 50 users, mixed operations"
        },
        "heavy": {
            "users": 100,
            "spawn_rate": 10,
            "duration": "30m",
            "description": "Heavy load - 100 users, intensive operations"
        },
        "stress": {
            "users": 200,
            "spawn_rate": 20,
            "duration": "10m",
            "description": "Stress test - 200 users, find breaking point"
        }
    }

    def run_scenario(self, scenario_name, host, headless=False):
        """Run a specific test scenario"""
        if scenario_name not in self.scenarios:
            print(f"Unknown scenario: {scenario_name}")
            print(f"Available scenarios: {list(self.scenarios.keys())}")
            return

        scenario = self.scenarios[scenario_name]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        cmd = [
            "locust",
            "-f", "odoo_load_test.py",
            "--host", host,
            "-u", str(scenario["users"]),
            "-r", str(scenario["spawn_rate"]),
            "-t", scenario["duration"],
            "--csv", f"results_{scenario_name}_{timestamp}",
            "--csv-full-history",
            "--logfile", f"locust_{scenario_name}_{timestamp}.log"
        ]

        if headless:
            cmd.append("--headless")

        print(f"\nRunning scenario: {scenario['description']}")
        print(f"Command: {' '.join(cmd)}")

        try:
            subprocess.run(cmd, check=True)
            print(f"\nScenario '{scenario_name}' completed successfully!")
            print(f"Results saved with timestamp: {timestamp}")
        except subprocess.CalledProcessError as e:
            print(f"Test failed with error: {e}")

    def run_all_scenarios(self, host):
        """Run all scenarios sequentially"""
        for scenario_name in self.scenarios:
            print(f"\n{'='*60}")
            print(f"Starting scenario: {scenario_name}")
            print(f"{'='*60}")

            self.run_scenario(scenario_name, host, headless=True)

            print("\nWaiting 60 seconds before next scenario...")
            time.sleep(60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Odoo Load Test Runner")
    parser.add_argument("--host", required=True, help="Odoo host URL")
    parser.add_argument("--scenario", choices=list(OdooLoadTestRunner.scenarios.keys()) + ["all"],
                        default="medium", help="Test scenario to run")
    parser.add_argument("--headless", action="store_true", help="Run without web UI")

    args = parser.parse_args()

    runner = OdooLoadTestRunner()

    if args.scenario == "all":
        runner.run_all_scenarios(args.host)
    else:
        runner.run_scenario(args.scenario, args.host, args.headless)
