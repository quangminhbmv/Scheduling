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
        self.current_cpu_index = 0
        self.current_resource_index = 0
        self.first_arrival_time = arrival_time
        self.last_executed_time = arrival_time
        self.resource_queue = []
        self.in_resource = False
        self.resource_remaining = 0
        self.resource_wait_start_time = None  # <-- Thêm để tính waiting time trong resource
        self.just_released_from_resource = False

class RR:
    def __init__(self, p_list, quantum):
        self.processes_list = []
        self.quantum = quantum
        self.create_processes(p_list)

    def create_processes(self, p):
        for x in p:
            name = x[0]
            arrival_time = x[1]
            cpu_times = []
            resource_types = []
            resource_amounts = []
            i = 2
            while i < len(x):
                if isinstance(x[i], str) and '(' in x[i]:
                    amount = int(x[i].split('(')[0])
                    r_type = x[i].split('(')[1].split(')')[0]
                    resource_amounts.append(amount)
                    resource_types.append(r_type)
                    i += 1
                elif isinstance(x[i], int):
                    cpu_times.append(x[i])
                    i += 1
                else:
                    i += 1
            self.processes_list.append(Process(name, arrival_time, cpu_times, resource_types, resource_amounts))

    def run(self):
        t = 0
        cpu_execution = []
        resource_execution = []
        ready_queue = []
        waiting_list = sorted(self.processes_list, key=lambda p: p.arrival_time)
        resource_queue = []
        finished_processes = []

        while ready_queue or waiting_list or resource_queue:
            # Đưa tiến trình từ waiting_list vào ready_queue nếu đã đến thời điểm arrival
            while waiting_list and waiting_list[0].arrival_time <= t:
                ready_queue.append(waiting_list.pop(0))

            # Xử lý resource_queue
            new_resource_queue = []
            resource_holder = "_"
            for p in resource_queue:
                if p.resource_remaining > 0:
                    p.resource_remaining -= 1
                    resource_holder = p.name
                    new_resource_queue.append(p)
                    if p.resource_remaining == 0:
                        if p.current_cpu_index < len(p.cpu_times):
                            p.arrival_time = t
                            ready_queue.append(p)
                        else:
                            p.e_time = t
                            p.turnaround_time = p.e_time - p.first_arrival_time
                            finished_processes.append(p)

            resource_queue = [p for p in new_resource_queue if p.resource_remaining > 0]
            resource_execution.append(resource_holder)

            # ✅ Check lại waiting_list một lần nữa sau resource (đảm bảo không bị chậm đưa vào ready_queue)
            while waiting_list and waiting_list[0].arrival_time <= t:
                ready_queue.append(waiting_list.pop(0))

            # Nếu không có tiến trình sẵn sàng chạy, tăng thời gian
            if not ready_queue:
                cpu_execution.append("_")
                t += 1
                continue

            # Lấy tiến trình từ ready_queue
            process = ready_queue.pop(0)

            # ✅ Cộng waiting time nếu tiến trình thực sự chờ (không phải vừa xong resource)
            if process.last_executed_time < t:
                process.w_time += t - process.arrival_time

            burst_remaining = process.cpu_times[process.current_cpu_index]
            time_slice = min(self.quantum, burst_remaining)

            tqdm.write(f'Process {process.name} executes from Time {t} to {t + time_slice}')
            for _ in tqdm(range(time_slice), desc=f'{process.name}'):
                cpu_execution.append(process.name)
                if len(resource_execution) < len(cpu_execution):
                    resource_execution.append(resource_holder if resource_holder != "_" else "_")
                t += 1

            # Cập nhật lại tiến trình sau khi chạy xong quantum
            process.cpu_times[process.current_cpu_index] -= time_slice
            process.last_executed_time = t

            if process.cpu_times[process.current_cpu_index] == 0:
                process.current_cpu_index += 1
                if process.current_resource_index < len(process.resource_amounts):
                    process.resource_remaining = process.resource_amounts[process.current_resource_index]
                    process.resource_wait_start_time = t
                    process.current_resource_index += 1
                    resource_queue.append(process)
                elif process.current_cpu_index < len(process.cpu_times):
                    process.arrival_time = t
                    waiting_list.append(process)
                else:
                    process.e_time = t
                    process.turnaround_time = process.e_time - process.first_arrival_time
                    finished_processes.append(process)
            else:
                process.arrival_time = t
                waiting_list.append(process)

        # Đảm bảo 2 timeline CPU và resource có độ dài bằng nhau
        max_len = max(len(cpu_execution), len(resource_execution))
        cpu_execution += ["_"] * (max_len - len(cpu_execution))
        resource_execution += ["_"] * (max_len - len(resource_execution))

        tqdm.write("All processes completed.")
        with open("output.txt", "w") as f:
            f.write(" ".join(cpu_execution) + "\n")
            f.write(" ".join(resource_execution) + "\n")
            f.write(" ".join(str(p.turnaround_time) for p in self.processes_list) + "\n")
            f.write(" ".join(str(p.w_time) for p in self.processes_list) + "\n") 

