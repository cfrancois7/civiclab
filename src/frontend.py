import logging
from nicegui import ui
from pathlib import Path
from .preprocess import section_data
from .extract import section_extract
from .state import State
from .header import add_header, add_head_html
from .style import section_heading, link_target, subtitle, title
from .study_case import section_study_case
from .future import section_future
from fastapi import FastAPI

path_log = Path("./log").absolute()
path_log.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    filename=path_log / "app.log", encoding="utf-8", level=logging.DEBUG
)

DATA_STATE = State(
    uploaded=False, validated=False, validated_data=None, refresh_all=False, example=""
)


########
# LAYOUT
########


def init(fastapi_app: FastAPI = None) -> None:

    def check_change_data():
        if DATA_STATE.refresh_all:
            DATA_STATE.reset()

    ui.timer(1.0, check_change_data)

    def color_apply():
        ui.colors(
            primary="#c4a45a", secondary="#53B689", accent="#111B1E", positive="#53B689"
        )

    @ui.page("/")
    def page_welcome():
        ui.page_title("Perspectiva")
        add_head_html()
        add_header()
        color_apply()
        with ui.column().classes("w-full p-8 lg:p-16"):
            section_heading(
                "Simplifier et accélérer le traitement des consultations publiques",
                "Démocratiser la consultation",
            )
            msg = """
            L'objectif d'une plateforme de consultation est d'accélérer le traitement des
            contributions des consultations publiques. En particulier, le projet vise à permettre
            le traitement des questions ouvertes. Celles-ci offrent plus d'expressivité au contributeur.
            
            Le nom de projet est *Perspectiva*, comme perspectives. En effet, c'est en multipliant les perspectives
            fidèles que l'on est mieux à même de saisir une situation.
                        
            L'objectif est triple :
            
            1. permettre le traitement des questions ouvertes de façon plus systématique,
            
            2. accélérer et faciliter le traitement des contributions dans le cadre de consultations publiques,
            
            3. démocratiser ce service en le rendant moins chronophage, donc plus accessible et moins onéreux.
            
            """
            ui.markdown(msg).classes("gap-2 bold-links arrow-links text-lg")
            ui.markdown(
                """Vous trouverez plus d'information sur la génèse de ce projet et son équipe en cliquant sur ce lien :
                [cliquez ici](https://drive.google.com/file/d/1_JuBo3rOHl3aEEgfFOuOUb6b_rdC-6TV/view?usp=sharing)"""
            ).classes("gap-2 bold-links arrow-links text-lg")

            with ui.link(
                target="https://drive.google.com/file/d/1_JuBo3rOHl3aEEgfFOuOUb6b_rdC-6TV/view?usp=sharing"
            ):
                ui.image("./image/perspectiva.png").classes("w-80")

    @ui.page("/load_data")
    def page_import():
        ui.page_title("Perspectiva")
        add_header()
        color_apply()
        # with ui.column().classes("gap-4 md:gap-8 pt-32"):
        #     title("Perspectiva")
        #     subtitle("Une plateforme pour démocratiser la consultation !")
        #     ui.link(target="#why")  # .classes("scroll-indicator")

        # with ui.column().classes("w-full p-8 lg:p-16 max-w-[1600px] mx-auto"):
        #     link_target("why", "-50px")
        #     section_heading(
        #         "Pourquoi",
        #         """La démocratie à un coût,<p>
        #         mais est un investissement précieux""",
        #     )

        with ui.column().classes("w-full p-8 lg:p-16 max-w-[1600px] mx-auto"):
            section_data(DATA_STATE)

    @ui.page("/llm")
    def page_extract():
        ui.page_title("Perspectiva")
        color_apply()
        add_header()
        with ui.column().classes("w-full p-8 lg:p-16 max-w-[1600px] mx-auto"):
            section_heading(
                "Synthétiser les contributions", "Donner de l'expression à vos données"
            )
            section_extract(DATA_STATE)

    @ui.page("/study_case")
    def page_extract():
        ui.page_title("Perspectiva")
        color_apply()
        add_header()
        with ui.column().classes("w-full p-8 lg:p-16 max-w-[1600px] mx-auto"):
            section_study_case()

    @ui.page("/future")
    def page_extract():
        ui.page_title("Perspectiva")
        color_apply()
        add_header()
        with ui.column().classes("w-full p-8 lg:p-16 max-w-[1600px] mx-auto"):
            section_future()

    if __name__ != "__main__":
        ui.run_with(fastapi_app, mount_path="/app")
    # ui.run()


# if __name__ in {"__main__", "__mp_main__"}:
#     ui.run()
#     init()
