#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  "add_gtnt_v2.py"
#
network = input('Введите адрес сети с префиксом(Например 10.1.1.0/30):')
number_of_mag = input('Введите номер магазина: ')
ip, _ = network.split('/')
ip = ip.split('.')
oct1 = int(ip[0])
oct2 = int(ip[1])
oct3 = int(ip[2])
oct4 = 1 + (int(ip[3]))
oct5 = 1 + (int(oct4))
ce_ip = [str(oct1), str(oct2), str(oct3), str(oct4)]
ce_ip = '.'.join(ce_ip)
pe_ip = [str(oct1), str(oct2), str(oct3), str(oct5)]
pe_ip = '.'.join(pe_ip)

src_file_930 = '/var/share/config/rt-{}.hp-msr930.txt'.format(number_of_mag)
src_file_880 = '/var/share/config/rt-{}.cisco-880.txt'.format(number_of_mag)
src_file_2800 = '/var/share/config/rt-{}.cisco-2800.txt'.format(number_of_mag)

result_lst_930 = []
result_lst_880 = []
result_lst_2800 = []

#  made config for hp-msr930
with open(src_file_930) as src:
    for line in src:
        line += '\r\n'
        if 'ip address 10.0.0.2' in line:
            line = line.replace('10.0.0.2', pe_ip)
            result_lst_930.append(line)
        elif 'peer 10.0.0.1' in line and '64996' in line:
            line = "peer {} as-number 65301\r\n".format(ce_ip)
            result_lst_930.append(line)
        elif 'peer 10.0.0.1' in line and '64995' in line:
            line = "peer {} fake-as 65524\r\n".format(ce_ip)
            result_lst_930.append(line)
        elif 'peer 10.0.0.1' in line:
            line = line.replace('10.0.0.1', ce_ip)
            result_lst_930.append(line)
        else:
            result_lst_930.append(line)
with open(src_file_930, 'w') as dest:
    dest.writelines(result_lst_930)

#  made config for cisco-880
with open(src_file_880) as src:
    for line in src:
        line += '\r\n'
        if 'ip address 10.0.0.2' in line:
            line = line.replace('10.0.0.2', pe_ip)
            result_lst_880.append(line)
        elif 'neighbor 10.0.0.1' in line and '64996' in line:
            line = "neighbor {} remote-as 65301\r\n".format(ce_ip)
            result_lst_880.append(line)
        elif 'neighbor 10.0.0.1' in line and '64995' in line:
            line = "neighbor {} local-as 65524\r\n".format(ce_ip)
            result_lst_880.append(line)
        elif 'neighbor 10.0.0.1' in line:
            line = line.replace('10.0.0.1', ce_ip)
            result_lst_880.append(line)
        else:
            result_lst_880.append(line)
with open(src_file_880, 'w') as dest:
    dest.writelines(result_lst_880)

#  made config for cisco-2800
with open(src_file_2800) as src:
    for line in src:
        line += '\r\n'
        if 'ip address 10.0.0.2' in line:
            line = line.replace('10.0.0.2', pe_ip)
            result_lst_2800.append(line)
        elif 'neighbor 10.0.0.1' in line and '64996' in line:
            line = "neighbor {} remote-as 65301\r\n".format(ce_ip)
            result_lst_2800.append(line)
        elif 'neighbor 10.0.0.1' in line and '64995' in line:
            line = "neighbor {} local-as 65524\r\n".format(ce_ip)
            result_lst_2800.append(line)
        elif 'neighbor 10.0.0.1' in line:
            line = line.replace('10.0.0.1', ce_ip)
            result_lst_2800.append(line)
        else:
            result_lst_2800.append(line)
with open(src_file_2800, 'w') as dest:
    dest.writelines(result_lst_2800)

print('''
<<<<<<<<<<----------------------->>>>>>>>>>
          CONFIG'S WITH GTNT DONE
<<<<<<<<<<_______________________>>>>>>>>>>
''')
