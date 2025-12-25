# driver_stats.py

from dash import html, dcc, register_page, callback, Output, Input
import plotly.graph_objects as go
import pandas as pd
import fastf1 as ff1
import os
from collections import Counter

# =====================================================
# Page registration
# =====================================================
register_page(__name__, path="/driver", name="Driver")

# =====================================================
# FastF1 cache
# =====================================================
CACHE_DIR = "ff1cache"
os.makedirs(CACHE_DIR, exist_ok=True)
ff1.Cache.enable_cache(CACHE_DIR)

# =====================================================
# Data helpers
# =====================================================
def load_season_results(year: int):
    results = {}
    try:
        schedule = ff1.get_event_schedule(year)
    except Exception:
        return results

    for _, row in schedule.iterrows():
        gp = row["EventName"]
        try:
            session = ff1.get_session(year, gp, "R")
            session.load(telemetry=False, weather=False)
            df = session.results
            df["GrandPrix"] = gp
            results[gp] = df.reset_index(drop=True)
        except Exception:
            continue

    return results


def extract_drivers(results):
    drivers = {}
    for df in results.values():
        for _, r in df.iterrows():
            drivers[r["Abbreviation"]] = r["FullName"]
    return [{"label": f"{v} ({k})", "value": k} for k, v in sorted(drivers.items())]


def finish_distribution(results, driver):
    counter = Counter()
    for df in results.values():
        row = df[df["Abbreviation"] == driver]
        if not row.empty:
            counter[int(row.iloc[0]["Position"])] += 1
    return counter


def cumulative_points(results, driver):
    races, cumulative, total = [], [], 0
    for gp, df in results.items():
        races.append(gp)
        row = df[df["Abbreviation"] == driver]
        pts = float(row.iloc[0]["Points"]) if not row.empty else 0
        total += pts
        cumulative.append(total)
    return races, cumulative


# =====================================================
# Layout
# =====================================================
layout = html.Div(
    className="features-container race-page",
    children=[

        # ---------- TITLE ----------
        html.Div(
            className="driver-title-block",
            children=[
                html.H1("Driver Statistics", className="hero-title"),
                html.P(
                    "Season-level performance overview",
                    className="hero-subtitle"
                )
            ]
        ),

        # ---------- FILTERS ----------
        html.Div(
            className="driver-filters",
            children=[
                dcc.Dropdown(
                    id="season-dropdown",
                    options=[{"label": "2025", "value": 2025}],
                    value=2025,
                    clearable=False,
                    className="custom-dropdown"
                ),

                dcc.Dropdown(
                    id="driver-dropdown",
                    placeholder="Driver",
                    clearable=False,
                    className="custom-dropdown"
                ),
            ]
        ),

        # ---------- DRIVER NAME ----------
        html.Div(
            id="driver-header",
            children=html.H2(
                "Select a driver",
                id="driver-name",
                className="driver-name"
            )
        ),

        # ---------- CONTENT (HIDDEN INITIALLY) ----------
        html.Div(
            id="driver-content",
            style={"display": "none"},
            children=[

                # KPIs
                html.Div(
                    className="feature-grid results-summary",
                    children=[
                        html.Div(id="kpi-wins", className="result-card"),
                        html.Div(id="kpi-podiums", className="result-card"),
                        html.Div(id="kpi-points", className="result-card"),
                    ]
                ),

                # ---------- FULL-WIDTH GRAPHS ----------
                html.Div(
                    dcc.Graph(id="points-graph"),
                    className="dash-graph-full"
                ),

                html.Div(
                    dcc.Graph(id="finish-graph"),
                    className="dash-graph-full"
                ),
            ]
        ),

        dcc.Store(id="season-data")
    ]
)

# =====================================================
# Callbacks
# =====================================================
@callback(
    Output("season-data", "data"),
    Output("driver-dropdown", "options"),
    Input("season-dropdown", "value"),
)
def load_season(season):
    if not season:
        return {}, []

    results = load_season_results(season)
    drivers = extract_drivers(results)

    return (
        {gp: df.to_dict("records") for gp, df in results.items()},
        drivers
    )


@callback(
    Output("driver-name", "children"),
    Output("driver-content", "style"),
    Output("kpi-wins", "children"),
    Output("kpi-podiums", "children"),
    Output("kpi-points", "children"),
    Output("points-graph", "figure"),
    Output("finish-graph", "figure"),
    Input("season-data", "data"),
    Input("driver-dropdown", "value"),
)
def update_dashboard(data, driver):

    empty_fig = go.Figure().update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )

    if not data or not driver:
        return "Select a driver", {"display": "none"}, "", "", "", empty_fig, empty_fig

    results = {gp: pd.DataFrame(rows) for gp, rows in data.items()}

    # KPIs
    dist = finish_distribution(results, driver)
    wins = dist.get(1, 0)
    podiums = sum(dist.get(p, 0) for p in (1, 2, 3))
    points_total = sum(
        float(df[df["Abbreviation"] == driver]["Points"].iloc[0])
        for df in results.values()
        if not df[df["Abbreviation"] == driver].empty
    )

    def kpi(title, value):
        return [
            html.Div(title, className="result-card-title"),
            html.Div(value, className="result-card-value")
        ]

    # ---------- CUMULATIVE POINTS ----------
    races, cum_pts = cumulative_points(results, driver)
    fig_points = go.Figure(
        go.Scatter(
            x=races,
            y=cum_pts,
            mode="lines+markers",
            line=dict(width=3),
            marker=dict(size=7)
        )
    ).update_layout(
        title="Cumulative Season Points",
        template="plotly_dark",
        height=520,
        margin=dict(l=70, r=40, t=70, b=140),
        xaxis_tickangle=-30
    )

    # ---------- FINISH DISTRIBUTION ----------
    fig_finish = go.Figure(
        go.Bar(
            x=list(dist.values()),
            y=[f"P{p}" for p in dist.keys()],
            orientation="h"
        )
    ).update_layout(
        title="Finish Position Distribution",
        template="plotly_dark",
        height=520,
        margin=dict(l=90, r=40, t=70, b=60),
        yaxis=dict(categoryorder="category ascending")
    )

    return (
        driver,
        {"display": "block"},
        kpi("Wins", wins),
        kpi("Podiums", podiums),
        kpi("Points", int(points_total)),
        fig_points,
        fig_finish
    )
