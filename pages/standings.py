from dash import html, dcc, register_page, callback, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import requests

# ---------------------------------------------------------
# PAGE REGISTRATION
# ---------------------------------------------------------
register_page(__name__, path="/standings", name="Standings")

# ---------------------------------------------------------
# CONSTANTS
# ---------------------------------------------------------
SEASONS = ["2025"]

JOLPICA_SEASON_URL = "https://api.jolpi.ca/ergast/f1/{season}.json"
ERGAST_SEASON_URL = "http://ergast.com/api/f1/{season}.json"
JOLPICA_RACE_RESULT = "https://api.jolpi.ca/ergast/f1/{season}/{round}/results.json"
ERGAST_RACE_RESULT = "http://ergast.com/api/f1/{season}/{round}/results.json"

# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------
def try_get_json(url, timeout=8):
    try:
        r = requests.get(url, timeout=timeout)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None


def fetch_season_races(season):
    for url in (
        JOLPICA_SEASON_URL.format(season=season),
        ERGAST_SEASON_URL.format(season=season),
    ):
        j = try_get_json(url)
        if j:
            try:
                return j["MRData"]["RaceTable"]["Races"]
            except Exception:
                pass
    return []


def fetch_race_results(season, round_):
    for url in (
        JOLPICA_RACE_RESULT.format(season=season, round=round_),
        ERGAST_RACE_RESULT.format(season=season, round=round_),
    ):
        j = try_get_json(url)
        if j and j.get("MRData"):
            return j
    return None


def parse_race_summary(j):
    races = j["MRData"]["RaceTable"]["Races"]
    if not races:
        return None

    race = races[0]
    results = race.get("Results", [])
    winner = results[0] if results else None

    fastest = None
    best = None
    for r in results:
        fl = r.get("FastestLap")
        if fl:
            t = fl.get("Time", {}).get("time")
            if t:
                secs = (
                    int(t.split(":")[0]) * 60 + float(t.split(":")[1])
                    if ":" in t else float(t)
                )
                if best is None or secs < best:
                    best = secs
                    fastest = {
                        "driver": f"{r['Driver']['givenName']} {r['Driver']['familyName']}",
                        "time": t,
                        "lap": fl.get("lap"),
                    }

    rows = []
    for r in results:
        rows.append({
            "pos": int(r.get("position", 0)),
            "number": r.get("number", ""),
            "driver": f"{r['Driver']['givenName']} {r['Driver']['familyName']}",
            "team": r["Constructor"]["name"],
            "time": r.get("Time", {}).get("time", ""),
            "gap": r.get("status", ""),
            "interval": "",
            "points": r.get("points", ""),
            "laps": r.get("laps", ""),
        })

    return {
        "winner": f"{winner['Driver']['givenName']} {winner['Driver']['familyName']}" if winner else "—",
        "fastest": fastest,
        "circuit": race["Circuit"]["circuitName"],
        "rows": rows,
    }

# ---------------------------------------------------------
# UI COMPONENTS
# ---------------------------------------------------------
def stat_card(title, value):
    return html.Div(
        [
            html.Div(title, className="result-card-title"),
            html.Div(value, className="result-card-value"),
        ],
        className="result-card",
    )

# ---------------------------------------------------------
# CONTROLS
# ---------------------------------------------------------
controls = dbc.Row(
    [
        dbc.Col(
            dcc.Dropdown(
                id="season-select",
                options=[{"label": s, "value": s} for s in SEASONS],
                value=SEASONS[0],
                clearable=False,
                className="custom-dropdown",
            ),
            md=3,
        ),
        dbc.Col(
            dcc.Dropdown(
                id="race-select",
                options=[],
                value=None,                 # 🔑 explicitly empty
                placeholder="Select race",
                clearable=False,
                className="custom-dropdown",
            ),
            md=6,
        ),
        dbc.Col(
            dbc.Button("Refresh", id="refresh-button", color="secondary"),
            md=2,
        ),
    ],
    className="mb-4 justify-content-center",
)

# ---------------------------------------------------------
# LAYOUT
# ---------------------------------------------------------
layout = html.Div(
    [
        html.H2("Race Results — Standings", className="hero-title"),
        controls,
        html.Div(id="summary-cards"),
        dash_table.DataTable(
            id="results-table",
            columns=[
                {"name": "POS.", "id": "pos"},
                {"name": "NO.", "id": "number"},
                {"name": "DRIVER", "id": "driver"},
                {"name": "TEAM", "id": "team"},
                {"name": "TIME", "id": "time"},
                {"name": "GAP TO LEADER", "id": "gap"},
                {"name": "INTERVAL", "id": "interval"},
                {"name": "POINTS", "id": "points"},
                {"name": "LAPS", "id": "laps"},
            ],
            data=[],
            page_size=25,
            style_table={"overflowX": "auto"},
            style_header={
                "backgroundColor": "#12161d",
                "color": "#00e6c3",
                "fontWeight": "600",
                "borderBottom": "1px solid #00e6c3",
            },
            style_cell={
                "backgroundColor": "#0b0f14",
                "color": "#e6e6e6",
                "padding": "10px",
                "fontFamily": "monospace",
            },
        ),
    ],
    className="features-container",
)

# ---------------------------------------------------------
# CALLBACKS
# ---------------------------------------------------------
@callback(
    Output("race-select", "options"),
    Output("race-select", "value"),
    Input("season-select", "value"),
    Input("refresh-button", "n_clicks"),
)
def update_races(season, _):
    races = fetch_season_races(season)

    options = [
        {"label": f"{r['round']}. {r['raceName']}", "value": r["round"]}
        for r in races
    ]

    # ❌ Do NOT auto-select anything
    return options, None


@callback(
    Output("summary-cards", "children"),
    Output("results-table", "data"),
    Input("race-select", "value"),
    State("season-select", "value"),
)
def load_results(round_, season):
    if not round_:
        return None, []

    j = fetch_race_results(season, round_)
    summary = parse_race_summary(j)

    fastest = summary["fastest"]
    fastest_text = (
        f"{fastest['driver']} — {fastest['time']} (Lap {fastest['lap']})"
        if fastest else "—"
    )

    cards = html.Div(
        dbc.Row(
            [
                dbc.Col(stat_card("Race Winner", summary["winner"]), md=4),
                dbc.Col(stat_card("Fastest Lap", fastest_text), md=4),
                dbc.Col(stat_card("Circuit", summary["circuit"]), md=4),
            ],
            className="g-4 justify-content-center",
        ),
        className="results-summary",
    )

    return cards, summary["rows"]
