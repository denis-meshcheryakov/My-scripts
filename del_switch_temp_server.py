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


def del_switch_command(switch_device):
    """Функция удаляет на свитче vlan2
    и переводит порты в default"""
    try:
        with ConnectHandler(**switch_device) as ssh:
            model_of_router = ssh.find_prompt()
            print(model_of_router)
            if 'hp_comware' in switch_vendor:
                sw_intf = 'int eth1/0/'
                show_intf_brie = 'display interface brief'
                del_vlan2 = 'undo vlan 2'
                default_intf_temp = ['default', 'y']
                save_command = 'save force'
                show_mac = 'dis mac-ad'
            if 'S5720' in model_of_router and 'S5720'  in model_of_router:
                sw_intf = 'int GigabitEthernet0/0/'
                show_intf_brie = 'display interface brief'
                del_vlan2 = 'undo vlan 2'
                default_intf_temp = ['default', 'y']
                save_command = ['return', 'save', 'y']
                show_mac = 'dis mac-ad'
            if 'hp_procurve' in switch_vendor:
                sw_intf = 'int '
                show_intf_brie = 'show interfaces status'
                del_vlan2 = 'no vlan 2'
                default_intf_temp = ['no name', 'untagged vlan 1', ]
                show_intf_brie = 'show interfaces status'
                save_command = 'save'
                show_mac = 'show mac-ad'
            if 'cisco_ios' in switch_vendor:
                sw_intf = 'int fa0/'
                show_intf_brie = 'do show interfaces status'
                del_vlan2 = 'no vlan 2'
                default_intf_temp = ['no description', 'switchport access vlan 1',
                                     'switchport port-security maximum 3',
                                     'switchport port-security violation  restrict',
                                     'switchport port-security aging time 2',
                                     'switchport port-security aging type inactivity',
                                     'switchport port-security',
                                     'storm-control broadcast level pps 200',
                                     'storm-control multicast level pps 200',
                                     'storm-control action shutdown',
                                     'storm-control action trap',
                                     'no ip dhcp snooping trust']
                save_command = 'do wr'
                show_mac = 'show mac ad'
            intf_24_default = ['int 24', 'no tagged vlan 2', 'exit']
            intf_brie_output = ssh.send_config_set(show_intf_brie)
            # pprint(intf_brie_output)
            default_port_list = []
            for line in intf_brie_output.split('\n'):
                if 'temp_' in line:
                    # print(line)
                    wanted_intf = line.split()[0]
                    default_port_list.append(wanted_intf)
            pprint(default_port_list)
            default_commands = []
            default_intf_commands = []
            default_secur_commands = []
            for intf in default_port_list:
                line = 'interface ' + intf
                default_intf_commands.append(line)
                if 'hp_procurve' in switch_vendor:
                    line = f'port-security {intf}'
                    default_secur_commands.append(line)
                    line = f'spanning-tree {intf} admin-edge-port'
                    default_secur_commands.append(line)
                for line in default_intf_temp:
                    default_intf_commands.append(line)
            default_commands.append(del_vlan2)
            for line in default_intf_commands:
                default_commands.append(line)
            if 'hp_procurve' in switch_vendor:
                for line in intf_24_default:
                    default_commands.append(line)
                for line in default_secur_commands:
                    default_commands.append(line)
            # default_commands.append(save_command_send)
            send_default_commands = ssh.send_config_set(default_commands)
            save_command_send = ssh.send_config_set(save_command)
            send_show_mac = ssh.send_config_set(show_mac)
            result = send_default_commands.split('\n')
            for line in result:
                print(line)
            print(save_command_send)
            print(send_show_mac)
            # print(send_default_commands)
        return result
    except netmiko.ssh_exception.NetMikoAuthenticationException:
        print()
    except netmiko.ssh_exception.NetMikoTimeoutException:
        print('TimeoutExpired')
    except UnboundLocalError:
        print('Network is unreachable')

result = del_switch_command(switch_device)
print(result)