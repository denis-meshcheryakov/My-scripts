#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  "net_to_core.py"
#
import ipaddress
from netmiko import ConnectHandler
import netmiko
#from getpass import getpass

n = input('''Если хотите добавить подсеть, нажмите Enter
Введите подсети и нажмите Enter:
________________________________________________________
Если хотите удалить подсеть, введите "no" и нажмите Enter
Введите подсети и нажмите Enter:
<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
''')
print('*' * 57)
net = []
while True:
    net_input = input()
    if net_input:
        net.append(net_input)
    else:
        break

def get_commands(net, n):
    net_list = []
    commands = ['int vlan 700']
    for line in net:
        line = ipaddress.ip_network(line)
        ip = str(line[1])
        mask = str(line.netmask)
        net_list.append([ip, mask])
        lin = '{} ip address {} {} secondary'.format(n, ip, mask)
        commands.append(lin)
    return commands

commands = get_commands(net, n)

with open('accaunt.txt', 'r') as src:
    d_name, d_pass, *rest = src.read().split()

device = {
    "device_type": "cisco_ios",
    "ip": '10.190.25.122',
    "username": d_name,
    "password": d_pass,
    }

print('Connecting to 3750x-PRV-TS5-CORE ...')

def send_command(device, commands):
    try:
        with ConnectHandler(**device) as ssh:
            ssh.enable()
            output = ssh.send_config_set(commands, strip_prompt=False)
            print(output)
            output_wr = ssh.send_command('write', strip_prompt=False)
            print(output_wr)
            result = output, output_wr
        return result
    except netmiko.ssh_exception.NetMikoAuthenticationException:
       print('Authentication Failure')
    except netmiko.ssh_exception.NetMikoTimeoutException:
       print('Network is unreachable')


if __name__ == "__main__":
    result = send_command(device, commands)
