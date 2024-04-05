from nicegui import ui
from typing import Optional
from pathlib import Path

HEADER_HTML = (Path(__file__).parent / "static" / "header.html").read_text()
STYLE_CSS = (Path(__file__).parent / "static" / "style.css").read_text()


def add_head_html() -> None:
    """Add the code from header.html and reference style.css."""
    ui.add_head_html(HEADER_HTML + f"<style>{STYLE_CSS}</style>")


def add_header(menu: Optional[ui.left_drawer] = None) -> None:
    """Create the page header."""
    menu_items = {
        "Pourquoi ?": "/",
        "Visualiser les données": "/load_data",
        "L'usage de l'IA": "/llm",
        "Etude de cas": "/study_case",
    }

    with ui.header().classes("items-center duration-200 p-0 px-4 no-wrap").style(
        "box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1)"
    ):
        if menu:
            ui.button(on_click=menu.toggle, icon="menu").props(
                "flat color=white round"
            ).classes("lg:hidden")

        with ui.row().classes("max-[1050px]:hidden"):
            for title_, target in menu_items.items():
                ui.link(title_, target).classes(replace="text-lg text-white")
