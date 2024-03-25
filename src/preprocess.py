from nicegui import ui, events, app
from io import StringIO
import logging
from pandas import read_csv
import plotly.graph_objects as go
import plotly.express as px
import numpy as np


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
    dropdown_select.set_options([c["name"] for c in table.columns])
    dropdown_select.set_value("")
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
    data_state.example = selected_row[key]


def deselect_all():
    selected_columns.set_value([])


def create_plot(data):
    # plot the statistics of the images
    col = dropdown_select.value
    contributions = data.loc[:, col].dropna().values
    words_contribution = [len(c.split(" ")) for c in contributions]

    with ui.row().classes("flex-1 overflow-x-auto"):
        title = f"{col}"
        fig = px.histogram(
            x=np.log10(words_contribution),
            log_y=True,
            title=title,
        )
        fig.update_layout(xaxis_title_text="log distribution of length")
        plot = ui.plotly(fig)


########
# LAYOUT
########
@ui.refreshable
def section_data(data_state):
    global selected_columns, table, dropdown_select, upload
    global separator_input, button_plot
    # UPLOAD THE DATA
    with ui.column():
        ui.markdown(
            """
            La solution est compatible avec des fichiers `.csv` et `.json` qui
            représentent la majorité des formats d'exportation disponibles sur 
            les solutions de consultation.
            """
        ).classes("gap-2 bold-links arrow-links text-lg")
        with ui.row():
            separator_input = ui.input("Separator of the CSV", value=",")

        with ui.row():
            upload = ui.upload(on_upload=lambda e: upload_csv(e, data_state))
            upload.check = False

        names = [""]
        # IF OK LOAD THE MENU
        with ui.column().bind_visibility(upload, "check"):
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

            with ui.row():
                table = ui.table(
                    columns=[], rows=[], pagination={"rowsPerPage": 5}
                ).classes("max-w-screen-lg  overflow-x-auto")
                table.on("rowClick", lambda row: select_row(data_state, row))
            ui.markdown(
                "Sélectionner une columne, puis une ligne du tableau pour afficher la valeur."
            ).classes("gap-2 text-md")
            dropdown_select = ui.select(options=[]).classes("text-lg")

            with ui.row().classes("flex flex-row w-full"):
                with ui.scroll_area().classes("flex-1 overflow-x-auto border"):
                    ui.markdown().bind_content_from(data_state, "example").classes(
                        "italic justify gap-1 text-lg"
                    )
            # calculate the statistics for the selected row
            plot = None
            button_plot = ui.button(
                "Calculer les statistiques",
                on_click=lambda e: create_plot(upload.data),
            )
