import numpy as np
from scipy.signal import butter, filtfilt
from dash import Dash, html, dcc, Input, Output
import dash_daq as daq
import dash_bootstrap_components as dbc
import plotly.graph_objs as go

T   = 10.0
Fs0 = 100.0
t   = np.arange(0, T, 1/Fs0)

initial = {
    "A": 1.0,
    "f": 1.0,
    "phi": 0.0,
    "noise_mean": 0.0,
    "noise_var": 0.1,
    "cutoff": 1.0,
    "order": 5,
    "filter_type": "Butterworth"
}

def generate_harmonic(A, f, phi):
    return A * np.sin(2 * np.pi * f * t + phi)

def generate_noise(mean, var):
    return np.random.normal(mean, np.sqrt(var), size=len(t))

def butter_lowpass(sig, cutoff, fs, order):
    b, a = butter(order, cutoff/(0.5*fs), btype='low')
    return filtfilt(b, a, sig)

def custom_ma(sig, window):
    w = int(window)
    if w < 1:
        return sig
    kernel = np.ones(w) / w
    return np.convolve(sig, kernel, mode='same')


app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
app.title = "Lab5: Harmonic + Noise + Filtering"

app.layout = dbc.Container(fluid=True, children=[

    dbc.Row([

        dbc.Col(width=3, children=[
            html.H4("Controls", className="mb-3"),
            dbc.Tabs(
                id="tabs",
                active_tab="tab-signal",
                children=[

                    dbc.Tab(label="Гармоніка", tab_id="tab-signal", children=[
                        html.Div([
                            html.Label("Амплітуда", className="form-label"),
                            daq.Slider(
                                id="A",
                                min=0.1, max=10, step=0.1,
                                value=initial["A"],
                                handleLabel={"showCurrentValue": True, "label": "A"},
                                size=250
                            )
                        ], className="mb-4"),
                        html.Div([
                            html.Label("Частота (Hz)", className="form-label"),
                            daq.Slider(
                                id="f",
                                min=0.1, max=10, step=0.1,
                                value=initial["f"],
                                handleLabel={"showCurrentValue": True, "label": "f"},
                                size=250
                            )
                        ], className="mb-4"),
                        html.Div([
                            html.Label("Фазовий зсув (rad)", className="form-label"),
                            daq.Slider(
                                id="phi",
                                min=0, max=2*np.pi, step=0.1,
                                value=initial["phi"],
                                handleLabel={"showCurrentValue": True, "label": "φ"},
                                size=250
                            )
                        ], className="mb-4"),
                    ]),

                    dbc.Tab(label="Шум", tab_id="tab-noise", children=[
                        html.Div([
                            html.Label("Середнє шуму", className="form-label"),
                            daq.Slider(
                                id="noise_mean",
                                min=-1, max=1, step=0.1,
                                value=initial["noise_mean"],
                                handleLabel={"showCurrentValue": True, "label": "μ"},
                                size=250
                            )
                        ], className="mb-4"),
                        html.Div([
                            html.Label("Дисперсія шуму", className="form-label"),
                            daq.Slider(
                                id="noise_var",
                                min=0, max=1, step=0.01,
                                value=initial["noise_var"],
                                handleLabel={"showCurrentValue": True, "label": "σ²"},
                                size=250
                            )
                        ], className="mb-4"),
                        html.Div([
                            dcc.Checklist(
                                id="show_noise",
                                options=[{"label": "Show Noise", "value": 1}],
                                value=[1]
                            )
                        ], className="mb-4"),
                    ]),

                    dbc.Tab(label="Фільтер", tab_id="tab-filter", children=[
                        html.Div([
                            html.Label("Частота зрізу (Hz)", className="form-label"),
                            daq.Slider(
                                id="cutoff",
                                min=0.1, max=5, step=0.1,
                                value=initial["cutoff"],
                                handleLabel={"showCurrentValue": True, "label": "fc"},
                                size=250
                            )
                        ], className="mb-4"),
                        html.Div([
                            html.Label("Порядок фільтрації", className="form-label"),
                            daq.Slider(
                                id="order",
                                min=1, max=15, step=1,
                                value=initial["order"],
                                handleLabel={"showCurrentValue": True, "label": "n"},
                                size=250
                            )
                        ], className="mb-4"),
                        html.Div([
                            html.Label("Тип фільтра", className="form-label"),
                            dcc.Dropdown(
                                id="filter_type",
                                options=[
                                    {"label": "Butterworth",   "value": "Butterworth"},
                                    {"label": "Moving Average","value": "MA"}
                                ],
                                value=initial["filter_type"],
                                clearable=False
                            )
                        ], className="mb-4"),
                        dbc.Button(
                            "Reset",
                            id="reset-btn",
                            color="primary",
                            className="w-100",
                            style={"marginTop": "1rem"}
                        )
                    ]),
                ]
            )
        ]),

        dbc.Col(width=9, children=[
            dbc.Card(dcc.Graph(id="signal-plot"), body=True, className="mb-3"),
            dbc.Card(dcc.Graph(id="filtered-plot"), body=True)
        ])
    ])
])

@app.callback(
    [Output("signal-plot", "figure"), Output("filtered-plot", "figure")],
    [Input(k, "value") for k in [
        "A", "f", "phi",
        "noise_mean", "noise_var",
        "cutoff", "order",
        "show_noise", "filter_type"
    ]]
)
def update_graph(A, f, phi, nm, nv, cutoff, order, show_noise, filter_type):
    clean = generate_harmonic(A, f, phi)
    noise = generate_noise(nm, nv)
    sig   = clean + noise if 1 in show_noise else clean

    if filter_type == "Butterworth":
        filt = butter_lowpass(sig, cutoff, Fs0, order)
    else:
        filt = custom_ma(sig, order)

    fig1 = go.Figure([
        go.Scatter(x=t, y=clean, name="Clean", line=dict(color="blue")),
        go.Scatter(x=t, y=sig,   name="Noisy", line=dict(color="red"), opacity=0.6)
    ])
    fig1.update_layout(title="Harmonic Signal + Noise", template="simple_white")

    fig2 = go.Figure([
        go.Scatter(x=t, y=filt, name="Filtered", line=dict(color="green"))
    ])
    fig2.update_layout(
        title=f"Filtered Output ({filter_type})",
        template="simple_white"
    )

    return fig1, fig2


@app.callback(
    [Output(k, "value") for k in [
        "A", "f", "phi",
        "noise_mean", "noise_var",
        "cutoff", "order",
        "show_noise", "filter_type"
    ]],
    Input("reset-btn", "n_clicks")
)
def reset_all(n):
    return [
        initial["A"], initial["f"], initial["phi"],
        initial["noise_mean"], initial["noise_var"],
        initial["cutoff"], initial["order"],
        [1], initial["filter_type"]
    ]


if __name__ == "__main__":
    app.run(debug=True)