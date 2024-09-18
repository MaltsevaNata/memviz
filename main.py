import os
from datetime import datetime

import matplotlib
import psutil
import time
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from sys import platform

if platform == "darwin":
    matplotlib.use("TkAgg")


class RAMUsageMonitor:
    def __init__(self, pid, interval=500):
        self.pid = pid
        self.interval = interval
        self.times = []
        self.ram_usages = []
        self.start_time = time.time()
        try:
            self.process = psutil.Process(pid)
        except psutil.NoSuchProcess:
            print(f"No process with PID {pid}")
            self.process = None
            return

    def start_simulation(self):
        # Set up the plot
        self.fig = plt.figure()
        self.ax = plt.axes(xlim=(0, 100), ylim=(0, 100))
        self.line, = self.ax.plot([], [], label="RAM Usage (MB)", lw=2)  # Initialize line object

        # Set labels and title
        self.ax.set_xlabel("Time (seconds)")
        self.ax.set_ylabel("Memory Usage (MB)")
        self.ax.set_title(f"RAM Usage of PID {self.pid}")
        self.ax.legend()

        # Create the animation
        self.ani = FuncAnimation(self.fig, self.update, frames=10, interval=self.interval)
        plt.show()

    def get_ram_usage(self):
        try:
            memory_info = self.process.memory_info()
            return memory_info.rss  # in bytes
        except psutil.NoSuchProcess:
            return None

    def update(self, frame):
        if not self.process or not self.process.is_running():
            print(f"Process {self.pid} has finished.")
            self.ani.event_source.stop()  # Stop the animation
            self.save_plot()
            return self.line,

        current_time = time.time() - self.start_time
        ram_usage = self.get_ram_usage()

        if ram_usage is not None:
            self.times.append(current_time)
            self.ram_usages.append(float(ram_usage) / (1024.0 * 1024.0))  # Convert to MB

            # Update the line with new data
            self.line.set_data(self.times, self.ram_usages)

            # Dynamically adjust the axes to fit the new data
            self.ax.set_xlim(0, max(self.times) + 1)
            self.ax.set_ylim(0, max(self.ram_usages) + 10)  # Leave some padding for the Y-axis

        return self.line,

    def save_plot(self):
        dt_object = datetime.fromtimestamp(self.start_time)
        start_time_str = dt_object.strftime('%Y-%m-%d_%H:%M:%S')
        filename = f"pid_{self.pid}_{start_time_str}.png"
        script_dir = os.path.dirname(__file__)
        results_dir = os.path.join(script_dir, 'output/')
        plt.savefig(results_dir + filename)
        print(f"Plot saved as {filename}")


if __name__ == '__main__':
    pid = 97143  # Replace with your process PID
    monitor = RAMUsageMonitor(pid, interval=500)
    monitor.start_simulation()
