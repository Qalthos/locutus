from __future__ import print_function, unicode_literals
from datetime import datetime
from urllib.request import urlretrieve

from flask import Flask, request, render_template

from locutus import graphs, uprecord


app = Flask(__name__)
# For debugging
app.config['PROPAGATE_EXCEPTIONS'] = True
sites = [
    'locutus', 'tron', 'luna', 'chibiusa',
]
target_processes = {
    'spigot.jar': 'minecraft',
    'Plex Media Server': 'plex',
    'tf2server': 'tf2',
    'znc': 'znc',
}


@app.route('/')
def index():
    import psutil
    running = {x: False for x in target_processes.values()}
    for p in psutil.process_iter():
        name = p.name()
        if name == 'java' and p.cmdline()[-2] == 'spigot.jar':
            running['minecraft'] = True
        elif name in target_processes:
            running[target_processes[name]] = True
    try:
        text = render_template('index.html', running=running)
    except Exception:
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
        except Exception:
            since = None

    exclude = request.args.get('exclude', [])
    if exclude:
        try:
            exclude = exclude.split(',')
        except Exception:
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

    records = cache_and_sort(key=key, reverse=True)

    limit = request.args.get('limit')
    if limit:
        try:
            limit = int(limit)
            for name in records:
                # only look at the $limit most recent records
                records[name] = records[name][:limit]
        except Exception:
            pass

    return graphs.graph_records(records)


def cache_and_sort(exclude='', since=None, key=1, reverse=False):
    records_dict = dict()
    for hostname in filter(lambda x: x not in exclude, sites):
        try:
            local_copy = urlretrieve(
                'http://{}/uptimed/records'.format(hostname),
                '/tmp/{}_records'.format(hostname)
            )[0]
        except Exception:
            continue
        records = uprecord.read_file(local_copy)[0]
        if since:
            records = filter(lambda x: x[1] > since, records)
        records_dict[hostname] = sorted(records, key=lambda x: x[key],
                                        reverse=reverse)

    return records_dict


if __name__ == '__main__':
    app.debug = True
    app.run(host='0')
