from dash import html, register_page

register_page(__name__, path="/about", name="About")

layout = html.Div(
    [
        html.H1(
            "About",
            style={
                "color": "white",
                "fontSize": "50px",
                "fontWeight": "bold",
                "margin-top": "10px", 
                "margin-bottom": "12px",
                "textAlign": "left"
            },
        ),

        html.P(
            "Motorsport isn't just something I watch — it's something I've studied, rewound, questioned, "
            "and obsessed over. What started as curiosity turned into a passion to understand performance "
            "beyond commentary, beyond assumptions, and beyond team narratives. I created this dashboard "
            "to explore races with clarity and evidence, transforming timing data and telemetry into "
            "meaningful insight rather than noise.",
            style={"color": "#ccc", "fontSize": "19px", "lineHeight": "1.75", "marginBottom": "25px"},
        ),

        html.P(
            "Here, every chart and visualization is designed to reveal pace, execution, and racecraft — "
            "not hype. The goal is to make analysis engaging yet objective, technical yet accessible. "
            "Whether you're revisiting a qualifying session frame by frame or breaking down strategy calls, "
            "this space is built to help make sense of the sport at its most granular level.",
            style={"color": "#ccc", "fontSize": "19px", "lineHeight": "1.75", "marginBottom": "25px"},
        ),

        html.P(
            "As the project grows, more analytics, comparisons, and interactive tools will be added — carefully, "
            "methodically, and always guided by data rather than preference. My aim remains simple: provide a clear "
            "and unbiased way to explore Formula 1 performance, where numbers tell the story and every lap counts.",
            style={"color": "#ccc", "fontSize": "19px", "lineHeight": "1.75", "marginBottom": "50px"},
        ),

        html.Div(
            "— Anshuman Phadke",
            className="signature",

            style={
                "color": "white",
                "fontSize": "50px",
                "fontFamily": "'Alex Brush', 'Parisienne', cursive",
                "marginTop": "30px",
                "textAlign": "left",
                "letterSpacing": "1px",
            },
        )

    ],

    style={
        "padding": "60px",
        "maxWidth": "900px",
        "margin": "auto"
    }
)
