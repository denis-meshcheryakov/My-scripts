#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  "test_temp_server.py"
#


import ipaddress
import re
from pprint import pprint
from netmiko import ConnectHandler
import netmiko
from add_switch_temp_server import add_switch_command
from del_switch_temp_server import del_switch_command

action = int(input('''
Выберите небходимое действие:
1. Создать vlan 2 и прописать 2-е подсети
2. Добовить secondary подсеть
3. Удалить подсети
Выберите пункт (1-3):
'''))


def get_router_net():
    router_network = input('Введите подсеть роутера: ').strip()
    router_net = ipaddress.ip_network(router_network)
    router_ip = str(router_net[1])
    return router_ip


sap = ''


def get_sap():
    sap = input('Введите номер САП: ').strip()
    return sap


def get_port_number():
    port_number = input('''Введите номер порта/портов
через пробел в одну строку: ''')
    return port_number


def get_prime_net():
    prime_network = input('Введите основную подсеть: ').strip()
    prime_net = ipaddress.ip_network(prime_network)
    prime_net_addss = str(prime_net[0])
    prime_ip = str(prime_net[1])
    prime_ip_with_prefixlen = prime_net.with_prefixlen
    prime_just_prefixlen = prime_ip_with_prefixlen.split('/')[1]
    prime_mask = str(prime_net.netmask)
    return prime_net_addss, prime_ip, prime_ip_with_prefixlen, prime_just_prefixlen, prime_mask


def get_sub_net():
    sub_network = input('Введите secondary подсеть: ').strip()
    sub_net = ipaddress.ip_network(sub_network)
    sub_net_addss = str(sub_net[0])
    sub_ip = str(sub_net[1])
    sub_ip_with_prefixlen = sub_net.with_prefixlen
    sub_just_prefixlen = sub_ip_with_prefixlen.split('/')[1]
    sub_mask = str(sub_net.netmask)
    return sub_net_addss, sub_ip, sub_ip_with_prefixlen, sub_just_prefixlen, sub_mask


if action == 1:
    router_ip = get_router_net()
    sap = get_sap()
    port_list = get_port_number()
    prime_net_addss, prime_ip, prime_ip_with_prefixlen, prime_just_prefixlen, prime_mask = get_prime_net()
    sub_net_addss, sub_ip, sub_ip_with_prefixlen, sub_just_prefixlen, sub_mask = get_sub_net()
if action == 2:
    # router_ip =  get_router_net()
    prime_net_addss, prime_ip, prime_ip_with_prefixlen, prime_just_prefixlen, prime_mask = get_prime_net()
    sub_net_addss, sub_ip, sub_ip_with_prefixlen, sub_just_prefixlen, sub_mask = get_sub_net()
    router_ip = prime_ip
if action == 3:
    router_ip = get_router_net()
    prime_net_addss, prime_ip, prime_ip_with_prefixlen, prime_just_prefixlen, prime_mask = get_prime_net()
    sub_net_addss, sub_ip, sub_ip_with_prefixlen, sub_just_prefixlen, sub_mask = get_sub_net()

with open('accaunt.txt', 'r') as src:
    d_name, d_pass, l_name, l_pass = src.read().split()

cisco = {
    "device_type": "cisco_ios",
    "ip": router_ip,
    "username": l_name,
    "password": l_pass,
    "timeout": 120,
}

# d_pass = getpass()

cisco_dom = {
    "device_type": "cisco_ios",
    "ip": router_ip,
    "username": d_name,
    "password": d_pass,
    "timeout": 120,
}


def check_connction(cisco, cisco_dom, l_name, l_pass, d_name, d_pass):
    for device in (cisco, cisco_dom):
        try:
            with ConnectHandler(**device) as ssh:
                model_of_router = ssh.find_prompt()
                # print(model_of_router)
                if '930-RTR' in model_of_router:
                    vendor = 'hp_comware'
                    chek_routes = 'display current-configuration | i route-static'
                elif '2021-RTR' in model_of_router:
                    vendor = 'hp_comware'
                    chek_routes = 'display current-configuration | i route-static'
                else:
                    vendor = 'cisco_ios'
                    chek_routes = 'sh run | i ip route'
                routes = ssh.send_command(chek_routes)
                # print(routes)
                if '192.168.180.193' in routes:
                    u_name = l_name
                    pass_d = l_pass
                else:
                    u_name = d_name
                    pass_d = d_pass
            return vendor, u_name, pass_d
        except netmiko.ssh_exception.NetMikoAuthenticationException:
            print()
        except netmiko.ssh_exception.NetMikoTimeoutException:
            print('Network is unreachable')
        except UnboundLocalError:
            print('Network is unreachable')


