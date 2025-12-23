#!/usr/bin/env python3
import psutil
import time
import sys
import os
from datetime import datetime

with open('mempool.txt', 'r') as file:
    pid = int(file.readline())
print(pid)

PHYSICAL_CORES = 4
LOGICAL_CORES = 8

# Файл для сохранения статистики
log_file = 'monitor_log.csv'

# Создаем файл и записываем заголовки, если файл не существует
if not os.path.exists(log_file):
    with open(log_file, 'w') as f:
        f.write('timestamp,cpu_percent,ram_percent,ram_mb,disk_read_mb,disk_write_mb,threads,status\n')

while True:
    try:
        p = psutil.Process(pid)
        
        while True:
            cpu = p.cpu_percent(interval=0.2)
            #cpu = int(cpu/7.7)
            mem = p.memory_percent()
            mem_mb = p.memory_info().rss / 1024 / 1024
            io = p.io_counters()
            
            # Выводим ВСЕ в одну строку
            #print(f"CPU: {cpu:5.1f}% | RAM: {mem:5.1f}% ({mem_mb:6.1f}MB) | "
            #      f"Disk Read: {io.read_bytes / 1024 / 1024:6.3f}MB | "
            #      f"Disk Write: {io.write_bytes / 1024 / 1024:6.3f}MB | "
            #      f"Threads: {p.num_threads():3d} | Status: {p.status():8s}",
            #      flush=True)
            
            # Сохраняем в файл в виде столбцов
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            with open(log_file, 'a') as f:
                f.write(f'{timestamp},{cpu:.1f},{mem:.1f},{mem_mb:.1f},'
                        f'{io.read_bytes / 1024 / 1024:.3f},'
                        f'{io.write_bytes / 1024 / 1024:.3f},'
                        f'{p.num_threads()},{p.status()}\n')
            
            time.sleep(1)
            
    except psutil.NoSuchProcess:
        print("Status: stop")
        # Сохраняем последнее состояние
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(log_file, 'a') as f:
            f.write(f'{timestamp},0,0,0,0,0,0,stopped\n')
        break
    except KeyboardInterrupt:
        print("\nExiting...")
        break
    except Exception as e:
        print(f"Error: {e}")
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(log_file, 'a') as f:
            f.write(f'{timestamp},0,0,0,0,0,0,error\n')
        break
