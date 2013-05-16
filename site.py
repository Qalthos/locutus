from flask import Flask
app = Flask(__name__)

@app.route('/')
def index():
    return 'welcome to flask'

@app.route('/uptime')
def uptime():
    import uprecord
    records, total = uprecord.read_file('/var/log/uptimed/records')
    chart = uprecord.graph_records({'localhost': records})
    return chart

if __name__ == '__main__':
    app.run()
