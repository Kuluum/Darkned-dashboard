import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import plotly
import plotly.graph_objs as go


from DarknetLogParser import DarknetLogParser
import threading
import sys

log_path = sys.argv[1]

parser = DarknetLogParser(log_path)

t = threading.Thread(target=parser.run)


app = dash.Dash(__name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])


loss_defaul_layout = {
    'uirevision': True,
    'title': 'Loss',
    'xaxis': {
        'title': 'Iterations',
        'fixedrange':True
        },
    'yaxis': {
        'title': 'Avarage loss',
        'fixedrange':True
    }
}

map_default_layout = {
    'uirevision': True,
    'title': 'Map',
    'xaxis': {
        'title': 'Iterations'
        },
    'yaxis': {
        'title': 'Map'
    }
}


def loss_graph_data():
    return go.Scatter(
        y=parser.losses,
        mode='lines+markers'
    )


loss_graph = dcc.Graph(
                    id='loss-graph',
                    figure={
                        'data': [loss_graph_data()
                            # {
                            #     'y': parser.losses,
                            #     'type': 'line',
                            #     'title': 'Loss'
                            # },
                        ],
                        'layout': loss_defaul_layout
                    },
                    config={
                        'modeBarButtons': [['hoverClosestCartesian', 'hoverCompareCartesian']]
                    }
            )


def map_graph_data():
    return go.Scatter(
        x=parser.map_calculation_iterations,
        y=parser.map_list,
        mode='lines+markers'
    )


map_graph = dcc.Graph(
                    id='map-graph',
                    figure={
                        'data': [
                            map_graph_data()
                        ],
                        'layout': map_default_layout
                    },
                    config={
                        'modeBarButtons': [['pan2d', 'zoom2d', 'resetScale2d', 'hoverClosestCartesian', 'hoverCompareCartesian']]
                    }
            )

app.layout = html.Div([
        html.H1(children='Darknet train', id='first'),

        html.Div(id='iterations_info'),
        html.Div(style={'padding': 5}),
        html.Div(id='time_left'),
        html.Div(style={'padding': 5}),
        html.Div(id='best_map'),

        html.Div([
            # six columns = 50% (12-column fluid grid with a max width of 960px) external_stylesheets
            html.Div([loss_graph], className="six columns"),
            html.Div([map_graph], className="six columns")
        ], className="row"),


        dcc.Interval(id='timer', interval=2000),
    ]
)


@app.callback(Output('iterations_info', 'children'),
              [Input('timer', 'n_intervals')])
def update_iteration(n_intervals):
    style = {'fontSize': '18px'}
    return [
        html.Span('Iteration #{0} takes {1:.2f} sec'.format(len(parser.losses), parser.taked_times[-1]), style=style)
    ]


@app.callback(Output('time_left', 'children'),
              [Input('timer', 'n_intervals')])
def update_timeleft(n_intervals):
    style = {'fontSize': '18px'}
    return [
        html.Span('Time left: {0:.2f} hr'.format(parser.hours_left), style=style)
    ]


@app.callback(Output('best_map', 'children'),
              [Input('timer', 'n_intervals')])
def update_best_map(n_intervals):
    style = {'fontSize': '18px'}
    return [
        html.Span('Best map: {0:.2f}'.format(parser.best_map), style=style)
    ]


@app.callback(Output('loss-graph', 'figure'),
              [Input('timer', 'n_intervals')])
def update_loss_graph(n_intervals):

    x_range = []
    y_range = []

    history_len = 250

    if len(parser.losses) < 100:
        history_len = 50
    elif len(parser.losses) < 250:
        history_len = 100
    elif len(parser.losses) < 400:
        history_len = 150

    if len(parser.losses) > history_len:
        x_range = [len(parser.losses)-history_len, len(parser.losses)]
        last_losses = parser.losses[-history_len:]
        y_min = min(last_losses) * 0.9
        y_max = max(last_losses) * 1.1
        y_range = [y_min, y_max]

    layout = loss_defaul_layout.copy()
    layout['xaxis']['range'] = x_range
    layout['yaxis']['range'] = y_range

    return {
                'data': [loss_graph_data()],
                'layout': layout
            }


@app.callback(Output('map-graph', 'figure'),
              [Input('timer', 'n_intervals')])
def update_map_graph(n_intervals):
    return {
        'data': [map_graph_data()],
        'layout': map_default_layout
    }


if __name__ == '__main__':
    t.start()
    app.run_server(debug=True)
