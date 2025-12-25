from dash import html, register_page, dcc

register_page(__name__, path="/features", name="Features")


# ----------------------- Feature Definitions -----------------------
# I have separated the 'icon' from the 'title' here so we can style them independently
FEATURES = [
    {
        "icon": "📅", 
        "title": "Schedule",
        "desc": "Live race calendar, upcoming sessions, status indicators, and weekend flow.",
        "badge": "Live"
    },
    {
        "icon": "🏆",
        "title": "Standings",
        "desc": "Driver & Constructor standings with season progression and win visualizations.",
        "badge": "Live"
    },
    {
        "icon": "⚔️",
        "title": "Driver Comparison",
        "desc": "Lap time overlays, telemetry deltas, tire strategies, and head-to-head stats.",
        "badge": "Live"
    },
    {
        "icon": "📊",
        "title": "Season Analytics",
        "desc": "Performance trends, pace evolution, DNFs, pit stop averages, and regression charts.",
        "badge": "Live"
    },
    {
        "icon": "🏁",
        "title": "Race Analytics",
        "desc": "Battle maps, gaps over time, stint pace, race replay, and track evolution tools.",
        "badge": "Live"
    },
    {
        "icon": "🧠",
        "title": "Driver Insights",
        "desc": "Telemetry behavior patterns, braking style, throttle discipline, consistency index.",
        "badge": "Live"
    }
]


# ----------------------- Feature Card Component -----------------------
def feature_card(icon, title, desc, badge):
    return html.Div(
        [
            # Badge stays at the top right
            html.Div(badge, className="feature-badge"),
            
            # New Container: The glowing icon box
            html.Div(icon, className="feature-icon-box"),
            
            # Title and description follow
            html.H3(title, className="feature-title"),
            html.P(desc, className="feature-desc"),
        ],
        className="feature-card",
    )


# ----------------------- Page Layout -----------------------
layout = html.Div(
    [
        html.H1("Dashboard Features", className="hero-title"),
        html.P(
            "Equip yourself with a professional suite of analytics tools designed to reveal the hidden mechanics of Grand Prix racing. We provide every metric you need to analyze complex strategies and telemetry data so you can understand exactly how races are won and lost.",
            className="hero-sub"
        ),

        html.Div(
            # We now unpack the dictionary to pass 'icon' separately
            [feature_card(f["icon"], f["title"], f["desc"], f["badge"]) for f in FEATURES],
            className="feature-grid"
        ),
    ],
    className="features-container",
)