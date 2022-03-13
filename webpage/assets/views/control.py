import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from assets.views import plot_common

DEFAULT_IMAGE_PATH = "assets/images/AHU.PNG"

external_stylesheets = [dbc.themes.LUX]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

def make_default_figure(
    images=[DEFAULT_IMAGE_PATH],
):
    fig = plot_common.dummy_fig()
    plot_common.add_layout_images_to_fig(fig, images)
    fig.update_layout(
        {
            "margin": dict(l=0, r=0, b=0, t=0, pad=4),
        }
    )
    return fig

# Image Display
image_display = [
    dbc.Card(
        id="segmentation-card",
        children=[
            dbc.CardHeader("System"),
            dbc.CardBody(
                [
                    # Wrap dcc.Loading in a div to force transparency when loading
                    html.Div(
                        id="transparent-loader-wrapper",
                        children=[
                            dcc.Loading(
                                id="segmentations-loading",
                                type="circle",
                                children=[
                                    # Graph
                                    dcc.Graph(
                                        id="graph",
                                        figure=make_default_figure(),
                                        config={
                                            "modeBarButtonsToAdd": [
                                                "drawrect",
                                                "drawopenpath",
                                                "eraseshape",
                                            ]
                                        },
                                    ),
                                ],
                            )
                        ],
                    ),
                ]
            ),
        ],
    )
]
layout = html.Div(
    [
        dbc.Container(
            [
                dbc.Row(
                    id="app-content",
                    children=[dbc.Col(image_display, md=6)],
                )
            ],
            fluid=True,
        ),
    ]
)