#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  "add_switch_temp_server.py"
#
# import ipaddress
# from pprint import pprint
# from netmiko import ConnectHandler
# import netmiko

with open('accaunt.txt', 'r') as src:
    d_name, d_pass, l_name, l_pass = src.read().split()

check_switch_device = {
    "device_type": "hp_procurve",
    "ip": switch_ip,
    "username": d_name,
    "password": d_pass,
    "timeout": 120,
}


def check_switch_connction(check_switch_device):
    """Функция считывает prompt и в зависимости от этого определяет
    вендора и возвращает переменную switch_vendor
    """
    try:
        with ConnectHandler(**check_switch_device) as ssh:
            model_of_router = ssh.find_prompt()
            pprint(model_of_router)
            if 'HP2530' in model_of_router:
                switch_vendor = 'hp_procurve'
            elif '3600' in model_of_router:
                switch_vendor = 'hp_comware'
            elif '2960' in model_of_router:
                switch_vendor = 'cisco_ios'
            elif 'S5720' in model_of_router:
                switch_vendor = 'hp_comware'
                print(switch_vendor)
        return switch_vendor
    except netmiko.ssh_exception.NetMikoAuthenticationException:
        print()
    except netmiko.ssh_exception.NetMikoTimeoutException:
        print('Network is unreachable')
    except UnboundLocalError:
        print('Network is unreachable')


switch_vendor = check_switch_connction(check_switch_device)
print('switch_vendor is ' + switch_vendor)

switch_device = {
    "device_type": switch_vendor,
    "ip": switch_ip,
    "username": d_name,
    "password": d_pass,
    "timeout": 120,
}


def add_switch_command(switch_device):
    """Функция создает на свитче vlan2 и
     добавляет в него указанные порты"""
    try:
        with ConnectHandler(**switch_device) as ssh:
            model_of_router = ssh.find_prompt()
            print(model_of_router)
            if 'hp_comware' in switch_vendor:
                sw_intf = 'int eth1/0/'
                intf_commands_temp = [f'des temp_BO_{sap}',
                                      'port access vlan 2']
                save_command = 'save force'
                show_mac = 'dis mac-ad'
            if 'hp_comware' in switch_vendor and 'S5720' in model_of_router:
                sw_intf = 'int GigabitEthernet0/0/'
                intf_commands_temp = [f'des temp_BO_{sap}',
                                      'port default vlan 2',
                                      'undo  port-security enable']
                save_command = ['return', 'save', 'y']
                show_mac = 'dis mac-ad'
            if 'hp_procurve' in switch_vendor:
                sw_intf = 'int '
                intf_commands_temp = [f'name temp_BO_{sap}',
                                      'untagged vlan 2']
                save_command = 'save'
                show_mac = 'show mac-ad'
            if 'cisco_ios' in switch_vendor:
                sw_intf = 'int fa0/'
                intf_commands_temp = [f'des temp_BO_{sap}',
                                      'switchport access vlan 2',
                                      'no switchport port-security maximum 3',
                                      'no switchport port-security violation  restrict',
                                      'no switchport port-security aging time 2',
                                      'no switchport port-security aging type inactivity',
                                      'no switchport port-security',
                                      'no storm-control broadcast level pps 200',
                                      'no storm-control multicast level pps 200',
                                      'no storm-control action shutdown',
                                      'no storm-control action trap',
                                      'ip dhcp snooping trust']
                save_command = 'do wr'
                show_mac = 'show mac ad'
            vlan_commands = ['vlan 2', f'name temp_BO_{sap}']
            intf_24 = ['int 24', 'tagged vlan 2', 'exit']
            add_commands = []
            intf_commands = []
            secur_commands = []
            for intf in port_list:
                line = sw_intf + intf
                intf_commands.append(line)
                if 'hp_procurve' in switch_vendor:
                    line = f'no port-security {intf}'
                    secur_commands.append(line)
                    line = f'no spanning-tree {intf} admin-edge-port'
                    secur_commands.append(line)
                for line in intf_commands_temp:
                    intf_commands.append(line)
            for line in vlan_commands:
                add_commands.append(line)
            for line in intf_commands:
                add_commands.append(line)
            if 'hp_procurve' in switch_vendor:
                for line in intf_24:
                    add_commands.append(line)
                for line in secur_commands:
                    add_commands.append(line)
            send_add_commands = ssh.send_config_set(add_commands)
            save_command_send = ssh.send_config_set(save_command)
            send_show_mac = ssh.send_config_set(show_mac)
            result = send_add_commands.split('\n')
            for line in result:
                print(line)
            print(save_command_send)
            print(send_show_mac)
            # print(send_add_commands)
        return result
    except netmiko.ssh_exception.NetMikoAuthenticationException:
        print()
    except netmiko.ssh_exception.NetMikoTimeoutException:
        print('TimeoutExpired')
    except UnboundLocalError:
        print('Network is unreachable')


result = add_switch_command(switch_device)
print(result)
