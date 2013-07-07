from pygal import DateY


def graph_records(record_files):
    chart = DateY(x_label_rotation=20,
                  js=['http://kozea.github.io/pygal.js/javascripts/svg.jquery.js',
                      'http://linkybook.com/static/uptime.js'])
    for name, record_list in record_files.items():
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