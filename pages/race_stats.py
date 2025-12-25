import fastf1 as ff1
import pandas as pd
import plotly.express as px

from dash import (
    html,
    dcc,
    callback,
    Input,
    Output,
    register_page
)
from dash.exceptions import PreventUpdate

# -------------------------------------------------
# DASH PAGE REGISTRATION
# -------------------------------------------------
register_page(
    __name__,
    path="/race-stats",
    name="Race"
)

# -------------------------------------------------
# FASTF1 CACHE
# -------------------------------------------------
ff1.Cache.enable_cache("./fastf1_cache")

NAVBAR_COLOR = "#00e6c3"

# -------------------------------------------------
# LAYOUT
# -------------------------------------------------
layout = html.Div(
    [
        html.H1(
            "Race Analysis",
            style={
                "marginBottom": "20px",
                "textAlign": "center",
                "width": "100%"
            }
        ),

        # -------------------------------
        # CONTROLS
        # -------------------------------
        html.Div(
            [
                dcc.Dropdown(
                    id="rs-season",
                    options=[{"label": "2025", "value": 2025}],
                    value=None,
                    placeholder="Select season",
                    clearable=True,
                    className="custom-dropdown",
                    style={"flex": "1 1 48%", "minWidth": "360px"},
                ),

                dcc.Dropdown(
                    id="rs-gp",
                    options=[],
                    value=None,
                    placeholder="Select Grand Prix",
                    clearable=True,
                    className="custom-dropdown",
                    style={"flex": "1 1 48%", "minWidth": "360px"},
                ),
            ],
            className="race-controls",
            style={
                "display": "flex",
                "gap": "4%",
                "marginBottom": "24px",
                "maxWidth": "1200px",
                "width": "100%",
                "margin": "0 auto 24px auto",
            }
        ),

        # -------------------------------
        # ROW 1
        # -------------------------------
        html.Div(
            [
                dcc.Graph(id="rs-laptime-dist", className="dash-graph"),
                dcc.Graph(id="rs-position-changes", className="dash-graph"),
            ],
            className="race-row"
        ),

        # -------------------------------
        # ROW 2
        # -------------------------------
        html.Div(
            dcc.Graph(id="rs-team-pace", className="dash-graph-full"),
            style={"marginTop": "26px"}
        ),
    ],
    className="race-page",
)

# -------------------------------------------------
# UPDATE GRAND PRIX DROPDOWN
# -------------------------------------------------
@callback(
    Output("rs-gp", "options"),
    Output("rs-gp", "value"),
    Input("rs-season", "value"),
)
def update_gp_dropdown(season):
    if not season:
        return [], None

    schedule = ff1.get_event_schedule(season, include_testing=False)
    schedule = schedule.sort_values("RoundNumber")

    options = [
        {"label": row["OfficialEventName"], "value": int(row["RoundNumber"])}
        for _, row in schedule.iterrows()
    ]

    return options, None


# -------------------------------------------------
# UPDATE RACE PLOTS
# -------------------------------------------------
@callback(
    Output("rs-laptime-dist", "figure"),
    Output("rs-position-changes", "figure"),
    Output("rs-team-pace", "figure"),
    Input("rs-season", "value"),
    Input("rs-gp", "value"),
)
def update_race_plots(season, round_no):

    if not season or not round_no:
        raise PreventUpdate

    session = ff1.get_session(season, round_no, "R")
    session.load(laps=True, telemetry=False, weather=False)

    laps = session.laps

    # =================================================
    # LAP TIME DISTRIBUTION (TOP 10 DRIVERS)
    # =================================================
    quicklaps = laps.pick_quicklaps().dropna(subset=["LapTime"])
    quicklaps["LapTime_s"] = quicklaps["LapTime"].dt.total_seconds()

    top_drivers = (
        quicklaps.groupby("Driver")["LapTime_s"]
        .median()
        .sort_values()
        .head(10)
        .index
        .tolist()
    )

    dist_df = quicklaps[quicklaps["Driver"].isin(top_drivers)]

    fig_dist = px.violin(
        dist_df,
        x="Driver",
        y="LapTime_s",
        box=True,
        points=False,
        height=420,
    )

    fig_dist.update_layout(
        title={
            "text": "Lap Time Distribution (Top 10 Drivers)",
            "x": 0.5,
            "xanchor": "center",
            "font": {"size": 18, "color": NAVBAR_COLOR},
        },
        xaxis_title="Driver",
        yaxis_title="Lap Time (s)",
        showlegend=False,
        margin=dict(t=70),
        plot_bgcolor="rgb(0,0,0)",
        paper_bgcolor="rgb(0,0,0)",
    )

    # =================================================
    # POSITION CHANGES
    # =================================================
    pos_df = laps.dropna(subset=["Position"])

    fig_pos = px.line(
        pos_df,
        x="LapNumber",
        y="Position",
        color="Driver",
        height=420,
    )

    fig_pos.update_yaxes(autorange="reversed")

    fig_pos.update_layout(
        title={
            "text": "Position Changes Over Race",
            "x": 0.5,
            "xanchor": "center",
            "font": {"size": 18, "color": NAVBAR_COLOR},
        },
        xaxis_title="Lap",
        yaxis_title="Position",
        showlegend=False,
        margin=dict(t=70),
        plot_bgcolor="rgb(0,0,0)",
        paper_bgcolor="rgb(0,0,0)",
    )

    # =================================================
    # TEAM PACE
    # =================================================
    team_order = (
        quicklaps.groupby("Team")["LapTime_s"]
        .median()
        .sort_values()
        .index
        .tolist()
    )

    fig_team = px.box(
        quicklaps,
        x="Team",
        y="LapTime_s",
        height=420,
    )

    fig_team.update_xaxes(categoryorder="array", categoryarray=team_order)

    fig_team.update_layout(
        title={
            "text": "Team Pace (Median Lap Time)",
            "x": 0.5,
            "xanchor": "center",
            "font": {"size": 18, "color": NAVBAR_COLOR},
        },
        xaxis_title="Team",
        yaxis_title="Lap Time (s)",
        showlegend=False,
        margin=dict(t=70),
        plot_bgcolor="rgb(0,0,0)",
        paper_bgcolor="rgb(0,0,0)",
    )

    return fig_dist, fig_pos, fig_team


# -------------------------------------------------
# 🔹 ONLY ADDITION: HIDE GRAPHS UNTIL RACE IS SELECTED
# -------------------------------------------------
@callback(
    Output("rs-laptime-dist", "style"),
    Output("rs-position-changes", "style"),
    Output("rs-team-pace", "style"),
    Input("rs-season", "value"),
    Input("rs-gp", "value"),
)
def toggle_graph_visibility(season, gp):
    if not season or not gp:
        return (
            {"display": "none"},
            {"display": "none"},
            {"display": "none"},
        )

    return (
        {"display": "block"},
        {"display": "block"},
        {"display": "block"},
    )
