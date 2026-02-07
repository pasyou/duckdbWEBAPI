import requests
import time
import subprocess
import os
import sys
from datetime import datetime
import threading

class ServiceMonitor:
    def __init__(self, exe_path, health_url="http://localhost:8000/health", check_interval=30, max_failures=3):
        self.exe_path = exe_path
        self.health_url = health_url
        self.check_interval = check_interval
        self.max_failures = max_failures
        self.failure_count = 0
        self.running = False
        self.process = None
        self.log_file = "service_monitor.log"
        
    def log(self, message):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_message + '\n')
    
    def check_health(self):
        try:
            response = requests.get(self.health_url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'healthy':
                    self.failure_count = 0
                    return True
            return False
        except requests.exceptions.RequestException as e:
            self.log(f"健康检查失败: {str(e)}")
            return False
    
    def start_service(self):
        try:
            if self.process and self.process.poll() is None:
                self.log("服务已在运行，先停止服务")
                self.stop_service()
                time.sleep(2)
            
            self.log(f"启动服务: {self.exe_path}")
            self.process = subprocess.Popen(
                [self.exe_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
            )
            self.log("服务启动成功")
            time.sleep(3)
            return True
        except Exception as e:
            self.log(f"启动服务失败: {str(e)}")
            return False
    
    def stop_service(self):
        try:
            if self.process and self.process.poll() is None:
                self.log("停止服务")
                self.process.terminate()
                try:
                    self.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.log("强制终止服务")
                    self.process.kill()
                self.log("服务已停止")
            self.process = None
        except Exception as e:
            self.log(f"停止服务失败: {str(e)}")
    
    def restart_service(self):
        self.log("=" * 50)
        self.log("检测到服务卡死，准备重启服务")
        self.log("=" * 50)
        
        self.stop_service()
        time.sleep(2)
        
        if self.start_service():
            self.failure_count = 0
            self.log("服务重启成功")
        else:
            self.log("服务重启失败")
    
    def monitor_loop(self):
        self.log("服务监控启动")
        self.log(f"监控间隔: {self.check_interval}秒")
        self.log(f"最大失败次数: {self.max_failures}")
        self.log(f"健康检查URL: {self.health_url}")
        
        while self.running:
            try:
                if not self.process or self.process.poll() is not None:
                    self.log("检测到服务进程不存在，尝试启动服务")
                    if self.start_service():
                        self.failure_count = 0
                    else:
                        time.sleep(5)
                        continue
                
                if self.check_health():
                    if self.failure_count > 0:
                        self.log(f"服务恢复正常，失败计数重置为0")
                else:
                    self.failure_count += 1
                    self.log(f"健康检查失败 ({self.failure_count}/{self.max_failures})")
                    
                    if self.failure_count >= self.max_failures:
                        self.restart_service()
                
                time.sleep(self.check_interval)
            except KeyboardInterrupt:
                self.log("收到中断信号，停止监控")
                self.running = False
                break
            except Exception as e:
                self.log(f"监控循环出错: {str(e)}")
                time.sleep(self.check_interval)
        
        self.log("服务监控停止")
    
    def start(self):
        self.running = True
        monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
        monitor_thread.start()
        self.log("监控线程已启动")
        return monitor_thread
    
    def stop(self):
        self.running = False
        self.stop_service()
        self.log("监控已停止")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='DuckDB Web API 服务监控程序')
    parser.add_argument('--exe', required=True, help='EXE文件路径')
    parser.add_argument('--url', default='http://localhost:8000/health', help='健康检查URL')
    parser.add_argument('--interval', type=int, default=30, help='检查间隔（秒）')
    parser.add_argument('--max-failures', type=int, default=3, help='最大失败次数')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.exe):
        print(f"错误: EXE文件不存在: {args.exe}")
        sys.exit(1)
    
    monitor = ServiceMonitor(
        exe_path=args.exe,
        health_url=args.url,
        check_interval=args.interval,
        max_failures=args.max_failures
    )
    
    try:
        monitor.start()
        while monitor.running:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n收到中断信号")
        monitor.stop()

if __name__ == "__main__":
    main()