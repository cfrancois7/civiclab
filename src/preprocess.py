from nicegui import ui, events, app
from io import StringIO
import logging
from pandas import read_csv
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from pandas import DataFrame, MultiIndex
from style import link_target, section_heading
from header import add_head_html


##########
# FUNCTION
##########
def upload_csv(e: events.UploadEventArguments, data_state):
    content = StringIO(e.content.read().decode("utf-8"))
    data = read_csv(content, sep=separator_input.value, low_memory=False)
    upload.data = data
    upload.check = True
    columns = list(data.columns)
    selected_columns.set_options(columns)
    selected_columns.set_value(columns)
    selected_columns.update()
    data_state.refresh_all = True


def update_table(data_state):
    columns = [
        {"name": col, "label": col, "field": col, "align": "left"}
        for col in selected_columns.value
    ]
    table.columns = columns
    table.rows = upload.data.loc[:, selected_columns.value].to_dict("records")
    table.update()
    dropdown_select.set_options(
        ["Select a column"] + [c["name"] for c in table.columns]
    )
    dropdown_select.set_value("Select a column")
    dropdown_stats.set_options([c["name"] for c in table.columns])
    dropdown_stats.set_value("")
    with table.add_slot("top-left"):

        def toggle() -> None:
            table.toggle_fullscreen()
            button.props(
                "icon=fullscreen_exit" if table.is_fullscreen else "icon=fullscreen"
            )

        button = ui.button(
            "Toggle fullscreen", icon="fullscreen", on_click=toggle
        ).props("flat")
    logging.info(columns)
    data_state.refresh_all = True


def valid_data(data_state, upload):
    validated_data = upload.data.loc[:, selected_columns.value]
    data_state.validated = True
    data_state.data = validated_data
    ui.notify(f"Data validated! You have selected:\n{selected_columns.value}")


def select_row(data_state, row):
    selected_row = row.args[1]
    key = dropdown_select.value
    selection = selected_row.get(key)
    if selection is None:
        selection = """```
        WARNING: no contribution for this selection.
        
        Select another row.
        ```"""
    data_state.example = selection


def deselect_all():
    selected_columns.set_value([])


def update_stats_plot():
    global fig_stats, plot_stats, fig_price, plot_price
    # STATISTICS
    ## parse data
    data = upload.data
    col = dropdown_stats.value
    contributions = data.loc[:, col].dropna().values
    words_contribution = [len(c.split(" ")) for c in contributions]
    length_character = [len(c) for c in contributions]

    ## reset plot trace
    fig_stats.data = []
    # fig.layout = {}

    ## reset plot trace
    traces = list(
        px.histogram(
            x=np.log10(words_contribution),
            log_y=True,
        ).select_traces()
    )[0]
    fig_stats.add_trace(traces)
    plot_stats.update()

    # PRICE
    model = ["GPT 3.5", "GPT 4"]
    type_price = ["context", "generation"]
    price_context = np.array([0.5, 30]) / 1e6
    price_generation = np.array([1.5, 60]) / 1e6
    length_token = np.sum(np.array(length_character) / 3)
    prices_context = (length_token + 536) * price_context
    prices_generation = length_token * 2 * price_generation

    df_price = (
        DataFrame(
            data=np.concatenate([prices_context, prices_generation]),
            index=MultiIndex.from_product(
                [model, type_price], names=["model", "token type"]
            ),
        )
        .reset_index()
        .melt(id_vars=["model", "token type"])
    )

    ## reset plot trace
    fig_price.data = []
    # fig.layout = {}

    ## reset plot trace
    traces = list(
        px.bar(
            df_price,
            x="model",
            y="value",
            color="token type",
        ).select_traces()
    )
    for trace in traces:
        fig_price.add_trace(trace)
    plot_price.update()

    button_plot.active = True


########
# LAYOUT
########
@ui.refreshable
def section_data(data_state):
    global selected_columns, table, dropdown_select, upload
    global separator_input, button_plot

    section_heading("Pré-traiter les données", "Explorer vos données")
    ## UPLOAD THE DATA
    ui.markdown(
        """
        La solution est compatible avec des fichiers `.csv` et `.json` qui
        représentent la majorité des formats d'exportation disponibles sur 
        les solutions de consultation.
        """
    ).classes("gap-2 bold-links arrow-links text-lg")
    separator_input = ui.input("Separator of the CSV", value=",")
    upload = ui.upload(on_upload=lambda e: upload_csv(e, data_state))
    upload.check = False

    names = [""]
    ## IF OK LOAD THE MENU
    with ui.row().classes("h-screen").bind_visibility(upload, "check"):
        selected_columns = (
            ui.select(
                names,
                multiple=True,
                value=names,
                label="Select columns",
                on_change=lambda e: update_table(data_state),
            )
            .props("use-chips")
            .classes("max-w-screen-lg")
        )
        ui.button("Deselect all", on_click=deselect_all)

        table = ui.table(columns=[], rows=[], pagination={"rowsPerPage": 5}).classes(
            "max-w-screen-lg  overflow-x-auto"
        )
        table.on("rowClick", lambda row: select_row(data_state, row))

        ## DISPLAY TEXT FROM SELECTION
        ui.markdown(
            "Sélectionner une columne, puis une ligne du tableau pour afficher la valeur."
        ).classes("gap-2 text-md")
        dropdown_select = ui.select(
            options=["Select a column"], value="Select a column"
        ).classes("text-lg")
        with ui.row().classes("flex flex-row w-full"):
            with ui.scroll_area().classes("flex-1 overflow-x-auto border"):
                ui.markdown().bind_content_from(data_state, "example").classes(
                    "italic justify gap-1 text-lg"
                )
        ui.link(target="#prix").classes("scroll-indicator")

    ## PLOTS AND STATISTICS


@ui.refreshable
def section_price():
    add_head_html()
    global button_plot
    with ui.column().bind_visibility(upload, "check"):
        section_heading("Le prix de l'automatisation", "Des coûts accessibles")
        link_target("prix")
        with ui.row():
            global dropdown_stats
            dropdown_stats = (
                ui.select(options=["Select a column"], value="Select a column")
                .classes("text-lg")
                .classes("max-w-screen-lg")
            )
        with ui.row():
            button_plot = ui.button(
                "Calculer les statistiques",
                on_click=update_stats_plot,
            )
            button_plot.active = False
        with ui.row().bind_visibility(button_plot, "active"):
            global fig_stats, plot_stats
            with ui.column():
                fig_stats = go.Figure()
                fig_stats.update_layout(
                    # margin=dict(l=0, r=0, t=0, b=0),
                    title_text="""Distribution des taille des contributions en nombre de mot
                    <br>(échelle logarithmique)""",
                    title_font_size=18,
                    xaxis_title="Logarithme 10 (Taille des contributions)",
                    yaxis_title="Occurence",
                )
                plot_stats = ui.plotly(fig_stats)
            with ui.row():
                # TODO: TRANSFOR PLOT INTO BAR PLOT WITH PRICE GPT 3.5 and GPT4
                global fig_price, plot_price
                fig_price = go.Figure()
                fig_price.update_layout(
                    # margin=dict(l=0, r=0, t=0, b=0),
                    title_text="""Prix du traitement de la question en $ US""",
                    title_font_size=18,
                    yaxis_title="Total price ($ US)",
                )
                plot_price = ui.plotly(fig_price)
