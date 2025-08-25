# ============================================================================
# monitoring.py - Performance monitoring during load tests
# ============================================================================

import psutil
import time
import json
from datetime import datetime

class PerformanceMonitor:
    """Monitor system performance during load tests"""

    def __init__(self, interval=5):
        self.interval = interval
        self.metrics = []
        self.monitoring = False

    def start_monitoring(self):
        """Start performance monitoring"""
        self.monitoring = True
        print("Performance monitoring started...")

        while self.monitoring:
            metric = {
                "timestamp": datetime.now().isoformat(),
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_io": psutil.disk_io_counters()._asdict() if psutil.disk_io_counters() else {},
                "network_io": psutil.net_io_counters()._asdict() if psutil.net_io_counters() else {},
                "active_connections": len(psutil.net_connections())
            }

            self.metrics.append(metric)
            print(f"CPU: {metric['cpu_percent']}%, Memory: {metric['memory_percent']}%")

            time.sleep(self.interval)

    def stop_monitoring(self):
        """Stop monitoring and save results"""
        self.monitoring = False

        with open(f'performance_metrics_{int(time.time())}.json', 'w') as f:
            json.dump(self.metrics, f, indent=2)

        print(f"Performance monitoring stopped. {len(self.metrics)} metrics saved.")
