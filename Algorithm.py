import heapq

#RR (Round Robin) Algorithm
def round_robin(processes, burst_times, arrival_times, quantum):
    n = len(processes)
    remaining_burst = burst_times[:]
    time = 0
    queue = []
    waiting_time = [0] * n
    turnaround_time = [0] * n
    index = 0  # Dùng để kiểm tra tiến trình mới đến

    while any(remaining_burst):
        # Thêm tiến trình vào hàng đợi nếu đã đến thời điểm arrival
        while index < n and arrival_times[index] <= time:
            queue.append(index)
            index += 1

        if queue:
            current = queue.pop(0)  # Lấy tiến trình đầu tiên từ hàng đợi
            execution_time = min(quantum, remaining_burst[current])
            time += execution_time
            remaining_burst[current] -= execution_time

            # Thêm các tiến trình mới đến vào hàng đợi
            while index < n and arrival_times[index] <= time:
                queue.append(index)
                index += 1

            # Nếu tiến trình chưa hoàn thành, đưa lại vào cuối hàng đợi
            if remaining_burst[current] > 0:
                queue.append(current)
            else:
                turnaround_time[current] = time - arrival_times[current]
                waiting_time[current] = turnaround_time[current] - burst_times[current]
        else:
            time += 1  # CPU rảnh, tiến tới thời điểm tiếp theo

    print("Process\tWaiting Time\tTurnaround Time")
    for i in range(n):
        print(f"P{processes[i]}\t{waiting_time[i]}\t\t{turnaround_time[i]}")

#SRTN (Shortest Remaining Time Next) Algorithm
def shortest_remaining_time_next(processes, burst_times, arrival_times):
    n = len(processes)
    remaining_time = burst_times[:]
    time = 0
    completed = 0
    waiting_time = [0] * n
    turnaround_time = [0] * n
    min_heap = []
    index = 0
    last_process = -1

    while completed < n:
        # Thêm tiến trình mới đến vào min heap
        while index < n and arrival_times[index] <= time:
            heapq.heappush(min_heap, (remaining_time[index], index))
            index += 1

        if min_heap:
            burst, current = heapq.heappop(min_heap)
            if last_process != current:
                last_process = current

            time += 1
            remaining_time[current] -= 1

            # Nếu tiến trình chưa hoàn thành, đưa lại vào heap với thời gian còn lại
            if remaining_time[current] > 0:
                heapq.heappush(min_heap, (remaining_time[current], current))
            else:
                completed += 1
                turnaround_time[current] = time - arrival_times[current]
                waiting_time[current] = turnaround_time[current] - burst_times[current]
        else:
            time += 1  # CPU rảnh, tiến tới thời điểm tiếp theo

    print("Process\tWaiting Time\tTurnaround Time")
    for i in range(n):
        print(f"P{processes[i]}\t{waiting_time[i]}\t\t{turnaround_time[i]}")
