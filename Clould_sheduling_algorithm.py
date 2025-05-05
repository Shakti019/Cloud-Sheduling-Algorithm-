import heapq
from collections import deque
import threading
import time
import matplotlib.pyplot as plt

class Process:
    def __init__(self, pid, burst_time, priority):
        self.pid = pid
        self.burst_time = burst_time
        self.priority = priority
        self.remaining_time = burst_time
        self.is_leader = False
        self.start_time = None
        self.end_time = None

    def __lt__(self, other):
        return (self.burst_time, -self.priority) < (other.burst_time, -other.priority)

class CloudScheduler:
    def __init__(self):
        self.ready_queue = deque()
        self.completed_processes = []
        self.start_time = time.time()
        self.total_execution_time = 0
        self.total_processes = 0

    def add_process(self, process):
        self.ready_queue.append(process)
        self.total_processes += 1

    def schedule(self):
        while self.ready_queue:
            if len(self.ready_queue) < 3:
                self.execute_sequential()
            else:
                self.execute_group()

    def execute_sequential(self):
        while self.ready_queue:
            process = self.ready_queue.popleft()
            process.start_time = time.time() - self.start_time
            print(f"Executing Process {process.pid} (BT: {process.burst_time}, Priority: {process.priority})")
            time.sleep(process.burst_time * 0.1)
            process.end_time = time.time() - self.start_time
            self.total_execution_time += process.burst_time * 0.1
            self.completed_processes.append(process)

    def execute_group(self):
        group = []
        for _ in range(3):
            if self.ready_queue:
                group.append(self.ready_queue.popleft())

        group.sort(key=lambda p: (-p.burst_time, p.priority))
        leader = group[0]
        leader.is_leader = True
        children = group[1:]

        print(f"Group Created: Leader - Process {leader.pid}, Children - {[p.pid for p in children]}")

        def execute_child(process):
            process.start_time = time.time() - self.start_time
            while process.remaining_time > 0:
                print(f"Executing Child Process {process.pid}")
                process.remaining_time -= 1
                time.sleep(0.1)
            process.end_time = time.time() - self.start_time

        def execute_leader():
            leader.start_time = time.time() - self.start_time
            time.sleep(0.5)  # Delay leader execution to allow child processes to progress
            while leader.remaining_time > 0:
                print(f"Executing Leader Process {leader.pid}")
                leader.remaining_time -= 1
                time.sleep(0.1)
            leader.end_time = time.time() - self.start_time

        child_threads = [threading.Thread(target=execute_child, args=(child,)) for child in children]
        leader_thread = threading.Thread(target=execute_leader)

        for t in child_threads:
            t.start()
        leader_thread.start()

        for t in child_threads:
            t.join()
        leader_thread.join()

        for process in group:
            self.total_execution_time += process.burst_time * 0.1
            self.completed_processes.append(process)

    def print_results(self):
        print("\nExecution Complete. Process Order:")
        for process in self.completed_processes:
            print(f"Process {process.pid} - Completed")

        throughput = self.total_processes / self.total_execution_time
        print(f"Total Execution Time: {self.total_execution_time:.2f} seconds")
        print(f"Throughput: {throughput:.2f} processes per second")

        self.generate_graphs()

    def generate_graphs(self):
        process_ids = [p.pid for p in self.completed_processes]
        burst_times = [p.burst_time for p in self.completed_processes]
        turnaround_times = [p.end_time - p.start_time for p in self.completed_processes]
        waiting_times = [tat - bt for tat, bt in zip(turnaround_times, burst_times)]
        throughput = [self.total_processes / self.total_execution_time] * len(process_ids)

        plt.figure(figsize=(12, 6))
        plt.subplot(1, 3, 1)
        plt.bar(process_ids, turnaround_times, color='blue', label='Turnaround Time')
        plt.bar(process_ids, waiting_times, color='red', label='Waiting Time')
        plt.xlabel('Process ID')
        plt.ylabel('Time (s)')
        plt.title('Turnaround & Waiting Time')
        plt.legend()

        plt.subplot(1, 3, 2)
        plt.bar(process_ids, burst_times, color='green', label='Burst Time')
        plt.xlabel('Process ID')
        plt.ylabel('Time (s)')
        plt.title('Burst Time of Processes')
        plt.legend()

        plt.subplot(1, 3, 3)
        plt.plot(process_ids, throughput, marker='o', linestyle='-', color='purple', label='Throughput')
        plt.xlabel('Process ID')
        plt.ylabel('Processes per Second')
        plt.title('Throughput Over Processes')
        plt.legend()

        plt.tight_layout()
        plt.show()

# Testing
scheduler = CloudScheduler()
processes = [
    Process(1, 5, 2),
    Process(2, 3, 1),
    Process(3, 8, 3),
    Process(4, 4, 2),
    Process(5, 6, 1),
    Process(6, 2, 3),
]

for p in processes:
    scheduler.add_process(p)

scheduler.schedule()
scheduler.print_results()
