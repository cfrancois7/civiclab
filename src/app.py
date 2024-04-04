import logging
from nicegui import ui
from pathlib import Path
from preprocess import section_data, section_price
from extract import section_extract
from state import State
from header import add_header
from style import section_heading, link_target, subtitle, title

path_log = Path("./log").absolute()
path_log.mkdir(exist_ok=True)
logging.basicConfig(
    filename=path_log / "app.log", encoding="utf-8", level=logging.DEBUG
)

DATA_STATE = State(
    uploaded=False, validated=False, validated_data=None, refresh_all=False, example=""
)


def check_change_data():
    if DATA_STATE.refresh_all:
        DATA_STATE.reset()


ui.timer(1.0, check_change_data)


def color_apply():
    ui.colors(
        primary="#c4a45a", secondary="#53B689", accent="#111B1E", positive="#53B689"
    )


########
# LAYOUT
########


@ui.page("/")
def page_import():
    ui.page_title("Perspectiva")
    add_header()
    color_apply()
    with ui.column().classes("gap-4 md:gap-8 pt-32"):
        title("Perspectiva")
        subtitle("Une plateforme pour démocratiser la consultation !")
        ui.link(target="#why")  # .classes("scroll-indicator")

    with ui.column().classes("w-full p-8 lg:p-16 max-w-[1600px] mx-auto"):
        link_target("why", "-50px")
        section_heading(
            "Pourquoi",
            """La démocratie à un coût,<p>
            mais est un investissement précieux""",
        )

    with ui.column().classes("w-full p-8 lg:p-16 max-w-[1600px] mx-auto"):
        link_target("load_data", "-50px")
        section_data(DATA_STATE)
        section_price()


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


# @ui.page("/gdn_vs_ours")
# def page_compare_results():

# tailwind=False
ui.run()
