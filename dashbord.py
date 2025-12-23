#!/usr/bin/env python3
"""
Консольный дашборд для мониторинга процесса из CSV файла
"""

import pandas as pd
import time
import os
import sys
from datetime import datetime
import numpy as np

class ProcessDashboard:
    def __init__(self, csv_file='monitor_log.csv'):
        self.csv_file = csv_file
        self.update_interval = 5
        self.history_size = 60     # количество записей для графиков
        
    def clear_screen(self):
        """Очистка экрана консоли"""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def load_data(self):
        """Загрузка данных из CSV файла"""
        try:
            if not os.path.exists(self.csv_file):
                print(f"Файл {self.csv_file} не найден!")
                return None
            
            df = pd.read_csv(self.csv_file)
            
            # Проверяем наличие необходимых колонок
            required_cols = ['timestamp', 'cpu_percent', 'ram_percent', 
                           'ram_mb', 'disk_read_mb', 'disk_write_mb', 
                           'threads', 'status']
            
            for col in required_cols:
                if col not in df.columns:
                    print(f"Колонка {col} не найдена в файле!")
                    return None
            
            return df.tail(self.history_size)  # Последние записи
        
        except Exception as e:
            print(f"Ошибка загрузки данных: {e}")
            return None
    
    def create_progress_bar(self, value, max_value=100, width=30):
        """Создание текстового progress bar"""
        filled = int(width * value / max_value)
        bar = '█' * filled + '░' * (width - filled)
        return f"[{bar}] {value:.1f}%"
    
    def create_sparkline(self, data, height=5):
        """Создание sparkline графика"""
        if len(data) < 2:
            return ""
        
        min_val, max_val = min(data), max(data)
        if max_val == min_val:
            return "─" * len(data)
        
        # Нормализуем данные для отображения
        normalized = [(val - min_val) / (max_val - min_val) * (height - 1) 
                     for val in data]
        
        # Символы для графика
        bars = [' ', '▫', '□', '▪', '■', '▣', '▤', '▥', '█']
        
        sparkline = ""
        for val in normalized:
            idx = min(int(val), len(bars) - 1)
            sparkline += bars[idx]
        
        return sparkline
    
    def format_bytes(self, bytes_value):
        """Форматирование байтов в читаемый вид"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.1f} PB"
    
    def display_dashboard(self, df):
        """Отображение дашборда в консоли"""
        if df is None or len(df) == 0:
            print("Нет данных для отображения")
            return
        
        # Получаем последнюю запись
        latest = df.iloc[-1]
        
        # Получаем историю для графиков
        cpu_history = df['cpu_percent'].tail(20).tolist()
        ram_history = df['ram_percent'].tail(20).tolist()
        
        # Рассчитываем статистику
        avg_cpu = df['cpu_percent'].mean()
        max_cpu = df['cpu_percent'].max()
        avg_ram = df['ram_percent'].mean()
        total_read = df['disk_read_mb'].sum()
        total_write = df['disk_write_mb'].sum()
        
        # Очищаем экран
        self.clear_screen()
        
        # Шапка дашборда
        print("=" * 80)
        print(f"ПРОЦЕСС МОНИТОРИНГ - ДАШБОРД")
        print(f"Файл данных: {self.csv_file}")
        print(f"Последнее обновление: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Всего записей: {len(df)} | Интервал обновления: {self.update_interval} сек")
        print("=" * 80)
        print()
        
        # Секция 1: Текущее состояние
        print("📊 ТЕКУЩЕЕ СОСТОЯНИЕ")
        print("-" * 80)
        
        status_icon = "✅" if latest['status'] != 'stoped' else "❌"
        print(f"{status_icon} Статус: {latest['status'].upper():<10} "
              f"Потоков: {int(latest['threads']):<4} ")
        
        # CPU информация
        cpu_bar = self.create_progress_bar(latest['cpu_percent'])
        print(f"⚡ CPU: {cpu_bar}")
        
        # RAM информация
        ram_bar = self.create_progress_bar(latest['ram_percent'])
        ram_mb = latest['ram_mb']
        print(f"💾 RAM: {ram_bar} ({ram_mb:.1f} MB)")
        
        # Дисковая активность
        read_mb = latest['disk_read_mb']
        write_mb = latest['disk_write_mb']
        print(f"📁 Диск: Чтение: {read_mb:6.2f} MB  |  Запись: {write_mb:6.2f} MB")
        
        print()
        
        # Секция 2: Графики
        print("📈 ИСТОРИЯ (последние 20 измерений)")
        print("-" * 80)
        
        # CPU график
        cpu_spark = self.create_sparkline(cpu_history)
        print(f"CPU:  {cpu_spark}")
        
        print()
        
        # Секция 3: Статистика
        print("📋 СТАТИСТИКА")
        print("-" * 80)
        
        print(f"CPU: Среднее: {avg_cpu:6.1f}%  |  Максимум: {max_cpu:6.1f}%")
        print(f"RAM: Среднее: {avg_ram:6.1f}%")
        print(f"Диск: Всего прочитано: {total_read:8.2f} MB")
        print(f"      Всего записано: {total_write:8.2f} MB")
        
        print()
        
        # Секция 4: Последние 5 записей
        print("🕒 ПОСЛЕДНИЕ ИЗМЕРЕНИЯ")
        print("-" * 80)
        print(f"{'Время':<20} {'CPU%':<8} {'RAM%':<8} {'RAM(MB)':<10} {'Статус':<10}")
        print("-" * 80)
        
        # Показываем последние 5 записей
        for i, row in df.tail(5).iterrows():
            time_str = row['timestamp'][11:19] if len(row['timestamp']) > 10 else row['timestamp']
            print(f"{time_str:<20} {row['cpu_percent']:<8.1f} "
                  f"{row['ram_percent']:<8.1f} {row['ram_mb']:<10.1f} "
                  f"{row['status']:<10}")
        
        print()
        print("=" * 80)
        print(f"Ctrl+C для выхода | Автообновление каждые {self.update_interval} секунд")
    
    def run(self):
        """Основной цикл дашборда"""
        print(f"Запуск консольного дашборда...")
        print(f"Чтение данных из: {self.csv_file}")
        print(f"Интервал обновления: {self.update_interval} секунд")
        print()
        
        try:
            while True:
                # Загружаем данные
                df = self.load_data()
                
                # Отображаем дашборд
                self.display_dashboard(df)
                
                # Ждем перед следующим обновлением
                time.sleep(self.update_interval)
                
        except KeyboardInterrupt:
            print("\n\nДашборд остановлен.")
            sys.exit(0)
        except Exception as e:
            print(f"\nОшибка: {e}")
            sys.exit(1)

# Упрощенная версия дашборда (минималистичная)
class SimpleDashboard:
    def __init__(self, csv_file='monitor_log.csv'):
        self.csv_file = csv_file
    
    def display(self, df):
        """Минималистичный диспетчер задач"""
        os.system('clear' if os.name == 'posix' else 'cls')
        
        if df is None or len(df) == 0:
            print("Нет данных")
            return
        
        latest = df.iloc[-1]
        
        print("═" * 70)
        print(f" ДИСПЕТЧЕР ЗАДАЧ - МОНИТОРИНГ ПРОЦЕССА ".center(70))
        print("═" * 70)
        print(f" Статус: {'ЗАПУЩЕН' if latest['status'] == 'running' else 'ОСТАНОВЛЕН'} "
              f"| Потоки: {int(latest['threads'])} | "
              f"Время: {datetime.now().strftime('%H:%M:%S')}")
        print("─" * 70)
        
        # CPU
        cpu = latest['cpu_percent']
        cpu_bar = '█' * int(cpu/2) + '░' * (50 - int(cpu/2))
        print(f" CPU: {cpu_bar} {cpu:5.1f}%")
        
        # RAM
        ram = latest['ram_percent']
        ram_bar = '█' * int(ram/2) + '░' * (50 - int(ram/2))
        print(f" RAM: {ram_bar} {ram:5.1f}% ({latest['ram_mb']:.1f} MB)")
        
        print("─" * 70)
        print(f" Диск R/W: {latest['disk_read_mb']:6.2f} MB / {latest['disk_write_mb']:6.2f} MB")
        print("─" * 70)
        
        # История CPU
        cpu_history = df['cpu_percent'].tail(30).tolist()
        print(" CPU история:", end=" ")
        for val in cpu_history[-20:]:
            if val < 25:
                print('▁', end='')
            elif val < 50:
                print('▂', end='')
            elif val < 75:
                print('▄', end='')
            else:
                print('█', end='')
        print()
        
        print("═" * 70)
        print(f" Обновление через 5 сек | Ctrl+C для выхода ".center(70))

def main():
    """Точка входа в программу"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Консольный дашборд мониторинга процесса')
    parser.add_argument('--file', '-f', default='monitor_log.csv',
                       help='CSV файл с данными мониторинга')
    parser.add_argument('--simple', '-s', action='store_true',
                       help='Простой режим (как диспетчер задач)')
    parser.add_argument('--interval', '-i', type=int, default=2,
                       help='Интервал обновления в секундах')
    
    args = parser.parse_args()
    
    if args.simple:
        dashboard = SimpleDashboard(args.file)
        dashboard.csv_file = args.file
        
        try:
            while True:
                df = pd.read_csv(args.file) if os.path.exists(args.file) else None
                dashboard.display(df)
                time.sleep(args.interval)
        except KeyboardInterrupt:
            print("\nЗавершено")
            
    else:
        dashboard = ProcessDashboard(args.file)
        dashboard.update_interval = args.interval
        dashboard.run()

if __name__ == "__main__":
    # Проверяем наличие pandas
    try:
        import pandas as pd
    except ImportError:
        print("Установите библиотеку pandas:")
        print("pip install pandas")
        sys.exit(1)
    
    main()
