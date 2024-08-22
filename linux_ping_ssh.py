# pip install paramiko          - ssh client
# pip install pexpect           - ssh X11 forwarding
# pip install aioping           - aioping
# pip install ansible-runner    - ansible

import ansible_runner
import os
from time import sleep
import pexpect
import asyncio
import aioping
import paramiko
from paramiko.ssh_exception import NoValidConnectionsError, SSHException


IP_LIST = []

LOGIN_SSH_ROOT = 'root'
LOGIN_SSH_DGMU = 'dgmu'
PASSWORD_SSH = '12345678'


async def ping_host_asyncio(ip):
    try:
        delay = await aioping.ping(ip)
        print(f"{ip}: Ping successful, delay = {delay} ms")
        IP_LIST.append(ip)
    except TimeoutError:
        print(f"{ip}: Ping timeout")


async def search_host_to_network_asyncio(subnet_start, subnet_stop):
    task = [ping_host_asyncio("192.168." + str(i) + "." + str(j)) for i in range(subnet_start, subnet_stop + 1)
            for j in range(1, 255)]
    await asyncio.gather(*task)


def ssh_command_to_host(ip_host, command, hosts_txt_create=False):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=ip_host, port=22, username=LOGIN_SSH_DGMU, password=PASSWORD_SSH)

        stdin, stdout, stderr = ssh.exec_command(command)
        stdin.write('Входные данные')
        stdin.flush()

        result = stdout.read().decode('utf-8')
        ssh.close()
        print(f"--------INFO--------IP-{ip_host}-------{command}--------")
        if hosts_txt_create:
            with open('hosts.txt', 'a',) as file:
                file.write(f'{ip_host}\n')

    except NoValidConnectionsError:
        print(f"Failed to connect {ip_host}")
    except SSHException:
        print(f"No existing session {ip_host}")
    except TimeoutError:
        print(f"TimeoutError123 {ip_host}")


def ssh_command_X11_forward(ip_address, commandX11):
    # Запуск ssh -X
    child = pexpect.spawn(f'ssh -X {LOGIN_SSH_DGMU}@{ip_address}')
    child.expect('password:')
    child.sendline(PASSWORD_SSH)  # Вставьте ваш пароль
    child.expect('[dgmu@localhost ~]$')  # Ожидайте приглашения командной строки

    # Выполнение команд
    child.sendline(commandX11)  # Выполняем команду на сервере
    sleep(30)
    child.close()  # Завершаем SSH-соединение


def main():
    if os.path.exists("hosts.txt"):
        os.remove("hosts.txt")
    asyncio.run(search_host_to_network_asyncio(96, 102))

    for ip_addr in IP_LIST:
        ssh_command_to_host(ip_host=ip_addr, command="uname -a", hosts_txt_create=True)

    r = ansible_runner.run(private_data_dir='/etc/ansible', playbook='playbook1.yml',
                           status_handler=my_ansible_status_handler)

    with open('hosts.txt', 'r') as file:
        load_host_txt = file.readlines()

    for ip_item in load_host_txt:
        ip_item = ip_item.rstrip('\n')
        ssh_command_X11_forward(ip_item, 'winecfg')


def my_ansible_status_handler(data, runner_config):
    print(data)


if __name__ == '__main__':
    main()

    # ssh_command_to_host(ip_host="192.168.102.16", command="scp -r /mnt/a1056def-4df1-4959-9904-5b654aed0dfd/Soft/Rasim/BF/medic root@192.168.102.16:'/home/dgmu/.wine/drive_c/Program\ Files\ \(x86\)/medic'")



"""         Фон рабочего стола
gsettings set org.mate.background picture-filename '/home/dgmu/Загрузки/girl-beauty-girl-smile-wallpaper-preview.jpg'
"""

# scp -r /mnt/a1056def-4df1-4959-9904-5b654aed0dfd/Soft/Rasim/BF/medic root@192.168.102.16:'/home/dgmu/.wine/drive_c/Program\ Files\ (x86)/medic'

# MUC.desktop
#
# #!/usr/bin/env xdg-open
# [Desktop Entry]
# Version=1.0
# Type=Application
# Terminal=false
# Exec=bash -c 'cd "/home/dgmu/.wine/drive_c/Program Files (x86)/medic/"; wine ./MUC.exe'
# Name[ru_RU]=MUC
# Icon=/home/dgmu/.wine/drive_c/Program Files (x86)/medic/1.ico
# Icon[ru_RU]=/home/dgmu/.wine/drive_c/Program Files (x86)/medic/1.ico
# Name=MUC