vendor, u_name, pass_d = check_connction(cisco, cisco_dom, l_name, l_pass, d_name, d_pass)
print(vendor)
# model_of_rtr = model_of_router

device = {
    "device_type": vendor,
    "ip": router_ip,
    "username": u_name,
    "password": pass_d,
    "timeout": 120,
}


def send_command(device, vendor):
    try:
        with ConnectHandler(**device) as ssh:
            # vendor = ssh.find_prompt()
            if 'hp_comware' in vendor:
                sh_version = 'display version'
            else:
                sh_version = 'show version'
            chek_version = ssh.send_command(sh_version)
            chek_version = chek_version.split('\n')
            print(vendor)
            for line in chek_version:
                if line.startswith('Comware Software'):
                    vendor = 'hp_comware'
                if 'MSR930' in line:
                    rtr_model = 'MSR_930'
                if 'MSR20-21' in line:
                    rtr_model = 'MSR_2021'
                if line.startswith('Cisco IOS Software'):
                    vendor = 'cisco_ios'
                if 'C880 Software' in line:
                    rtr_model = 'C_880'
                if 'C800 Software' in line:
                    rtr_model = 'C_800'
                if '1841 Software' in line:
                    rtr_model = 'C_1841'
                if '2801 Software' in line:
                    rtr_model = 'C_2801'
                if '2900 Software' in line:
                    rtr_model = 'C_2901'
            print(rtr_model)
            if 'hp_comware' in vendor:
                chek_bgp_cmd = 'dis cur | i bgp'
                chek_prefix_cmd = 'dis cur | i prefix'
                prefix_point1 = 'ip ip-prefix'
                prefix_point2 = 'index'
                undo = 'undo '
                sub_address = f'ip address {sub_ip} {sub_mask} sub'
                secondary = 'sub'
                bgp_block_out = 'quit'
                mask_word = ''
                interface_brief = 'dis int brie'
                do_interface_brief = 'dis int brie'
                save_command = 'save force'
            else:
                chek_bgp_cmd = 'sh run | i bgp'
                chek_prefix_cmd = 'sh run | i prefix'
                prefix_point1 = 'ip prefix-list'
                prefix_point2 = 'seq'
                undo = 'no '
                sub_address = f'ip address {sub_ip} {sub_mask} secondary'
                secondary = 'secondary'
                bgp_block_out = 'exit'
                mask_word = 'mask'
                interface_brief = 'sh ip int brie'
                do_interface_brief = 'do sh ip int brie'
                save_command = 'wr'
            chek_bgp = ssh.send_command(chek_bgp_cmd)
            # print(chek_bgp)
            for line in chek_bgp.split('\n'):
                # print(line)
                if 'bgp 6' in line:
                    # print(line)
                    bgp_num = line
            # print(bgp_num)
            chek_prefix = ssh.send_command(chek_prefix_cmd)
            # print(chek_prefix)
            prefix_name = []
            for_undo_prefix = []
            for line in chek_prefix.split('\n'):
                if '-out' in line:
                    match = re.search(r'\S+ \S+ (\S+-out).*', line)
                    m = match.group(1)
                    prefix_name.append(m)
                if prime_net_addss in line:
                    for_undo_prefix.append(line)
                if sub_net_addss in line:
                    for_undo_prefix.append(line)
            prefix_name = set(prefix_name)
            print(prefix_name)
            prefix_name_len = len(prefix_name)
            print(prefix_name_len)
            pprint(for_undo_prefix)
            undo_f_pref = ''
            undo_s_pref = ''
            undo_f_pref_2 = ''
            undo_s_pref_2 = ''
            undo_f_pref_3 = ''
            undo_s_pref_3 = ''
            undo_prefix = []
            if action == 3:
                for line in for_undo_prefix:
                    if 'hp_comware' in vendor:
                        match = re.search(r'(\S+ \S+ \S+-out \S+ \d+).*', line)
                        line = match.group(1)
                        line = undo + line
                        undo_prefix.append(line)
                    else:
                        line = undo + line
                        undo_prefix.append(line)
                print('undo_prefix len is:')
                pprint(len(undo_prefix))
                print('undo_prefix is:')
                pprint(undo_prefix)

                undo_f_pref, undo_s_pref = undo_prefix[0], undo_prefix[1]
                if len(for_undo_prefix) >= 4:
                    undo_f_pref_2, undo_s_pref_2 = undo_prefix[2], undo_prefix[3]
                if len(for_undo_prefix) >= 6:
                    undo_f_pref_3, undo_s_pref_3 = undo_prefix[4], undo_prefix[5]
            f_name, *s_name = prefix_name
            s_name = ''.join(s_name)
            pprint(f_name)
            pprint(s_name)
            pref3 = ''
            pref4 = ''
            pref5 = ''
            pref6 = ''
            if 'hp_comware' in vendor:
                pref1 = f'{prefix_point1} {f_name} {prefix_point2} 2 permit {prime_net_addss} {prime_just_prefixlen}'
                pref2 = f'{prefix_point1} {f_name} {prefix_point2} 3 permit {sub_net_addss} {sub_just_prefixlen}'
            if 'hp_comware' in vendor and prefix_name_len == 2:
                pref3 = f'{prefix_point1} {s_name} {prefix_point2} 2 permit {prime_net_addss} {prime_just_prefixlen}'
                pref4 = f'{prefix_point1} {s_name} {prefix_point2} 3 permit {sub_net_addss} {sub_just_prefixlen}'
            if 'hp_comware' in vendor and prefix_name_len == 3:
                pref5 = f'{prefix_point1} {s_name} {prefix_point2} 2 permit {prime_net_addss} {prime_just_prefixlen}'
                pref6 = f'{prefix_point1} {s_name} {prefix_point2} 3 permit {sub_net_addss} {sub_just_prefixlen}'
            if 'cisco_ios' in vendor:
                pref1 = f'{prefix_point1} {f_name} {prefix_point2} 2 permit {prime_ip_with_prefixlen}'
                pref2 = f'{prefix_point1} {f_name} {prefix_point2} 3 permit {sub_ip_with_prefixlen}'
            if 'cisco_ios' in vendor and prefix_name_len == 2:
                pref3 = f'{prefix_point1} {s_name} {prefix_point2} 2 permit {prime_ip_with_prefixlen}'
                pref4 = f'{prefix_point1} {s_name} {prefix_point2} 3 permit {sub_ip_with_prefixlen}'
            if 'cisco_ios' in vendor and prefix_name_len == 3:
                pref5 = f'{prefix_point1} {s_name} {prefix_point2} 2 permit {prime_ip_with_prefixlen}'
                pref6 = f'{prefix_point1} {s_name} {prefix_point2} 3 permit {sub_ip_with_prefixlen}'
            pprint(undo_f_pref)
            pprint(undo_s_pref)
            pprint(undo_f_pref_2)
            pprint(undo_s_pref_2)
            pprint(pref1)
            pprint(pref2)
            pprint(pref3)
            pprint(pref4)
            pprint(pref5)
            pprint(pref6)

            vlan_name = f'name temp_BO_{sap}'
            description = f'des temp_BO_{sap}'

            # encapsulation = ''
            # if 'C_2801' in rtr_model:
            #    vlan2 = ''
            #    vlan_name = ''
            #    int_vlan2 = 'interface {vlan2_intf}.2'
            #    encapsulation = 'encapsulation dot1Q 2'
            # if 'C_2901' in rtr_model:
            #    vlan2 = ''
            #    vlan_name = ''
            #    int_vlan2 = f'interface {vlan2_intf}.2'
            #    encapsulation = 'encapsulation dot1Q 2'
            # if 'C_800' in rtr_model:
            #    vlan2 = ''
            #    vlan_name = ''
            #    int_vlan2 = 'int Vlan 1'
            #    description = ''
            # else:
            #    vlan2 = 'Vlan 2'
            #    int_vlan2 = 'int Vlan 2'

            interface_brief_output = ssh.send_command(interface_brief)
            print(interface_brief_output)

            for line in interface_brief_output.split('\n'):
                if not line.startswith('NVI0') and prime_ip in line or sub_ip in line:
                    pprint(line)
                    wanted_intf = 'int ' + line.split()[0]
                # if not line.startswith('NVI0') and router_ip in line:
                #    vlan2_intf = line.split()[0]
                else:
                    if router_ip in line and not line.startswith('NVI0'):
                        wanted_intf = 'int ' + line.split()[0]
                if not line.startswith('NVI0') and router_ip in line:
                    vlan2_intf = line.split()[0]
            print('wanted_intf is ' + wanted_intf)
            print(vlan2_intf)

            prime_address = f'ip address {prime_ip} {prime_mask}'
            prime_net_bgp = f'network {prime_net_addss} {mask_word} {prime_mask}'
            print(prime_net_bgp)
            sub_net_bgp = f'network {sub_net_addss} {mask_word} {sub_mask}'
            print(sub_net_bgp)

            encapsulation = ''
            if 'C_2801' in rtr_model or 'C_1841' in rtr_model:
                vlan2 = ''
                vlan_name = ''
                int_vlan2 = f'interface {vlan2_intf}.2'
                encapsulation = 'encapsulation dot1Q 2'
            if 'C_2901' in rtr_model:
                vlan2 = ''
                vlan_name = ''
                int_vlan2 = f'interface {vlan2_intf}.2'
                encapsulation = 'encapsulation dot1Q 2'
            if 'C_800' in rtr_model:
                vlan2 = ''
                vlan_name = ''
                int_vlan2 = 'int Vlan 1'
                description = ''
                prime_address = f'ip address {prime_ip} {prime_mask} {secondary}'
            if 'C_880' in rtr_model or 'MSR_930' in rtr_model:
                vlan2 = 'Vlan 2'
                int_vlan2 = 'int Vlan 2'
            print(int_vlan2)

            if 'C_880' in rtr_model:
                sh_arp = 'do sh arp ' + wanted_intf
            elif 'C_2801' in rtr_model or 'C_1841' in rtr_model:
                sh_arp = 'do sh arp | i ' + wanted_intf
            else:
                sh_arp = 'dis arp ' + wanted_intf
            # print(save_command)

            if action == 1:
                commands_template = [vlan2, vlan_name, int_vlan2, encapsulation, description,
                                     prime_address, sub_address, bgp_num, prime_net_bgp, sub_net_bgp,
                                     bgp_block_out, pref1, pref2, pref3, pref4, do_interface_brief]
            if action == 2:
                commands_template = [wanted_intf, sub_address, bgp_num,
                                     sub_net_bgp, bgp_block_out, pref2, pref4, do_interface_brief]
            if action == 3 and '2' in wanted_intf:
                commands_template = [undo + vlan2, undo + int_vlan2, bgp_num,
                                     undo + prime_net_bgp, undo + sub_net_bgp, bgp_block_out,
                                     undo_f_pref, undo_s_pref, undo_f_pref_2, undo_s_pref_2,
                                     do_interface_brief]
            if action == 3 and '2' not in wanted_intf:
                commands_template = [wanted_intf, undo + prime_address + ' secondary', undo + sub_address, bgp_num,
                                     undo + prime_net_bgp, undo + sub_net_bgp, bgp_block_out,
                                     undo_f_pref, undo_s_pref, undo_f_pref_2, undo_s_pref_2,
                                     undo_f_pref_3, undo_s_pref_3, do_interface_brief]
            commands = ssh.send_config_set(commands_template)
            print(commands)
            save_command_send = ssh.send_command(save_command)
            print(save_command_send)

            # получаем ip-адрес свича
            for line in interface_brief_output.split('\n'):
                if not line.startswith(
                        'NVI0') and 'Vlan30' in line or 'FastEthernet0/1.30' in line or 'FastEthernet0/0.30' in line or "GigabitEthernet0/1.30" in line or 'GigabitEthernet0/0.30' in line:  # print(line)
                    if 'hp_comware' in vendor:
                        true_line = line.split()[3]
                        # print(true_line )
                    else:
                        true_line = line.split()[1]
                    # print(true_line)
            switch_ip = ipaddress.ip_address(true_line)
            switch_ip += 1
            # print(switch_ip)
        # return commands_template, switch_ip
        return switch_ip
    except netmiko.ssh_exception.NetMikoAuthenticationException:
        print('Authentication Failure')
    except netmiko.ssh_exception.NetMikoTimeoutException:
        print('Network is unreachable')


switch_ip = send_command(device, vendor)
switch_ip = str(switch_ip)
print()
pprint('switch_ip is ' + switch_ip)
pprint('ports: ' + port_list)


if action == 1:
    activate = add_switch_command(switch_device)
if action == 3:
    activate = del_switch_command(switch_device)
