

# ============================================================================
# analysis.py - Analyze load test results
# ============================================================================

import pandas as pd
import matplotlib.pyplot as plt
import glob
import argparse
from datetime import datetime

class LoadTestAnalyzer:
    """Analyze and visualize load test results"""

    def __init__(self, csv_prefix):
        self.csv_prefix = csv_prefix
        self.stats_df = None
        self.failures_df = None
        self.history_df = None

    def load_data(self):
        """Load CSV results from Locust"""
        try:
            # Load stats data
            stats_files = glob.glob(f"{self.csv_prefix}_stats.csv")
            if stats_files:
                self.stats_df = pd.read_csv(stats_files[0])
                print(f"Loaded stats data: {len(self.stats_df)} rows")

            # Load failures data
            failures_files = glob.glob(f"{self.csv_prefix}_failures.csv")
            if failures_files:
                self.failures_df = pd.read_csv(failures_files[0])
                print(f"Loaded failures data: {len(self.failures_df)} rows")

            # Load history data
            history_files = glob.glob(f"{self.csv_prefix}_stats_history.csv")
            if history_files:
                self.history_df = pd.read_csv(history_files[0])
                self.history_df['Timestamp'] = pd.to_datetime(self.history_df['Timestamp'])
                print(f"Loaded history data: {len(self.history_df)} rows")

        except Exception as e:
            print(f"Error loading data: {e}")

    def generate_summary_report(self):
        """Generate summary report"""
        if self.stats_df is None:
            print("No stats data available")
            return

        print("\n" + "="*60)
        print("LOAD TEST SUMMARY REPORT")
        print("="*60)

        # Overall statistics
        total_requests = self.stats_df['Request Count'].sum()
        total_failures = self.stats_df['Failure Count'].sum()
        failure_rate = (total_failures / total_requests * 100) if total_requests > 0 else 0

        print(f"Total Requests: {total_requests:,}")
        print(f"Total Failures: {total_failures:,}")
        print(f"Failure Rate: {failure_rate:.2f}%")

        # Response time statistics
        avg_response_time = self.stats_df['Average Response Time'].mean()
        max_response_time = self.stats_df['Max Response Time'].max()
        p50_response_time = self.stats_df['50%'].mean()
        p95_response_time = self.stats_df['95%'].mean()

        print(f"\nResponse Time Statistics:")
        print(f"Average: {avg_response_time:.2f}ms")
        print(f"50th Percentile: {p50_response_time:.2f}ms")
        print(f"95th Percentile: {p95_response_time:.2f}ms")
        print(f"Maximum: {max_response_time:.2f}ms")

        # Top slow endpoints
        print(f"\nSlowest Endpoints:")
        slow_endpoints = self.stats_df.nlargest(5, 'Average Response Time')[['Name', 'Average Response Time']]
        for _, row in slow_endpoints.iterrows():
            print(f"  {row['Name']}: {row['Average Response Time']:.2f}ms")

        # Failure analysis
        if self.failures_df is not None and not self.failures_df.empty:
            print(f"\nTop Failure Types:")
            failure_counts = self.failures_df.groupby('Error')['Occurrences'].sum().nlargest(5)
            for error, count in failure_counts.items():
                print(f"  {error}: {count} occurrences")

    def create_visualizations(self):
        """Create performance visualizations"""
        if self.history_df is None:
            print("No timeline data available for visualizations")
            return

        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Load Test Performance Analysis', fontsize=16)

        # Response time over time
        axes[0, 0].plot(self.history_df['Timestamp'], self.history_df['Average Response Time'])
        axes[0, 0].set_title('Average Response Time Over Time')
        axes[0, 0].set_ylabel('Response Time (ms)')
        axes[0, 0].tick_params(axis='x', rotation=45)

        # Requests per second over time
        axes[0, 1].plot(self.history_df['Timestamp'], self.history_df['Requests/s'])
        axes[0, 1].set_title('Requests per Second Over Time')
        axes[0, 1].set_ylabel('Requests/s')
        axes[0, 1].tick_params(axis='x', rotation=45)

        # User count over time
        axes[1, 0].plot(self.history_df['Timestamp'], self.history_df['User Count'])
        axes[1, 0].set_title('User Count Over Time')
        axes[1, 0].set_ylabel('Active Users')
        axes[1, 0].tick_params(axis='x', rotation=45)

        # Failure rate over time
        axes[1, 1].plot(self.history_df['Timestamp'],
                        self.history_df['Failures/s'] / self.history_df['Requests/s'] * 100)
        axes[1, 1].set_title('Failure Rate Over Time')
        axes[1, 1].set_ylabel('Failure Rate (%)')
        axes[1, 1].tick_params(axis='x', rotation=45)

        plt.tight_layout()
        plt.savefig(f'{self.csv_prefix}_analysis.png', dpi=300, bbox_inches='tight')
        print(f"Visualizations saved as {self.csv_prefix}_analysis.png")

    def analyze(self):
        """Run complete analysis"""
        self.load_data()
        self.generate_summary_report()
        self.create_visualizations()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze Locust load test results")
    parser.add_argument("csv_prefix", help="Prefix of CSV files to analyze (e.g., 'results_medium_20231201_143000')")

    args = parser.parse_args()

    analyzer = LoadTestAnalyzer(args.csv_prefix)
    analyzer.analyze()
