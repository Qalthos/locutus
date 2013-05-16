from flask import Flask
from urllib import urlretrieve

app = Flask(__name__)

@app.route('/')
def index():
    return 'welcome to flask'

@app.route('/uptime')
def uptime():
    import uprecord

    records_dict = dict()
    records = uprecord.read_file('/var/log/uptimed/records')[0]
    records_dict['localhost'] = sorted(records, key=lambda x: x[1])
    for hostname in ['tron', 'locutus']:
        local_copy = urlretrieve('http://' + hostname + '/uptimed/records', hostname)[0]
        records = uprecord.read_file(local_copy)[0]
        records_dict[hostname] = sorted(records, key=lambda x: x[1])

    chart = uprecord.graph_records(records_dict)
    return chart

if __name__ == '__main__':
    app.run()
