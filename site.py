from __future__ import print_function, unicode_literals
from datetime import datetime
from urllib import urlretrieve

from flask import Flask, request, render_template
app = Flask(__name__)
sites = ['tron', 'locutus']
target_processes = ['minecraft', 'Team Fortress 2', 'znc', 'minidlna']


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
    import uprecord

    since = request.args.get('since')
    if since:
        try:
            since = since.split('-')
            since = datetime(year=int(since[0]), month=int(since[1]),
                             day=int(since[2]))
        except:
            since = None

    records_dict = dict()
    for hostname in sites:
        try:
            local_copy = urlretrieve('http://{}/uptimed/records'.format(hostname), '/tmp/{}_records'.format(hostname))[0]
        except:
            continue
        records = uprecord.read_file(local_copy)[0]
        if since:
            records = filter(lambda x: x[1] > since, records)
        records_dict[hostname] = sorted(records, key=lambda x: x[1])

    chart = uprecord.graph_records(records_dict)
    return chart

if __name__ == '__main__':
    app.run()
