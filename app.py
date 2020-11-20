import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import re
import threading
import sys

p = re.compile('(\d.*):(.*)')
losses = []
taked_times = []
hours_left = []
log_file_path = sys.argv[1]

def follow(thefile):
    from_beginning = True
    while True:
        if from_beginning:
            for line in thefile.readlines():
                yield line
                # time.sleep(0.05)
        else:
            thefile.seek(0, 2)
            from_beginning = True


def extract(line: str):
    info_splt = [i.strip() for i in line.split(',')]
    if len(info_splt) < 6:
        print('wtf', info_splt)
        return None
    avg_loss = float(info_splt[1].split()[0])
    taked_time = float(info_splt[3].split()[0])
    time_left = float(info_splt[5].split()[0])
    return (avg_loss, taked_time, time_left)


def run():
    logfile = open(log_file_path, "r")

    loglines = follow(logfile)
    for line in loglines:
        line = line.strip()
        if p.match(line):
            extracted = extract(line)
            if extracted is not None:
                loss, taked_time, time_left = extracted
                losses.append(loss)
                taked_times.append(taked_time)
                hours_left.append(time_left)


t = threading.Thread(target=run)


app = dash.Dash(__name__)


app.layout = html.Div(
    children=[
        html.H1(children='Darknet train', id='first'),

        html.Div(id='iterations_info'),
        dcc.Graph(
                id='example-graph',
                figure={
                    'data': [
                        {
                            'y': losses,
                            'type': 'line'
                        },
                    ],
                    'layout': {
                        'uirevision': True,
                        'title': 'Avarage loss'
                    }
                },
                config={
                    'modeBarButtons': [['pan2d', 'zoom2d', 'resetScale2d', 'hoverClosestCartesian', 'hoverCompareCartesian']]
                }
            ),

        html.Div(id='time_left'),

        dcc.Interval(id='timer', interval=2000),
    ]
)


@app.callback(Output('iterations_info', 'children'),
              [Input('timer', 'n_intervals')])
def update_iteration(n_intervals):
    style = {'padding': '5px', 'fontSize': '16px'}
    return [
        html.Span('Iteration #{0} takes {1:.2f} sec'.format(len(losses), taked_times[-1]), style=style)
    ]


@app.callback(Output('time_left', 'children'),
              [Input('timer', 'n_intervals')])
def update_timeleft(n_intervals):
    style = {'padding': '5px', 'fontSize': '16px'}
    return [
        html.Span('Time left: {0:.2f} hr'.format(hours_left[-1]), style=style)
    ]


@app.callback(Output('example-graph', 'figure'),
              [Input('timer', 'n_intervals')])
def update_graph(n_intervals):

    x_range = []
    y_range = []
    history_len = 150

    if len(losses) < 100:
        history_len = 50
    elif len(losses) < 250:
        history_len = 100

    if len(losses) > history_len:
        x_range = [len(losses)-history_len, len(losses)]
        last_losses = losses[-history_len:]
        y_min = min(last_losses) * 0.9
        y_max = max(last_losses) * 1.1
        y_range = [y_min, y_max]

    data = [
        {
            'y': losses,
            'type': 'line'
        },
    ]

    return {
                'data': data,
                'layout': {
                    'uirevision': True,
                    'title': 'Dash Data Visualization',
                    'xaxis': {
                        'title': 'Iterations',
                        'range': x_range
                        },
                    'yaxis': {
                        'title': 'Avarage loss',
                        'range': y_range
                    }
                }
            }


if __name__ == '__main__':
    t.start()
    app.run_server(debug=True, threaded=False)
