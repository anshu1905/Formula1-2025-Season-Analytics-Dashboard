from dash import html, dcc, register_page, callback, Input, Output
import folium
import datetime
import os
import traceback

# ---------------------------------------------------------
# CONSTANTS
# ---------------------------------------------------------
WORLD_ZOOM = 5
MAP_FILE = "assets/f1_map.html"

register_page(__name__, path="/schedule", name="Schedule")

# ---------------------------------------------------------
# 2025 F1 SEASON DATA
# ---------------------------------------------------------
SEASON_2025 = [
    {"round": 1, "name": "Bahrain GP", "lat": 26.0325, "lon": 50.5106, "date": "2025-03-02"},
    {"round": 2, "name": "Saudi Arabian GP", "lat": 21.6319, "lon": 39.1044, "date": "2025-03-09"},
    {"round": 3, "name": "Australian GP", "lat": -37.8497, "lon": 144.968, "date": "2025-03-23"},
    {"round": 4, "name": "Japanese GP", "lat": 34.8431, "lon": 136.5419, "date": "2025-04-06"},
    {"round": 5, "name": "Chinese GP", "lat": 31.3389, "lon": 121.22, "date": "2025-04-20"},
    {"round": 6, "name": "Miami GP", "lat": 25.9581, "lon": -80.2389, "date": "2025-05-04"},
    {"round": 7, "name": "Emilia Romagna GP", "lat": 44.3439, "lon": 11.7167, "date": "2025-05-18"},
    {"round": 8, "name": "Monaco GP", "lat": 43.7347, "lon": 7.4206, "date": "2025-05-25"},
    {"round": 9, "name": "Canadian GP", "lat": 45.5, "lon": -73.5228, "date": "2025-06-08"},
    {"round": 10, "name": "Spanish GP", "lat": 41.57, "lon": 2.2611, "date": "2025-06-22"},
    {"round": 11, "name": "Austrian GP", "lat": 47.2197, "lon": 14.7647, "date": "2025-06-29"},
    {"round": 12, "name": "British GP", "lat": 52.0786, "lon": -1.0169, "date": "2025-07-06"},
    {"round": 13, "name": "Hungarian GP", "lat": 47.5789, "lon": 19.2486, "date": "2025-07-20"},
    {"round": 14, "name": "Belgian GP", "lat": 50.4372, "lon": 5.9714, "date": "2025-07-27"},
    {"round": 15, "name": "Dutch GP", "lat": 52.3888, "lon": 4.5409, "date": "2025-08-31"},
    {"round": 16, "name": "Italian GP", "lat": 45.6156, "lon": 9.2811, "date": "2025-09-07"},
    {"round": 17, "name": "Azerbaijan GP", "lat": 40.3725, "lon": 49.8533, "date": "2025-09-21"},
    {"round": 18, "name": "Singapore GP", "lat": 1.2914, "lon": 103.8644, "date": "2025-10-05"},
    {"round": 19, "name": "United States GP", "lat": 30.1328, "lon": -97.6411, "date": "2025-10-19"},
    {"round": 20, "name": "Mexico City GP", "lat": 19.4042, "lon": -99.0907, "date": "2025-10-26"},
    {"round": 21, "name": "São Paulo GP", "lat": -23.7036, "lon": -46.6997, "date": "2025-11-09"},
    {"round": 22, "name": "Las Vegas GP", "lat": 36.1147, "lon": -115.1728, "date": "2025-11-22"},
    {"round": 23, "name": "Qatar GP", "lat": 25.49, "lon": 51.4542, "date": "2025-11-29"},
    {"round": 24, "name": "Abu Dhabi GP", "lat": 24.4672, "lon": 54.6031, "date": "2025-12-07"},
]

# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------
def get_next_race(races):
    today = datetime.date.today()
    for r in races:
        if datetime.date.fromisoformat(r["date"]) >= today:
            return r
    return races[-1]


def build_folium_map(races, selected_round):
    """
    FIXED:
    - No date-based fallback
    - No silent override to Abu Dhabi
    - Trust dropdown value completely
    """

    selected_round_int = int(selected_round)
    selected_race = next(r for r in races if r["round"] == selected_round_int)

    m = folium.Map(
        location=[selected_race["lat"], selected_race["lon"]],
        zoom_start=WORLD_ZOOM,
        tiles="CartoDB.Positron",
        control_scale=True
    )

    for r in races:
        is_selected = (r["round"] == selected_round_int)
        folium.Marker(
            location=[r["lat"], r["lon"]],
            tooltip=f"{r['name']} — {r['date']}",
            icon=folium.Icon(
                color="green" if is_selected else "red",
                icon="flag",
                prefix="fa"
            )
        ).add_to(m)

    os.makedirs(os.path.dirname(MAP_FILE), exist_ok=True)
    m.save(MAP_FILE)


# ---------------------------------------------------------
# INITIAL MAP
# ---------------------------------------------------------
initial_race = get_next_race(SEASON_2025)
build_folium_map(SEASON_2025, initial_race["round"])


# ---------------------------------------------------------
# LAYOUT (UNCHANGED)
# ---------------------------------------------------------
layout = html.Div(
    style={"height": "100vh", "width": "100vw", "position": "relative"},
    children=[

        html.Iframe(
            id="folium-map",
            src="/assets/f1_map.html",
            style={"height": "100%", "width": "100%", "border": "none"},
        ),

        html.Div(
            style={
                "position": "absolute",
                "top": "20px",
                "left": "20px",
                "width": "360px",
                "background": "rgba(0,0,0,0.75)",
                "padding": "16px",
                "borderRadius": "14px",
                "zIndex": 1000
            },
            children=[
                html.H2("F1 Season Schedule", style={"color": "white", "margin": "0 0 8px 0"}),

                dcc.Dropdown(
                    id="gp-dropdown",
                    options=[
                        {"label": f"R{r['round']} – {r['name']}", "value": r["round"]}
                        for r in SEASON_2025
                    ],
                    value=initial_race["round"],
                    clearable=False,
                    style={
                        "marginTop": "10px",
                        "color": "black",
                        "backgroundColor": "white"
                    },
                    persistence=True,
                    persistence_type="session"
                ),
            ]
        )
    ]
)

# ---------------------------------------------------------
# CALLBACK
# ---------------------------------------------------------
@callback(
    Output("folium-map", "src"),
    Input("gp-dropdown", "value")
)
def update_map(selected_round):
    try:
        build_folium_map(SEASON_2025, selected_round)
    except Exception:
        print("Error building folium map:", traceback.format_exc())

    ts = int(datetime.datetime.now().timestamp())
    return f"/assets/f1_map.html?ts={ts}"
