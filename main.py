import os
from FCFS import FCFS
from RR import RR
from SJF import SJF
from SRTF import SRTF

def read_input_file(filename):
    if not os.path.exists(filename):
        print(f"Error: File {filename} not found!")
        return None, None, None

    with open(filename, 'r') as file:
        lines = [line.strip() for line in file if line.strip()]

    try:
        algorithm_choice = int(lines[0])
        if algorithm_choice not in {1, 2, 3, 4}:
            raise ValueError("Invalid algorithm choice!")

        if algorithm_choice == 2:
            time_quantum = int(lines[1])
            if time_quantum <= 0:
                raise ValueError("Time quantum must be a positive integer!")
            start_idx = 2
        else:
            time_quantum = None
            start_idx = 1

        n = int(lines[start_idx])
        if not (1 <= n <= 4):
            raise ValueError("Number of processes must be between 1 and 4!")

        p_list = []
        for i in range(start_idx + 1, start_idx + 1 + n):
            parts = lines[i].split()
            if len(parts) < 2:
                raise ValueError(f"Invalid process format in line {i+1}!")

            process_name = f"{i - start_idx}"
            arrival_time = int(parts[0])
            burst_info = []

            j = 1
            while j < len(parts):
                if "(" in parts[j] and ")" in parts[j]:
                    burst_info.append(parts[j])
                else:
                    burst_info.append(int(parts[j]))
                j += 1

            p_list.append((process_name, arrival_time, *burst_info))

    except (ValueError, IndexError) as e:
        print(f"Error in input file: {e}")
        return None, None, None

    return algorithm_choice, time_quantum, p_list

# Đọc dữ liệu từ file input
filename = "input.txt"
algorithm_choice, time_quantum, p_list = read_input_file(filename)

if algorithm_choice is None or p_list is None:
    exit()

resources = {}

# Chạy thuật toán tương ứng
schedulers = {1: FCFS, 2: RR, 3: SJF, 4: SRTF}
scheduler_class = schedulers.get(algorithm_choice)

if algorithm_choice == 2:
    scheduler = scheduler_class(p_list, time_quantum)
else:
    scheduler = scheduler_class(p_list, resources)

scheduler.run()
