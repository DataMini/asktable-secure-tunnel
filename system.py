import platform
import socket
import psutil
from datetime import datetime


def gather_system_info() -> dict:
    # 创建一个字典来保存信息
    info = {
        'os': platform.system(),
        'os_release': platform.release(),
        'os_version': platform.version(),
        'machine': platform.machine(),
        'processor': platform.processor(),
    }

    # 使用platform模块获取操作系统信息

    # 使用socket模块获取网络信息
    hostname = socket.gethostname()
    info['hostname'] = hostname
    try:
        ip_address = socket.gethostbyname(hostname)
        info['ip'] = ip_address
    except socket.gaierror:
        info['ip'] = ''

    # 获取当前进程的信息
    current_process = psutil.Process()
    start_time = current_process.create_time()
    readable_time = datetime.fromtimestamp(start_time).strftime("%Y-%m-%d %H:%M:%S")
    info['start_time'] = readable_time
    info['start_timestamp'] = int(start_time)

    return info


if __name__ == '__main__':
    print(gather_system_info())
