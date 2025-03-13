from tqdm import tqdm
from time import sleep

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

class SRTF:
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
                process.current_resource_index += 1
                resource_waiting_queue.append(process)
        else:
            if process.current_cpu_index >= len(process.cpu_times) and process.current_resource_index >= len(process.resource_types):
                process.e_time = t
                finished_processes.append(process)
            else:
                cpu_queue.append(process)

    def update_resource_execution(self, resource_execution, current_time):
        executing_process = None
        for p in self.processes_list:
            if hasattr(p, 'resource_acquired_time') and hasattr(p, 'resource_release_time'):
                if p.resource_acquired_time <= current_time < p.resource_release_time:
                    executing_process = p
                    break

        if executing_process:
            resource_execution.append(executing_process.name)
        else:
            resource_execution.append("_")

    def update_cpu_execution(self, actual_p, cpu_time, cpu_execution, resource_execution):
        for _ in tqdm(range(cpu_time), desc=str(actual_p.name)):
            cpu_execution.append(actual_p.name)
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
            p.remaining_cpu_time = p.cpu_times[0] if p.cpu_times else 0
            p.started = False
            p.initial_arrival_time = p.arrival_time
            p.first_arrival_time = None

        while cpu_queue or resource_waiting_queue:
            new_resource_waiting = []
            for p in resource_waiting_queue:
                if hasattr(p, 'resource_release_time') and p.resource_release_time <= t:
                    tqdm.write(f'Process {p.name} finished resource at Time: {t}')
                    p.waiting_for_resource = False
                    # ✅ FIX: Check if CPU burst is also finished
                    if p.current_cpu_index < len(p.cpu_times):
                        p.remaining_cpu_time = p.cpu_times[p.current_cpu_index]
                        p.arrival_time = t
                        cpu_queue.append(p)
                    else:
                        # ✅ If no CPU burst left, process is DONE
                        p.e_time = t
                        finished_processes.append(p)
                else:
                    new_resource_waiting.append(p)
            resource_waiting_queue = new_resource_waiting

            ready_processes = [p for p in cpu_queue if p.arrival_time <= t and p.current_cpu_index < len(p.cpu_times)]

            if ready_processes:
                actual_p = min(ready_processes, key=lambda p: p.remaining_cpu_time)

                if not actual_p.started:
                    actual_p.started = True
                    actual_p.first_arrival_time = t

                if not hasattr(actual_p, 'last_cpu_time') or actual_p.last_cpu_time is None:
                    actual_p.w_time += t - actual_p.arrival_time
                else:
                    if actual_p.arrival_time < t:
                        actual_p.w_time += t - actual_p.arrival_time

                tqdm.write(f'Process {actual_p.name} is executing CPU burst {actual_p.current_cpu_index + 1} at Time: {t}')
                self.update_cpu_execution(actual_p, 1, cpu_execution, resource_execution)
                self.update_resource_execution(resource_execution, t)

                actual_p.remaining_cpu_time -= 1
                t += 1

                actual_p.last_cpu_time = t
                cpu_queue = [p for p in cpu_queue if p != actual_p]

                if actual_p.remaining_cpu_time == 0:
                    actual_p.current_cpu_index += 1
                    actual_p.e_time = t
                    self.handle_resource_after_cpu(actual_p, t, cpu_queue, resource_waiting_queue, finished_processes)
                    if actual_p.current_cpu_index < len(actual_p.cpu_times):
                        actual_p.remaining_cpu_time = actual_p.cpu_times[actual_p.current_cpu_index]
                else:
                    actual_p.arrival_time = t
                    cpu_queue.append(actual_p)
            else:
                cpu_execution.append("_")
                self.update_resource_execution(resource_execution, t)
                t += 1

        tqdm.write("All processes completed.")
        self.trim_executions(cpu_execution, resource_execution)

        waiting_times, turnaround_times = self.calculate()

        # Ghi file output.txt: gồm CPU line, resource line, rồi đến turnaround và waiting
        with open("output.txt", "w") as f:
            f.write(" ".join(cpu_execution) + "\n")
            f.write(" ".join(resource_execution) + "\n")
            f.write(" ".join(str(t) for t in turnaround_times) + "\n")
            f.write(" ".join(str(w) for w in waiting_times) + "\n")

    def allocate_resources(self, process, index=0, t=0):
        if index >= len(process.resource_types) or index >= len(process.resource_amounts):
            return False

        resource_type = process.resource_types[index]
        resource_amount = process.resource_amounts[index]

        if self.resources.get(resource_type, 0) >= resource_amount:
            self.resources[resource_type] -= resource_amount
            process.resource_acquired_time = t
            process.resource_release_time = t + resource_amount
            process.resource_type_holding = resource_type
            process.resource_amount_holding = resource_amount
            return True
        return False

    def calculate(self):
        print("\n" + f"{'Process':<10} {'Waiting-Time':<16} {'Turn-Around-Time':<20}")
        waiting_times = []
        turnaround_times = []

        for p in self.processes_list:
            if hasattr(p, 'e_time'):
                p.turnaround_time = p.e_time - p.initial_arrival_time
            turnaround_times.append(p.turnaround_time)
            waiting_times.append(p.w_time)
        
        return waiting_times, turnaround_times

