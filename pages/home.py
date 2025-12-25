from dash import html, register_page

register_page(__name__, path="/", name="Home")

layout = html.Div(
    [
        # Background video
        html.Video(
            src="/assets/background.mp4",
            autoPlay=True,
            loop=True,
            muted=True,
            controls=False,
            preload="auto",
            className="bg-video"
        ),

        # Foreground content
        html.Div(
            [

                # HERO SECTION
                html.Div(
                    [
                        html.H1("Ultimate F1 Analytics Dashboard", className="hero-title"),
                        html.P(
                            "Don’t just watch the race. Decode it. Master the data that separates the mid-field from the World Champion by analyzing everything from raw telemetry and tyre degradation to championship-defining trends.",
                            className="hero-subtitle"
                        ),
                    ],
                    className="hero-container"
                ),

            ],
            className="content-wrapper"
        ),
    ],
    className="home-page"
)
