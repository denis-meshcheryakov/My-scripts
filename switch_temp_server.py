#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  "switch_temp_server.py"
#
import ipaddress
import re
from pprint import pprint
from netmiko import ConnectHandler
import netmiko

action = int(input('Введите action: '))
switch_ip = input('Введите адрес свича: ')
if action == 1:
    sap = input('Введите САП: ')
    port_number = input('Введите номер порта: ')
    port_list = port_number.split()

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


def send_switch_command(switch_device):
    try:
        with ConnectHandler(**switch_device) as ssh:
            model_of_router = ssh.find_prompt()
            print(model_of_router)
            if 'S5720' in model_of_router:
                sw_intf = 'int GigabitEthernet0/0/'
                if action == 1:
                    intf_commands_temp = [f'des temp_BO_{sap}',
                                          'port default vlan 2',
                                          'undo  port-security enable']
                show_intf_brie = 'display interface brief'
                del_vlan2 = 'undo vlan 2'
                default_intf_temp = ['default', 'y']
                save_command = ['return', 'save', 'y']
            if 'hp_comware' in switch_vendor and 'S5720' not in model_of_router:
                sw_intf = 'int eth1/0/'
                if action == 1:
                    intf_commands_temp = [f'des temp_BO_{sap}',
                                          'port access vlan 2']
                show_intf_brie = 'display interface brief'
                del_vlan2 = 'undo vlan 2'
                default_intf_temp = ['default', 'y']
                save_command = 'save force'
            if 'hp_procurve' in switch_vendor:
                sw_intf = 'int '
                if action == 1:
                    intf_commands_temp = [f'name temp_BO_{sap}',
                                          'untagged vlan 2']
                show_intf_brie = 'show interfaces status'
                del_vlan2 = 'no vlan 2'
                default_intf_temp = ['no name', 'untagged vlan 1', ]
                show_intf_brie = 'show interfaces status'
                save_command = 'save'
            if 'cisco_ios' in switch_vendor:
                sw_intf = 'int fa0/'
                if action == 1:
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

            # if action == 3
            # intf_brie_output = ssh.send_config_set(show_int_brie)
            # pprint(intf_brie_output)
            # default_port_list = []
            # for line in intf_brie_output.split('\n'):
            #    if 'temp_' in line:
            #        #print(line)
            #        wanted_intf = line.split()[0]
            #        default_port_list.append(wanted_int)
            # pprint(default_port_list)

            # pprint(vlan_commands)
            intf_24 = ['int 24', 'tagged vlan 2', 'exit']
            intf_24_default = ['int 24', 'no tagged vlan 2', 'exit']

            if action == 1:
                vlan_commands = ['vlan 2', f'name temp_BO_{sap}']
                add_commands = []
                intf_commands = []
                secur_commands = []
                for intf in port_list:
                    line = sw_intf + intf
                    intf_commands.append(line)
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
                # add_commands.append(save_command_send)
                send_add_commands = ssh.send_config_set(add_commands)
                save_command_send = ssh.send_config_set(save_command)
                result = send_add_commands.split('\n')
                for line in result:
                    print(line)
                print(save_command_send)
                # print(send_add_commands)

            if action == 3:
                intf_brie_output = ssh.send_config_set(show_intf_brie)
                # pprint(intf_brie_output)
                default_port_list = []
                for line in intf_brie_output.split('\n'):
                    if 'temp' in line:
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
                result = send_default_commands.split('\n')
                for line in result:
                    print(line)
                print(save_command_send)
                # print(send_default_commands)

            # pprint(add_commands)
            # pprint(default_commands)
            # if action == 1:
            #    send_add_commands = ssh.send_config_set(add_commands)
            #    print(send_add_commands)
            # if action == 3:
            #    send_default_commands = ssh.send_config_set(default_commands)
            #    print(send_default_commands)
        return
    except netmiko.ssh_exception.NetMikoAuthenticationException:
        print()
    except netmiko.ssh_exception.NetMikoTimeoutException:
        print('TimeoutExpired')
    except UnboundLocalError:
        print('Network is unreachable')


out = send_switch_command(switch_device)
