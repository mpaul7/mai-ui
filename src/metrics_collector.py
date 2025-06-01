# metrics_collector.py

import time
import pynvml
import psutil
import pandas as pd

pynvml.nvmlInit()
handle = pynvml.nvmlDeviceGetHandleByIndex(0)

MAX_GPU_MEMORY_BW = 336  # GB/s for RTX 3060

def collect_metrics(duration=60, interval=1):
    timestamps = []
    memory_total_list = []
    memory_used_list = []
    memory_free_list = []
    gpu_util_list = []
    cpu_util_list = []
    cpu_core_utils = []
    sys_mem_total_list = []
    sys_mem_used_list = []
    sys_mem_free_list = []
    mem_bw_gbps_list = []

    start_time = time.time()
    num_iterations = duration // interval

    for _ in range(num_iterations):
        current_time = time.time() - start_time
        mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
        gpu_util = pynvml.nvmlDeviceGetUtilizationRates(handle)

        timestamps.append(current_time)
        memory_total_list.append(mem_info.total / 1024**3)
        memory_used_list.append(mem_info.used / 1024**3)
        memory_free_list.append(mem_info.free / 1024**3)
        gpu_util_list.append(gpu_util.gpu)

        mem_bw_util = gpu_util.memory
        mem_bw_gbps = (mem_bw_util / 100.0) * MAX_GPU_MEMORY_BW
        mem_bw_gbps_list.append(mem_bw_gbps)

        core_utils = psutil.cpu_percent(interval=None, percpu=True)
        cpu_core_utils.append(core_utils)
        cpu_util_list.append(sum(core_utils) / len(core_utils))

        sys_mem = psutil.virtual_memory()
        sys_mem_total_list.append(sys_mem.total / 1024**3)
        sys_mem_used_list.append(sys_mem.used / 1024**3)
        sys_mem_free_list.append(sys_mem.available / 1024**3)

        time.sleep(interval)

    pynvml.nvmlShutdown()

    df = pd.DataFrame({
        "time": timestamps,
        "gpu_mem_total": memory_total_list,
        "gpu_mem_used": memory_used_list,
        "gpu_mem_free": memory_free_list,
        "gpu_util": gpu_util_list,
        "gpu_mem_bw": mem_bw_gbps_list,
        "cpu_util": cpu_util_list,
        "sys_mem_total": sys_mem_total_list,
        "sys_mem_used": sys_mem_used_list,
        "sys_mem_free": sys_mem_free_list,
    })

    # Add CPU core metrics
    core_count = len(cpu_core_utils[0])
    for i in range(core_count):
        df[f"cpu_core_{i}"] = [core[i] for core in cpu_core_utils]

    return df
