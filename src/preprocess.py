from nicegui import ui, events
from io import StringIO
import logging
from pandas import read_csv
from pathlib import Path

from .style import link_target, section_heading
from .header import add_head_html


##########
# FUNCTION
##########
def upload_csv(data_state):
    # content = StringIO(e.content.read().decode("utf-8"))
    # data = read_csv(content, sep=separator_input.value)
    ui.notify("Data loading")
    path_data = Path("./data/LA_FISCALITE_ET_LES_DEPENSES_PUBLIQUES.csv")
    data = read_csv(path_data, low_memory=False)
    data_state.validated_data = data
    data_state.to_display = data.iloc[:200]
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
    table.rows = data_state.to_display.loc[:, selected_columns.value].to_dict("records")
    logging.info("Success update table")
    table.update()
    dropdown_select.set_options(
        ["Select a column"] + [c["name"] for c in table.columns]
    )
    dropdown_select.set_value("Select a column")
    with table.add_slot("top-left"):

        def toggle() -> None:
            table.toggle_fullscreen()
            button.props(
                "icon=fullscreen_exit" if table.is_fullscreen else "icon=fullscreen"
            )

        button = ui.button(
            "Toggle fullscreen", icon="fullscreen", on_click=toggle
        ).props("flat")
    data_state.refresh_all = True


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


########
# LAYOUT
########
@ui.refreshable
def section_data(data_state):
    global selected_columns, table, dropdown_select, upload
    global separator_input, button_plot

    add_head_html()
    with ui.row().classes(
        """ no-wrap
            justify-center items-center flex-col md:flex-row
            py-20 px-8
            lg:px-16
            gap-8 sm:gap-16 md:gap-8 lg:gap-16"""
    ):
        with ui.column():
            section_heading("Pré-traiter les données", "Explorer vos données")
            ## UPLOAD THE DATA
            ui.markdown(
                """
                Les données de consultation peuvent se retrouver sous de nombreux formats.
                Ces formats dépendent des solutions de consultation publiques qui ont chacun leur
                modules d'exportation différents. Pour le prototype, nous utiliserons les données du Grand Débat National 2019.
                Ces données sont accessibles via la plateforme
                [data.gouv.fr](https://www.data.gouv.fr/fr/datasets/grand-debat-national-debats/).
                
                Un des premiers enjeux d'une solution pereine est de développer des modules d'importation
                et de manipulation des données. Ces modules permetteront d'importer les données
                utiles à l'analyse. Voici un exemple, avec une solution compatible avec des fichiers `.csv` qui
                représentent la majorité des formats d'exportation disponibles sur 
                les solutions de consultation.
                """
            ).classes("gap-2 bold-links arrow-links text-lg")
            # separator_input = ui.input("Separator of the CSV", value=",")
            msg = """Attention: Le fichier a charger est relativement lourd (env. 500 Mo). Soyez patient.
            En cas de bug, rafraichir la page."""
            ui.markdown(msg).classes("italic gap-2 bold-links arrow-links text-lg")
            upload = ui.button(
                "Load contributions", on_click=lambda e: upload_csv(data_state)
            )
            upload.check = False

            names = [""]
            ## IF OK LOAD THE MENU

    with ui.row().classes("flex").bind_visibility(upload, "check"):

        msg = """
        Le document `.csv` est constitué d'un ensemble de lignes et de colonnes.
        Les lignes représentent un auteur, ou contributeur, quand les colonnes
        représentent l'information associé à cet auteur.
        
        Parmi ces colonnes, certainnes sont relatives aux systèmes d'acquisitions (`id`, `reference`, `createdAt`,
        `authorId`, etc...) et des colonnes relatives aux contributions en tant que telle.
        Les colonnes relatives aux systèmes d'acquisition ne nous sont pas utiles.
        Nous nous intéresserons uniquement aux colonnes des questions. Pour cela, utilisez les outils ci-dessous pour `Déselectionner tout`, puis
        sélectionner quelques colonnes des questions. Ensuite, à l'aide de l'interface sous
        le tableau, vous pouvez sélectionner une colonne et la ligne dont vous voulez observer
        le contenu. Attention, certaines questions ont été laissées sans réponse. Dans ce cas,
        un message vous préviendra.
        
        *Attention: pour des raisons de performances, seuls les 200 premières lignes sont affichées.*
        """

        ui.markdown(msg).classes("gap-2 bold-links arrow-links text-lg")
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
