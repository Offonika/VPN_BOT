import subprocess

def add_vpn_user(username: str):
    # Пример команды для добавления VPN пользователя через WireGuard
    command = f"wg set wg0 peer {username} allowed-ips 10.0.0.2/32"
    subprocess.run(command, shell=True)
    return True

def remove_vpn_user(username: str):
    # Пример команды для удаления VPN пользователя через WireGuard
    command = f"wg set wg0 peer {username} remove"
    subprocess.run(command, shell=True)
    return True
