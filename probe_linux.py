import os
import subprocess
import gspread

gc = gspread.service_account(filename='service_account.json')

sh = gc.open("Org Comp")
worksheet = sh.worksheet("p2")

def get_cpu_info():
    cpu_info = {
        'model_name': 'N/A',
        'base_frequency': 'N/A',
        'total_frequency': 'N/A',
        'cores': 'N/A',
        'threads': 'N/A',
        'cache_size': 'N/A',
        'lithography': 'N/A',
        'cpuidlevel': 'N/A',
        'address_sizes': 'N/A'  # Adicionando 'address_sizes' aqui
    }
    
    # Frequência base, modelo, cache, cores e threads
    with open("/proc/cpuinfo") as f:
        for line in f:
            if "model name" in line:
                cpu_info['model_name'] = line.split(":")[1].strip()
            if "cpu MHz" in line and cpu_info['base_frequency'] == 'N/A':
                frequency = float(line.split(":")[1].strip())/1000
                cpu_info['base_frequency'] = f"{frequency:.2f} GHz"
            if "cache size" in line:
                cpu_info['cache_size'] = line.split(":")[1].strip()
            if "cpu cores" in line:
                cpu_info['cores'] = line.split(":")[1].strip()
            if "siblings" in line:
                cpu_info['threads'] = line.split(":")[1].strip()
            if "cpuid level" in line:
                cpu_info['cpuidlevel'] = line.split(":")[1].strip()
            if "address sizes" in line:
                cpu_info['address_sizes'] = line.split(":")[1].strip()

    # Calcular a frequência total da CPU
    if cpu_info['base_frequency'] != 'N/A' and cpu_info['cores'] != 'N/A':
        total_frequency = frequency * int(cpu_info['cores'])
        cpu_info['total_frequency'] = f"{total_frequency:.2f} GHz"

    # Litografia (using lscpu as an alternative)
    try:
        result = subprocess.run(['lscpu'], capture_output=True, text=True)
        for line in result.stdout.splitlines():
            if "BogoMIPS" in line:
                lithography = line.split(":")[1].strip().split()[-1]
                cpu_info['lithography'] = lithography
                break
            if "CPU max MHz" in line:
                cpu_info['total_frequency'] = str(float(line.split(':')[1].strip().split()[-1].split(',')[0])/1000)+"GHz"
    except Exception as e:
        pass

    return cpu_info

def get_memory_info():
    mem_info = {
        'total_memory': 'N/A',
        'memory_type_frequency': 'N/A'
    }
    
    # Tamanho da memória RAM
    with open("/proc/meminfo") as f:
        for line in f:
            if "MemTotal" in line:
                mem_total_kb = int(line.split(":")[1].strip().split()[0])
                mem_total_gb = mem_total_kb / 1024 / 1024
                mem_info['total_memory'] = f"{mem_total_gb:.2f} GB"
                break

    # Geração-frequência da memória (using dmidecode as an alternative)
    try:
        result = subprocess.run(['dmidecode', '--type', 'memory'], capture_output=True, text=True)
        for line in result.stdout.splitlines():
            if "Type:" in line and "DDR" in line:
                mem_info['memory_type_frequency'] = line.split(":")[1].strip()
            if "Speed:" in line and "MHz" in line:
                mem_info['memory_type_frequency'] += f"-{line.split(':')[1].strip()}"
                break
    except Exception as e:
        pass
    
    return mem_info

def get_storage_info():
    storage_info = {
        'storage_type': 'N/A'
    }
    
    # HD SATA ou SSD
    try:
        result = subprocess.run(['lsblk', '-d', '-o', 'NAME,ROTA'], capture_output=True, text=True)
        for line in result.stdout.splitlines()[1:]:  # Skip header
            device, rota = line.split()
            if rota == '0':
                storage_info['storage_type'] = 'SSD'
                break
            else:
                storage_info['storage_type'] = 'HDD'
    except Exception as e:
        pass
    
    return storage_info

def collect_system_info():
    system_info = {}
    system_info.update(get_cpu_info())
    system_info.update(get_memory_info())
    system_info.update(get_storage_info())
    
    return system_info

def find_next_available_row(worksheet):
    str_list = list(filter(None, worksheet.col_values(1)))  # Coluna 1 é a coluna A
    return len(str_list) + 1

def update_sheet_with_system_info(worksheet, info):
    next_row = find_next_available_row(worksheet)
    worksheet.update(f'A{next_row}', [[info['model_name'],  info['total_frequency'], info['cores'], info['threads'], info['cache_size'], info['total_memory'], info['storage_type'],info['cpuidlevel'],info['address_sizes']]])

if __name__ == "__main__":
    info = collect_system_info()
    update_sheet_with_system_info(worksheet, info)
    for key, value in info.items():
        print(f"{key.replace('_', ' ').capitalize()}: {value}")

