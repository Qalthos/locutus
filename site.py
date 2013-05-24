from datetime import datetime
from urllib import urlretrieve

from flask import Flask, request
app = Flask(__name__)
sites = ['tron', 'locutus']

@app.route('/')
def index():
    return 'welcome to flask'

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
    records = uprecord.read_file('/var/log/uptimed/records')[0]
    if since:
        records = filter(lambda x: x[1] > since, records)
    records_dict['localhost'] = sorted(records, key=lambda x: x[1])
    for hostname in sites:
        local_copy = urlretrieve('http://{}/uptimed/records'.format(hostname), '/tmp/{}_records'.format(hostname))[0]
        records = uprecord.read_file(local_copy)[0]
        if since:
            records = filter(lambda x: x[1] > since, records)
        records_dict[hostname] = sorted(records, key=lambda x: x[1])

    chart = uprecord.graph_records(records_dict)
    return chart

if __name__ == '__main__':
    app.run()
