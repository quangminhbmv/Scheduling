import os
import FCFS
import RR
import SJF
import SRTF

def read_input_file(filename):
    if not os.path.exists(filename):
        print(f"Error: File {filename} not found!")
        return None, None, None

    with open(filename, 'r') as file:
        lines = [line.strip() for line in file if line.strip()]  # Loại bỏ dòng trống

    try:
        algorithm_choice = int(lines[0])  # Đọc thuật toán
        if algorithm_choice not in {1, 2, 3, 4}:
            raise ValueError("Invalid algorithm choice!")

        # Đọc time quantum nếu là Round Robin
        if algorithm_choice == 2:
            time_quantum = int(lines[1])
            if time_quantum <= 0:
                raise ValueError("Time quantum must be a positive integer!")
            start_idx = 2
        else:
            time_quantum = None
            start_idx = 1

        # Đọc số lượng tiến trình
        n = int(lines[start_idx])
        if not (1 <= n <= 4):
            raise ValueError("Number of processes must be between 1 and 4!")

        # Đọc danh sách tiến trình
        p_list = []
        for i in range(start_idx + 1, start_idx + 1 + n):
            parts = lines[i].split()
            if len(parts) < 2:
                raise ValueError(f"Invalid process format in line {i+1}!")

            process_name = f"P{i - start_idx}"
            arrival_time = int(parts[0])
            burst_info = []

            j = 1
            while j < len(parts):
                if "(" in parts[j] and ")" in parts[j]:  # Tài nguyên (R1, R2)
                    burst_info.append(parts[j])
                else:  # CPU burst time
                    burst_info.append(int(parts[j]))
                j += 1

            p_list.append((process_name, arrival_time, *burst_info))

    except (ValueError, IndexError) as e:
        print(f"Error in input file: {e}")
        return None, None, None

    return algorithm_choice, time_quantum, p_list

def write_output_file(filename, gantt_cpu, gantt_resources, turnaround_times, waiting_times):
    """Ghi kết quả của thuật toán lập lịch vào file output.txt"""
    with open(filename, 'w') as file:
        # Gantt chart của CPU
        file.write(" ".join(str(x) for x in gantt_cpu) + "\n")

        # Gantt chart của tài nguyên
        for gantt in gantt_resources:
            file.write(" ".join(str(x) for x in gantt) + "\n")

        # Turnaround time của các tiến trình
        file.write(" ".join(str(x) for x in turnaround_times) + "\n")

        # Waiting time của các tiến trình
        file.write(" ".join(str(x) for x in waiting_times) + "\n")

# Đọc dữ liệu từ file input
filename = "input.txt"
algorithm_choice, time_quantum, p_list = read_input_file(filename)

# Kiểm tra lỗi
if algorithm_choice is None or p_list is None:
    exit()

resources = {"R": 16, "R1": 16, "R2": 16}

# Chạy thuật toán tương ứng
schedulers = {1: FCFS.FCFS, 2: RR.RR, 3: SJF.SJF, 4: SRTF.SRTF}
scheduler_class = schedulers.get(algorithm_choice)

if scheduler_class:
    scheduler = scheduler_class(p_list, time_quantum, resources) if time_quantum else scheduler_class(p_list, resources)
    gantt_cpu, gantt_resources, turnaround_times, waiting_times = scheduler.run()

    # Ghi kết quả vào file output.txt
    write_output_file("output.txt", gantt_cpu, gantt_resources, turnaround_times, waiting_times)
else:
    print("Algorithm not supported yet!")
