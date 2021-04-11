# from pprint import pprint
#
prime_address = '10.10.10.1'
wanted_intf = 'vlan1'
if '2' not in wanted_intf:
    prime_address = prime_address + ' secondary'
print(prime_address)
# switch_vendor = 'hp_procurve'
# sap = 'X333'
# port_number = '10'
# port_list = port_number.split()
# # print(port_list)
#
# if 'hp_comware' in switch_vendor:
#     sw_intf = 'int eth1/0/'
#     intf_commands_temp = [f'des temp_BO_{sap}', 'port access vlan 2']
#     save_command = 'save force'
# if 'hp_procurve' in switch_vendor:
#     sw_intf = 'int '
#     intf_commands_temp = [f'name temp_BO_{sap}', 'untagged vlan 2', 'exit']
#     save_command = 'save'
# if 'cisco_ios' in switch_vendor:
#     sw_intf = 'int fa0/'
#     intf_commands_temp = [f'des temp_BO_{sap}', 'switchport access vlan 2',
#                           'no switchport port-security maximum 3',
#                           'no switchport port-security violation  restrict',
#                           'no switchport port-security aging time 2',
#                           'no switchport port-security aging type inactivity',
#                           'no switchport port-security',
#                           'no storm-control broadcast level pps 200',
#                           'no storm-control multicast level pps 200',
#                           'no storm-control action shutdown',
#                           'no storm-control action trap',
#                           'ip dhcp snooping trust']
#     save_command = 'do wr'
# commands = []
# vlan_commands = ['vlan 2', f'name temp_BO_{sap}']
# # pprint(vlan_commands)
# intf_24 = ['int 24', 'tagged vlan 2']
#
# intf_commands = []
# secur_commands = []
# for intf in port_list:
#     line = sw_intf + intf
#     intf_commands.append(line)
#     if 'hp_procurve' in switch_vendor:
#         line = f'no port-security {intf}'
#         secur_commands.append(line)
#         line = f'no spanning-tree {intf} admin-edge-port'
#         secur_commands.append(line)
#     for line in intf_commands_temp:
#         intf_commands.append(line)
#
# for line in vlan_commands:
#     commands.append(line)
# for line in intf_commands:
#     commands.append(line)
# if 'hp_procurve' in switch_vendor:
#     for line in intf_24:
#         commands.append(line)
#     for line in secur_commands:
#         commands.append(line)
# commands.append(save_command)
#
# pprint(commands)
#
# # pprint(intf_commands)
# # pprint(intf_24)
# # pprint(secur_commands)
#
# '''
# if 'hp_procurve' in switch_vendor:
#     vlan_commands_send = ssh.send_config_set(vlan_commands)
#     intf_commands_send = ssh.send_config_set(intf_commands)
#     intf_24_send = ssh.send_config_set(intf_24)
#     secur_commands_send = ssh.send_config_set(secur_commands)
#     save_command_send = ssh.send_command(save_command)
# else:
#     vlan_commands_send = ssh.send_config_set(vlan_commands)
#     intf_commands_send = ssh.send_config_set(intf_commands)
#     save_command_send = ssh.send_command(save_command)
# '''
