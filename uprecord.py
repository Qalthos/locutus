#!/usr/bin/env python
from __future__ import print_function, unicode_literals

from datetime import datetime, timedelta

def fill_print(index, uptime, boot, kernel, bold=False):
    index = str(index).rjust(6)
    uptime = str(uptime).rjust(20)
    kernel = kernel.strip().ljust(24)[:24]
    if isinstance(boot, datetime):
        boot = boot.strftime('%a %b %d %H:%M:%S %Y')
    boot = boot.rjust(24)
    if bold:
        print('\033[1m{} {} \033[0m|\033[1m {}  {}\033[0m'.format(index, uptime, kernel, boot))
    else:
        print('{} {} | {}  {}'.format(index, uptime, kernel, boot))

def show_details(records, newest, oldest, total):
    print('-'*28+'+'+'-'*51)
    now = datetime.now().replace(microsecond=0)
    newest_index = records.index(newest)
    newest = newest[0]
    if not newest == records[0][0]:
        time_until = records[newest_index-1][0] - newest
        fill_print('1up in', time_until, now+time_until, 'at')
    if newest not in [record[0] for record in records[:10]]:
        time_until = records[9][0] - newest
        fill_print('t10 in', time_until, now+time_until, 'at')
    if not newest == records[0][0]:
        time_until = records[0][0] - newest
        fill_print('no1 in', time_until, now+time_until, 'at')

    fill_print('up', total, oldest, 'since')
    total_down = now-oldest-total
    fill_print('down', total_down, oldest, 'since')
    percent_up = total.total_seconds()/(total+total_down).total_seconds() * 100
    fill_print('%up', '%.3f' % percent_up, oldest, 'since')

def print_records(records, newest):
    fill_print('#', 'Uptime', 'Boot up', 'System')
    print('-'*28+'+'+'-'*51)
    newest_index = records.index(newest)
    for index, row in enumerate(records[:10]):
        if index == newest_index:
            index = '->' + str(index+1).rjust(4)
        else:
            index = index+1
        fill_print(index, *row)

    if index < newest_index:
        print('-'*28+'+'+'-'*51)
        fill_print('->' + str(newest_index).rjust(4), *newest, bold=True)

def read_file(filename):
    records = []
    total = timedelta()
    with open(filename) as record_file:
        for index, line in enumerate(record_file):
            record_tuple = line.split(':', 2)
            record_tuple[0] = timedelta(seconds=int(record_tuple[0]))
            record_tuple[1] = datetime.fromtimestamp(int(record_tuple[1]))
            records.append(record_tuple)
            total += record_tuple[0]
    return records, total

if __name__ == '__main__':
    records, total = read_file('/var/spool/uptimed/records')
    newest = max(records, key=lambda x: x[1])
    oldest = min(records, key=lambda x: x[1])
    print_records(records, newest)
    show_details(records, newest, oldest[1], total)
