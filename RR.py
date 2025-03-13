from tqdm import tqdm
from time import sleep

class Process:
    def __init__(self, name, arrival_time, cpu_times, resource_types=None, resource_amounts=None):
        self.name = name
        self.arrival_time = arrival_time
        self.cpu_times = cpu_times  # Danh sách các CPU burst
        self.resource_types = resource_types or []
        self.resource_amounts = resource_amounts or []
        
        self.w_time = 0  # Thời gian chờ
        self.e_time = 0  # Thời gian kết thúc
        self.turnaround_time = 0  # Thời gian hoàn thành
        self.current_cpu_index = 0  # Chỉ mục CPU burst hiện tại
        self.current_resource_index = 0  # Chỉ mục tài nguyên hiện tại
        self.remaining_time = sum(cpu_times)  # Tổng thời gian CPU cần xử lý
        self.first_arrival_time = arrival_time  # Lưu thời điểm đầu tiên tiến trình vào hàng đợi

class RR:
    def __init__(self, p_list, quantum):
        self.processes_list = []
        self.quantum = quantum
        self.create_processes(p_list)
    
    def create_processes(self, p):
        for x in p:
            name = x[0]
            arrival_time = x[1]
            cpu_times = [t for t in x[2:] if isinstance(t, int)]
            resource_types = []
            resource_amounts = []
            
            self.processes_list.append(Process(name, arrival_time, cpu_times, resource_types, resource_amounts))

    def run(self):
        t = 0
        cpu_execution = []
        queue = [p for p in sorted(self.processes_list, key=lambda x: x.arrival_time)]
        finished_processes = []

        while queue:
            process = queue.pop(0)
            if not hasattr(process, 'first_arrival_time'):
                process.first_arrival_time = process.arrival_time
            
            execution_time = min(self.quantum, process.remaining_time)
            tqdm.write(f'Process {process.name} executes from Time {t} to {t + execution_time}')
            
            for _ in tqdm(range(execution_time), desc=str(process.name)):
                cpu_execution.append(process.name)
                sleep(1)
            
            t += execution_time
            process.remaining_time -= execution_time
            
            if process.remaining_time > 0:
                queue.append(process)
            else:
                process.e_time = t
                process.turnaround_time = process.e_time - process.first_arrival_time
                finished_processes.append(process)

        tqdm.write("All processes completed.")
        
        with open("output.txt", "w") as f:
            f.write(" ".join(cpu_execution) + "\n")
            f.write(" ".join(str(p.turnaround_time) for p in self.processes_list) + "\n")
            f.write(" ".join(str(p.w_time) for p in self.processes_list) + "\n")

