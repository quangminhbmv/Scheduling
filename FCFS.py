from tqdm import tqdm
from time import sleep
import threading

class Process:
    def __init__(self, name, arrival_time, cpu_times, resource_types=None, resource_amounts=None):
        self.name = name
        self.arrival_time = arrival_time
        self.cpu_times = cpu_times
        self.resource_types = resource_types or []
        self.resource_amounts = resource_amounts or []
        
        self.w_time = 0
        self.e_time = 0
        self.turnaround_time = 0
        self.resource_release_time = None

class FCFS:
    def __init__(self, p_list, resources):
        self.processes_list = []
        self.resources = resources   
        self.create_processes(p_list)

    def create_processes(self, p):
        p.sort(key=lambda x: x[1])  
        for x in p:
            name = x[0]
            arrival_time = x[1]
            cpu_times = []
            resource_types = []
            resource_amounts = []

            i = 2
            while i < len(x):
                if isinstance(x[i], str) and "(" in x[i] and ")" in x[i]:
                    resource_info = str(x[i])
                    resource_type = resource_info[resource_info.find("(") + 1:resource_info.find(")")]
                    resource_amount = int(resource_info[:resource_info.find("(")])
                    resource_types.append(resource_type)
                    resource_amounts.append(resource_amount)

                    # lấy thời gian sử dụng resource nếu có
                    if i + 1 < len(x) and isinstance(x[i + 1], int):
                        cpu_times.append(x[i + 1])
                        i += 1

                elif isinstance(x[i], int):
                    cpu_times.append(x[i])
                i += 1

            if not cpu_times:
                cpu_times = [0]

            self.processes_list.append(Process(name, arrival_time, cpu_times, resource_types, resource_amounts))

    def handle_resource_after_cpu(self, process, t, cpu_queue, resource_waiting_queue, finished_processes):
        if process.current_resource_index < len(process.resource_types):
            process.waiting_for_resource = True
            if not self.allocate_resources(process, process.current_resource_index, t):
                tqdm.write(f'Process {process.name} is waiting for resource at Time: {t}')
                resource_waiting_queue.append(process)
            else:
                tqdm.write(f'Process {process.name} acquired resource at Time: {t}')
                process.resource_acquired_time = t
                process.resource_release_time = t + process.resource_amounts[process.current_resource_index]
                process.arrival_time = process.resource_release_time
                process.current_resource_index += 1

                if process.current_cpu_index < len(process.cpu_times):
                    cpu_queue.append(process)
                else:
                    process.e_time = process.resource_release_time
                    process.turnaround_time = process.e_time - process.first_arrival_time
                    finished_processes.append(process)
        else:
            if process.current_cpu_index >= len(process.cpu_times):
                process.e_time = t
                process.turnaround_time = process.e_time - process.first_arrival_time
                finished_processes.append(process)
            else:
                cpu_queue.append(process)

    def update_resource_execution(self, resource_execution, t):
        resource_holding = False
        for p in self.processes_list:
            if hasattr(p, 'resource_acquired_time') and p.resource_acquired_time <= t < p.resource_release_time:
                for _ in range(p.resource_acquired_time, p.resource_release_time):
                    resource_execution.append(p.name)
                resource_holding = True
                break
        if not resource_holding:
            resource_execution.append("_")

    def update_cpu_execution(self, actual_p, cpu_time, cpu_execution, resource_execution):
        for _ in tqdm(range(cpu_time), desc=str(actual_p.name)):
            cpu_execution.append(actual_p.name)
            if len(resource_execution) < len(cpu_execution):
                resource_execution.append("_")
            sleep(1)

    def trim_executions(self, cpu_execution, resource_execution):
        max_len = max(len(cpu_execution), len(resource_execution))
        while len(cpu_execution) < max_len:
            cpu_execution.append("_")
        while len(resource_execution) < max_len:
            resource_execution.append("_")

        while cpu_execution and resource_execution and cpu_execution[-1] == "_" and resource_execution[-1] == "_":
            cpu_execution.pop()
            resource_execution.pop()

        max_len = max(len(cpu_execution), len(resource_execution))
        while len(cpu_execution) < max_len:
            cpu_execution.append("_")
        while len(resource_execution) < max_len:
            resource_execution.append("_")

    def run(self):
        t = 0
        cpu_execution = []
        resource_execution = []
        finished_processes = []
        cpu_queue = self.processes_list.copy()
        resource_waiting_queue = []

        for p in cpu_queue:
            p.current_cpu_index = 0
            p.current_resource_index = 0
            p.w_time = 0

        while cpu_queue or resource_waiting_queue:
            new_resource_waiting = []
            for p in resource_waiting_queue:
                if self.allocate_resources(p, p.current_resource_index, t):
                    tqdm.write(f'Process {p.name} acquired resource at Time: {t}')
                    p.resource_acquired_time = t
                    p.resource_release_time = t + p.resource_amounts[p.current_resource_index]
                    p.waiting_for_resource = False

                    p.last_arrival_time = p.arrival_time
                    p.arrival_time = p.resource_release_time

                    if p.current_cpu_index < len(p.cpu_times):
                        cpu_queue.append(p)
                    else:
                        p.e_time = p.resource_release_time
                        p.turnaround_time = p.e_time - p.first_arrival_time
                        finished_processes.append(p)
                else:
                    new_resource_waiting.append(p)
            resource_waiting_queue = new_resource_waiting

            ready_processes = [p for p in cpu_queue if p.arrival_time <= t]

            if ready_processes:
                actual_p = min(ready_processes, key=lambda p: p.arrival_time)
                cpu_queue.remove(actual_p)

                if not hasattr(actual_p, 'first_arrival_time'):
                    actual_p.first_arrival_time = actual_p.arrival_time

                actual_p.w_time += t - actual_p.arrival_time

                i = actual_p.current_cpu_index
                if i >= len(actual_p.cpu_times):
                    continue

                cpu_time = actual_p.cpu_times[i]
                tqdm.write(f'Process {actual_p.name} is executing CPU burst {i+1} at Time: {t}')
                self.update_cpu_execution(actual_p, cpu_time, cpu_execution, resource_execution)
                t += cpu_time

                actual_p.current_cpu_index += 1
                self.handle_resource_after_cpu(actual_p, t, cpu_queue, resource_waiting_queue, finished_processes)
                self.update_resource_execution(resource_execution, t)
            else:
                cpu_execution.append("_")
                if len(resource_execution) < len(cpu_execution):
                    resource_execution.append("_")
                sleep(1)
                t += 1

        tqdm.write("All processes completed.")
        self.trim_executions(cpu_execution, resource_execution)

        # In ra output.txt
        with open("output.txt", "w") as f:
            f.write(" ".join(cpu_execution) + "\n")
            f.write(" ".join(resource_execution) + "\n")
            f.write(" ".join(str(p.turnaround_time) for p in self.processes_list) + "\n")
            f.write(" ".join(str(p.w_time) for p in self.processes_list) + "\n")

    def allocate_resources(self, process, index=0, t=0):
        # Kiểm tra xem index có hợp lệ không trước khi truy cập danh sách
        if index >= len(process.resource_types) or index >= len(process.resource_amounts):
            return False  # Không thể cấp phát nếu chỉ mục ngoài phạm vi

        resource_type = process.resource_types[index]
        resource_amount = process.resource_amounts[index]

        # Kiểm tra tài nguyên có đủ để cấp phát không
        if self.resources.get(resource_type, 0) >= resource_amount:
            self.resources[resource_type] -= resource_amount
            process.resource_acquired_time = t
            process.resource_release_time = t + resource_amount
            process.resource_type_holding = resource_type
            process.resource_amount_holding = resource_amount
            return True  # Cấp phát thành công

        return False  # Không đủ tài nguyên để cấp phát

    def calculate(self):
        print("\n" + f"{'Process':<10} {'Waiting-Time':<16} {'Turn-Around-Time':<20}")
        for p in self.processes_list:
            print(f"{p.name:<10} {p.w_time:<16} {p.turnaround_time:<20}")

