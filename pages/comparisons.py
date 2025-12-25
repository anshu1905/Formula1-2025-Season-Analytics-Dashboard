from dash import html, dcc, register_page, callback, Input, Output
from dash.exceptions import PreventUpdate
import fastf1
import fastf1.plotting
import plotly.graph_objects as go
import os

register_page(__name__, path="/comparisons", name="Comparisons")

# -------------------------------------------------------
# Cache Setup
# -------------------------------------------------------
cache_path = os.path.join(os.path.dirname(__file__), "..", "cache")
cache_path = os.path.abspath(cache_path)
os.makedirs(cache_path, exist_ok=True)
fastf1.Cache.enable_cache(cache_path)


# -------------------------------------------------------
# Dark Theme Helper
# -------------------------------------------------------
def make_dark(fig):
    fig.update_layout(
        paper_bgcolor="#0b0b0b",
        plot_bgcolor="#0b0b0b",
        font=dict(color="white"),
        xaxis=dict(showgrid=False, zeroline=False, title_font=dict(color="white")),
        yaxis=dict(showgrid=False, zeroline=False, title_font=dict(color="white")),
        legend=dict(font=dict(color="white")),
    )
    return fig


# -------------------------------------------------------
# Page Layout (UPDATED)
# -------------------------------------------------------
layout = html.Div(
    [
        html.H1("Driver & Team Comparisons", className="hero-title"),

        # ----------------------------- YEAR / GP / SESSION (UPDATED STYLE) -----------------------------
        html.Div(
            [
                dcc.Dropdown(
                    id="year-dropdown",
                    className="custom-dropdown",
                    options=[{"label": "2025", "value": 2025}],
                    value=2025,
                    clearable=False,
                ),

                dcc.Dropdown(
                    id="event-dropdown",
                    className="custom-dropdown",
                    placeholder="Select Grand Prix",
                    # style={"width": "260px"}, <-- REMOVED
                ),

                dcc.Dropdown(
                    id="session-dropdown",
                    className="custom-dropdown",
                    placeholder="Select Session (FP1/FP2/FP3/Qualifying/Race)",
                    # style={"width": "260px"}, <-- REMOVED
                ),
            ],
            style={
                "display": "flex",
                "gap": "20px",
                "justifyContent": "center",
                "marginTop": "35px",
                "flexWrap": "wrap", # <-- ADDED FOR RESPONSIVENESS
                "maxWidth": "900px", # <-- ADDED FOR CENTERING
                "margin": "35px auto 0 auto", # <-- ADDED FOR CENTERING
            },
        ),

        # ----------------------------- DRIVER SELECTORS (UPDATED STYLE) --------------------------------
        html.Div(
            [
                dcc.Dropdown(
                    id="driver1-dropdown",
                    className="custom-dropdown",
                    placeholder="Select Driver 1",
                    # style={"width": "260px"}, <-- REMOVED
                ),
                dcc.Dropdown(
                    id="driver2-dropdown",
                    className="custom-dropdown",
                    placeholder="Select Driver 2",
                    # style={"width": "260px"}, <-- REMOVED
                ),
            ],
            style={
                "display": "flex",
                "gap": "20px",
                "justifyContent": "center",
                "marginTop": "30px",
                "flexWrap": "wrap", # <-- ADDED FOR RESPONSIVENESS
                "maxWidth": "600px", # <-- ADDED FOR CENTERING
                "margin": "30px auto 0 auto", # <-- ADDED FOR CENTERING
            },
        ),

        html.Div(id="comparison-output", style={"marginTop": "40px"}),
    ],
    className="comparison-page-container",
)


# -------------------------------------------------------
# Load GP Events for Year
# -------------------------------------------------------
@callback(Output("event-dropdown", "options"), Input("year-dropdown", "value"))
def load_events(year):
    if not year:
        return []

    try:
        events = fastf1.get_event_schedule(year)
        return [
            {"label": events.loc[i, "EventName"], "value": events.loc[i, "EventName"]}
            for i in events.index
        ]
    except:
        return []


