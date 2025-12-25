from dash import html, register_page

# use /season so it appears as "Season" in your navigation
register_page(__name__, path="/season", name="Season")


# ---------------------------------------------------------
# STATIC DATA
# ---------------------------------------------------------
DRIVERS = [
    {"pos": 1, "name": "Lando Norris", "team": "McLaren", "points": 408, "logo": "/assets/mclaren.png"},
    {"pos": 2, "name": "Max Verstappen", "team": "Red Bull", "points": 396, "logo": "/assets/redbull.png"},
    {"pos": 3, "name": "Oscar Piastri", "team": "McLaren", "points": 392, "logo": "/assets/mclaren.png"},
]

CONSTRUCTORS = [
    {"pos": 1, "team": "McLaren", "points": 800, "logo": "/assets/mclaren.png"},
    {"pos": 2, "team": "Red Bull Racing", "points": 620, "logo": "/assets/redbull.png"},
    {"pos": 3, "team": "Mercedes", "points": 459, "logo": "/assets/mercedes.png"},
]

# ---------------------------------------------------------
# COMPONENTS
# ---------------------------------------------------------
def standings_row(pos, name, points, logo):
    return html.Div(
        [
            html.Span(str(pos), style={"width": "30px", "color": "#aaa"}),
            html.Img(src=logo, style={"height": "26px", "marginRight": "10px"}),
            html.Span(name, style={"flex": "1"}),
            html.Span(str(points), style={"color": "#00ff9c"}),
        ],
        style={
            "display": "flex",
            "alignItems": "center",
            "padding": "10px 0",
            "borderBottom": "1px solid #222",
            "color": "white",
        },
    )


def column_card(title, rows):
    return html.Div(
        [
            html.H3(title, style={"marginBottom": "15px", "textAlign": "left"}),
            *rows,
        ],
        style={
            "background": "rgba(11, 15, 26, 0.85)",
            "backdropFilter": "blur(8px)",
            "padding": "25px",
            "borderRadius": "16px",
            "width": "48%",
            "boxShadow": "0 20px 40px rgba(0,0,0,0.5)",
        },
    )

# ---------------------------------------------------------
# LAYOUT
# ---------------------------------------------------------
layout = html.Div(
    [
        # ---------- HEADER (CENTERED, NO ICON) ----------
        html.Div(
            [
                html.H1(
                    "Season Analysis",
                    style={
                        "color": "white",
                        "textAlign": "center",
                        "fontSize": "48px",
                        "marginBottom": "10px",
                    },
                ),
                html.P(
                    "Drivers vs Constructors performance overview",
                    style={
                        "color": "white",
                        "textAlign": "center",
                        "fontSize": "18px",
                        "marginBottom": "60px",
                    },
                ),
            ]
        ),

        # ---------- CARDS ----------
        html.Div(
            [
                column_card(
                    "Drivers Championship",
                    [standings_row(d["pos"], d["name"], d["points"], d["logo"]) for d in DRIVERS],
                ),
                column_card(
                    "Constructors Championship",
                    [standings_row(c["pos"], c["team"], c["points"], c["logo"]) for c in CONSTRUCTORS],
                ),
            ],
            style={
                "display": "flex",
                "justifyContent": "center",
                "gap": "40px",
            },
        ),
    ],
    style={
        "minHeight": "100vh",
        "padding": "60px",
        "backgroundImage": "url('/assets/background.jpg')",
        "backgroundSize": "cover",
        "backgroundPosition": "center",
        "backgroundRepeat": "no-repeat",
    },
)
