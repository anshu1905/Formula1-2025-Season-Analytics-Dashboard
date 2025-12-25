from dash import Dash, html, dcc
import dash
import dash_bootstrap_components as dbc

app = Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[dbc.themes.DARKLY],
    suppress_callback_exceptions=True
)

server = app.server

# Desired page order
NAV_ORDER = [
    "Home",
    "Features",
    "About",
    "Schedule",
    "Season",
    "Standings",
    "Race",
    "Comparisons",
    "Driver"
]

# Sort pages based on custom order
sorted_pages = sorted(
    dash.page_registry.values(),
    key=lambda x: NAV_ORDER.index(x["name"])
)

# Navigation links
nav_links = [
    dcc.Link(
        page["name"],
        href=page["relative_path"],
        className="navbar-link"
    )
    for page in sorted_pages
]

app.layout = html.Div(
    [
        html.Div(
            html.Div(nav_links, className="navbar-link-container"),
            className="navbar",
            # ADD THIS STYLE TO SET A SOLID BLACK BACKGROUND
            style={"background-color": "#0b0b0b"} 
        ),
        dash.page_container
    ],
    # This style is fine, keep it for overall transparency
    style={
        "fontFamily": "sans-serif",
        "background-color": "transparent"
    }
)

if __name__ == "__main__":
    app.run(debug=True)