# -------------------------------------------------------
# Load Session Options
# -------------------------------------------------------
@callback(
    Output("session-dropdown", "options"),
    Input("year-dropdown", "value"),
    Input("event-dropdown", "value"),
)
def load_sessions(year, gp):
    if not (year and gp):
        return []

    sessions = ["FP1", "FP2", "FP3", "Qualifying", "Race"]
    return [{"label": s, "value": s} for s in sessions]


# -------------------------------------------------------
# Load Drivers for Session
# -------------------------------------------------------
@callback(
    Output("driver1-dropdown", "options"),
    Output("driver2-dropdown", "options"),
    Input("year-dropdown", "value"),
    Input("event-dropdown", "value"),
    Input("session-dropdown", "value"),
)
def load_drivers(year, gp, session_type):
    if not (year and gp and session_type):
        return [], []

    try:
        event = fastf1.get_event(year, gp)
        session = event.get_session(session_type)
        session.load()

        results = session.results

        driver_opts = [
            {
                "label": f"{row['LastName']} ({row['DriverNumber']})",
                "value": row["DriverNumber"],
            }
            for _, row in results.iterrows()
        ]

        return driver_opts, driver_opts

    except Exception as e:
        print("Driver load error:", e)
        return [], []


# -------------------------------------------------------
# MAIN COMPARISON PLOTS
# -------------------------------------------------------
@callback(
    Output("comparison-output", "children"),
    Input("year-dropdown", "value"),
    Input("event-dropdown", "value"),
    Input("session-dropdown", "value"),
    Input("driver1-dropdown", "value"),
    Input("driver2-dropdown", "value"),
)
def update_comparisons(year, gp, session_type, d1, d2):
    if not (year and gp and session_type and d1 and d2):
        raise PreventUpdate

    try:
        event = fastf1.get_event(year, gp)
        ses = event.get_session(session_type)
        ses.load(telemetry=True, laps=True, weather=False)

        laps = ses.laps

        laps1 = laps.pick_driver(d1)
        laps2 = laps.pick_driver(d2)

        if laps1.empty or laps2.empty:
            return html.P("⚠️ No usable lap data available for one or both drivers.")

        # Get telemetry for fastest laps
        tel1 = laps1.pick_fastest().get_telemetry()
        tel2 = laps2.pick_fastest().get_telemetry()

        # Names for legend
        name1 = laps1.pick_fastest()["Driver"]
        name2 = laps2.pick_fastest()["Driver"]

    except Exception as e:
        return html.P(f"⚠️ Not enough data for this session. Error: {str(e)}")

    # ----------------------------------------------------
    # LAP TIME COMPARISON
    # ----------------------------------------------------
    fig_lap = go.Figure()
    fig_lap.add_trace(go.Scatter(
        x=laps1["LapNumber"],
        y=laps1["LapTime"].dt.total_seconds(),
        mode="lines+markers",
        name=f"{name1} ({d1})"
    ))
    fig_lap.add_trace(go.Scatter(
        x=laps2["LapNumber"],
        y=laps2["LapTime"].dt.total_seconds(),
        mode="lines+markers",
        name=f"{name2} ({d2})"
    ))
    fig_lap.update_layout(
        title={"text":"Lap Time Comparison", "x": 0.5, "xanchor": "center"},
        height=450,
        xaxis_title="Lap Number",
        yaxis_title="Lap Time (sec)"
    )
    fig_lap = make_dark(fig_lap)

    # ----------------------------------------------------
    # SPEED TRACE
    # ----------------------------------------------------
    fig_speed = go.Figure()
    fig_speed.add_trace(go.Scatter(
        x=tel1["Distance"], y=tel1["Speed"],
        name=f"{name1} ({d1}) Speed"
    ))
    fig_speed.add_trace(go.Scatter(
        x=tel2["Distance"], y=tel2["Speed"],
        name=f"{name2} ({d2}) Speed"
    ))
    fig_speed.update_layout(
        title={"text":"Speed Trace (Fastest Lap)", "x": 0.5, "xanchor": "center"},
        height=450,
        xaxis_title="Distance (m)",
        yaxis_title="Speed (km/h)",
        legend=dict(
            orientation="h",   # horizontal legend
            yanchor="bottom",
            y=1.05,
            xanchor="center",
            x=0.5,
            bgcolor="rgba(0,0,0,0)"  # keep transparent (matches your theme)
        ),
    )
    fig_speed = make_dark(fig_speed)

    # ----------------------------------------------------
    # THROTTLE
    # ----------------------------------------------------
    fig_throttle = go.Figure()
    fig_throttle.add_trace(go.Scatter(
        x=tel1["Distance"], y=tel1["Throttle"],
        name=f"{name1} ({d1})"
    ))
    fig_throttle.add_trace(go.Scatter(
        x=tel2["Distance"], y=tel2["Throttle"],
        name=f"{name2} ({d2})"
    ))
    fig_throttle.update_layout(
        title={"text":"Throttle Comparison", "x": 0.5, "xanchor": "center"},
        height=450,
        xaxis_title="Distance (m)",
        yaxis_title="Throttle (%)",
        legend=dict(
            orientation="h",   # horizontal legend
            yanchor="bottom",
            y=1.05,
            xanchor="center",
            x=0.5,
            bgcolor="rgba(0,0,0,0)"  # keep transparent (matches your theme)
        ),
    )
    fig_throttle = make_dark(fig_throttle)

    # ----------------------------------------------------
    # BRAKE
    # ----------------------------------------------------
    fig_brake = go.Figure()
    fig_brake.add_trace(go.Scatter(
        x=tel1["Distance"], y=tel1["Brake"],
        name=f"{name1} ({d1})"
    ))
    fig_brake.add_trace(go.Scatter(
        x=tel2["Distance"], y=tel2["Brake"],
        name=f"{name2} ({d2})"
    ))
    fig_brake.update_layout(
        title={"text":"Brake Comparison", "x": 0.5, "xanchor": "center"},
        height=450,
        xaxis_title="Distance (m)",
        yaxis_title="Brake (boolean)",
        legend=dict(
            orientation="h",   # horizontal legend
            yanchor="bottom",
            y=1.05,
            xanchor="center",
            x=0.5,
            bgcolor="rgba(0,0,0,0)"  # keep transparent (matches your theme)
        ),
    )
    fig_brake = make_dark(fig_brake)

    # ----------------------------------------------------
    # GEAR
    # ----------------------------------------------------
    fig_gear = go.Figure()
    fig_gear.add_trace(go.Scatter(
        x=tel1["Distance"], y=tel1["nGear"],
        name=f"{name1} ({d1})"
    ))
    fig_gear.add_trace(go.Scatter(
        x=tel2["Distance"], y=tel2["nGear"],
        name=f"{name2} ({d2})"
    ))
    fig_gear.update_layout(
        title={"text":"Gear Comparison", "x": 0.5, "xanchor": "center"},
        height=450,
        xaxis_title="Distance (m)",
        yaxis_title="Gear",
        legend=dict(
            orientation="h",   # horizontal legend
            yanchor="bottom",
            y=1.05,
            xanchor="center",
            x=0.5,
            bgcolor="rgba(0,0,0,0)"  # keep transparent (matches your theme)
        ),
    )
    fig_gear = make_dark(fig_gear)

    # ----------------------------------------------------
    # RETURN ALL GRAPHS
    # ----------------------------------------------------
    return html.Div(
        [
            dcc.Graph(figure=fig_lap, className="comparison-chart"),
            dcc.Graph(figure=fig_speed, className="comparison-chart"),
            dcc.Graph(figure=fig_throttle, className="comparison-chart"),
            dcc.Graph(figure=fig_brake, className="comparison-chart"),
            dcc.Graph(figure=fig_gear, className="comparison-chart"),
        ],
        className="comparison-container",
    )