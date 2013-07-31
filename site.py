from __future__ import print_function, unicode_literals
from datetime import datetime
from urllib import urlretrieve

from flask import Flask, request, render_template

import graphs
import uprecord
app = Flask(__name__)
sites = ['locutus.131.countess', 'tron.131.countess', 'media_pi.131.countess', 'retro_pi.131.countess', 'foss.rit.edu', 'yacht.rit.edu']
target_processes = ['minecraft', 'minidlna', 'tf2', 'znc']


@app.route('/')
def index():
    import psutil
    try:
        running = dict(map(lambda x: (x, False), target_processes))
        for p in psutil.process_iter():
            if p.name == 'java' and p.cmdline[-1] == 'craftbukkit.jar':
                running['minecraft'] = True
            elif p.name in ['znc', 'minidlna']:
                running[p.name] = True
            elif p.name == 'tmux':
                cmd = p.cmdline
                if len(cmd) == 5 and cmd[3] == 'srcds':
                    running['Team Fortress 2'] = True
        text = render_template('index.html', running=running)
    except Exception as e:
        text = str(running)
    return text


@app.route('/uptime')
def uptime():
    since = request.args.get('since')
    if since:
        try:
            since = since.split('-')
            since = datetime(year=int(since[0]), month=int(since[1]),
                             day=int(since[2]))
        except:
            since = None

    exclude = request.args.get('exclude', [])
    if exclude:
        try:
            exclude = exclude.split(',')
        except:
            exclude = []

    return graphs.graph_uptime(cache_and_sort(exclude, since, key=1))


@app.route('/records')
def records():
    sort = request.args.get('sort')
    sortable = ['big', 'new']
    try:
        key = sortable.index(sort)
    except ValueError:
        key = 0

    records = cache_and_sort(key=key)

    limit = request.args.get('limit')
    if limit:
        try:
            limit = int(limit)
            for name in records:
                # only look at the $limit most recent records
                records[name] = records[name][:limit]
        except:
            pass

    return graphs.graph_records(records)


def cache_and_sort(exclude='', since=None, key=1):
    records_dict = dict()
    for hostname in filter(lambda x: x not in exclude, sites):
        try:
            local_copy = urlretrieve('http://{}/uptimed/records'.format(hostname), '/tmp/{}_records'.format(hostname))[0]
        except:
            continue
        records = uprecord.read_file(local_copy)[0]
        if since:
            records = filter(lambda x: x[1] > since, records)
        records_dict[hostname] = sorted(records, key=lambda x: x[key],
                                        reverse=not key)

    return records_dict


if __name__ == '__main__':
    app.debug = True
    app.run(host='0')
