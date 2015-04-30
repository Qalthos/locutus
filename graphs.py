from __future__ import division

from datetime import timedelta

from pygal import Bar, Config, DateY


class BaseConfig(Config):
    def __init__(self, *a, **kw):
        super(BaseConfig, self).__init__(*a, **kw)
        self.print_values = False
        self.x_label_rotation = 20
        self.js = ['http://kozea.github.io/pygal.js/javascripts/svg.jquery.js',
                   'http://linkybook.com/static/uptime.js']


def sort_domains(list_of_tuples):
    # Sort the domains by increasing specificity.
    # Eg: host.dom.aaa comes before host.dom.bbb comes before xost.dom.bbb
    return sorted(list_of_tuples, key=lambda x: x[0].split('.')[::-1])


def graph_uptime(record_files):
    chart = DateY(BaseConfig)
    for name, record_list in sort_domains(record_files.items()):
        values = []
        up, down = timedelta(), timedelta()
        last = None
        for record in record_list:
            if last:
                down += record[1] - last
                values.append((record[1],
                               100 * up.total_seconds() /
                               (up+down).total_seconds()))
            else:
                values.append((record[1], 100))
            last = record[1] + record[0]
            up += record[0]
            values.append((record[1] + record[0],
                           100 * up.total_seconds() /
                           (up+down).total_seconds()))

        chart.add(name, values)
    return chart.render()

def graph_records(record_files):
    chart = Bar(BaseConfig)
    max_len = max(map(len, record_files.values()))
    for name, record_list in sort_domains(record_files.items()):
        chart.add(name, [x[0].total_seconds()/86400 for x in record_list] +
                        [None] * (max_len - len(record_list)))

    return chart.render()
