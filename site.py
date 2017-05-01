from __future__ import print_function, unicode_literals
from datetime import datetime
import logging
try:
    from urllib.request import urlretrieve
except ImportError:
    from urllib import urlretrieve

from flask import Flask, request, render_template

from locutus import graphs, uprecord


app = Flask(__name__)
# For debugging
app.config['PROPAGATE_EXCEPTIONS'] = True
sites = [
    'locutus', 'tron', 'luna', 'chibiusa',
]
target_processes = ['minecraft', 'minidlna', 'tf2', 'znc']


@app.route('/')
def index():
    import psutil
    running = dict(map(lambda x: (x, False), target_processes))
    for p in psutil.process_iter():
        name = p.name()
        if name == 'java' and p.username() == 'minecraft':
            running['minecraft'] = True
        elif name == 'tf2server':
            running['tf2'] = True
        elif name in ['znc', 'minidlna']:
            running[name] = True
    try:
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

    records = cache_and_sort(key=key, reverse=True)

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


def cache_and_sort(exclude='', since=None, key=1, reverse=False):
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
                                        reverse=reverse)

    return records_dict


if __name__ == '__main__':
    app.debug = True
    app.run(host='0')
