#!/usr/bin/env python3
"""
Минимальная проверка статуса и параллельный запуск
"""

import subprocess
import sys
import time
import os

# Функция проверки статуса
def is_stopped():
    try:
        if os.path.exists('monitor_log.csv'):
            with open('monitor_log.csv', 'r') as f:
                for line in f:
                    pass
                if 'stopped' in line:
                    return True
    except:
        pass
    return False

# Запуск процессов
monitoring = subprocess.Popen([sys.executable, 'monitoring.py'])
time.sleep(2)  # Ждем создания файла
dashboard = None

# Главный цикл
try:
    while True:
        # Запускаем дашборд, если не запущен и статус не stopped
        if not dashboard and not is_stopped():
            dashboard = subprocess.Popen([sys.executable, 'dashbord.py', '--interval', '2'])
        
        # Если дашборд завершился или статус stopped - выходим
        if dashboard and (dashboard.poll() is not None or is_stopped()):
            break
            
        time.sleep(1)
        
except KeyboardInterrupt:
    pass
finally:
    # Останавливаем процессы
    if dashboard:
        dashboard.terminate()
    monitoring.terminate()
